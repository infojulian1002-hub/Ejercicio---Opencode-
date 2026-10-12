"""
Descarga y preparación de imágenes Sentinel-2 desde Google Earth Engine.
"""

import ee
from config import (
    COLECCION_S2, MAX_NUBES, MESES_HISTORICO, VIS_RGB, BUFFER_METROS
)


def definir_zona(lat, lon, buffer_metros=BUFFER_METROS):
    """
    Define la zona de estudio como un buffer circular.
    
    Parámetros:
        lat (float): Latitud del punto central.
        lon (float): Longitud del punto central.
        buffer_metros (int): Radio del buffer en metros.
    
    Retorna:
        ee.Geometry: Geometría del área de estudio.
    """
    punto = ee.Geometry.Point([lon, lat])
    return punto.buffer(buffer_metros).bounds()


def buscar_imagen(zona, fecha_inicio, fecha_fin, max_nubes=MAX_NUBES):
    """
    Busca la imagen Sentinel-2 con menos nubosidad en el rango de fechas.
    
    Parámetros:
        zona (ee.Geometry): Área de estudio.
        fecha_inicio (str): Fecha inicial (YYYY-MM-DD).
        fecha_fin (str): Fecha final (YYYY-MM-DD).
        max_nubes (int): Porcentaje máximo de nubosidad permitido.
    
    Retorna:
        ee.Image: Imagen Sentinel-2 seleccionada.
    """
    coleccion = (ee.ImageCollection(COLECCION_S2)
                 .filterBounds(zona)
                 .filterDate(fecha_inicio, fecha_fin)
                 .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_nubes))
                 .sort('CLOUDY_PIXEL_PERCENTAGE'))
    
    imagen = ee.Image(coleccion.first())
    return imagen


def obtener_info_imagen(imagen):
    """
    Obtiene metadatos relevantes de la imagen.
    
    Parámetros:
        imagen (ee.Image): Imagen de GEE.
    
    Retorna:
        dict: Información con fecha, nubosidad y número de imágenes disponibles.
    """
    info = imagen.getInfo()
    fecha = imagen.date().format('YYYY-MM-dd').getInfo()
    nubes = imagen.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
    
    return {
        'fecha': fecha,
        'nubes': nubes,
        'info_completa': info,
    }


def preparar_imagen(lat, lon, meses_historico=MESES_HISTORICO, max_nubes=MAX_NUBES):
    """
    Flujo completo: define zona, busca imagen y retorna imagen recortada.
    
    Parámetros:
        lat (float): Latitud del punto central.
        lon (float): Longitud del punto central.
        meses_historico (int): Número de meses hacia atrás para buscar.
        max_nubes (int): Porcentaje máximo de nubosidad.
    
    Retorna:
        tuple: (imagen_recortada, zona, info)
    """
    # Definir zona
    zona = definir_zona(lat, lon)
    
    # Rango de fechas
    fecha_fin = ee.Date('2026-09-01')
    fecha_inicio = fecha_fin.advance(-meses_historico, 'month')
    
    # Buscar imagen
    imagen = buscar_imagen(zona, fecha_inicio, fecha_fin, max_nubes)
    
    # Obtener información
    info = obtener_info_imagen(imagen)
    
    # Recortar a la zona
    imagen_recortada = imagen.clip(zona)
    
    # Verificar que hay imágenes disponibles
    coleccion = (ee.ImageCollection(COLECCION_S2)
                 .filterBounds(zona)
                 .filterDate(fecha_inicio, fecha_fin)
                 .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_nubes)))
    num_imagenes = coleccion.size().getInfo()
    
    if num_imagenes == 0:
        raise ValueError(
            f"No se encontraron imágenes con menos de {max_nubes}% de nubes. "
            f"Intenta aumentar el umbral de nubosidad o el rango de fechas."
        )
    
    info['num_imagenes'] = num_imagenes
    
    return imagen_recortada, zona, info
