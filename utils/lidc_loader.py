"""
Módulo de integración LUNA16 + LIDC-IDRI

Este módulo proporciona herramientas para:
- Acceder a anotaciones de LIDC-IDRI usando pylidc
- Mapear seriesuids de LUNA16 a anotaciones de LIDC
- Extraer scores de malignidad y otras características
- Obtener máscaras de segmentación de nódulos

Nota: pylidc incluye una base de datos SQLite pre-construida con
las anotaciones de los 1018 pacientes de LIDC-IDRI.
No se requiere descargar archivos adicionales para las anotaciones.

Requiere: pip install pylidc
"""

import numpy as np
import warnings
from typing import Optional, List, Dict, Tuple, Any

# Patch de compatibilidad numpy para pylidc (usa np.int deprecado)
np.int = np.int64
np.float = np.float64
np.bool = np.bool_

import pylidc as pl
from pylidc.Scan import Scan


class LIDCAnnotationLoader:
    """
    Cargador de anotaciones LIDC-IDRI para imágenes LUNA16

    LIDC-IDRI contiene anotaciones de 4 radiólogos expertos para cada nódulo,
    incluyendo:
    - Contornos de segmentación (múltiples slices)
    - Score de malignidad (1-5)
    - Características morfológicas (textura, esfericidad, etc.)

    pylidc proporciona acceso a todas estas anotaciones sin necesidad
    de descargar archivos DICOM adicionales.

    Attributes:
        FEATURE_NAMES (list): Nombres de las 9 características anotadas
        MALIGNANCY_LABELS (dict): Mapeo de scores a descripciones
    """

    FEATURE_NAMES = [
        'subtlety',      # 1-5: Sutileza del nódulo
        'internalStructure',  # 1-4: Estructura interna
        'calcification', # 1-6: Calcificación
        'sphericity',    # 1-5: Esfericidad
        'margin',        # 1-5: Definición del margen
        'lobulation',    # 1-5: Lobulación
        'spiculation',   # 1-5: Espiculación
        'texture',       # 1-5: Textura (sólido vs ground-glass)
        'malignancy'     # 1-5: Probabilidad de malignidad
    ]

    MALIGNANCY_LABELS = {
        1: 'Altamente improbable',
        2: 'Moderadamente improbable',
        3: 'Indeterminado',
        4: 'Moderadamente sospechoso',
        5: 'Altamente sospechoso'
    }

    def __init__(self, verbose: bool = True):
        """
        Inicializa el cargador de anotaciones

        Args:
            verbose: Si True, imprime información de estado
        """
        self.verbose = verbose
        self._scan_cache = {}

        # Verificar conexión a la base de datos
        try:
            total_scans = len(pl.query(Scan).all())
            if verbose:
                print(f"LIDC-IDRI database conectada: {total_scans} scans disponibles")
        except Exception as e:
            raise RuntimeError(f"Error conectando a pylidc database: {e}")

    def get_scan_by_seriesuid(self, seriesuid: str) -> Optional[Scan]:
        """
        Obtiene un scan de LIDC-IDRI por SeriesInstanceUID

        Args:
            seriesuid: SeriesInstanceUID (igual al nombre del archivo .mhd en LUNA16)

        Returns:
            Scan object o None si no se encuentra
        """
        if seriesuid in self._scan_cache:
            return self._scan_cache[seriesuid]

        scan = pl.query(Scan).filter(
            Scan.series_instance_uid == seriesuid
        ).first()

        if scan:
            self._scan_cache[seriesuid] = scan

        return scan

    def get_annotations(self, seriesuid: str) -> List[Dict[str, Any]]:
        """
        Obtiene todas las anotaciones para un scan específico

        Cada nódulo puede tener múltiples anotaciones (hasta 4 radiólogos).
        Esta función devuelve TODAS las anotaciones individuales.

        Args:
            seriesuid: SeriesInstanceUID del scan

        Returns:
            Lista de diccionarios con información de cada anotación:
            - annotation_id: ID único de la anotación
            - malignancy: Score de malignidad (1-5)
            - subtlety: Sutileza (1-5)
            - texture: Textura (1-5)
            - sphericity: Esfericidad (1-5)
            - margin: Margen (1-5)
            - lobulation: Lobulación (1-5)
            - spiculation: Espiculación (1-5)
            - calcification: Calcificación (1-6)
            - contour_count: Número de contornos (slices)
            - z_positions: Lista de posiciones z de los contornos
        """
        scan = self.get_scan_by_seriesuid(seriesuid)
        if scan is None:
            if self.verbose:
                print(f"Scan no encontrado: {seriesuid[:50]}...")
            return []

        annotations = []
        for ann in scan.annotations:
            ann_dict = {
                'annotation_id': ann.id,
                'malignancy': ann.malignancy,
                'subtlety': ann.subtlety,
                'texture': ann.texture,
                'sphericity': ann.sphericity,
                'margin': ann.margin,
                'lobulation': ann.lobulation,
                'spiculation': ann.spiculation,
                'calcification': ann.calcification,
                'contour_count': len(ann.contours),
                'z_positions': [c.image_z_position for c in ann.contours]
            }
            annotations.append(ann_dict)

        return annotations

    def get_clustered_nodules(self, seriesuid: str) -> List[List[Dict[str, Any]]]:
        """
        Obtiene nódulos agrupados por consenso de radiólogos

        pylidc agrupa automáticamente las anotaciones que corresponden
        al mismo nódulo físico. Cada grupo contiene las anotaciones
        de diferentes radiólogos para el mismo nódulo.

        Args:
            seriesuid: SeriesInstanceUID del scan

        Returns:
            Lista de grupos, donde cada grupo es una lista de anotaciones
            del mismo nódulo por diferentes radiólogos
        """
        scan = self.get_scan_by_seriesuid(seriesuid)
        if scan is None:
            return []

        # cluster_annotations agrupa por nódulo físico
        nodule_clusters = scan.cluster_annotations()

        result = []
        for cluster in nodule_clusters:
            nodule_annotations = []
            for ann in cluster:
                ann_dict = {
                    'annotation_id': ann.id,
                    'malignancy': ann.malignancy,
                    'subtlety': ann.subtlety,
                    'texture': ann.texture,
                    'sphericity': ann.sphericity,
                    'margin': ann.margin,
                    'lobulation': ann.lobulation,
                    'spiculation': ann.spiculation,
                    'calcification': ann.calcification,
                }
                nodule_annotations.append(ann_dict)
            result.append(nodule_annotations)

        return result

    def get_consensus_malignancy(self, seriesuid: str) -> List[Dict[str, Any]]:
        """
        Calcula el score de malignidad por consenso para cada nódulo

        Promedia los scores de malignidad de todos los radiólogos
        para cada nódulo identificado en el scan.

        Args:
            seriesuid: SeriesInstanceUID del scan

        Returns:
            Lista de diccionarios por nódulo:
            - nodule_idx: Índice del nódulo
            - num_radiologists: Número de radiólogos que anotaron
            - malignancy_mean: Media de scores de malignidad
            - malignancy_std: Desviación estándar
            - malignancy_scores: Lista de scores individuales
            - consensus_label: Etiqueta descriptiva del consenso
        """
        nodule_clusters = self.get_clustered_nodules(seriesuid)

        results = []
        for idx, cluster in enumerate(nodule_clusters):
            scores = [ann['malignancy'] for ann in cluster]
            mean_score = np.mean(scores)

            # Determinar etiqueta de consenso
            rounded = int(round(mean_score))
            label = self.MALIGNANCY_LABELS.get(rounded, 'Desconocido')

            results.append({
                'nodule_idx': idx,
                'num_radiologists': len(cluster),
                'malignancy_mean': mean_score,
                'malignancy_std': np.std(scores),
                'malignancy_scores': scores,
                'consensus_label': label
            })

        return results

    def get_reliable_nodules(self, seriesuid: str, min_annotations: int = 3) -> List:
        """
        Obtiene nódulos con un mínimo de anotaciones de radiólogos

        Filtra los clusters de nódulos para devolver solo aquellos
        que tienen suficiente consenso (múltiples radiólogos).

        Args:
            seriesuid: SeriesInstanceUID del scan
            min_annotations: Mínimo de anotaciones requeridas (default: 3)

        Returns:
            Lista de clusters (cada cluster es una lista de objetos Annotation)
            que tienen al menos min_annotations anotaciones
        """
        scan = self.get_scan_by_seriesuid(seriesuid)
        if scan is None:
            return []

        nodule_clusters = scan.cluster_annotations()
        reliable = [cluster for cluster in nodule_clusters if len(cluster) >= min_annotations]

        if self.verbose and nodule_clusters:
            print(f"Nódulos totales: {len(nodule_clusters)}, "
                  f"con ≥{min_annotations} anotaciones: {len(reliable)}")

        return reliable

    def get_cluster_malignancy(self, cluster: List) -> Dict[str, Any]:
        """
        Calcula el score de malignidad para un cluster de anotaciones

        Args:
            cluster: Lista de objetos Annotation (de pylidc)

        Returns:
            Diccionario con:
            - num_radiologists: Número de radiólogos que anotaron
            - malignancy_mean: Media de scores de malignidad
            - malignancy_std: Desviación estándar
            - malignancy_scores: Lista de scores individuales
            - consensus_label: Etiqueta descriptiva del consenso
        """
        if not cluster:
            return {
                'num_radiologists': 0,
                'malignancy_mean': 0,
                'malignancy_std': 0,
                'malignancy_scores': [],
                'consensus_label': 'Sin datos'
            }

        scores = [ann.malignancy for ann in cluster]
        mean_score = np.mean(scores)

        # Determinar etiqueta de consenso
        rounded = int(round(mean_score))
        label = self.MALIGNANCY_LABELS.get(rounded, 'Desconocido')

        return {
            'num_radiologists': len(cluster),
            'malignancy_mean': mean_score,
            'malignancy_std': np.std(scores),
            'malignancy_scores': scores,
            'consensus_label': label
        }

    def get_annotation_mask(self, seriesuid: str, annotation_idx: int = 0) -> Optional[Tuple[np.ndarray, Tuple]]:
        """
        Obtiene la máscara de segmentación de una anotación específica

        Args:
            seriesuid: SeriesInstanceUID del scan
            annotation_idx: Índice de la anotación (default: primera)

        Returns:
            Tuple (mask, bbox) o None si no se encuentra:
            - mask: Array booleano 3D con la segmentación
            - bbox: Tuple de slices (z, y, x) indicando la posición en el volumen
        """
        scan = self.get_scan_by_seriesuid(seriesuid)
        if scan is None:
            return None

        if annotation_idx >= len(scan.annotations):
            if self.verbose:
                print(f"Anotación {annotation_idx} no existe (total: {len(scan.annotations)})")
            return None

        ann = scan.annotations[annotation_idx]

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                mask = ann.boolean_mask()
                bbox = ann.bbox()
            return mask, bbox
        except Exception as e:
            if self.verbose:
                print(f"Error extrayendo máscara: {e}")
            return None

    def get_consensus_mask(self, seriesuid: str, nodule_idx: int = 0,
                          threshold: float = 0.5) -> Optional[Tuple[np.ndarray, Tuple]]:
        """
        Obtiene la máscara de consenso para un nódulo específico

        Combina las máscaras de todos los radiólogos usando un umbral
        de consenso (por defecto, ≥50% de acuerdo).

        Args:
            seriesuid: SeriesInstanceUID del scan
            nodule_idx: Índice del nódulo en los clusters
            threshold: Fracción mínima de radiólogos de acuerdo (0-1)

        Returns:
            Tuple (mask, bbox) o None:
            - mask: Array booleano 3D con la segmentación de consenso
            - bbox: Bounding box que contiene todas las anotaciones
        """
        scan = self.get_scan_by_seriesuid(seriesuid)
        if scan is None:
            return None

        nodule_clusters = scan.cluster_annotations()
        if nodule_idx >= len(nodule_clusters):
            if self.verbose:
                print(f"Nódulo {nodule_idx} no existe (total: {len(nodule_clusters)})")
            return None

        cluster = nodule_clusters[nodule_idx]

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                # Obtener máscaras y bboxes de todas las anotaciones
                masks_and_bboxes = []
                for ann in cluster:
                    mask = ann.boolean_mask()
                    bbox = ann.bbox()
                    masks_and_bboxes.append((mask, bbox))

                if not masks_and_bboxes:
                    return None

                # Calcular el bbox combinado
                all_starts = []
                all_ends = []
                for mask, bbox in masks_and_bboxes:
                    starts = [s.start for s in bbox]
                    ends = [s.stop for s in bbox]
                    all_starts.append(starts)
                    all_ends.append(ends)

                min_starts = np.min(all_starts, axis=0)
                max_ends = np.max(all_ends, axis=0)

                # Crear volumen combinado
                combined_shape = tuple(max_ends - min_starts)
                vote_volume = np.zeros(combined_shape, dtype=np.float32)

                # Sumar votos de cada radiólogo
                for mask, bbox in masks_and_bboxes:
                    offsets = [bbox[i].start - min_starts[i] for i in range(3)]
                    vote_volume[
                        offsets[0]:offsets[0]+mask.shape[0],
                        offsets[1]:offsets[1]+mask.shape[1],
                        offsets[2]:offsets[2]+mask.shape[2]
                    ] += mask.astype(np.float32)

                # Normalizar por número de radiólogos
                vote_volume /= len(masks_and_bboxes)

                # Aplicar umbral de consenso
                consensus_mask = vote_volume >= threshold

                # Crear bbox combinado
                combined_bbox = tuple(slice(int(min_starts[i]), int(max_ends[i])) for i in range(3))

                return consensus_mask, combined_bbox

        except Exception as e:
            if self.verbose:
                print(f"Error calculando máscara de consenso: {e}")
            return None

    def get_scan_metadata(self, seriesuid: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene metadatos del scan (spacing, etc.)

        Args:
            seriesuid: SeriesInstanceUID del scan

        Returns:
            Diccionario con metadatos o None:
            - patient_id: ID del paciente (LIDC-IDRI-XXXX)
            - pixel_spacing: Espaciado xy en mm
            - slice_thickness: Grosor de slice en mm
            - slice_spacing: Espaciado entre slices en mm
            - num_annotations: Número total de anotaciones
            - num_nodules: Número de nódulos únicos (clusters)
        """
        scan = self.get_scan_by_seriesuid(seriesuid)
        if scan is None:
            return None

        return {
            'patient_id': scan.patient_id,
            'pixel_spacing': scan.pixel_spacing,
            'slice_thickness': scan.slice_thickness,
            'slice_spacing': scan.slice_spacing,
            'num_annotations': len(scan.annotations),
            'num_nodules': len(scan.cluster_annotations())
        }

    def get_aligned_mask(self, seriesuid: str, annotation_idx: int,
                         origin: np.ndarray, spacing: np.ndarray,
                         ct_shape: Tuple[int, int, int]) -> Optional[Tuple[np.ndarray, Tuple]]:
        """
        Obtiene máscara de segmentación alineada con coordenadas LUNA16.

        Convierte las coordenadas DICOM de pylidc a índices LUNA16 usando
        el origin y spacing del archivo .mhd.

        Args:
            seriesuid: SeriesInstanceUID del scan
            annotation_idx: Índice de la anotación
            origin: Origin del volumen LUNA16 (z, y, x) en mm
            spacing: Spacing del volumen LUNA16 (z, y, x) en mm
            ct_shape: Shape del volumen CT (slices, height, width)

        Returns:
            Tuple (mask, bbox) alineado con LUNA16, o None si falla:
            - mask: Array booleano 3D con la segmentación
            - bbox: Tuple de slices (z, y, x) en coordenadas LUNA16
        """
        scan = self.get_scan_by_seriesuid(seriesuid)
        if scan is None:
            return None

        if annotation_idx >= len(scan.annotations):
            return None

        ann = scan.annotations[annotation_idx]

        try:
            # Obtener contornos con sus posiciones z en mm
            contours = ann.contours
            if not contours:
                return None

            # Convertir z_positions de mm a índices LUNA16
            z_positions_mm = [c.image_z_position for c in contours]
            z_indices = [int(round((z_mm - origin[0]) / spacing[0])) for z_mm in z_positions_mm]

            # Filtrar índices válidos
            valid_contours = []
            for i, (contour, z_idx) in enumerate(zip(contours, z_indices)):
                if 0 <= z_idx < ct_shape[0]:
                    valid_contours.append((contour, z_idx))

            if not valid_contours:
                if self.verbose:
                    print(f"No hay contornos válidos dentro del rango del CT")
                return None

            # Calcular bounding box en coordenadas LUNA16
            z_indices_valid = [z for _, z in valid_contours]
            z_min, z_max = min(z_indices_valid), max(z_indices_valid)

            # Obtener límites x, y de los contornos
            all_y, all_x = [], []
            for contour, _ in valid_contours:
                coords = contour.to_matrix()  # (N, 3) array con (i, j, k)
                all_y.extend(coords[:, 0].tolist())
                all_x.extend(coords[:, 1].tolist())

            y_min, y_max = int(min(all_y)), int(max(all_y)) + 1
            x_min, x_max = int(min(all_x)), int(max(all_x)) + 1

            # Asegurar límites dentro del CT
            y_min = max(0, y_min)
            y_max = min(ct_shape[1], y_max)
            x_min = max(0, x_min)
            x_max = min(ct_shape[2], x_max)

            # Crear máscara alineada
            mask_shape = (z_max - z_min + 1, y_max - y_min, x_max - x_min)
            mask = np.zeros(mask_shape, dtype=bool)

            # Rellenar la máscara con los contornos
            from skimage.draw import polygon

            for contour, z_idx in valid_contours:
                coords = contour.to_matrix()
                # coords[:, 0] = i (row/y), coords[:, 1] = j (col/x)
                rr, cc = polygon(coords[:, 0] - y_min, coords[:, 1] - x_min,
                                shape=(y_max - y_min, x_max - x_min))
                z_local = z_idx - z_min
                if 0 <= z_local < mask.shape[0]:
                    mask[z_local, rr, cc] = True

            # Crear bbox en coordenadas LUNA16
            bbox = (slice(z_min, z_max + 1), slice(y_min, y_max), slice(x_min, x_max))

            return mask, bbox

        except Exception as e:
            if self.verbose:
                print(f"Error creando máscara alineada: {e}")
            return None

    def get_aligned_consensus_mask(self, seriesuid: str, nodule_idx: int,
                                   origin: np.ndarray, spacing: np.ndarray,
                                   ct_shape: Tuple[int, int, int],
                                   threshold: float = 0.5) -> Optional[Tuple[np.ndarray, Tuple]]:
        """
        Obtiene máscara de consenso alineada con coordenadas LUNA16.

        Combina las máscaras de todos los radiólogos para un nódulo,
        convertidas a coordenadas LUNA16.

        Args:
            seriesuid: SeriesInstanceUID del scan
            nodule_idx: Índice del nódulo en los clusters
            origin: Origin del volumen LUNA16 (z, y, x) en mm
            spacing: Spacing del volumen LUNA16 (z, y, x) en mm
            ct_shape: Shape del volumen CT (slices, height, width)
            threshold: Fracción mínima de radiólogos de acuerdo (0-1)

        Returns:
            Tuple (mask, bbox) de consenso alineado, o None si falla
        """
        scan = self.get_scan_by_seriesuid(seriesuid)
        if scan is None:
            return None

        nodule_clusters = scan.cluster_annotations()
        if nodule_idx >= len(nodule_clusters):
            return None

        cluster = nodule_clusters[nodule_idx]

        try:
            from skimage.draw import polygon

            # Recolectar todos los contornos de todas las anotaciones
            all_contour_data = []  # Lista de (z_idx, y_coords, x_coords)

            for ann in cluster:
                for contour in ann.contours:
                    z_mm = contour.image_z_position
                    z_idx = int(round((z_mm - origin[0]) / spacing[0]))

                    if 0 <= z_idx < ct_shape[0]:
                        coords = contour.to_matrix()
                        all_contour_data.append((z_idx, coords[:, 0], coords[:, 1]))

            if not all_contour_data:
                return None

            # Calcular bounding box global
            all_z = [d[0] for d in all_contour_data]
            all_y = np.concatenate([d[1] for d in all_contour_data])
            all_x = np.concatenate([d[2] for d in all_contour_data])

            z_min, z_max = min(all_z), max(all_z)
            y_min, y_max = int(min(all_y)), int(max(all_y)) + 1
            x_min, x_max = int(min(all_x)), int(max(all_x)) + 1

            # Asegurar límites
            y_min, y_max = max(0, y_min), min(ct_shape[1], y_max)
            x_min, x_max = max(0, x_min), min(ct_shape[2], x_max)

            # Crear volumen de votos
            mask_shape = (z_max - z_min + 1, y_max - y_min, x_max - x_min)
            vote_volume = np.zeros(mask_shape, dtype=np.float32)

            # Contar votos por radiólogo (no por contorno)
            for ann in cluster:
                ann_mask = np.zeros(mask_shape, dtype=bool)

                for contour in ann.contours:
                    z_mm = contour.image_z_position
                    z_idx = int(round((z_mm - origin[0]) / spacing[0]))

                    if z_min <= z_idx <= z_max:
                        coords = contour.to_matrix()
                        rr, cc = polygon(coords[:, 0] - y_min, coords[:, 1] - x_min,
                                        shape=(y_max - y_min, x_max - x_min))
                        z_local = z_idx - z_min
                        if 0 <= z_local < mask_shape[0]:
                            ann_mask[z_local, rr, cc] = True

                vote_volume += ann_mask.astype(np.float32)

            # Normalizar por número de radiólogos
            vote_volume /= len(cluster)

            # Aplicar umbral de consenso
            consensus_mask = vote_volume >= threshold

            bbox = (slice(z_min, z_max + 1), slice(y_min, y_max), slice(x_min, x_max))

            return consensus_mask, bbox

        except Exception as e:
            if self.verbose:
                print(f"Error creando máscara de consenso alineada: {e}")
            return None

    def get_aligned_mask_for_cluster(self, cluster: List,
                                      origin: np.ndarray, spacing: np.ndarray,
                                      ct_shape: Tuple[int, int, int],
                                      threshold: float = 0.5) -> Optional[Tuple[np.ndarray, Tuple]]:
        """
        Obtiene máscara de consenso alineada para un cluster específico.

        Útil cuando ya se tiene el cluster (por ejemplo, de get_reliable_nodules).

        Args:
            cluster: Lista de objetos Annotation (de pylidc)
            origin: Origin del volumen LUNA16 (z, y, x) en mm
            spacing: Spacing del volumen LUNA16 (z, y, x) en mm
            ct_shape: Shape del volumen CT (slices, height, width)
            threshold: Fracción mínima de radiólogos de acuerdo (0-1)

        Returns:
            Tuple (mask, bbox) de consenso alineado, o None si falla
        """
        if not cluster:
            return None

        try:
            from skimage.draw import polygon

            # Recolectar todos los contornos de todas las anotaciones
            all_contour_data = []  # Lista de (z_idx, y_coords, x_coords)

            for ann in cluster:
                for contour in ann.contours:
                    z_mm = contour.image_z_position
                    z_idx = int(round((z_mm - origin[0]) / spacing[0]))

                    if 0 <= z_idx < ct_shape[0]:
                        coords = contour.to_matrix()
                        all_contour_data.append((z_idx, coords[:, 0], coords[:, 1]))

            if not all_contour_data:
                return None

            # Calcular bounding box global
            all_z = [d[0] for d in all_contour_data]
            all_y = np.concatenate([d[1] for d in all_contour_data])
            all_x = np.concatenate([d[2] for d in all_contour_data])

            z_min, z_max = min(all_z), max(all_z)
            y_min, y_max = int(min(all_y)), int(max(all_y)) + 1
            x_min, x_max = int(min(all_x)), int(max(all_x)) + 1

            # Asegurar límites
            y_min, y_max = max(0, y_min), min(ct_shape[1], y_max)
            x_min, x_max = max(0, x_min), min(ct_shape[2], x_max)

            # Crear volumen de votos
            mask_shape = (z_max - z_min + 1, y_max - y_min, x_max - x_min)
            vote_volume = np.zeros(mask_shape, dtype=np.float32)

            # Contar votos por radiólogo (no por contorno)
            for ann in cluster:
                ann_mask = np.zeros(mask_shape, dtype=bool)

                for contour in ann.contours:
                    z_mm = contour.image_z_position
                    z_idx = int(round((z_mm - origin[0]) / spacing[0]))

                    if z_min <= z_idx <= z_max:
                        coords = contour.to_matrix()
                        rr, cc = polygon(coords[:, 0] - y_min, coords[:, 1] - x_min,
                                        shape=(y_max - y_min, x_max - x_min))
                        z_local = z_idx - z_min
                        if 0 <= z_local < mask_shape[0]:
                            ann_mask[z_local, rr, cc] = True

                vote_volume += ann_mask.astype(np.float32)

            # Normalizar por número de radiólogos
            vote_volume /= len(cluster)

            # Aplicar umbral de consenso
            consensus_mask = vote_volume >= threshold

            bbox = (slice(z_min, z_max + 1), slice(y_min, y_max), slice(x_min, x_max))

            return consensus_mask, bbox

        except Exception as e:
            if self.verbose:
                print(f"Error creando máscara para cluster: {e}")
            return None

    def map_luna16_to_lidc(self, seriesuids: List[str]) -> Dict[str, Optional[str]]:
        """
        Mapea una lista de seriesuids de LUNA16 a patient_ids de LIDC

        Args:
            seriesuids: Lista de SeriesInstanceUIDs de LUNA16

        Returns:
            Diccionario {seriesuid: patient_id} o {seriesuid: None} si no existe
        """
        mapping = {}
        found = 0

        for uid in seriesuids:
            scan = self.get_scan_by_seriesuid(uid)
            if scan:
                mapping[uid] = scan.patient_id
                found += 1
            else:
                mapping[uid] = None

        if self.verbose:
            print(f"Mapeados {found}/{len(seriesuids)} seriesuids a LIDC-IDRI")

        return mapping

    def get_all_lidc_seriesuids(self) -> List[str]:
        """
        Obtiene todos los seriesuids disponibles en LIDC-IDRI

        Returns:
            Lista de 1018 SeriesInstanceUIDs
        """
        scans = pl.query(Scan).all()
        return [scan.series_instance_uid for scan in scans]


def verify_luna16_lidc_overlap(luna16_seriesuids: List[str], verbose: bool = True) -> Dict[str, Any]:
    """
    Verifica el overlap entre seriesuids de LUNA16 y LIDC-IDRI

    Args:
        luna16_seriesuids: Lista de seriesuids de LUNA16
        verbose: Imprimir resultados

    Returns:
        Diccionario con estadísticas de overlap
    """
    loader = LIDCAnnotationLoader(verbose=False)
    lidc_uids = set(loader.get_all_lidc_seriesuids())
    luna_uids = set(luna16_seriesuids)

    overlap = luna_uids & lidc_uids
    only_luna = luna_uids - lidc_uids
    only_lidc = lidc_uids - luna_uids

    result = {
        'luna16_total': len(luna_uids),
        'lidc_total': len(lidc_uids),
        'overlap': len(overlap),
        'overlap_percentage': len(overlap) / len(luna_uids) * 100 if luna_uids else 0,
        'only_in_luna16': len(only_luna),
        'only_in_lidc': len(only_lidc),
        'overlapping_uids': list(overlap)
    }

    if verbose:
        print(f"=== LUNA16 <-> LIDC-IDRI Overlap ===")
        print(f"LUNA16 seriesuids: {result['luna16_total']}")
        print(f"LIDC-IDRI seriesuids: {result['lidc_total']}")
        print(f"Overlap: {result['overlap']} ({result['overlap_percentage']:.1f}%)")
        print(f"Solo en LUNA16: {result['only_in_luna16']}")
        print(f"Solo en LIDC-IDRI: {result['only_in_lidc']}")

    return result


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== Demo LIDCAnnotationLoader ===\n")

    loader = LIDCAnnotationLoader()

    # Ejemplo con un seriesuid de LUNA16
    example_uid = "1.3.6.1.4.1.14519.5.2.1.6279.6001.100225287222365663678666836860"

    print(f"\n--- Metadata del scan ---")
    metadata = loader.get_scan_metadata(example_uid)
    if metadata:
        for k, v in metadata.items():
            print(f"  {k}: {v}")

    print(f"\n--- Consensus malignancy ---")
    consensus = loader.get_consensus_malignancy(example_uid)
    for nodule in consensus:
        print(f"  Nódulo {nodule['nodule_idx']}: "
              f"malignancy={nodule['malignancy_mean']:.2f} ± {nodule['malignancy_std']:.2f} "
              f"({nodule['num_radiologists']} radiólogos) - {nodule['consensus_label']}")