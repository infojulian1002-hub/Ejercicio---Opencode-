"""
Cálculo de estadísticas de cobertura terrestre.
"""

import ee
import pandas as pd
from config import CLASES, ESCALA_M, MAX_PIXELES


def calcular_estadisticas(clasificada, zona, escala=ESCALA_M):
    """
    Calcula el área en km² y porcentaje para cada clase de cobertura.
    
    Parámetros:
        clasificada (ee.Image): Imagen clasificada.
        zona (ee.Geometry): Área de estudio.
        escala (int): Resolución espacial en metros.
    
    Retorna:
        tuple: (datos, total_area) donde datos es una lista de diccionarios.
    """
    # Área de cada píxel en km²
    pixel_area = ee.Image.pixelArea().divide(1e6)  # m² a km²
    
    datos = []
    total_area = 0
    
    for clase_id in range(len(CLASES)):
        # Crear máscara para la clase
        mask = clasificada.eq(clase_id)
        
        # Sumar área de píxeles de esta clase
        area = (pixel_area.updateMask(mask)
                .reduceRegion(
                    reducer=ee.Reducer.sum(),
                    geometry=zona,
                    scale=escala,
                    maxPixels=MAX_PIXELES
                ).getInfo())
        
        area_valor = list(area.values())[0] if area else 0
        total_area += area_valor
        
        datos.append({
            'clase_id': clase_id,
            'clase': CLASES[clase_id]['nombre'],
            'color': CLASES[clase_id]['color'],
            'area_km2': area_valor,
            'porcentaje': 0,  # Se calcula después
        })
    
    # Calcular porcentajes
    for d in datos:
        if total_area > 0:
            d['porcentaje'] = (d['area_km2'] / total_area) * 100
        else:
            d['porcentaje'] = 0
    
    return datos, total_area


def generar_dataframe(datos):
    """
    Convierte los estadísticas en un DataFrame de pandas.
    
    Parámetros:
        datos (list): Lista de diccionarios con estadísticas.
    
    Returns:
        pd.DataFrame: DataFrame con las estadísticas.
    """
    df = pd.DataFrame(datos)
    return df[['clase', 'area_km2', 'porcentaje', 'color']]


def imprimir_resumen(datos, total_area, fecha=None, nubes=None):
    """
    Imprime un resumen formateado de las estadísticas.
    
    Parámetros:
        datos (list): Lista de diccionarios con estadísticas.
        total_area (float): Área total en km².
        fecha (str, optional): Fecha de la imagen.
        nubes (float, optional): Porcentaje de nubosidad.
    """
    print("=" * 60)
    print("ESTADÍSTICAS DE COBERTURA TERRESTRE")
    print("Zona: San Andrés y Providencia")
    if fecha:
        print(f"Imagen: {fecha}")
    if nubes is not None:
        print(f"Nubosidad: {nubes}%")
    print("=" * 60)
    print(f"{'Clase':<30} {'km²':>10} {'%':>10}")
    print("-" * 50)
    
    for d in datos:
        print(f"{d['clase']:<30} {d['area_km2']:>10.2f} {d['porcentaje']:>9.1f}%")
    
    print("-" * 50)
    print(f"{'TOTAL':<30} {total_area:>10.2f} {100.0:>9.1f}%")
    print("=" * 60)
