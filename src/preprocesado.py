"""
Módulo para pre-procesar imágenes satelitales antes de la clasificación.
"""
import numpy as np
import torch
from torchvision import transforms


def normalizar_imagen(imagen):
    """
    Normaliza la imagen para el modelo ResNet-18.
    Espera imagen con forma (bands, height, width) con bandas [B02, B03, B04, B08].

    Args:
        imagen: numpy array (4, H, W) con valores de reflectancia

    Returns:
        torch tensor normalizado (3, H, W) listo para el modelo
    """
    # Usar solo RGB (B04=Rojo, B03=Verde, B02=Azul) -> índices [2, 1, 0]
    rgb = imagen[[2, 1, 0], :, :]

    # Convertir a float32 y normalizar a [0, 1]
    rgb = rgb.astype(np.float32)
    # Los valores de Sentinel-2 L2A están en rango 0-10000, dividir por 10000
    rgb = np.clip(rgb / 10000.0, 0, 1)

    # Convertir a tensor
    tensor = torch.from_numpy(rgb)

    # Normalización de ImageNet (esperada por ResNet-18 pre-entrenado)
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
    tensor = normalize(tensor)

    return tensor


def crear_parches(imagen, tamano_parche=64, solapamiento=0):
    """
    Divide la imagen en parches del tamaño especificado.

    Args:
        imagen: torch tensor (3, H, W)
        tamano_parche: tamaño de cada parche en píxeles
        solapamiento: solapamiento entre parches en píxeles

    Returns:
        lista de parches y sus posiciones (fila, columna)
    """
    _, alto, ancho = imagen.shape
    paso = tamano_parche - solapamiento

    parches = []
    posiciones = []

    for fila in range(0, alto - tamano_parche + 1, paso):
        for col in range(0, ancho - tamano_parche + 1, paso):
            parche = imagen[:, fila:fila + tamano_parche, col:col + tamano_parche]
            parches.append(parche)
            posiciones.append((fila, col))

    return parches, posiciones


def reconstruir_mapa(predicciones, posiciones, tamano_parche, alto, ancho):
    """
    Reconstruye el mapa de clasificación a partir de las predicciones de parches.

    Args:
        predicciones: lista de índices de clase predichos
        posiciones: lista de (fila, columna) de cada parche
        tamano_parche: tamaño del parche
        alto, ancho: dimensiones de la imagen original

    Returns:
        numpy array (alto, ancho) con la clase predicha por píxel
    """
    mapa = np.zeros((alto, ancho), dtype=np.int32)
    conteo = np.zeros((alto, ancho), dtype=np.int32)

    for pred, (fila, col) in zip(predicciones, posiciones):
        mapa[fila:fila + tamano_parche, col:col + tamano_parche] += pred
        conteo[fila:fila + tamano_parche, col:col + tamano_parche] += 1

    # Promediar en caso de solapamiento
    conteo = np.maximum(conteo, 1)
    mapa = np.round(mapa / conteo).astype(np.int32)

    return mapa
