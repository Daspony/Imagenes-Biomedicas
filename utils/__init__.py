"""
Utilities para procesamiento de imágenes médicas CT - LUNA16

Módulos disponibles:
- data_loader: Carga de datos LUNA16
- preprocessor: Preprocesamiento de imágenes CT
- visualizer: Visualización de imágenes y resultados
- metrics: Métricas de evaluación
- download_luna16: Descarga y configuración del dataset
"""

from .data_loader import LUNA16DataLoader
from .preprocessor import LungPreprocessor
from .visualizer import LungVisualizer
from .metrics import SegmentationMetrics, DiceLoss
from .download_luna16 import download_luna16

__all__ = [
    'LUNA16DataLoader',
    'LungPreprocessor',
    'LungVisualizer',
    'SegmentationMetrics',
    'DiceLoss',
    'download_luna16',
]

__version__ = '0.1.0'
