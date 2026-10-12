"""
Visualización de mapas y gráficos para el clasificador de cobertura terrestre.
"""

import folium
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import config


def agregar_ee_al_mapa(mapa, imagen, vis_params, nombre):
    """
    Añade una capa de Google Earth Engine al mapa de folium.
    
    Parámetros:
        mapa (folium.Map): Mapa destino.
        imagen (ee.Image): Imagen de GEE.
        vis_params (dict): Parámetros de visualización.
        nombre (str): Nombre de la capa.
    """
    map_id_dict = imagen.getMapId(vis_params)
    folium.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Google Earth Engine',
        name=nombre,
        overlay=True,
        control=True
    ).add_to(mapa)


def crear_mapa(lat, lon, zoom=12):
    """
    Crea un mapa centrado en las coordenadas dadas.
    
    Parámetros:
        lat (float): Latitud.
        lon (float): Longitud.
        zoom (int): Nivel de zoom inicial.
    
    Retorna:
        folium.Map: Mapa creado.
    """
    return folium.Map(location=[lat, lon], zoom_start=zoom)


def generar_leyenda_html(clases=None):
    """
    Genera el HTML para la leyenda del mapa.
    
    Parámetros:
        clases (dict, optional): Diccionario de clases. Si None, usa config.CLASES.
    
    Retorna:
        str: HTML de la leyenda.
    """
    if clases is None:
        clases = config.CLASES
    
    leyenda_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; 
                background-color: white; 
                padding: 10px; 
                border: 2px solid grey; 
                border-radius: 5px; 
                z-index: 9999; 
                font-size: 14px;">
    <b>Leyenda - Cobertura Terrestre</b><br>
    """
    for i in range(len(clases)):
        leyenda_html += f'<div style="display:flex;align-items:center;margin:2px;">'
        leyenda_html += f'<div style="width:20px;height:20px;background:{clases[i]["color"]};margin-right:5px;"></div>'
        leyenda_html += f'<span>{clases[i]["nombre"]}</span></div>'
    leyenda_html += "</div>"
    
    return leyenda_html


def crear_mapa_clasificado(clasificada, lat, lon, zoom=12):
    """
    Crea un mapa interactivo con la clasificación y leyenda.
    
    Parámetros:
        clasificada (ee.Image): Imagen clasificada.
        lat (float): Latitud central.
        lon (float): Longitud central.
        zoom (int): Nivel de zoom inicial.
    
    Retorna:
        folium.Map: Mapa con clasificación y leyenda.
    """
    mapa = crear_mapa(lat, lon, zoom)
    agregar_ee_al_mapa(mapa, clasificada, config.VIS_CLASIFICACION, 'Cobertura Clasificada')
    folium.LayerControl().add_to(mapa)
    
    # Añadir leyenda
    leyenda_html = generar_leyenda_html()
    mapa.get_root().html.add_child(folium.Element(leyenda_html))
    
    return mapa


def crear_grafico_barras(datos, clases=None):
    """
    Crea un gráfico de barras horizontales con las estadísticas.
    
    Parámetros:
        datos (list): Lista de diccionarios con 'clase', 'area_km2', 'porcentaje'.
        clases (dict, optional): Diccionario de clases para colores.
    
    Retorna:
        matplotlib.figure.Fecha: Figura creada.
    """
    if clases is None:
        clases = config.CLASES
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    nombres = [d['clase'] for d in datos]
    areas = [d['area_km2'] for d in datos]
    colores = [clases[i]['color'] for i in range(len(datos))]
    
    bars = ax.barh(nombres, areas, color=colores, edgecolor='black')
    ax.set_xlabel('Área (km²)')
    ax.set_title('Área por Cobertura Terrestre')
    ax.grid(axis='x', alpha=0.3)
    
    # Añadir valores
    for bar, area in zip(bars, areas):
        ax.text(bar.get_width() + max(areas) * 0.01, 
                bar.get_y() + bar.get_height() / 2,
                f'{area:.2f} km²', va='center', fontsize=9)
    
    plt.tight_layout()
    return fig


def crear_grafico_pastel(datos, clases=None):
    """
    Crea un gráfico de pastel con los porcentajes.
    
    Parámetros:
        datos (list): Lista de diccionarios con 'clase', 'area_km2', 'porcentaje'.
        clases (dict, optional): Diccionario de clases para colores.
    
    Retorna:
        matplotlib.figure.Figure: Figura creada.
    """
    if clases is None:
        clases = config.CLASES
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    nombres = [d['clase'] for d in datos]
    porcentajes = [d['porcentaje'] for d in datos]
    colores = [clases[i]['color'] for i in range(len(datos))]
    
    ax.pie(porcentajes, labels=nombres, colors=colores,
           autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
    ax.set_title('Porcentaje de Cobertura Terrestre')
    
    plt.tight_layout()
    return fig


def crear_comparacion_rgb_clasificado(imagen_rgb, clasificada, lat, lon, zoom=12):
    """
    Crea una comparación lado a lado entre RGB y clasificación.
    
    Parámetros:
        imagen_rgb (ee.Image): Imagen RGB original.
        clasificada (ee.Image): Imagen clasificada.
        lat (float): Latitud central.
        lon (float): Longitud central.
        zoom (int): Nivel de zoom inicial.
    
    Retorna:
        tuple: (mapa_rgb, mapa_clasificado)
    """
    # Mapa RGB
    mapa_rgb = crear_mapa(lat, lon, zoom)
    agregar_ee_al_mapa(mapa_rgb, imagen_rgb, config.VIS_RGB, 'RGB')
    folium.LayerControl().add_to(mapa_rgb)
    
    # Mapa clasificado
    mapa_clas = crear_mapa_clasificado(clasificada, lat, lon, zoom)
    
    return mapa_rgb, mapa_clas
