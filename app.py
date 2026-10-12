"""
Aplicación Streamlit - Clasificador de Cobertura Terrestre
San Andrés y Providencia, Colombia
"""

import streamlit as st
import ee
import sys
import os

# Añadir directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import (
    LATITUD, LONGITUD, BUFFER_METROS, MAX_NUBES, MESES_HISTORICO,
    VIS_RGB, VIS_CLASIFICACION, CLASES, PALETA_COLORES, UMBRALES_DEFAULT
)
from src.auth import inicializar_ee
from src.data import preparar_imagen
from src.indices import calcular_todos
from src.classification import clasificar, reclasificar_interactivo
from src.visualization import (
    crear_mapa, agregar_ee_al_mapa, crear_mapa_clasificado,
    crear_grafico_barras, crear_grafico_pastel, generar_leyenda_html
)
from src.stats import calcular_estadisticas, generar_dataframe, imprimir_resumen


def main():
    """Función principal de la aplicación Streamlit."""
    
    # Inicializar session_state para el botón de reset
    if 'reset_umbrales' not in st.session_state:
        st.session_state.reset_umbrales = False
    
    # Configuración de página
    st.set_page_config(
        page_title="Clasificador de Cobertura Terrestre",
        page_icon="🛰️",
        layout="wide"
    )
    
    # Título
    st.title("🛰️ Clasificador de Cobertura Terrestre")
    st.subheader("San Andrés y Providencia, Colombia")
    st.markdown("---")
    
    # Sidebar - Configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Autenticación
        st.subheader("Autenticación GEE")
        proyecto_id = st.text_input(
            "ID del proyecto Google Cloud (opcional)",
            value="",
            help="Déjalo vacío si usaste ee.Authenticate() en Colab"
        )
        
        # Zona de estudio
        st.subheader("Zona de Estudio")
        lat = st.number_input("Latitud", value=LATITUD, format="%.4f")
        lon = st.number_input("Longitud", value=LONGITUD, format="%.4f")
        buffer_km = st.number_input("Radio (km)", min_value=1, value=BUFFER_METROS // 1000)
        
        # Parámetros de imagen
        st.subheader("Parámetros de Imagen")
        max_nubes = st.slider("Máx. nubosidad (%)", min_value=1, max_value=50, value=MAX_NUBES)
        meses = st.slider("Meses hacia atrás", min_value=1, max_value=24, value=MESES_HISTORICO)
        
        # Umbrales
        st.subheader("Umbrales de Clasificación")
        st.caption("⚠️ Ajusta según la zona. Valores por defecto son solo un punto de partida.")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Restablecer valores", help="Volver a los valores por defecto"):
                st.session_state.reset_umbrales = True
                st.rerun()
        
        if st.session_state.get('reset_umbrales', False):
            mndwi_agua = UMBRALES_DEFAULT['mndwi_agua']
            ndvi_bosque = UMBRALES_DEFAULT['ndvi_bosque_min']
            ndbi_urbano = UMBRALES_DEFAULT['ndbi_urbano']
            st.session_state.reset_umbrales = False
        else:
            mndwi_agua = st.slider("MNDWI Agua", min_value=0.0, max_value=1.0, 
                                   value=UMBRALES_DEFAULT['mndwi_agua'], step=0.05)
            ndvi_bosque = st.slider("NDVI Bosque", min_value=0.2, max_value=1.0,
                                    value=UMBRALES_DEFAULT['ndvi_bosque_min'], step=0.05)
            ndbi_urbano = st.slider("NDBI Urbano", min_value=-0.5, max_value=0.5,
                                    value=UMBRALES_DEFAULT['ndbi_urbano'], step=0.05)
        
        # Botón de análisis
        st.markdown("---")
        iniciar_analisis = st.button("🔍 Iniciar Análisis", type="primary")
    
    # Contenido principal
    if iniciar_analisis:
        try:
            with st.spinner("Conectando con Google Earth Engine..."):
                # Inicializar GEE
                exito = inicializar_ee(proyecto_id if proyecto_id else None)
                if not exito:
                    st.error("No se pudo autenticar con GEE. Verifica tus credenciales.")
                    return
            
            with st.spinner("Descargando imagen Sentinel-2..."):
                # Preparar imagen
                imagen, zona, info = preparar_imagen(
                    lat, lon, 
                    meses_historico=meses, 
                    max_nubes=max_nubes
                )
            
            st.success(f"Imagen del {info['fecha']} ({info['nubes']}% nubes)")
            
            # Calcular índices
            with st.spinner("Calculando índices espectrales..."):
                indices = calcular_todos(imagen)
            
            # Clasificar
            with st.spinner("Clasificando cobertura terrestre..."):
                clasificada = reclasificar_interactivo(
                    indices['ndvi'], indices['ndwi'], 
                    indices['mndwi'], indices['ndbi'], indices['savi'],
                    mndwi_agua=mndwi_agua,
                    ndvi_bosque_min=ndvi_bosque,
                    ndbi_urbano=ndbi_urbano
                )
                clasificada = clasificada.clip(zona)
            
            # Calcular estadísticas
            with st.spinner("Calculando estadísticas..."):
                datos, total_area = calcular_estadisticas(clasificada, zona)
                df = generar_dataframe(datos)
            
            # Mostrar resultados
            st.markdown("---")
            st.header("📊 Resultados")
            
            # Mapa clasificado
            st.subheader("Mapa de Cobertura")
            mapa = crear_mapa_clasificado(clasificada, lat, lon)
            st.components.v1.html(mapa._repr_html_(), height=600)
            
            # Estadísticas
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Área por Cobertura")
                st.dataframe(df.style.format({
                    'area_km2': '{:.2f}',
                    'porcentaje': '{:.1f}%'
                }))
            
            with col2:
                st.subheader("Gráfico de Barras")
                fig_barras = crear_grafico_barras(datos)
                st.pyplot(fig_barras)
            
            # Gráfico de pastel
            st.subheader("Distribución Porcentual")
            fig_pastel = crear_grafico_pastel(datos)
            st.pyplot(fig_pastel)
            
            # Resumen
            st.markdown("---")
            st.header("📝 Resumen")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Área Total", f"{total_area:.2f} km²")
            with col2:
                st.metric("Fecha Imagen", info['fecha'])
            with col3:
                st.metric("Nubosidad", f"{info['nubes']}%")
            
            st.markdown("---")
            st.caption("Desarrollado con Google Earth Engine + Python")
        
        except Exception as e:
            st.error(f"Error durante el análisis: {str(e)}")
            st.info("Verifica tu conexión a internet y autenticación con GEE.")
    
    else:
        # Pantalla inicial
        st.info("👈 Configura los parámetros en el sidebar y presiona **Iniciar Análisis**")
        
        st.markdown("---")
        st.markdown("""
        ### ¿Qué hace esta aplicación?
        
        Esta herramienta clasifica la cobertura terrestre de San Andrés y Providencia 
        usando imágenes **Sentinel-2** de la ESA y **Google Earth Engine**.
        
        ### Coberturas detectadas:
        """)
        
        for i in range(len(CLASES)):
            st.markdown(f"- **{CLASES[i]['nombre']}**: {CLASES[i]['descripcion']}")
        
        st.markdown("""
        ### Fuente de datos
        - **Imágenes**: Sentinel-2 L2A (10m resolución)
        - **Plataforma**: Google Earth Engine
        - **Índices**: NDVI, NDWI, MNDWI, NDBI, SAVI
        """)


if __name__ == "__main__":
    main()
