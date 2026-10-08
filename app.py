"""
Aplicación web principal con Streamlit para clasificación de cobertura terrestre.
"""
import streamlit as st
import yaml
import os
import sys
import numpy as np
import torch

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from descarga import descargar_imagen_s2, guardar_imagen_geotiff
from clasificacion import clasificar_imagen, calcular_estadisticas
from visualizacion import (
    visualizar_mapa,
    visualizar_imagen_rgb,
    crear_mapa_interactivo,
    guardar_resultados,
    COLORES_CLASES,
)


def cargar_configuracion():
    """Carga la configuración desde config.yaml."""
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    # Configuración de la página
    config = cargar_configuracion()
    st.set_page_config(
        page_title=config["app"]["titulo"],
        page_icon="🛰️",
        layout="wide",
    )

    # Título
    st.title("🛰️ Clasificación de Cobertura Terrestre")
    st.subheader(f"Zona de estudio: {config['zona']['nombre']}, Colombia")

    # Información del dispositivo
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    if dispositivo == "cuda":
        st.success(f"✅ GPU detectada: {torch.cuda.get_device_name(0)}")
    else:
        st.info("ℹ️  Usando CPU (la clasificación será más lenta pero funcional)")

    # Sidebar con opciones
    st.sidebar.header("⚙️ Configuración")

    # Fechas
    fecha_inicio = st.sidebar.date_input(
        "Fecha de inicio",
        value=None,
        help="Selecciona la fecha para la imagen satelital"
    )

    # Tamaño de parche
    tamano_parche = st.sidebar.slider(
        "Tamaño de parche (px)",
        min_value=32,
        max_value=128,
        value=config["modelo"]["tamano_parche"],
        step=32,
        help="Tamaño de los parches para clasificación"
    )

    # Solapamiento
    solapamiento = st.sidebar.slider(
        "Solapamiento entre parches (px)",
        min_value=0,
        max_value=32,
        value=0,
        step=16,
        help="Solapamiento entre parches consecutivos"
    )

    # Botón de clasificación
    if st.sidebar.button("🚀 Clasificar Cobertura", type="primary"):
        with st.spinner("Descargando imagen Sentinel-2..."):
            # Descargar imagen
            bbox = config["zona"]["bbox"]
            fechas = (config["fechas"]["inicio"], config["fechas"]["fin"])

            imagen = descargar_imagen_s2(bbox, fechas)

            if imagen is None:
                st.error("❌ No se pudo descargar la imagen. Verifica tus credenciales de Sentinel Hub.")
                return

            # Mostrar imagen RGB
            st.subheader("📷 Imagen Sentinel-2 (RGB)")
            fig_rgb = visualizar_imagen_rgb(imagen)
            st.pyplot(fig_rgb)

            # Clasificar
            with st.spinner("Clasificando cobertura terrestre..."):
                mapa, clases, confianzas = clasificar_imagen(
                    imagen,
                    tamano_parche=tamano_parche,
                    solapamiento=solapamiento,
                    dispositivo=dispositivo,
                )

            # Mostrar resultados
            st.subheader("🗺️ Mapa de Cobertura Terrestre")
            fig_mapa = visualizar_mapa(mapa, clases, titulo=f"Cobertura - {config['zona']['nombre']}")
            st.pyplot(fig_mapa)

            # Estadísticas
            st.subheader("📊 Estadísticas de Cobertura")
            estadisticas = calcular_estadisticas(mapa, clases)

            # Mostrar en columnas
            cols = st.columns(2)
            for i, (clase, datos) in enumerate(estadisticas.items()):
                with cols[i % 2]:
                    st.metric(
                        label=clase,
                        value=f"{datos['porcentaje']}%",
                        delta=f"{datos['pixeles']} píxeles"
                    )

            # Guardar resultados
            ruta_salida = os.path.join(os.path.dirname(__file__), "resultados")
            guardar_resultados(mapa, clases, estadisticas, ruta_salida)

            st.success("✅ Resultados guardados en la carpeta 'resultados/'")

    # Información adicional
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Información")
    st.sidebar.markdown("""
    **Modelo**: ResNet-18 pre-entrenado en EuroSAT
    **Resolución**: 10m (Sentinel-2)
    **Clases**: 10 tipos de cobertura

    **Zona**: San Andrés, Colombia
    **Coordenadas**: 12.5567°N, 81.7185°O
    """)

    # Instrucciones
    with st.expander("📖 Instrucciones de uso"):
        st.markdown("""
        1. **Configura las fechas** en el panel lateral
        2. **Ajusta el tamaño de parche** según necesites (64px recomendado)
        3. **Haz clic en "Clasificar Cobertura"**
        4. **Espera** a que se descargue la imagen y se procese
        5. **Explora** el mapa y las estadísticas generadas

        **Nota**: La primera ejecución puede tardar varios minutos debido a la descarga del modelo y la imagen.
        """)

    # Requisitos
    with st.expander("🔧 Requisitos y configuración"):
        st.markdown("""
        **Credenciales de Sentinel Hub**:
        1. Crea una cuenta gratuita en [Copernicus Data Space](https://dataspace.copernicus.eu/)
        2. Configura las variables de entorno:
           - `SENTINELHUB_CLIENT_ID`
           - `SENTINELHUB_CLIENT_SECRET`

        **Instalación**:
        ```bash
        pip install -r requirements.txt
        streamlit run app.py
        ```
        """)


if __name__ == "__main__":
    main()
