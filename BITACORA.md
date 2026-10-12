# Bitácora del Proyecto

Registro cronológico de actividades realizadas.

| Fecha | Actividad | Detalle |
|---|---|---|
| 2026-10-12 | Definición del proyecto | Clasificador de cobertura terrestre para Colombia usando Sentinel-2 y GEE |
| 2026-10-12 | Selección de herramientas | Google Earth Engine, Python, índices espectrales, 6 clases básicas |
| 2026-10-12 | Cuaderno original | Creado `clasificador_cobertura.py` con 16 celdas documentadas para Colab |
| 2026-10-12 | Corrección de errores | Ajustes de sintaxis y autenticación GEE |
| 2026-10-12 | Reestructuración para GitHub | Migración a arquitectura modular con Streamlit |
| 2026-10-12 | Aplicación Streamlit | Interfaz web local en localhost:8501 |
| 2026-10-12 | Preparación para GitHub | Subida al repositorio destino |

## Decisiones técnicas

- **Enfoque**: Índices espectrales + reglas umbrales (no deep learning)
- **Clases**: 6 coberturas básicas adaptadas de Corine Land Cover
- **Interfaz**: Streamlit para localhost, sin dependencias de Colab
- **Arquitectura**: Modular (src/) para facilitar mantenimiento y testing
