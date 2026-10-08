"""
Módulo para cargar y usar el modelo de clasificación ResNet-18.
"""
import torch
import torch.nn as nn
from torchvision import models


def cargar_modelo(num_clases=10, dispositivo=None):
    """
    Carga el modelo ResNet-18 pre-entrenado en ImageNet y adapta la última capa
    para el número de clases de cobertura terrestre.

    Args:
        num_clases: número de clases de salida (10 para EuroSAT)
        dispositivo: 'cpu', 'cuda' o None (auto-detectar)

    Returns:
        modelo cargado y listo para inferencia
    """
    if dispositivo is None:
        dispositivo = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"🖥️  Usando dispositivo: {dispositivo}")

    # Cargar ResNet-18 pre-entrenado en ImageNet
    modelo = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

    # Reemplazar la última capa fully connected para nuestras clases
    num_features = modelo.fc.in_features
    modelo.fc = nn.Linear(num_features, num_clases)

    # Mover al dispositivo
    modelo = modelo.to(dispositivo)
    modelo.eval()  # Modo evaluación (sin dropout, batchnorm fijo)

    print(f"✅ Modelo ResNet-18 cargado con {num_clases} clases")
    return modelo, dispositivo


def cargar_pesos_eurosat(modelo, ruta_pesos=None):
    """
    Carga pesos pre-entrenados en EuroSAT si están disponibles.
    Si no hay pesos, usa el modelo con pesos de ImageNet (transfer learning básico).

    Args:
        modelo: modelo ResNet-18
        ruta_pesos: ruta al archivo de pesos EuroSAT (opcional)

    Returns:
        modelo con pesos cargados
    """
    if ruta_pesos and torch.cuda.is_available():
        try:
            checkpoint = torch.load(ruta_pesos, map_location="cpu")
            modelo.load_state_dict(checkpoint["model_state_dict"])
            print(f"✅ Pesos EuroSAT cargados desde: {ruta_pesos}")
        except Exception as e:
            print(f"⚠️  No se pudieron cargar pesos EuroSAT: {e}")
            print("   Usando pesos de ImageNet (transfer learning)")
    else:
        print("ℹ️  No se proporcionaron pesos EuroSAT. Usando pesos de ImageNet.")
        print("   Para mejores resultados, descarga pesos pre-entrenados en EuroSAT.")

    return modelo


def obtener_clases_eurosat():
    """
    Retorna los nombres de las clases de cobertura terrestre (EuroSAT).
    """
    return [
        "Cultivo_anual",
        "Bosque",
        "Matorral",
        "Carretera",
        "Edificios_industriales",
        "Pastizal",
        "Cultivo_permanente",
        "Residencial",
        "Rio",
        "Mar_Lago",
    ]
