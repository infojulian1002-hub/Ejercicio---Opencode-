"""
Módulo para visualizar los resultados de la clasificación.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import folium
from folium import plugins


# Colores para cada clase (EuroSAT)
COLORES_CLASES = {
    "Cultivo_anual": "#FFD700",      # Amarillo dorado
    "Bosque": "#228B22",             # Verde bosque
    "Matorral": "#9ACD32",           # Verde amarillento
    "Carretera": "#696969",          # Gris oscuro
    "Edificios_industriales": "#8B4513",  # Marrón
    "Pastizal": "#7CFC00",           # Verde césped
    "Cultivo_permanente": "#DAA520", # Dorado
    "Residencial": "#FF6347",        # Tomate
    "Rio": "#1E90FF",               # Azul
    "Mar_Lago": "#0000CD",           # Azul medio
}


def visualizar_mapa(mapa, clases, titulo="Mapa de Cobertura Terrestre"):
    """
    Visualiza el mapa de clasificación con matplotlib.

    Args:
        mapa: numpy array (H, W) con clases predichas
        clases: lista de nombres de clases
        titulo: título del gráfico

    Returns:
        figura de matplotlib
    """
    # Crear colores para el mapa
    colores = [COLORES_CLASES[c] for c in clases]
    cmap = ListedColormap(colores)

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    im = ax.imshow(mapa, cmap=cmap, vmin=0, vmax=len(clases) - 1)

    # Leyenda
    patches = [
        mpatches.Patch(color=COLORES_CLASES[c], label=c)
        for c in clases
        if np.any(mapa == clases.index(c))
    ]
    ax.legend(handles=patches, loc="upper right", bbox_to_anchor=(1.3, 1))

    ax.set_title(titulo, fontsize=14, fontweight="bold")
    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")

    plt.tight_layout()
    return fig


def visualizar_imagen_rgb(imagen, titulo="Imagen Sentinel-2 (RGB)"):
    """
    Visualiza la imagen RGB original.

    Args:
        imagen: numpy array (4, H, W) con bandas [B02, B03, B04, B08]
        titulo: título del gráfico

    Returns:
        figura de matplotlib
    """
    # Extraer RGB (B04=Rojo, B03=Verde, B02=Azul) -> índices [2, 1, 0]
    rgb = imagen[[2, 1, 0], :, :].transpose(1, 2, 0)
    rgb = np.clip(rgb / 10000.0, 0, 1)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.imshow(rgb)
    ax.set_title(titulo, fontsize=14, fontweight="bold")
    ax.axis("off")

    plt.tight_layout()
    return fig


def crear_mapa_interactivo(mapa, clases, bbox, centro=None):
    """
    Crea un mapa interactivo con Folium.

    Args:
        mapa: numpy array (H, W) con clases predichas
        clases: lista de nombres de clases
        bbox: bounding box [min_lon, min_lat, max_lon, max_lat]
        centro: [lat, lon] del centro del mapa

    Returns:
        objeto mapa de Folium
    """
    if centro is None:
        centro = [(bbox[1] + bbox[3]) / 2, (bbox[0] + bbox[2]) / 2]

    m = folium.Map(location=centro, zoom_start=13, tiles="OpenStreetMap")

    # Añadir capa de imagen clasificada como overlay
    # Nota: Para un caso real, se rasterizaría el mapa y se superpondría
    # Aquí añadimos un marcador informativo
    folium.Marker(
        location=centro,
        popup="Zona clasificada",
        icon=folium.Icon(color="green"),
    ).add_to(m)

    # Añadir leyenda
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                background-color: white; padding: 10px; border: 2px solid grey;
                border-radius: 5px; font-size: 12px;">
    <b>Clases de Cobertura</b><br>
    """
    for clase in clases:
        color = COLORES_CLASES[clase]
        legend_html += f'<i style="background:{color};width:12px;height:12px;display:inline-block;"></i> {clase}<br>'
    legend_html += "</div>"

    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def guardar_resultados(mapa, clases, estadisticas, ruta_salida):
    """
    Guarda los resultados en archivos.

    Args:
        mapa: numpy array (H, W) con clases predichas
        clases: lista de nombres de clases
        estadisticas: diccionario con estadísticas
        ruta_salida: carpeta de salida
    """
    import os
    import json

    os.makedirs(ruta_salida, exist_ok=True)

    # Guardar mapa como numpy array
    np.save(os.path.join(ruta_salida, "mapa_clasificacion.npy"), mapa)

    # Guardar estadísticas como JSON
    with open(os.path.join(ruta_salida, "estadisticas.json"), "w", encoding="utf-8") as f:
        json.dump(estadisticas, f, ensure_ascii=False, indent=2)

    # Guardar mapa como imagen
    fig = visualizar_mapa(mapa, clases)
    fig.savefig(os.path.join(ruta_salida, "mapa_clasificacion.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"💾 Resultados guardados en: {ruta_salida}")
