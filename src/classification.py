"""
Clasificación de cobertura terrestre basada en reglas espectrales.
"""

import ee
from config import UMBRALES_DEFAULT


def clasificar(ndvi, ndwi, mndwi, ndbi, savi=None, umbrales=None):
    """
    Clasifica cobertura terrestre basada en umbrales de índices espectrales.
    
    Clases:
        0: Agua
        1: Suelo desnudo / Playas
        2: Pastos / Matorral
        3: Agricultura
        4: Bosque
        5: Urbano
    
    Parámetros:
        ndvi (ee.Image): Índice NDVI.
        ndwi (ee.Image): Índice NDWI.
        mndwi (ee.Image): Índice MNDWI.
        ndbi (ee.Image): Índice NDBI.
        savi (ee.Image, optional): Índice SAVI para refuerzo.
        umbrales (dict, optional): Diccionario con umbrales personalizados.
    
    Retorna:
        ee.Image: Imagen clasificada (valores 0-5).
    """
    if umbrales is None:
        umbrales = UMBRALES_DEFAULT
    
    # 0: Agua (MNDWI alto O NDWI muy alto)
    agua = (mndwi.gt(umbrales['mndwi_agua']).Or(
            ndwi.gt(umbrales['ndwi_agua']))).multiply(0)
    
    # 1: Suelo desnudo (NDVI muy bajo, NDWI bajo)
    suelo = (ndvi.lt(umbrales['ndvi_suelo_max']).And(
             ndwi.lt(0.1))).multiply(1)
    
    # 2: Pastos/Matorral (NDVI bajo-medio)
    pastos = (ndvi.gte(umbrales['ndvi_pastos_min']).And(
              ndvi.lt(umbrales['ndvi_pastos_max']))).multiply(2)
    
    # 3: Agricultura (NDVI medio, SAVI medio)
    if savi is not None:
        agricultura = (ndvi.gte(umbrales['ndvi_agricultura_min']).And(
                       ndvi.lt(umbrales['ndvi_agricultura_max'])).And(
                       savi.gte(0.2)).And(
                       savi.lt(0.5))).multiply(3)
    else:
        agricultura = (ndvi.gte(umbrales['ndvi_agricultura_min']).And(
                       ndvi.lt(umbrales['ndvi_agricultura_max']))).multiply(3)
    
    # 4: Bosque (NDVI alto, SAVI alto)
    if savi is not None:
        bosque = (ndvi.gte(umbrales['ndvi_bosque_min']).And(
                  savi.gte(umbrales['savi_bosque_min']))).multiply(4)
    else:
        bosque = ndvi.gte(umbrales['ndvi_bosque_min']).multiply(4)
    
    # 5: Urbano (NDBI alto o NDVI muy bajo con NDBI medio)
    urbano = (ndbi.gt(umbrales['ndbi_urbano']).Or(
              ndvi.lt(0.15).And(ndbi.gt(-0.1)))).multiply(5)
    
    # Combinar todas las clases (la última sobrescribe a la anterior)
    clasificacion = (agua.add(suelo).add(pastos)
                      .add(agricultura).add(bosque).add(urbano))
    
    return clasificacion.rename('clase')


def reclasificar_interactivo(ndvi, ndwi, mndwi, ndbi, savi=None, **kwargs):
    """
    Reclasifica con umbrales ajustables (interfaz Streamlit).
    
    Parámetros:
        **kwargs: Umbrales personalizados.
    
    Retorna:
        ee.Image: Imagen clasificada.
    """
    umbrales = UMBRALES_DEFAULT.copy()
    umbrales.update(kwargs)
    return clasificar(ndvi, ndwi, mndwi, ndbi, savi, umbrales)
