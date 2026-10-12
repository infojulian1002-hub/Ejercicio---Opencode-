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
        print("\n" + "=" * 60)
        print("SOLUCIÓN PARA AUTENTICACIÓN LOCAL:")
        print("=" * 60)
        print("\n1. Abre una terminal y ejecuta:")
        print("   earthengine authenticate")
        print("\n2. Se abrirá un enlace en tu navegador")
        print("3. Inicia sesión con tu cuenta Google")
        print("4. Copia el código de autorización")
        print("5. Pégalo en la terminal")
        print("\n6. Vuelve a ejecutar la aplicación:")
        print("   streamlit run app.py")
        print("\n" + "=" * 60)
        print("\nAlternativa automática:")
        print("Ejecuta en la terminal: earthengine authenticate")
        print("Y luego vuelve a correr la app.")
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


def verificar_credenciales():
    """
    Verifica si las credenciales de GEE están configuradas.
    
    Retorna:
        bool: True si las credenciales son válidas.
    """
    try:
        ee.Initialize()
        # Intentar una operación simple
        ee.Number(1).getInfo()
        return True
    except Exception:
        return False
