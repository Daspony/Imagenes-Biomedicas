"""
Módulo de métricas para evaluación de segmentación y detección

Proporciona:
- Métricas de segmentación (Dice, IoU, Sensitivity, Specificity)
- Funciones de pérdida para entrenamiento (Dice Loss, Focal Loss)
"""

import numpy as np
import torch
import torch.nn as nn


class SegmentationMetrics:
    """
    Métricas de evaluación para segmentación de imágenes médicas

    Métricas implementadas:
    - Dice Coefficient (F1-score para segmentación)
    - IoU (Intersection over Union / Jaccard Index)
    - Sensitivity (Recall / True Positive Rate)
    - Specificity (True Negative Rate)
    """

    @staticmethod
    def dice_coefficient(y_true, y_pred, smooth=1e-7):
        """
        Calcula el coeficiente de Dice (F1-score)

        Args:
            y_true (np.ndarray): Máscara ground truth (0 o 1)
            y_pred (np.ndarray): Máscara predicha (0 o 1)
            smooth (float): Factor de suavizado para evitar división por cero

        Returns:
            float: Dice coefficient en rango [0, 1]

        Formula:
            Dice = 2 * |A ∩ B| / (|A| + |B|)
        """
        y_true_f = y_true.flatten()
        y_pred_f = y_pred.flatten()

        intersection = np.sum(y_true_f * y_pred_f)
        dice = (2. * intersection + smooth) / (np.sum(y_true_f) + np.sum(y_pred_f) + smooth)

        return dice

    @staticmethod
    def iou_score(y_true, y_pred, smooth=1e-7):
        """
        Calcula Intersection over Union (IoU / Jaccard Index)

        Args:
            y_true (np.ndarray): Máscara ground truth (0 o 1)
            y_pred (np.ndarray): Máscara predicha (0 o 1)
            smooth (float): Factor de suavizado

        Returns:
            float: IoU score en rango [0, 1]

        Formula:
            IoU = |A ∩ B| / |A ∪ B|
        """
        y_true_f = y_true.flatten()
        y_pred_f = y_pred.flatten()

        intersection = np.sum(y_true_f * y_pred_f)
        union = np.sum(y_true_f) + np.sum(y_pred_f) - intersection

        iou = (intersection + smooth) / (union + smooth)

        return iou

    @staticmethod
    def sensitivity(y_true, y_pred, smooth=1e-7):
        """
        Calcula Sensitivity (Recall / True Positive Rate)

        Args:
            y_true (np.ndarray): Máscara ground truth
            y_pred (np.ndarray): Máscara predicha
            smooth (float): Factor de suavizado

        Returns:
            float: Sensitivity en rango [0, 1]

        Formula:
            Sensitivity = TP / (TP + FN)

        Notes:
            Importante para detectar todos los nódulos (minimizar falsos negativos)
        """
        y_true_f = y_true.flatten()
        y_pred_f = y_pred.flatten()

        true_positives = np.sum(y_true_f * y_pred_f)
        possible_positives = np.sum(y_true_f)

        return (true_positives + smooth) / (possible_positives + smooth)

    @staticmethod
    def specificity(y_true, y_pred, smooth=1e-7):
        """
        Calcula Specificity (True Negative Rate)

        Args:
            y_true (np.ndarray): Máscara ground truth
            y_pred (np.ndarray): Máscara predicha
            smooth (float): Factor de suavizado

        Returns:
            float: Specificity en rango [0, 1]

        Formula:
            Specificity = TN / (TN + FP)

        Notes:
            Importante para minimizar falsos positivos
        """
        y_true_f = y_true.flatten()
        y_pred_f = y_pred.flatten()

        # Invertir máscaras para calcular negativos
        y_true_neg = 1 - y_true_f
        y_pred_neg = 1 - y_pred_f

        true_negatives = np.sum(y_true_neg * y_pred_neg)
        possible_negatives = np.sum(y_true_neg)

        return (true_negatives + smooth) / (possible_negatives + smooth)

    @staticmethod
    def compute_all_metrics(y_true, y_pred):
        """
        Calcula todas las métricas de segmentación

        Args:
            y_true (np.ndarray): Máscara ground truth
            y_pred (np.ndarray): Máscara predicha

        Returns:
            dict: Diccionario con todas las métricas
        """
        return {
            'dice': SegmentationMetrics.dice_coefficient(y_true, y_pred),
            'iou': SegmentationMetrics.iou_score(y_true, y_pred),
            'sensitivity': SegmentationMetrics.sensitivity(y_true, y_pred),
            'specificity': SegmentationMetrics.specificity(y_true, y_pred)
        }


class DiceLoss(nn.Module):
    """
    Dice Loss para entrenamiento de redes de segmentación

    Útil para datasets desbalanceados (pocos píxeles positivos)
    Comúnmente usado en segmentación médica (U-Net, nnU-Net, etc.)

    Usage:
        criterion = DiceLoss()
        loss = criterion(predictions, targets)
    """

    def __init__(self, smooth=1e-7):
        """
        Args:
            smooth (float): Factor de suavizado para evitar división por cero
        """
        super(DiceLoss, self).__init__()
        self.smooth = smooth

    def forward(self, predictions, targets):
        """
        Calcula Dice Loss

        Args:
            predictions (torch.Tensor): Predicciones del modelo [B, C, H, W]
            targets (torch.Tensor): Ground truth [B, C, H, W]

        Returns:
            torch.Tensor: Dice loss (1 - Dice coefficient)

        Notes:
            - Minimizar Dice Loss equivale a maximizar Dice Coefficient
            - Rango: [0, 1] donde 0 es predicción perfecta
        """
        predictions = torch.sigmoid(predictions)

        # Flatten
        predictions = predictions.view(-1)
        targets = targets.view(-1)

        intersection = (predictions * targets).sum()
        dice = (2. * intersection + self.smooth) / (predictions.sum() + targets.sum() + self.smooth)

        return 1 - dice


class FocalLoss(nn.Module):
    """
    Focal Loss para clasificación binaria desbalanceada

    Útil para detección de nódulos (muchos más negativos que positivos)

    Reference:
        Lin et al. "Focal Loss for Dense Object Detection" (2017)
    """

    def __init__(self, alpha=0.25, gamma=2.0):
        """
        Args:
            alpha (float): Peso para clase positiva (default: 0.25)
            gamma (float): Focusing parameter (default: 2.0)
        """
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, predictions, targets):
        """
        Calcula Focal Loss

        Args:
            predictions (torch.Tensor): Predicciones crudas [B, C, H, W]
            targets (torch.Tensor): Ground truth [B, C, H, W]

        Returns:
            torch.Tensor: Focal loss
        """
        bce_loss = nn.functional.binary_cross_entropy_with_logits(
            predictions, targets, reduction='none'
        )

        predictions_prob = torch.sigmoid(predictions)
        p_t = predictions_prob * targets + (1 - predictions_prob) * (1 - targets)

        alpha_factor = targets * self.alpha + (1 - targets) * (1 - self.alpha)
        modulating_factor = (1.0 - p_t) ** self.gamma

        loss = alpha_factor * modulating_factor * bce_loss

        return loss.mean()
