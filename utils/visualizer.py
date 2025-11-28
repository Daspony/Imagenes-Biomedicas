"""
Módulo de visualización para imágenes CT pulmonares

Proporciona herramientas para visualizar:
- Slices CT con anotaciones
- Máscaras de segmentación
- Comparaciones NDCT vs LDCT
- Volúmenes 3D
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


class LungVisualizer:
    """
    Herramientas de visualización para imágenes CT pulmonares
    """

    @staticmethod
    def plot_ct_with_annotations(ct_slice, lung_mask=None, nodule_mask=None,
                                 annotations=None, title="CT Scan", figsize=(15, 5)):
        """
        Visualiza slice de CT con máscaras y anotaciones

        Args:
            ct_slice (np.ndarray): Imagen CT 2D
            lung_mask (np.ndarray, optional): Máscara de segmentación pulmonar
            nodule_mask (np.ndarray, optional): Máscara de nódulos
            annotations (list, optional): Lista de diccionarios con 'x', 'y', 'diameter'
            title (str): Título de la figura
            figsize (tuple): Tamaño de la figura
        """
        n_plots = 1 + (lung_mask is not None) + (nodule_mask is not None)

        fig, axes = plt.subplots(1, n_plots, figsize=figsize)
        if n_plots == 1:
            axes = [axes]

        plot_idx = 0

        # CT original con anotaciones
        axes[plot_idx].imshow(ct_slice, cmap='bone')
        axes[plot_idx].set_title(f"{title} - Original")
        axes[plot_idx].axis('off')

        # Dibujar anotaciones de nódulos
        if annotations is not None:
            for ann in annotations:
                circle = Circle((ann['x'], ann['y']),
                              ann['diameter']/2,
                              color='red',
                              fill=False,
                              linewidth=2)
                axes[plot_idx].add_patch(circle)

        plot_idx += 1

        # Segmentación pulmonar
        if lung_mask is not None:
            axes[plot_idx].imshow(ct_slice, cmap='bone')
            axes[plot_idx].imshow(lung_mask, cmap='Reds', alpha=0.3)
            axes[plot_idx].set_title("Segmentación Pulmonar")
            axes[plot_idx].axis('off')
            plot_idx += 1

        # Nódulos detectados
        if nodule_mask is not None:
            axes[plot_idx].imshow(ct_slice, cmap='bone')
            axes[plot_idx].imshow(nodule_mask, cmap='Greens', alpha=0.5)
            axes[plot_idx].set_title("Nódulos Detectados")
            axes[plot_idx].axis('off')

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_volume_slices(volume, num_slices=9, cmap='bone', title="Volumen CT"):
        """
        Visualiza múltiples slices de un volumen 3D

        Args:
            volume (np.ndarray): Volumen 3D (slices, height, width)
            num_slices (int): Número de slices a visualizar
            cmap (str): Colormap para visualización
            title (str): Título de la figura
        """
        step = volume.shape[0] // num_slices
        slices_to_plot = range(0, volume.shape[0], step)[:num_slices]

        rows = int(np.sqrt(num_slices))
        cols = int(np.ceil(num_slices / rows))

        fig, axes = plt.subplots(rows, cols, figsize=(15, 15))
        axes = axes.flatten()

        for idx, slice_idx in enumerate(slices_to_plot):
            axes[idx].imshow(volume[slice_idx], cmap=cmap)
            axes[idx].set_title(f"Slice {slice_idx}")
            axes[idx].axis('off')

        # Ocultar ejes vacíos
        for idx in range(len(slices_to_plot), len(axes)):
            axes[idx].axis('off')

        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def compare_ndct_ldct(ndct_slice, ldct_slice, title="Comparación NDCT vs LDCT", figsize=(12, 5)):
        """
        Compara lado a lado imágenes NDCT (Normal Dose) vs LDCT (Low Dose)

        Args:
            ndct_slice (np.ndarray): Slice NDCT
            ldct_slice (np.ndarray): Slice LDCT
            title (str): Título de la figura
            figsize (tuple): Tamaño de la figura
        """
        fig, axes = plt.subplots(1, 3, figsize=figsize)

        # NDCT
        axes[0].imshow(ndct_slice, cmap='bone')
        axes[0].set_title("NDCT (Normal Dose)")
        axes[0].axis('off')

        # LDCT
        axes[1].imshow(ldct_slice, cmap='bone')
        axes[1].set_title("LDCT (Low Dose)")
        axes[1].axis('off')

        # Diferencia
        diff = np.abs(ndct_slice - ldct_slice)
        axes[2].imshow(diff, cmap='hot')
        axes[2].set_title("Diferencia Absoluta")
        axes[2].axis('off')

        plt.suptitle(title, fontsize=14)
        plt.tight_layout()
        plt.show()
