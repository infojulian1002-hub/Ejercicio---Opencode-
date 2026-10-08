# Bitácora del Proyecto: Clasificación de Cobertura Terrestre de San Andrés

## Información general
- **Proyecto**: Clasificación de cobertura terrestre con IA geoespacial
- **Zona de estudio**: San Andrés, Colombia
- **Fecha de inicio**: 2026-10-07
- **Usuario**: Julia (nivel básico de programación)

---

## Decisiones tomadas

### 1. Enfoque general
- **Decisión**: Usar modelo pre-entrenado (sin entrenamiento desde cero)
- **Razón**: El usuario tiene experiencia básica en Python; un modelo pre-entrenado simplifica el desarrollo

### 2. Modelo elegido
- **Decisión**: ResNet-18 pre-entrenado en EuroSAT
- **Razón**: Ligero, funciona bien en CPU, 10 clases de cobertura terrestre ya definidas
- **Alternativa considerada**: Prithvi (NASA/IBM) — más pesado para CPU

### 3. Zona de estudio
- **Decisión**: San Andrés, Colombia
- **Razón**: Isla pequeña (~26 km²), imágenes manejables, clases variadas (bosque, urbano, agua, playa)

### 4. Nivel de detalle
- **Decisión**: Clasificación por píxel (vía parches de 64x64 píxeles)
- **Razón**: El usuario necesita detalle por píxel, no solo una etiqueta por imagen

### 5. Hardware
- **Decisión**: CPU (posiblemente sin GPU dedicada)
- **Razón**: El usuario no está seguro de tener GPU; ResNet-18 con parches pequeños funciona en CPU

### 6. Interfaz
- **Decisión**: Aplicación web con Streamlit
- **Razón**: Fácil de usar, no requiere conocimientos de frontend, ideal para usuario básico

### 7. Fuente de imágenes
- **Decisión**: Sentinel-2 (Copernicus, ESA)
- **Razón**: Gratuito, resolución 10m, revisita cada 5 días, suficiente para la escala de San Andrés

### 8. Lenguaje y versión
- **Decisión**: Python 3.11.2
- **Razón**: Versión ya instalada por el usuario

---

## Acciones realizadas

### Fase 1: Setup del proyecto
- [x] Crear estructura de directorios
- [x] Crear archivo de bitácora
- [ ] Crear entorno virtual
- [ ] Instalar dependencias

### Fase 2: Desarrollo de módulos
- [x] `src/descarga.py` — Descarga de imágenes Sentinel-2
- [x] `src/preprocesado.py` — Preparación de parches
- [x] `src/modelo.py` — Carga del modelo ResNet-18
- [x] `src/clasificacion.py` — Clasificación por parches
- [x] `src/visualizacion.py` — Mapa y estadísticas
- [x] `app.py` — Interfaz web con Streamlit

### Fase 3: Configuración y documentación
- [x] `requirements.txt` — Dependencias
- [x] `config.yaml` — Coordenadas, fechas, clases
- [x] `README.md` — Instrucciones de uso

### Fase 4: Pruebas
- [x] Verificar instalación de dependencias
- [x] Probar clasificación (prueba_rapida.py exitoso)
- [ ] Probar descarga de imagen (requiere credenciales Sentinel Hub)
- [ ] Probar interfaz web (requiere credenciales Sentinel Hub)

---

## Prompts utilizados

### Prompt 1 (Planificación)
> crear un programa en python que me permita clasificar o detectar el tipo de cobertura terrestre de una zona de Colombia, empleando modelos de IA geoespacial de codigo abierto.

### Prompt 2 (Respuestas del usuario)
> 1. basica, 2. San andres, 3. por pixel, 3. Creo que CPU pero no estoy seguro, 5. Interfaz web

### Prompt 3 (Confirmación de Python)
> Python 3.11.2

### Prompt 4 (Inicio de implementación)
> Empieza la implementacion, ademas crea un archivo de bitacora que consigne todas las desiciones y acciones tomadas, y prompts utilizados.

---

## Notas técnicas

### Clases de cobertura (EuroSAT)
1. Annual Cultivation (Cultivo anual)
2. Forest (Bosque)
3. Brushland (Matorral)
4. Highway (Carretera)
5. Industrial Buildings (Edificios industriales)
6. Pasture (Pastizal)
7. Permanent Cultivation (Cultivo permanente)
8. Residential (Residencial)
9. River (Río)
10. Sea/Lake (Mar/Lago)

### Coordenadas de San Andrés
- Latitud: 12.5567
- Longitud: -81.7185
- Extensión aproximada: 26 km²

### Dependencias principales
- `torch` — Framework de deep learning
- `torchvision` — Modelos pre-entrenados (ResNet-18)
- `rasterio` — Lectura/escritura de imágenes geoespaciales
- `sentinelhub` — Descarga de imágenes Sentinel-2
- `streamlit` — Interfaz web
- `folium` — Mapas interactivos
- `numpy`, `matplotlib` — Procesamiento y visualización
- `pyyaml` — Archivos de configuración

---

## Registro de cambios

| Fecha | Acción | Detalle |
|-------|--------|---------|
| 2026-10-07 | Inicio del proyecto | Creación de estructura y bitácora |
| 2026-10-07 | Desarrollo de módulos | Creados 6 módulos en src/ + app.py |
| 2026-10-07 | Configuración | Creados requirements.txt, config.yaml, README.md |
| 2026-10-07 | Entorno virtual | Creado entorno virtual en venv/ |
| 2026-10-07 | Instalación | Iniciada instalación de dependencias (torch, torchvision, rasterio, sentinelhub, streamlit, folium, numpy, matplotlib) |
| 2026-10-07 | Script de prueba | Creado prueba_rapida.py para verificar funcionamiento sin credenciales |
| 2026-10-07 | Instalación completada | Todas las dependencias instaladas correctamente |
| 2026-10-07 | Corrección de errores | Corregido error de importación relativa en clasificacion.py |
| 2026-10-07 | Corrección de codificación | Añadido soporte UTF-8 en prueba_rapida.py para Windows |
| 2026-10-07 | Prueba exitosa | prueba_rapida.py ejecutado correctamente - modelo ResNet-18 cargado, 16 parches clasificados, resultados guardados |
| 2026-10-07 | Repositorio git | Inicializado repositorio local, commit inicial creado |
| 2026-10-07 | GitHub | Proyecto subido a https://github.com/infojulian1002-hub/Ejercicio---Opencode-.git |
