"""
Módulo de preprocesamiento para imágenes CT pulmonares

Proporciona métodos para:
- Segmentación pulmonar usando técnicas clásicas
- CLAHE para realce de contraste
- Creación de máscaras de nódulos
"""

import numpy as np
import cv2
from skimage import measure, morphology
from skimage.segmentation import clear_border


class LungPreprocessor:
    """
    Preprocesamiento de imágenes CT para segmentación pulmonar

    Métodos:
    - Segmentación pulmonar usando umbralización y morfología
    - CLAHE para realce de contraste
    - Filtrado de ruido
    """

    @staticmethod
    def segment_lung_mask(image, threshold=-320):
        """
        Segmentación pulmonar usando umbralización y operaciones morfológicas

        Inspirado en técnicas comunes de LUNA16 (ej: EliasVansteenkiste/dsb3,
        s-mostafa-a/Luna16) con adaptaciones en el valor de threshold.

        Args:
            image (np.ndarray): Slice 2D en unidades HU
            threshold (int): Umbral HU para binarización (default: -320)
                           Valores típicos en literatura: -604, -350, -320

        Returns:
            np.ndarray: Máscara binaria de pulmones (uint8)

        Algorithm:
            1. Binarización: pixeles < threshold
            2. clear_border: elimina aire externo
            3. Etiquetado de componentes conectados
            4. Selección de las 2 regiones más grandes (pulmones izq/der)
            5. Operaciones morfológicas: dilation → fill_holes → erosion

        Referencias:
            - EliasVansteenkiste/dsb3 usa threshold=-350
            - s-mostafa-a/Luna16 usa threshold=-604
        """
        # Binarización
        binary = image < threshold

        # Limpiar bordes (elimina aire externo)
        cleared = clear_border(binary)

        # Etiquetado de componentes conectados
        label_image = measure.label(cleared)

        # Mantener solo las 2 regiones más grandes (pulmones izquierdo y derecho)
        regions = measure.regionprops(label_image)
        regions = sorted(regions, key=lambda x: x.area, reverse=True)

        # Crear máscara final
        mask = np.zeros_like(binary, dtype=bool)
        for region in regions[:2]:  # Top 2 componentes
            mask[label_image == region.label] = True

        # Operaciones morfológicas para suavizar
        mask = morphology.binary_dilation(mask, morphology.disk(2))
        mask = morphology.binary_fill_holes(mask)
        mask = morphology.binary_erosion(mask, morphology.disk(2))

        return mask.astype(np.uint8)

    @staticmethod
    def apply_clahe(image, clip_limit=2.0, tile_size=(8, 8)):
        """
        Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization)
        para realzar contraste local

        Args:
            image (np.ndarray): Imagen normalizada en [0, 1]
            clip_limit (float): Límite de contraste (default: 2.0)
            tile_size (tuple): Tamaño de tiles (default: (8, 8))

        Returns:
            np.ndarray: Imagen con contraste realzado en [0, 1]

        Notes:
            Útil para visualización de GGOs (Ground Glass Opacities) en LDCT
        """
        # Convertir a uint8 para CLAHE
        image_uint8 = (image * 255).astype(np.uint8)

        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
        enhanced = clahe.apply(image_uint8)

        return enhanced.astype(np.float32) / 255.0

    @staticmethod
    def create_nodule_mask(image_shape, center_coords, diameter, spacing):
        """
        Crea máscara esférica para un nódulo

        Args:
            image_shape (tuple): Dimensiones del volumen (slices, height, width)
            center_coords (array-like): Coordenadas del centro (z, y, x) en voxel
            diameter (float): Diámetro en mm
            spacing (array-like): Espaciado de voxels (z, y, x) en mm

        Returns:
            np.ndarray: Máscara binaria 3D del nódulo (uint8)

        Algorithm:
            Crea una esfera 3D usando distancia euclidiana normalizada
        """
        mask = np.zeros(image_shape, dtype=np.uint8)

        # Radio en voxels
        radius_voxels = (diameter / 2) / spacing

        # Coordenadas
        z, y, x = center_coords

        # Crear esfera
        for dz in range(-int(radius_voxels[0])-1, int(radius_voxels[0])+2):
            for dy in range(-int(radius_voxels[1])-1, int(radius_voxels[1])+2):
                for dx in range(-int(radius_voxels[2])-1, int(radius_voxels[2])+2):
                    z_idx, y_idx, x_idx = z + dz, y + dy, x + dx

                    # Verificar límites
                    if (0 <= z_idx < image_shape[0] and
                        0 <= y_idx < image_shape[1] and
                        0 <= x_idx < image_shape[2]):
                        # Calcular distancia euclidiana
                        dist = np.sqrt(
                            (dz/radius_voxels[0])**2 +
                            (dy/radius_voxels[1])**2 +
                            (dx/radius_voxels[2])**2
                        )
                        if dist <= 1.0:
                            mask[z_idx, y_idx, x_idx] = 1

        return mask
