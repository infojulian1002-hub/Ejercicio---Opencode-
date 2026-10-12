"""
Autenticación con Google Earth Engine.
"""

import ee


def inicializar_ee(proyecto_id=None):
    """
    Inicializa Google Earth Engine para Google Colab o uso local.
    
    Parámetros:
        proyecto_id (str): ID del proyecto de Google Cloud.
                          Si es None, usa autenticación por defecto.
    
    Retorna:
        bool: True si la autenticación fue exitosa.
    
    Ejemplo:
        >>> inicializar_ee('mi-proyecto-gcp')
        True
    """
    try:
        # Intentar usar credenciales por defecto (Colab ya autenticado)
        if proyecto_id is None:
            ee.Initialize()
        else:
            ee.Initialize(project=proyecto_id)
        return True
    except Exception as e:
        print(f"Error en autenticación: {e}")
        print("\nOpciones para solucionar:")
        print("1. En Google Colab: ejecuta ee.Authenticate() primero")
        print("2. En local: configura las credenciales con: earthengine authenticate")
        print("3. Usa autenticación con google.auth (ver documentación)")
        return False


def autenticacion_colab():
    """
    Autenticación específica para Google Colab.
    Abre un enlace para autorizar el acceso.
    """
    ee.Authenticate()
    ee.Initialize()
    print("✓ Autenticación en Colab completada")


def autenticacion_manual(proyecto_id):
    """
    Autenticación manual con google.auth (alternativa).
    
    Parámetros:
        proyecto_id (str): ID del proyecto de Google Cloud.
    """
    import google.auth
    credentials, project = google.auth.default()
    ee.Initialize(credentials, project=proyecto_id)
    print(f"✓ Autenticación con proyecto '{proyecto_id}' completada")
