# =============================================================================
# CLASIFICADOR DE COBERTURA TERRESTRE - SAN ANDRÉS Y PROVIDENCIA
# Usando Google Earth Engine + Índices Espectrales
# =============================================================================
# INSTRUCCIONES:
# 1. Abre Google Colab (https://colab.research.google.com)
# 2. Crea un nuevo cuaderno
# 3. Pega cada sección en una celda separada
# 4. Ejecuta en orden (Shift+Enter)
# =============================================================================

# =============================================================================
# CELDA 1: INSTALACIÓN Y AUTENTICACIÓN (solo primera vez)
# =============================================================================
# !pip install earthengine-api folium ipywidgets -q

# import ee

# --- AUTENTICACIÓN EN GOOGLE COLAB ---
# Opción 1: Autenticación estándar (funciona en la mayoría de casos)
# ee.Authenticate()
# ee.Initialize(project='tu-proyecto-id')

# Opción 2: Si la Opción 1 falla con "credential propagation was unsuccessful",
# usa este método alternativo:
# import google.auth
# credentials, project = google.auth.default()
# ee.Initialize(credentials, project='tu-proyecto-id')

# Opción 3: Autenticación manual con código (si las anteriores fallan)
# ee.Authenticate()
# ee.Initialize()

print("✓ Autenticación completada")

# =============================================================================
# CELDA 2: IMPORTAR BIBLIOTECAS Y CONFIGURAR
# =============================================================================
import ee
import folium
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
warnings.filterwarnings('ignore')

# Configurar visualización en Colab
ee.Initialize()

# =============================================================================
# CELDA 3: DEFINIR ÁREA DE ESTUDIO
# =============================================================================
# Coordenadas de San Andrés
lat = 12.55
lon = -81.72
buffer_metros = 5000  # 5 km de radio

# Crear geometría
punto = ee.Geometry.Point([lon, lat])
zona = punto.buffer(buffer_metros).bounds()

# Parámetros de visualización
vis_rgb = {
    'min': 0,
    'max': 3000,
    'bands': ['B4', 'B3', 'B2'],
    'gamma': 1.4
}

# =============================================================================
# CELDA 4: OBTENER IMAGEN SENTINEL-2 MÁS LIMPIA
# =============================================================================
# Rango de fechas (últimos 12 meses)
fecha_fin = ee.Date('2026-09-01')
fecha_inicio = fecha_fin.advance(-12, 'month')

# Colección Sentinel-2 L2A
coleccion = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
             .filterBounds(zona)
             .filterDate(fecha_inicio, fecha_fin)
             .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15))
             .sort('CLOUDY_PIXEL_PERCENTAGE'))

# Seleccionar imagen con menos nubes
imagen = ee.Image(coleccion.first())

# Obtener metadatos
info = imagen.getInfo()
fecha_adquisicion = imagen.date().format('YYYY-MM-dd').getInfo()
porcentaje_nubes = imagen.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()

print(f"Imagen seleccionada:")
print(f"  Fecha: {fecha_adquisicion}")
print(f"  Nubosidad: {porcentaje_nubes}%")
print(f"  Número de imágenes disponibles: {coleccion.size().getInfo()}")

# Recortar a la zona de estudio
imagen = imagen.clip(zona)

# =============================================================================
# CELDA 5: VISUALIZACIÓN RGB EN MAPA INTERACTIVO
# =============================================================================
def agregar_ee_al_mapa(mapa, imagen, vis_params, nombre):
    """Añade una capa de Google Earth Engine al mapa de folium."""
    map_id_dict = ee.Image(imagen).getMapId(vis_params)
    folium.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Google Earth Engine',
        name=nombre,
        overlay=True,
        control=True
    ).add_to(mapa)

# Crear mapa
mapa = folium.Map(location=[lat, lon], zoom_start=12)
agregar_ee_al_mapa(mapa, imagen, vis_rgb, 'Sentinel-2 RGB')
folium.LayerControl().add_to(mapa)
mapa

# =============================================================================
# CELDA 6: CALCULAR ÍNDICES ESPECTRALES
# =============================================================================
# NDVI - Vegetación (NIR - Rojo) / (NIR + Rojo)
ndvi = imagen.normalizedDifference(['B8', 'B4']).rename('NDVI')

# NDWI - Agua (Verde - NIR) / (Verde + NIR)
ndwi = imagen.normalizedDifference(['B3', 'B8']).rename('NDWI')

# MNDWI - Agua mejorada (Verde - SWIR) / (Verde + SWIR)
mndwi = imagen.normalizedDifference(['B3', 'B11']).rename('MNDWI')

# NDBI - Construcción (SWIR - NIR) / (SWIR + NIR)
ndbi = imagen.normalizedDifference(['B11', 'B8']).rename('NDBI')

# SAVI - Vegetación ajustada al suelo (L=0.5)
savi = (imagen.expression(
    '((NIR - RED) / (NIR + RED + L)) * (1 + L)', {
        'NIR': imagen.select('B8'),
        'RED': imagen.select('B4'),
        'L': 0.5
    })).rename('SAVI')

print("Índices calculados: NDVI, NDWI, MNDWI, NDBI, SAVI")

# =============================================================================
# CELDA 7: VISUALIZAR ÍNDICES INDIVIDUALES
# =============================================================================
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Índices Espectrales - San Andrés', fontsize=14, fontweight='bold')

indices = [
    ('NDVI', ndvi, 'RdYlGn'),
    ('NDWI', ndwi, 'Blues'),
    ('MNDWI', mndwi, 'Blues'),
    ('NDBI', ndbi, 'hot'),
    ('SAVI', savi, 'RdYlGn'),
]

for idx, (nombre, indice, cmap) in enumerate(indices):
    ax = axes[idx // 3, idx % 3]
    # Extraer array numpy para visualización
    # Nota: En Colab, usamos getInfo() para obtener valores
    ax.set_title(nombre)
    ax.axis('off')

axes[1, 2].axis('off')
plt.tight_layout()
plt.show()

# =============================================================================
# CELDA 8: CLASIFICACIÓN POR REGLAS ESPECTRALES
# =============================================================================
def clasificar_cobertura(ndvi, ndwi, mndwi, ndbi, savi):
    """
    Clasifica cobertura terrestre basada en umbrales de índices espectrales.
    
    Clases:
    0: Agua
    1: Suelo desnudo / Playas
    2: Pastos / Matorral
    3: Agricultura
    4: Bosque
    5: Urbano
    """
    # Crear imagen vacía (clase por defecto)
    clasificacion = ee.Image(0).rename('clase')
    
    # 0: Agua (MNDWI alto O NDWI muy alto)
    agua = (mndwi.gt(0.3).Or(ndwi.gt(0.5))).multiply(0)
    
    # 1: Suelo desnudo (NDVI muy bajo, NDWI bajo)
    suelo = ndvi.lt(0.1).And(ndwi.lt(0.1)).multiply(1)
    
    # 2: Pastos/Matorral (NDVI bajo-medio)
    pastos = ndvi.gte(0.1).And(ndvi.lt(0.3)).And(savi.lt(0.35)).multiply(2)
    
    # 3: Agricultura (NDVI medio, SAVI medio)
    agricultura = ndvi.gte(0.2).And(ndvi.lt(0.45)).And(savi.gte(0.2)).And(savi.lt(0.5)).multiply(3)
    
    # 4: Bosque (NDVI alto, SAVI alto)
    bosque = ndvi.gte(0.4).And(savi.gte(0.4)).multiply(4)
    
    # 5: Urbano (NDBI alto o NDVI muy bajo con NDBI medio)
    urbano = ndbi.gt(0.05).Or(ndvi.lt(0.15).And(ndbi.gt(-0.1))).multiply(5)
    
    # Combinar todas las clases (la última sobrescribe a la anterior)
    clasificacion = (agua.add(suelo).add(pastos)
                      .add(agricultura).add(bosque).add(urbano))
    
    return clasificacion

# Aplicar clasificación
clasificada = clasificar_cobertura(ndvi, ndwi, mndwi, ndbi, savi)
clasificada = clasificada.clip(zona)

print("✓ Clasificación completada")

# =============================================================================
# CELDA 9: CONFIGURAR LEYENDA Y COLORES
# =============================================================================
# Diccionario de clases
CLASES = {
    0: {'nombre': 'Agua', 'color': '#1E90FF'},
    1: {'nombre': 'Suelo desnudo / Playas', 'color': '#F5DEB3'},
    2: {'nombre': 'Pastos / Matorral', 'color': '#9ACD32'},
    3: {'nombre': 'Agricultura', 'color': '#FFA500'},
    4: {'nombre': 'Bosque', 'color': '#228B22'},
    5: {'nombre': 'Urbano', 'color': '#DC143C'},
}

colores = [CLASES[i]['color'] for i in range(6)]
cmap = ListedColormap(colores)

# =============================================================================
# CELDA 10: VISUALIZAR MAPA CLASIFICADO
# =============================================================================
# Crear mapa clasificado
mapa_clas = folium.Map(location=[lat, lon], zoom_start=12)

# Parámetros de visualización para clasificación
vis_clas = {
    'min': 0,
    'max': 5,
    'palette': colores
}

agregar_ee_al_mapa(mapa_clas, clasificada, vis_clas, 'Cobertura Clasificada')
folium.LayerControl().add_to(mapa_clas)

# Añadir leyenda HTML
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
for i in range(6):
    leyenda_html += f'<div style="display:flex;align-items:center;margin:2px;">'
    leyenda_html += f'<div style="width:20px;height:20px;background:{CLASES[i]["color"]};margin-right:5px;"></div>'
    leyenda_html += f'<span>{CLASES[i]["nombre"]}</span></div>'
leyenda_html += "</div>"

mapa_clas.get_root().html.add_child(folium.Element(leyenda_html))
mapa_clas

# =============================================================================
# CELDA 11: ESTADÍSTICAS POR CLASE
# =============================================================================
def calcular_estadistica(clase_id, zona, escala=10):
    """Calcula área en km² para una clase específica."""
    pixel_area = ee.Image.pixelArea().divide(1e6)  # m² a km²
    mask = clasificada.eq(clase_id)
    area = pixel_area.updateMask(mask).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=zona,
        scale=escala,
        maxPixels=1e9
    ).getInfo()
    return list(area.values())[0] if area else 0

# Calcular estadísticas
print("=" * 50)
print("ESTADÍSTICAS DE COBERTURA TERRESTRE")
print("Zona: San Andrés y Providencia")
print(f"Imagen: {fecha_adquisicion}")
print("=" * 50)
print(f"{'Clase':<30} {'km²':>10} {'%':>10}")
print("-" * 50)

total_area = 0
datos = []
for clase_id in range(6):
    area = calcular_estadistica(clase_id, zona)
    total_area += area
    datos.append({
        'clase': CLASES[clase_id]['nombre'],
        'area_km2': area
    })

for d in datos:
    porcentaje = (d['area_km2'] / total_area * 100) if total_area > 0 else 0
    d['porcentaje'] = porcentaje
    print(f"{d['clase']:<30} {d['area_km2']:>10.2f} {porcentaje:>9.1f}%")

print("-" * 50)
print(f"{'TOTAL':<30} {total_area:>10.2f} {100.0:>9.1f}%")
print("=" * 50)

# =============================================================================
# CELDA 12: GRÁFICO DE BARRAS
# =============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Distribución de Cobertura Terrestre - San Andrés', 
             fontsize=14, fontweight='bold')

# Gráfico de barras
clases_nombres = [d['clase'] for d in datos]
areas = [d['area_km2'] for d in datos]
colores_grafico = [CLASES[i]['color'] for i in range(len(datos))]

bars = ax1.barh(clases_nombres, areas, color=colores_grafico, edgecolor='black')
ax1.set_xlabel('Área (km²)')
ax1.set_title('Área por Cobertura')
ax1.grid(axis='x', alpha=0.3)

# Añadir valores
for i, (bar, area) in enumerate(zip(bars, areas)):
    ax1.text(bar.get_width() + max(areas)*0.01, bar.get_y() + bar.get_height()/2,
             f'{area:.2f} km²', va='center', fontsize=9)

# Gráfico de pastel
ax2.pie(areas, labels=clases_nombres, colors=colores_grafico, 
        autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
ax2.set_title('Porcentaje de Cobertura')

plt.tight_layout()
plt.show()

# =============================================================================
# CELDA 13: COMPARACIÓN RGB vs CLASIFICADO
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 8))
fig.suptitle('Comparación: Imagen Real vs Clasificación', 
             fontsize=14, fontweight='bold')

# Mapa RGB
mapa_rgb = folium.Map(location=[lat, lon], zoom_start=12)
agregar_ee_al_mapa(mapa_rgb, imagen, vis_rgb, 'RGB')
folium.LayerControl().add_to(mapa_rgb)

# Mapa clasificado
mapa_clas_comp = folium.Map(location=[lat, lon], zoom_start=12)
agregar_ee_al_mapa(mapa_clas_comp, clasificada, vis_clas, 'Clasificado')
folium.LayerControl().add_to(mapa_clas_comp)

# Mostrar mapas (nota: en Colab se muestran como imágenes estáticas)
axes[0].set_title('Imagen Sentinel-2 RGB')
axes[0].axis('off')
axes[1].set_title('Cobertura Clasificada')
axes[1].axis('off')

# Capturar mapas como imágenes (simplificación)
plt.tight_layout()
plt.show()

# =============================================================================
# CELDA 14: INTERFAZ INTERACTIVA PARA AJUSTAR UMBRALES
# =============================================================================
def reclasificar_interactivo(ndvi_agua=0.3, ndwi_agua=0.5, 
                              ndvi_suelo=0.1, ndvi_pastos_min=0.1, ndvi_pastos_max=0.3,
                              ndvi_bosque=0.4, ndbi_urbano=0.05):
    """
    Reclasifica con umbrales ajustables.
    """
    clasificacion = ee.Image(0).rename('clase')
    
    agua = (mndwi.gt(ndvi_agua).Or(ndwi.gt(ndwi_agua))).multiply(0)
    suelo = ndvi.lt(ndvi_suelo).And(ndwi.lt(0.1)).multiply(1)
    pastos = ndvi.gte(ndvi_pastos_min).And(ndvi.lt(ndvi_pastos_max)).multiply(2)
    bosque = ndvi.gte(ndvi_bosque).multiply(4)
    urbano = ndbi.gt(ndbi_urbano).multiply(5)
    
    nueva_clas = agua.add(suelo).add(pastos).add(bosque).add(urbano).clip(zona)
    return nueva_clas

# Crear sliders
style = {'description_width': 'initial'}
slider_ndvi_agua = widgets.FloatSlider(value=0.3, min=0.0, max=1.0, step=0.05, 
                                        description='MNDWI Agua:', style=style)
slider_ndwi_agua = widgets.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, 
                                        description='NDWI Agua:', style=style)
slider_ndvi_suelo = widgets.FloatSlider(value=0.1, min=0.0, max=0.5, step=0.05, 
                                         description='NDVI Suelo:', style=style)
slider_ndvi_bosque = widgets.FloatSlider(value=0.4, min=0.2, max=1.0, step=0.05, 
                                          description='NDVI Bosque:', style=style)
slider_ndbi_urbano = widgets.FloatSlider(value=0.05, min=-0.5, max=0.5, step=0.05, 
                                          description='NDBI Urbano:', style=style)

out = widgets.Output()

def on_reclassificar(_):
    with out:
        clear_output(wait=True)
        nueva = reclasificar_interactivo(
            ndvi_agua=slider_ndvi_agua.value,
            ndwi_agua=slider_ndwi_agua.value,
            ndvi_suelo=slider_ndvi_suelo.value,
            ndvi_bosque=slider_ndvi_bosque.value,
            ndbi_urbano=slider_ndbi_urbano.value
        )
        
        # Mostrar nuevo mapa
        mapa_nuevo = folium.Map(location=[lat, lon], zoom_start=12)
        agregar_ee_al_mapa(mapa_nuevo, nueva, vis_clas, 'Nueva Clasificación')
        display(mapa_nuevo)

boton = widgets.Button(description='Reclasificar', button_style='primary')
boton.on_click(on_reclassificar)

widgets.VBox([
    widgets.HTML("<h3>Ajusta los umbrales de clasificación:</h3>"),
    slider_ndvi_agua,
    slider_ndwi_agua,
    slider_ndvi_suelo,
    slider_ndvi_bosque,
    slider_ndbi_urbano,
    boton,
    out
])

# =============================================================================
# CELDA 15: GUARDAR RESULTADOS (opcional)
# =============================================================================
def exportar_resultados():
    """Exporta la clasificación como GeoTIFF a Google Drive."""
    tarea = ee.batch.Export.image.toDrive(
        image=clasificada,
        description='cobertura_sanandres',
        folder='GEE_Exports',
        fileNamePrefix='clasificacion_cobertura',
        region=zona,
        scale=10,
        maxPixels=1e9
    )
    tarea.start()
    print("Tarea de exportación iniciada en Google Drive")

# Descomentar para exportar:
# exportar_resultados()

# =============================================================================
# CELDA 16: RESUMEN FINAL
# =============================================================================
print("=" * 60)
print("RESUMEN DEL ANÁLISIS")
print("=" * 60)
print(f"Zona de estudio: San Andrés y Providencia")
print(f"Coordenadas: {lat}°N, {abs(lon)}°W")
print(f"Imagen Sentinel-2: {fecha_adquisicion}")
print(f"Nubosidad: {porcentaje_nubes}%")
print(f"Área total analizada: {total_area:.2f} km²")
print("-" * 60)
print("Coberturas detectadas:")
for d in datos:
    print(f"  • {d['clase']}: {d['area_km2']:.2f} km² ({d['porcentaje']:.1f}%)")
print("=" * 60)
print("\nPara ajustar los umbrales, usa los sliders en la Celda 14.")
print("Para exportar a GeoTIFF, descomenta la Celda 15.")
