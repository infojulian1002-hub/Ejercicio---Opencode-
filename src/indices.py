"""
Cálculo de índices espectrales a partir de bandas Sentinel-2.
"""

import ee


def calcular_ndvi(imagen):
    """
    NDVI - Normalized Difference Vegetation Index.
    Fórmula: (NIR - Rojo) / (NIR + Rojo)
    Rango: [-1, 1], donde > 0.4 indica vegetación densa.
    
    Parámetros:
        imagen (ee.Image): Imagen Sentinel-2.
    
    Retorna:
        ee.Image: Índice NDVI.
    """
    return imagen.normalizedDifference(['B8', 'B4']).rename('NDVI')


def calcular_ndwi(imagen):
    """
    NDWI - Normalized Difference Water Index.
    Fórmula: (Verde - NIR) / (Verde + NIR)
    Rango: [-1, 1], donde > 0.3 indica agua.
    
    Parámetros:
        imagen (ee.Image): Imagen Sentinel-2.
    
    Retorna:
        ee.Image: Índice NDWI.
    """
    return imagen.normalizedDifference(['B3', 'B8']).rename('NDWI')


def calcular_mndwi(imagen):
    """
    MNDWI - Modified Normalized Difference Water Index.
    Fórmula: (Verde - SWIR) / (Verde + SWIR)
    Mejor que NDWI para distinguir agua de sombras.
    
    Parámetros:
        imagen (ee.Image): Imagen Sentinel-2.
    
    Retorna:
        ee.Image: Índice MNDWI.
    """
    return imagen.normalizedDifference(['B3', 'B11']).rename('MNDWI')


def calcular_ndbi(imagen):
    """
    NDBI - Normalized Difference Built-up Index.
    Fórmula: (SWIR - NIR) / (SWIR + NIR)
    Valores altos indican zonas urbanizadas.
    
    Parámetros:
        imagen (ee.Image): Imagen Sentinel-2.
    
    Retorna:
        ee.Image: Índice NDBI.
    """
    return imagen.normalizedDifference(['B11', 'B8']).rename('NDBI')


def calcular_savi(imagen, L=0.5):
    """
    SAVI - Soil Adjusted Vegetation Index.
    Fórmula: ((NIR - Rojo) / (NIR + Rojo + L)) * (1 + L)
    Ajusta el NDVI en zonas con suelo expuesto.
    
    Parámetros:
        imagen (ee.Image): Imagen Sentinel-2.
        L (float): Factor de corrección del suelo (0 = NDVI, 1 = sin suelo).
    
    Retorna:
        ee.Image: Índice SAVI.
    """
    savi = imagen.expression(
        '((NIR - RED) / (NIR + RED + L)) * (1 + L)', {
            'NIR': imagen.select('B8'),
            'RED': imagen.select('B4'),
            'L': L
        })
    return savi.rename('SAVI')


def calcular_todos(imagen):
    """
    Calcula todos los índices espectrales de una vez.
    
    Parámetros:
        imagen (ee.Image): Imagen Sentinel-2.
    
    Retorna:
        dict: Diccionario con todos los índices calculados.
    """
    return {
        'ndvi': calcular_ndvi(imagen),
        'ndwi': calcular_ndwi(imagen),
        'mndwi': calcular_mndwi(imagen),
        'ndbi': calcular_ndbi(imagen),
        'savi': calcular_savi(imagen),
    }
