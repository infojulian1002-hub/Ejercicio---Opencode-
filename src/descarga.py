"""
Módulo para descargar imágenes Sentinel-2 desde Copernicus Data Space.
"""
import os
from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    DataCollection,
    MimeType,
    BBox,
    CRS,
)
import numpy as np


def configurar_sentinelhub():
    """
    Configura las credenciales de Sentinel Hub.
    Requiere un archivo .env con CLIENT_ID y CLIENT_ID_SECRET.
    """
    config = SHConfig()
    # Intentar cargar credenciales de variables de entorno
    client_id = os.getenv("SENTINELHUB_CLIENT_ID")
    client_secret = os.getenv("SENTINELHUB_CLIENT_SECRET")

    if client_id and client_secret:
        config.sh_client_id = client_id
        config.sh_client_secret = client_secret
        config.save()
        return config
    else:
        print("⚠️  Credenciales de Sentinel Hub no encontradas.")
        print("   Crea una cuenta gratuita en: https://dataspace.copernicus.eu/")
        print("   Y configura las variables de entorno SENTINELHUB_CLIENT_ID y SENTINELHUB_CLIENT_SECRET")
        return None


def descargar_imagen_s2(bbox, fechas, config=None, resolucion=10, tamano=512):
    """
    Descarga una imagen Sentinel-2 para la zona y fechas especificadas.

    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        fechas: Tupla (fecha_inicio, fin) en formato 'YYYY-MM-DD'
        config: Configuración de SentinelHub (opcional)
        resolucion: Resolución en metros (10 para Sentinel-2)
        tamano: Tamaño de la imagen en píxeles

    Returns:
        numpy array con la imagen (bands, height, width) o None si falla
    """
    if config is None:
        config = configurar_sentinelhub()
        if config is None:
            return None

    # Evalscript para obtener las bandas B02, B03, B04, B08 (RGB + NIR)
    evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: ["B02", "B03", "B04", "B08"],
            output: { bands: 4, sampleType: "FLOAT32" }
        };
    }
    function evaluatePixel(sample) {
        return [sample.B02, sample.B03, sample.B04, sample.B08];
    }
    """

    # Crear bounding box
    bbox_sh = BBox(bbox=bbox, crs=CRS.WGS84)

    # Crear solicitud
    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=fechas,
                mosaicking_order="leastCC",  # Menor nubosidad
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox_sh,
        size=(tamano, tamano),
        config=config,
    )

    try:
        data = request.get_data()
        imagen = data[0]
        print(f"✅ Imagen descargada: {imagen.shape}")
        return imagen
    except Exception as e:
        print(f"❌ Error al descargar imagen: {e}")
        return None


def guardar_imagen_geotiff(imagen, ruta_salida, bbox, crs="EPSG:4326"):
    """
    Guarda la imagen como GeoTIFF.

    Args:
        imagen: numpy array (bands, height, width)
        ruta_salida: ruta del archivo de salida
        bbox: bounding box [min_lon, min_lat, max_lon, max_lat]
        crs: sistema de referencia de coordenadas
    """
    import rasterio
    from rasterio.transform import from_bounds

    bands, height, width = imagen.shape
    min_lon, min_lat, max_lon, max_lat = bbox
    transform = from_bounds(min_lon, min_lat, max_lon, max_lat, width, height)

    with rasterio.open(
        ruta_salida,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=bands,
        dtype=imagen.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        for i in range(bands):
            dst.write(imagen[i], i + 1)

    print(f"💾 Imagen guardada en: {ruta_salida}")
