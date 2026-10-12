# Clasificador de Cobertura Terrestre - Colombia

Clasificación automática de cobertura terrestre para la isla de San Andrés y Providencia usando imágenes **Sentinel-2** y **Google Earth Engine**.

## Características

- Descarga automática de imágenes Sentinel-2 con filtro de nubosidad
- Cálculo de índices espectrales: NDVI, NDWI, MNDWI, NDBI, SAVI
- Clasificación en 6 coberturas: Bosque, Pastos, Agricultura, Urbano, Suelo desnudo, Agua
- Interfaz web interactiva con Streamlit
- Visualización de mapas con leyenda y estadísticas

## Estructura del proyecto

```
├── app.py                     # Aplicación Streamlit
├── config.py                  # Configuración central
├── ejemplo_san_andres.py     # Script de ejemplo rápido
├── requirements.txt           # Dependencias
├── src/
│   ├── auth.py                # Autenticación GEE
│   ├── data.py                # Descarga de imágenes
│   ├── indices.py             # Índices espectrales
│   ├── classification.py      # Reglas de clasificación
│   ├── visualization.py       # Mapas y gráficos
│   └── stats.py               # Estadísticas
```

## Instalación

```bash
git clone https://github.com/infojulian1002-hub/Ejercicio---Opencode-.git
cd Ejercicio---Opencode-
pip install -r requirements.txt
```

## Uso en localhost

```bash
streamlit run app.py
```

Se abre en `http://localhost:8501`

## Uso rápido (script)

```bash
python ejemplo_san_andres.py
```

Genera:
- `mapa_cobertura.html` - Mapa interactivo
- `grafico_barras.png` - Gráfico de área por clase
- `grafico_pastel.png` - Distribución porcentual

## Requisitos

- Cuenta de Google con proyecto de Google Cloud habilitado para Earth Engine
- Python 3.8+

## Fuente de datos

- **Imágenes**: Sentinel-2 L2A (Copernicus/ESA)
- **Plataforma**: Google Earth Engine
- **Resolución**: 10m

## Licencia

MIT
