"""
Módulo de carga de datos para el dataset LUNA16

Este módulo proporciona herramientas para:
- Cargar imágenes CT en formato .mhd/.raw
- Convertir entre coordenadas mundo (mm) y voxel (píxeles)
- Normalizar valores Hounsfield Units (HU)
- Gestionar anotaciones de nódulos
"""

import os
import numpy as np
import pandas as pd
import SimpleITK as sitk


class LUNA16DataLoader:
    """
    Cargador de datos para el dataset LUNA16

    Formato de entrada:
    - Archivos .mhd (MetaImage Header) + .raw (datos binarios)
    - annotations.csv: coordenadas (x,y,z) y diámetro de nódulos
    - candidates.csv: candidatos incluyendo falsos positivos

    Attributes:
        data_path (str): Ruta al directorio con archivos .mhd/.raw
        annotations (pd.DataFrame): DataFrame con anotaciones de nódulos
    """

    def __init__(self, data_path, annotations_path=None):
        """
        Inicializa el cargador de datos

        Args:
            data_path (str): Ruta al directorio con archivos .mhd/.raw
            annotations_path (str, optional): Ruta al archivo annotations.csv
        """
        self.data_path = data_path
        self.annotations = None

        if annotations_path and os.path.exists(annotations_path):
            self.annotations = pd.read_csv(annotations_path)
            print(f"Anotaciones cargadas: {len(self.annotations)} nódulos")

    def load_itk_image(self, filename):
        """
        Carga una imagen CT en formato MetaImage (.mhd)

        Args:
            filename (str): Ruta al archivo .mhd

        Returns:
            tuple: (ct_scan, origin, spacing)
                - ct_scan (np.ndarray): Array 3D con voxels en HU, shape (slices, height, width)
                - origin (np.ndarray): Coordenadas de origen en mm (z, y, x)
                - spacing (np.ndarray): Espaciado entre voxels en mm (z, y, x)

        Notes:
            - SimpleITK usa convención (X, Y, Z), este método invierte a (Z, Y, X)
            - Los valores están en Unidades Hounsfield (HU)
        """
        itkimage = sitk.ReadImage(filename)
        ct_scan = sitk.GetArrayFromImage(itkimage)  # Reconfigura a Shape: [slices, height, width]
        origin = np.array(list(reversed(itkimage.GetOrigin())))
        spacing = np.array(list(reversed(itkimage.GetSpacing())))

        return ct_scan, origin, spacing

    def world_to_voxel(self, world_coords, origin, spacing):
        """
        Convierte coordenadas mundo (mm) a coordenadas voxel (índices)

        Args:
            world_coords (array-like): Coordenadas en mm (z, y, x)
            origin (array-like): Origen del volumen en mm (z, y, x)
            spacing (array-like): Espaciado de voxels en mm (z, y, x)

        Returns:
            np.ndarray: Coordenadas voxel (z, y, x) como enteros

        Formula:
            voxel = round((world - origin) / spacing)
        """
        voxel_coords = np.rint((world_coords - origin) / spacing).astype(int)
        return voxel_coords

    def voxel_to_world(self, voxel_coords, origin, spacing):
        """
        Convierte coordenadas voxel (índices) a coordenadas mundo (mm)

        Args:
            voxel_coords (array-like): Coordenadas voxel (z, y, x)
            origin (array-like): Origen del volumen en mm (z, y, x)
            spacing (array-like): Espaciado de voxels en mm (z, y, x)

        Returns:
            np.ndarray: Coordenadas en mm (z, y, x)

        Formula:
            world = spacing * voxel + origin
        """
        world_coords = spacing * voxel_coords + origin
        return world_coords

    def normalize_hu(self, image, min_hu=-1000, max_hu=400):
        """
        Normaliza valores Hounsfield Units a rango [0, 1]

        Args:
            image (np.ndarray): Imagen en HU
            min_hu (int): Valor HU mínimo (default: -1000 para aire)
            max_hu (int): Valor HU máximo (default: 400 para hueso)

        Returns:
            np.ndarray: Imagen normalizada en rango [0, 1]

        Notes:
            Ventana pulmonar típica: [-1000, 400] HU
            - Valores < min_hu se clips a 0
            - Valores > max_hu se clips a 1
        """
        image = np.clip(image, min_hu, max_hu)
        image = (image - min_hu) / (max_hu - min_hu)
        return image.astype(np.float32)

    def get_annotations_for_scan(self, seriesuid):
        """
        Obtiene anotaciones de nódulos para un escaneo específico

        Args:
            seriesuid (str): Identificador único del escaneo (UID DICOM)

        Returns:
            pd.DataFrame: DataFrame con nódulos del escaneo, o None si no hay anotaciones

        Columns:
            - coordX, coordY, coordZ: Coordenadas en mm
            - diameter_mm: Diámetro del nódulo en mm
        """
        if self.annotations is None:
            return None

        scan_annotations = self.annotations[self.annotations['seriesuid'] == seriesuid]
        return scan_annotations
