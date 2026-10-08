# 🛰️ Clasificación de Cobertura Terrestre - San Andrés, Colombia

Aplicación web que clasifica el tipo de cobertura terrestre de San Andrés, Colombia, usando inteligencia artificial geoespacial.

## 📋 Descripción

Este proyecto utiliza un modelo **ResNet-18** pre-entrenado en **EuroSAT** para clasificar imágenes satelitales **Sentinel-2** en 10 categorías de cobertura terrestre:

| Clase | Color |
|-------|-------|
| Cultivo anual | 🟡 Amarillo |
| Bosque | 🟢 Verde oscuro |
| Matorral | 🟢 Verde claro |
| Carretera | ⚫ Gris |
| Edificios industriales | 🟤 Marrón |
| Pastizal | 🟢 Verde césped |
| Cultivo permanente | 🟡 Dorado |
| Residencial | 🔴 Rojo |
| Río | 🔵 Azul |
| Mar/Lago | 🔵 Azul oscuro |

## 🚀 Inicio rápido

### 1. Crear entorno virtual

```bash
cd cobertura_sanandres
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar credenciales de Sentinel Hub

1. Crea una cuenta gratuita en [Copernicus Data Space](https://dataspace.copernicus.eu/)
2. Configura las variables de entorno:

```bash
# Windows (PowerShell)
$env:SENTINELHUB_CLIENT_ID="tu_client_id"
$env:SENTINELHUB_CLIENT_SECRET="tu_client_secret"

# Linux/Mac
export SENTINELHUB_CLIENT_ID="tu_client_id"
export SENTINELHUB_CLIENT_SECRET="tu_client_secret"
```

### 5. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 📁 Estructura del proyecto

```
cobertura_sanandres/
├── app.py                    # Aplicación web (Streamlit)
├── src/
│   ├── descarga.py           # Descarga de imágenes Sentinel-2
│   ├── preprocesado.py       # Preparación de parches
│   ├── modelo.py             # Carga del modelo ResNet-18
│   ├── clasificacion.py      # Lógica de clasificación
│   └── visualizacion.py      # Mapas y gráficos
├── requirements.txt          # Dependencias
├── config.yaml               # Configuración (zona, fechas, clases)
├── resultados/               # Resultados generados (se crea automáticamente)
├── BITACORA.md               # Bitácora del proyecto
└── README.md                 # Este archivo
```

## ⚙️ Configuración

Edita `config.yaml` para cambiar:
- **Zona de estudio**: coordenadas y bounding box
- **Fechas**: rango de fechas para la imagen
- **Tamaño de parche**: resolución de la clasificación
- **Clases**: categorías de cobertura

## 📊 Resultados

La aplicación genera:
- **Mapa de cobertura**: imagen con las clases predichas
- **Estadísticas**: porcentaje de cada clase en la zona
- **Archivos guardados**: mapa en formato PNG y numpy, estadísticas en JSON

## 🔧 Solución de problemas

### Error: "Credenciales no encontradas"
- Verifica que las variables de entorno estén configuradas correctamente
- Asegúrate de tener una cuenta activa en Copernicus Data Space

### Error: "No se pudo descargar la imagen"
- Verifica tu conexión a internet
- Prueba con un rango de fechas diferente
- Reduce el tamaño del bounding box

### La clasificación es muy lenta
- Reduce el tamaño de parche (32px en lugar de 64px)
- Usa una zona más pequeña
- Considera usar una GPU si está disponible

## 📚 Recursos

- [EuroSAT Dataset](https://github.com/phelber/EuroSAT)
- [Sentinel Hub Documentation](https://www.sentinel-hub.com/develop/api/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [TorchGeo](https://torchgeo.readthedocs.io/)

## 📄 Licencia

Proyecto educativo. Libre para uso y modificación.

---

**Desarrollado con ❤️ para aprender IA geoespacial**
