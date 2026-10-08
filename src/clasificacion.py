"""
Módulo principal de clasificación de cobertura terrestre.
"""
import torch
import numpy as np
from preprocesado import normalizar_imagen, crear_parches, reconstruir_mapa
from modelo import cargar_modelo, obtener_clases_eurosat


def clasificar_imagen(imagen, tamano_parche=64, solapamiento=0, dispositivo=None):
    """
    Clasifica una imagen satelital por parches y genera el mapa de cobertura.

    Args:
        imagen: numpy array (4, H, W) con bandas [B02, B03, B04, B08]
        tamano_parche: tamaño de cada parche en píxeles
        solapamiento: solapamiento entre parches
        dispositivo: 'cpu', 'cuda' o None

    Returns:
        mapa_clasificacion: numpy array (H, W) con clases predichas
        clases: lista de nombres de clases
        confianzas: numpy array (H, W) con la confianza de cada predicción
    """
    # Cargar modelo
    modelo, dispositivo = cargar_modelo(num_clases=10, dispositivo=dispositivo)
    clases = obtener_clases_eurosat()

    # Normalizar imagen
    tensor = normalizar_imagen(imagen)
    _, alto, ancho = tensor.shape

    # Crear parches
    parches, posiciones = crear_parches(tensor, tamano_parche, solapamiento)
    print(f"📸 Imagen dividida en {len(parches)} parches de {tamano_parche}x{tamano_parche}")

    # Clasificar cada parche
    predicciones = []
    confianzas = []

    with torch.no_grad():
        for i, parche in enumerate(parches):
            # Añadir dimensión de batch y mover al dispositivo
            parche = parche.unsqueeze(0).to(dispositivo)

            # Inferencia
            salida = modelo(parche)
            probabilidades = torch.softmax(salida, dim=1)

            # Obtener clase predicha y confianza
            confianza, predicha = torch.max(probabilidades, dim=1)
            predicciones.append(predicha.item())
            confianzas.append(confianza.item())

            if (i + 1) % 50 == 0:
                print(f"   Procesados {i + 1}/{len(parches)} parches...")

    print(f"✅ Clasificación completada: {len(parches)} parches procesados")

    # Reconstruir mapa
    mapa = reconstruir_mapa(predicciones, posiciones, tamano_parche, alto, ancho)

    # Reconstruir mapa de confianzas
    mapa_confianza = reconstruir_mapa(
        [int(c * 100) for c in confianzas],
        posiciones,
        tamano_parche,
        alto,
        ancho
    ) / 100.0

    return mapa, clases, mapa_confianza


def calcular_estadisticas(mapa, clases):
    """
    Calcula estadísticas de cobertura a partir del mapa clasificado.

    Args:
        mapa: numpy array (H, W) con clases predichas
        clases: lista de nombres de clases

    Returns:
        diccionario con porcentaje de cada clase
    """
    total_pixeles = mapa.size
    estadisticas = {}

    for idx, nombre in enumerate(clases):
        count = np.sum(mapa == idx)
        porcentaje = (count / total_pixeles) * 100
        estadisticas[nombre] = {
            "pixeles": int(count),
            "porcentaje": round(porcentaje, 2)
        }

    return estadisticas
