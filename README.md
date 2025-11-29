# Análisis de Imágenes CT Pulmonares - LUNA16

Proyecto de procesamiento y análisis de imágenes médicas CT para detección de nódulos pulmonares usando el dataset LUNA16.

---

## Requisitos Previos

- Python 3.8 o superior
- Git (para clonar el repositorio)
- ~15 GB de espacio libre en disco (para subset0 de LUNA16)

---

## Instalación - Configuración Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/Daspony/Imagenes-Biomedicas.git
cd Imagenes-Biomedicas
```

### 2. Crear entorno virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

Una vez activado el entorno virtual:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Esto instalará todas las librerías necesarias:
- numpy, pandas, matplotlib, scipy
- SimpleITK (para archivos .mhd/.raw)
- scikit-image (para procesamiento de imágenes)
- opencv-python
- torch, torchvision (para deep learning)
- jupyter (para notebooks)
- Y más...

### 4. Descargar el dataset LUNA16

Tienes dos opciones:

#### Opción A: Descarga automática desde el notebook (Recomendado)

1. Abre el notebook `01_preprocesamiento.ipynb`
2. Ejecuta las primeras celdas
3. El dataset se descargará automáticamente a `LUNA16/subset0/`

#### Opción B: Descarga manual

1. Descarga desde Zenodo: https://zenodo.org/record/3723295
2. Descarga al menos:
   - `subset0.zip` (~13 GB)
   - `annotations.csv`
   - `candidates.csv`
3. Descomprime y organiza la estructura:

```
Imagenes-Biomedicas/
├── LUNA16/
│   ├── subset0/
│   │   ├── 1.3.6.1.4.1.14519.5.2.1.*.mhd
│   │   └── 1.3.6.1.4.1.14519.5.2.1.*.raw
│   ├── annotations.csv
│   └── candidates.csv
├── notebooks/
├── utils/
└── README.md
```

---

## Ejecutar los Notebooks

### 1. Iniciar Jupyter

Con el entorno virtual activado:

```bash
jupyter notebook
```

Se abrirá tu navegador con el explorador de archivos. Tambien se puede abrir con vscode

### 2. Abrir notebook de preprocesamiento

Navega a `notebooks/01_preprocesamiento.ipynb` y ábrelo.

### 3. Ejecutar celdas

Ejecuta las celdas secuencialmente con `Shift + Enter` o usa el botón "Run All".

**Nota**: La primera vez que ejecutes, si no tienes los datos, el notebook los descargará automáticamente (puede tardar 30-60 minutos según tu conexión).

---

## Estructura del Proyecto

```
Imagenes-Biomedicas/
├── notebooks/                    # Notebooks Jupyter
│   ├── 00_pipeline_completo.ipynb   # Pipeline completo
│   ├── 01_preprocesamiento.ipynb    # Preprocesamiento de CT
│   └── 02_visualizacion.ipynb       # Visualización avanzada
│
├── utils/                        # Módulos de código reutilizable
│   ├── __init__.py
│   ├── data_loader.py               # Carga de datos LUNA16
│   ├── preprocessor.py              # Preprocesamiento de imágenes
│   ├── visualizer.py                # Funciones de visualización
│   ├── metrics.py                   # Métricas de evaluación
│   └── download_luna16.py           # Descarga automática de datos
│
├── LUNA16/                       # Dataset (se crea al descargar)
│   ├── subset0/
│   ├── annotations.csv
│   └── candidates.csv
│
├── requirements.txt              # Dependencias Python
└── README.md                     # Este archivo
```

---

## Notebooks Disponibles

### 01_preprocesamiento.ipynb

**Contenido:**
- Carga de imágenes CT (.mhd/.raw)
- Segmentación pulmonar automática
- Normalización de valores Hounsfield (HU)
- CLAHE para realce de contraste
- Explicación del algoritmo `clear_border()`
- Comparación de diferentes thresholds

**Tiempo de ejecución:** ~5-10 minutos (primera vez incluye descarga de datos)

### 02_visualizacion.ipynb

**Contenido:**
- Visualización de slices 2D y volúmenes 3D
- Anotaciones de nódulos
- Comparación NDCT vs LDCT
- Máscaras de segmentación
- Mapas de calor de densidad
- Controles interactivos

---

## Solución de Problemas

### Error: "No module named 'SimpleITK'"

**Solución:** Asegúrate de tener el entorno virtual activado e instala las dependencias:
```bash
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Error: "No se encontró el directorio de datos"

**Solución:**
1. Verifica que `LUNA16/subset0/` existe en la raíz del proyecto
2. O deja que el notebook descargue automáticamente los datos


### Descarga muy lenta

**Solución:**
- La descarga de subset0 es ~13GB, puede tardar 30-60 minutos
- Puedes cancelar con Ctrl+C y reanudar después
- O descarga manualmente desde Zenodo (igual de lento)

---

## Dataset LUNA16

**LUNA16** (LUng Nodule Analysis 2016) es un dataset público de imágenes CT para detección de nódulos pulmonares.

- **Total:** ~130 GB (10 subsets)
- **Subset0:** ~13 GB (89 escaneos CT)
- **Formato:** MetaImage (.mhd + .raw)
- **Anotaciones:** CSV con coordenadas de nódulos
- **Fuente:** https://zenodo.org/record/3723295

---

## Uso en Google Colab

Si prefieres usar Google Colab (no requiere instalación local):

1. Abre Google Colab: https://colab.research.google.com/
2. File > Upload notebook
3. Sube `notebooks/01_preprocesamiento.ipynb`
4. Ejecuta las celdas
5. El código clonará automáticamente el repositorio desde GitHub
6. Descargará los datos automáticamente

**Ventajas:**
- No requiere instalación local
- GPU gratuita disponible
- Todo en la nube

**Desventajas:**
- Sesión limitada a 12 horas
- Debes volver a descargar datos si la sesión expira

---

## Referencias

- Dataset LUNA16: https://luna16.grand-challenge.org/
- SimpleITK: https://simpleitk.org/
- Scikit-image: https://scikit-image.org/

---

## Licencia

Este proyecto es de uso académico/educativo.
