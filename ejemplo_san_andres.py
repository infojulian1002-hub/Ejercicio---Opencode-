"""
Ejemplo rápido de uso del Clasificador de Cobertura Terrestre.
Ejecuta: python ejemplo_san_andres.py
"""

import sys
import os

# Añadir directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import LATITUD, LONGITUD, BUFFER_METROS, MAX_NUBES, MESES_HISTORICO
from src.auth import inicializar_ee
from src.data import preparar_imagen
from src.indices import calcular_todos
from src.classification import clasificar
from src.visualization import (
    crear_mapa_clasificado, crear_grafico_barras, 
    crear_grafico_pastel, agregar_ee_al_mapa, crear_mapa
)
from src.stats import calcular_estadisticas, imprimir_resumen


def main():
    """Ejecuta el análisis completo de cobertura terrestre."""
    
    print("=" * 60)
    print("CLASIFICADOR DE COBERTURA TERRESTRE")
    print("San Andrés y Providencia, Colombia")
    print("=" * 60)
    
    # Paso 1: Autenticación
    print("\n[1/5] Autenticando con Google Earth Engine...")
    exito = inicializar_ee()
    if not exito:
        print("Error en autenticación. Verifica tus credenciales.")
        return
    print("✓ Autenticación exitosa")
    
    # Paso 2: Preparar imagen
    print("\n[2/5] Descargando imagen Sentinel-2...")
    imagen, zona, info = preparar_imagen(LATITUD, LONGITUD, MESES_HISTORICO, MAX_NUBES)
    print(f"✓ Imagen del {info['fecha']} ({info['nubes']}% nubes)")
    print(f"  Imágenes disponibles: {info['num_imagenes']}")
    
    # Paso 3: Calcular índices
    print("\n[3/5] Calculando índices espectrales...")
    indices = calcular_todos(imagen)
    print("✓ NDVI, NDWI, MNDWI, NDBI, SAVI calculados")
    
    # Paso 4: Clasificar
    print("\n[4/5] Clasificando cobertura terrestre...")
    clasificada = clasificar(
        indices['ndvi'], indices['ndwi'], 
        indices['mndwi'], indices['ndbi'], indices['savi']
    )
    clasificada = clasificada.clip(zona)
    print("✓ Clasificación completada")
    
    # Paso 5: Estadísticas
    print("\n[5/5] Calculando estadísticas...")
    datos, total_area = calcular_estadisticas(clasificada, zona)
    
    # Imprimir resumen
    imprimir_resumen(datos, total_area, info['fecha'], info['nubes'])
    
    # Generar visualizaciones
    print("\nGenerando visualizaciones...")
    
    # Mapa RGB
    mapa_rgb = crear_mapa(LATITUD, LONGITUD)
    agregar_ee_al_mapa(mapa_rgb, imagen, __import__('config').VIS_RGB, 'RGB')
    
    # Mapa clasificado
    mapa_clas = crear_mapa_clasificado(clasificada, LATITUD, LONGITUD)
    
    # Gráficos
    fig_barras = crear_grafico_barras(datos)
    fig_pastel = crear_grafico_pastel(datos)
    
    # Guardar resultados
    fig_barras.savefig('grafico_barras.png', dpi=150, bbox_inches='tight')
    fig_pastel.savefig('grafico_pastel.png', dpi=150, bbox_inches='tight')
    mapa_clas.save('mapa_cobertura.html')
    
    print("✓ Archivos generados:")
    print("  - mapa_cobertura.html (ábrelo en tu navegador)")
    print("  - grafico_barras.png")
    print("  - grafico_pastel.png")
    
    print("\n" + "=" * 60)
    print("¡Análisis completado exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    main()
