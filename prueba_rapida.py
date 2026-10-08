"""
Script de prueba rápida sin necesidad de credenciales de Sentinel Hub.
Genera una imagen sintética y la clasifica para verificar que el modelo funciona.
"""
import os
import sys
import numpy as np
import torch

# Configurar codificación UTF-8 para Windows
sys.stdout.reconfigure(encoding='utf-8')

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from preprocesado import normalizar_imagen, crear_parches, reconstruir_mapa
from modelo import cargar_modelo, obtener_clases_eurosat
from clasificacion import calcular_estadisticas
from visualizacion import visualizar_mapa, guardar_resultados


def generar_imagen_sintetica(tamano=256):
    """
    Genera una imagen sintética que simula una zona de San Andrés.
    Crea patrones que se asemejan a agua, vegetación y zonas urbanas.
    """
    imagen = np.zeros((4, tamano, tamano), dtype=np.float32)

    # Banda B02 (Azul) - alta en agua
    imagen[0, :, :] = np.random.normal(500, 100, (tamano, tamano))

    # Banda B03 (Verde) - alta en vegetación
    imagen[1, :, :] = np.random.normal(800, 150, (tamano, tamano))

    # Banda B04 (Rojo) - media en general
    imagen[2, :, :] = np.random.normal(600, 120, (tamano, tamano))

    # Banda B08 (NIR) - muy alta en vegetación
    imagen[3, :, :] = np.random.normal(3000, 500, (tamano, tamano))

    # Simular agua en la parte inferior (mar)
    imagen[0, tamano//2:, :] = np.random.normal(2000, 200, (tamano//2, tamano))
    imagen[1, tamano//2:, :] = np.random.normal(500, 100, (tamano//2, tamano))
    imagen[2, tamano//2:, :] = np.random.normal(300, 80, (tamano//2, tamano))
    imagen[3, tamano//2:, :] = np.random.normal(200, 50, (tamano//2, tamano))

    # Simular vegetación en la parte superior (bosque)
    imagen[0, :tamano//4, :] = np.random.normal(300, 80, (tamano//4, tamano))
    imagen[1, :tamano//4, :] = np.random.normal(2000, 300, (tamano//4, tamano))
    imagen[2, :tamano//4, :] = np.random.normal(400, 100, (tamano//4, tamano))
    imagen[3, :tamano//4, :] = np.random.normal(5000, 800, (tamano//4, tamano))

    # Simular zona urbana en el centro
    centro = tamano // 2
    imagen[0, centro-20:centro+20, centro-20:centro+20] = np.random.normal(1000, 150, (40, 40))
    imagen[1, centro-20:centro+20, centro-20:centro+20] = np.random.normal(1000, 150, (40, 40))
    imagen[2, centro-20:centro+20, centro-20:centro+20] = np.random.normal(1000, 150, (40, 40))
    imagen[3, centro-20:centro+20, centro-20:centro+20] = np.random.normal(1500, 200, (40, 40))

    # Asegurar valores positivos
    imagen = np.clip(imagen, 0, 10000)

    return imagen


def main():
    print("=" * 60)
    print("🧪 PRUEBA RÁPIDA - Clasificación de Cobertura Terrestre")
    print("=" * 60)

    # Verificar dispositivo
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n🖥️  Dispositivo: {dispositivo}")

    # Generar imagen sintética
    print("\n📸 Generando imagen sintética de prueba...")
    imagen = generar_imagen_sintetica(tamano=256)
    print(f"   Imagen generada: {imagen.shape}")

    # Cargar modelo
    print("\n🤖 Cargando modelo ResNet-18...")
    modelo, dispositivo = cargar_modelo(num_clases=10, dispositivo=dispositivo)
    clases = obtener_clases_eurosat()

    # Normalizar imagen
    print("\n⚙️  Normalizando imagen...")
    tensor = normalizar_imagen(imagen)
    _, alto, ancho = tensor.shape

    # Crear parches
    tamano_parche = 64
    print(f"\n✂️  Creando parches de {tamano_parche}x{tamano_parche}...")
    parches, posiciones = crear_parches(tensor, tamano_parche, solapamiento=0)
    print(f"   {len(parches)} parches creados")

    # Clasificar parches
    print("\n🔍 Clasificando parches...")
    predicciones = []
    confianzas = []

    with torch.no_grad():
        for i, parche in enumerate(parches):
            parche = parche.unsqueeze(0).to(dispositivo)
            salida = modelo(parche)
            probabilidades = torch.softmax(salida, dim=1)
            confianza, predicha = torch.max(probabilidades, dim=1)
            predicciones.append(predicha.item())
            confianzas.append(confianza.item())

            if (i + 1) % 16 == 0:
                print(f"   Procesados {i + 1}/{len(parches)} parches...")

    print(f"\n✅ Clasificación completada")

    # Reconstruir mapa
    print("\n🗺️  Reconstruyendo mapa de clasificación...")
    mapa = reconstruir_mapa(predicciones, posiciones, tamano_parche, alto, ancho)

    # Calcular estadísticas
    print("\n📊 Calculando estadísticas...")
    estadisticas = calcular_estadisticas(mapa, clases)

    print("\n" + "=" * 60)
    print("📊 RESULTADOS DE LA CLASIFICACIÓN")
    print("=" * 60)
    for clase, datos in estadisticas.items():
        if datos["porcentaje"] > 0:
            print(f"  {clase:25s}: {datos['porcentaje']:6.2f}% ({datos['pixeles']} píxeles)")

    # Guardar resultados
    print("\n💾 Guardando resultados...")
    ruta_salida = os.path.join(os.path.dirname(__file__), "resultados")
    guardar_resultados(mapa, clases, estadisticas, ruta_salida)

    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA CON ÉXITO")
    print("=" * 60)
    print(f"\n📁 Resultados guardados en: {ruta_salida}")
    print("\nPara ver la aplicación web completa, ejecuta:")
    print("   streamlit run app.py")


if __name__ == "__main__":
    main()
