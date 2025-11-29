# Análisis de Imágenes CT Pulmonares - LUNA16

Proyecto de procesamiento y análisis de imágenes médicas CT para detección de nódulos pulmonares usando el dataset LUNA16.

---

## Uso en Google Colab

Si prefieres usar Google Colab (no requiere instalación local):

1. Abre cualquier notebook directamente desde GitHub:
   - [00_preparacion_datos.ipynb](https://colab.research.google.com/github/Daspony/Imagenes-Biomedicas/blob/main/notebooks/00_preparacion_datos.ipynb) - Descarga y verificación de datos
   - [01_preprocesamiento.ipynb](https://colab.research.google.com/github/Daspony/Imagenes-Biomedicas/blob/main/notebooks/01_preprocesamiento.ipynb) - Preprocesamiento + máscaras LIDC
   - [02_visualizacion.ipynb](https://colab.research.google.com/github/Daspony/Imagenes-Biomedicas/blob/main/notebooks/02_visualizacion.ipynb) - Visualización + comparación LUNA16 vs LIDC
   - [03_nnunet_segmentacion.ipynb](https://colab.research.google.com/github/Daspony/Imagenes-Biomedicas/blob/main/notebooks/03_nnunet_segmentacion.ipynb) - Segmentación con nnU-Net (Recomendado en Colab)
   - [04_clasificacion.ipynb](https://colab.research.google.com/github/Daspony/Imagenes-Biomedicas/blob/main/notebooks/04_clasificacion.ipynb) *(No testeado)*
   - [05_denoising.ipynb](https://colab.research.google.com/github/Daspony/Imagenes-Biomedicas/blob/main/notebooks/05_denoising.ipynb)
   - [06_pipeline_completo.ipynb](https://colab.research.google.com/github/Daspony/Imagenes-Biomedicas/blob/main/notebooks/06_pipeline_completo.ipynb) - Pipeline integrado
2. Ejecuta las celdas - el código clonará el repositorio y descargará los datos automáticamente
3. Para notebooks con entrenamiento (03_nnunet), los resultados se guardan en Google Drive

**Ventajas:**
- No requiere instalación local
- GPU gratuita disponible (T4)
- Resultados persistentes en Google Drive
- Todo en la nube

**Desventajas:**
- Sesión limitada a 12 horas
- Debes volver a descargar LUNA16 si la sesión expira (los resultados se mantienen en Drive)

---

## Ejecución Local

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
.venv\Scripts\Activate.ps1
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
│   ├── 00_preparacion_datos.ipynb      # Descarga LUNA16 y verificación LIDC
│   ├── 01_preprocesamiento.ipynb       # Preprocesamiento + máscaras LIDC
│   ├── 02_visualizacion.ipynb          # Visualización + comparación LUNA16 vs LIDC
│   ├── 03_nnunet_segmentacion.ipynb    # Segmentación con nnU-Net v2
│   ├── 04_clasificacion.ipynb          # Clasificación benigno/maligno
│   ├── 05_denoising.ipynb              # Simulación de ruido y denoising
│   └── 06_pipeline_completo.ipynb      # Pipeline integrado completo
│
├── utils/                        # Módulos de código reutilizable
│   ├── __init__.py
│   ├── data_loader.py               # Carga de datos LUNA16
│   ├── preprocessor.py              # Preprocesamiento de imágenes
│   ├── visualizer.py                # Funciones de visualización
│   ├── metrics.py                   # Métricas de evaluación
│   ├── download_luna16.py           # Descarga automática de datos
│   └── lidc_loader.py               # Integración con LIDC-IDRI (pylidc)
│
├── data/                         # Datos de Kaggle (clasificación)
│   ├── all_patches.hdf5             # Patches de nódulos
│   └── malignancy.csv               # Etiquetas benigno/maligno
│
├── weights/                      # Pesos de modelos entrenados
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

### 00_preparacion_datos.ipynb

**Contenido:**
- Descarga automática de LUNA16 (subset0)
- Verificación de solapamiento con LIDC-IDRI
- Lista de escaneos con anotaciones disponibles

**Tiempo de ejecución:** ~30-60 minutos (primera descarga)

### 01_preprocesamiento.ipynb

**Contenido:**
- Carga de imágenes CT (.mhd/.raw)
- Segmentación pulmonar automática
- Normalización de valores Hounsfield (HU)
- CLAHE para realce de contraste
- Explicación del algoritmo `clear_border()`
- Comparación de diferentes thresholds
- **Máscaras de nódulos LIDC-IDRI** (alineadas con coordenadas LUNA16)

**Tiempo de ejecución:** ~5-10 minutos

### 02_visualizacion.ipynb

**Contenido:**
- Visualización de slices 2D y volúmenes 3D
- Anotaciones de nódulos
- Comparación NDCT vs LDCT
- Máscaras de segmentación
- Mapas de calor de densidad
- Controles interactivos
- **Comparación LUNA16 vs LIDC:** Visualización de 6 paneles comparando el método de diámetro (LUNA16) con las máscaras de cada radiólogo (LIDC-IDRI)

### 03_nnunet_segmentacion.ipynb

**Contenido:**
- Pipeline completo para entrenar nnU-Net v2 con máscaras LIDC-IDRI
- Conversión automática de datos LUNA16 a formato NIfTI
- Split Train/Val/Test (70/15/15)
- Preprocesamiento y entrenamiento con nnU-Net
- Inferencia en nuevos casos
- **Detección automática:** El notebook detecta si los datos ya fueron preparados y salta pasos completados
- **Google Colab:** Guarda resultados en Google Drive para no perderlos

**Recomendado ejecutar en Google Colab** (requiere GPU y mucha RAM)

**Tiempo de ejecución:**
- Preparación de datos: ~10 minutos
- Preprocesamiento nnU-Net: ~15 minutos
- Entrenamiento (2D, 1 fold): ~2-6 horas

### 04_clasificacion.ipynb

**Contenido:**
- Clasificador ResNet18 para nódulos (benigno/maligno)
- Dataset de Kaggle con 6691 patches etiquetados
- Entrenamiento completo con métricas
- Curva ROC, matriz de confusión
- **Requiere:** Descargar dataset de [Kaggle](https://www.kaggle.com/datasets/kmader/lungnodemalignancy)

### 05_denoising.ipynb

**Contenido:**
- Simulación de ruido LDCT (Low Dose CT) a partir de NDCT
- Modelos de ruido: Gaussiano, Poisson, CT realista
- Técnicas clásicas: Bilateral, TV, Non-Local Means
- Deep Learning: DnCNN (Denoising CNN)
- Métricas de calidad: PSNR, SSIM
- Comparación de métodos clásicos vs deep learning
- **Soporte para Mayo Clinic LDCT dataset** (pares reales NDCT/LDCT)

**Tiempo de ejecución:** ~10-15 minutos (incluye entrenamiento)

**Dataset opcional:** [Mayo Clinic LDCT (TCIA)](https://www.cancerimagingarchive.net/collection/ldct-and-projection-data/) - 1.32 TB de pares reales

### 06_pipeline_completo.ipynb

**Contenido:**
- Pipeline integrado que combina todos los módulos
- Módulo 1: Preparación de datos (descarga LUNA16)
- Módulo 2: Preprocesamiento (máscaras pulmonares + nódulos LIDC)
- Módulo 3: Visualización (pipeline completo)
- Módulo 4: Métricas y análisis

**Nota:** Este notebook integra el flujo completo referenciando los notebooks individuales para detalles.

---

## Solución de Problemas

### Error: "No module named 'SimpleITK'"

**Solución:** Asegúrate de tener el entorno virtual activado e instala las dependencias:
```bash
.venv\Scripts\Activate.ps1 # Windows
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


## Referencias

- Dataset LUNA16: https://luna16.grand-challenge.org/
- SimpleITK: https://simpleitk.org/
- Scikit-image: https://scikit-image.org/

---

## Licencia

Este proyecto es de uso académico/educativo.
