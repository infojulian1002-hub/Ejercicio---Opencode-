"""
Configuración central del proyecto.
Clasificador de Cobertura Terrestre - Colombia
"""

# =============================================================================
# CONFIGURACIÓN DE ZONA DE ESTUDIO
# =============================================================================
LATITUD = 12.55          # San Andrés
LONGITUD = -81.72        # San Andrés
BUFFER_METROS = 5000     # 5 km de radio

# =============================================================================
# CONFIGURACIÓN DE IMÁGENES SENTINEL-2
# =============================================================================
COLECCION_S2 = 'COPERNICUS/S2_SR_HARMONIZED'
MAX_NUBES = 15           # Porcentaje máximo de nubosidad
MESES_HISTORICO = 12     # Buscar en los últimos 12 meses

# =============================================================================
# BANDAS UTILIZADAS
# =============================================================================
BANDAS = {
    'B2': 'Azul (490 nm)',
    'B3': 'Verde (560 nm)',
    'B4': 'Rojo (665 nm)',
    'B8': 'Infrarrojo cercano (842 nm)',
    'B11': 'SWIR 1 (1610 nm)',
    'B12': 'SWIR 2 (2190 nm)',
}

# Bandas para visualización RGB
VIS_RGB = {
    'min': 0,
    'max': 3000,
    'bands': ['B4', 'B3', 'B2'],
    'gamma': 1.4
}

# =============================================================================
# CLASES DE COBERTURA TERRESTRE
# =============================================================================
CLASES = {
    0: {'nombre': 'Agua', 'color': '#1E90FF', 'descripcion': 'Océano, lagos, embalses'},
    1: {'nombre': 'Suelo desnudo / Playas', 'color': '#F5DEB3', 'descripcion': 'Arena, tierra sin vegetación'},
    2: {'nombre': 'Pastos / Matorral', 'color': '#9ACD32', 'descripcion': 'Herbazales, vegetación baja'},
    3: {'nombre': 'Agricultura', 'color': '#FFA500', 'descripcion': 'Cultivos, plantaciones'},
    4: {'nombre': 'Bosque', 'color': '#228B22', 'descripcion': 'Vegetación densa, árboles'},
    5: {'nombre': 'Urbano', 'color': '#DC143C', 'descripcion': 'Zonas construidas, infraestructura'},
}

# Paleta de colores ordenada por clase
PALETA_COLORES = [CLASES[i]['color'] for i in range(len(CLASES))]

# =============================================================================
# UMBRALES DE CLASIFICACIÓN (valores por defecto)
# =============================================================================
UMBRALES_DEFAULT = {
    'mndwi_agua': 0.3,        # MNDWI > 0.3 → Agua
    'ndwi_agua': 0.5,         # NDWI > 0.5 → Agua (alternativo)
    'ndvi_suelo_max': 0.1,    # NDVI < 0.1 → Suelo desnudo
    'ndvi_pastos_min': 0.1,   # NDVI >= 0.1 → Pastos
    'ndvi_pastos_max': 0.3,   # NDVI < 0.3 → Pastos
    'ndvi_agricultura_min': 0.2,  # NDVI >= 0.2 → Agricultura
    'ndvi_agricultura_max': 0.45,  # NDVI < 0.45 → Agricultura
    'ndvi_bosque_min': 0.4,   # NDVI >= 0.4 → Bosque
    'savi_bosque_min': 0.4,   # SAVI >= 0.4 → Bosque (refuerzo)
    'ndbi_urbano': 0.05,      # NDBI > 0.05 → Urbano
}

# =============================================================================
# VISUALIZACIÓN DE CLASIFICACIÓN
# =============================================================================
VIS_CLASIFICACION = {
    'min': 0,
    'max': 5,
    'palette': PALETA_COLORES
}

# =============================================================================
# EXPORTACIÓN
# =============================================================================
ESCALA_M = 10  # Resolución espacial en metros
MAX_PIXELES = 1e9
