# Proyecto de postprocesamiento y análisis de imágenes LDCT para clasificación de nódulos pulmonares

## Descripción general

Este proyecto tiene como objetivo construir un pipeline completo para la segmentación y clasificación de nódulos pulmonares en estudios LDCT, apoyándose en bases de datos públicas (LUNA16, LIDC-IDRI) y reutilizando código libre del estado del arte.

## Etapas principales del pipeline

1. Segmentación del volumen torácico (pulmón)
2. Segmentación de nódulos pulmonares
3. Clasificación de nódulos (benignomaligno o score de riesgo)

---

## Repositorios base recomendados

### 1. Segmentación del volumen pulmonar (pulmón completo)

- [Lung Segmentation (3D U-Net)](httpsgithub.comThvnvtosLung_Segmentation)
- [LUNA16 Segmentation Pipeline](httpsgithub.comnauyanLuna16)
- [Lung-Segmentation-and-Nodule-Detection-LUNA16](httpsgithub.comRakshith2597Lung-Segmentation-and-Nodule-Detection-LUNA16)

### 2. Segmentación de nódulos

- [Lung nodule segmentation (UNetSwin-UNet)](httpsgithub.comAmulyaMatlung-nodule-segmentation)
- [Lung Nodules Segmentation from CT scans (U-Net)](httpsgithub.comayush9304Lung_Cancer_Detection)
- [Lung nodule segmentation - recopilación de proyectos](httpsgithub.comtopicslung-nodule-segmentation)

### 3. Clasificación de nódulos

- [Lung-Segmentation-and-Nodule-Detection-LUNA16](httpsgithub.comRakshith2597Lung-Segmentation-and-Nodule-Detection-LUNA16) (detectar y clasificar)
- [Lung-Nodules-Detection-and-Classification-using-UNet-DenseNet](httpsgithub.comabhikrm0102Lung-Nodules-Detection-and-Classification-using-UNet-DenseNet)
- [LungNoduleDetectionClassification](httpsgithub.commikejhuangLungNoduleDetectionClassification)
- [Lung_Nodule_Classification](httpsgithub.commarichka-dobkoLung_Nodule_Classification)
- [Pulmonary Nodule Classification Software (radiomics)](httpsgithub.comRaallaneslung-nodule-classification)

---

## Sugerencia práctica para iniciar tu pipeline

- Prepara el entorno Clona y prueba algunos de los repos recomendados (empieza por la segmentación de pulmón).
- Establece tu baseline Usa la estructura de datos y preprocesado de LUNA16 para estandarizar tus imágenes LDCT.
- Adapta y versiona Modifica el preprocesado (normalización HU, filtros, etc.) específicamente para LDCT según tus necesidades.
- Entrena o fine-tunea Aprovecha los modelos preentrenados de segmentación y clasificación. Fine-tunea con tus propias muestras LDCT si es posible.
- Evalúa y ajusta Itera sobre los resultados y ajusta las etapas (incluyendo postprocesado y combinación de features radiomics vs deep).

---

## Estructura recomendada del repositorio

