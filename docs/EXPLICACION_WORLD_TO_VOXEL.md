# Conversión World ↔ Voxel - Explicación Visual Detallada

## Tu comprensión actual (¡Correcto!)

> "En ct_scan tenemos una caja llena de voxels y entre cada voxel hay distinta distancia en el mundo real"

✅ **¡Exactamente!** Tienes razón:

```
Caja 3D de voxels (ct_scan):
- 133 slices (eje Z): separados 2.5 mm cada uno
- 512 filas (eje Y): separadas 0.703 mm cada una
- 512 columnas (eje X): separadas 0.703 mm cada una
```

---

## 1. Visualización del Problema

### 1.1 El Sistema de Coordenadas del Mundo Real

Imagina que el tórax del paciente está en un espacio 3D con coordenadas en **milímetros**:

```
Sistema de coordenadas del PACIENTE (mm):

        Z (eje cabeza-pies)
        ↑
        |
        |    ● Nódulo en (-128.7, -175.3, -298.4) mm
        |
        |
        0,0,0 (punto de referencia médico)
        |________________→ X (izquierda-derecha)
       /
      /
     ↓ Y (adelante-atrás)

Este es el MUNDO REAL con medidas FÍSICAS en milímetros
```

### 1.2 El Sistema de Coordenadas de la Imagen

Ahora, la tomografía captura esa región y la guarda como voxels:

```
Sistema de coordenadas del ARRAY ct_scan (índices):

        slice_index
        ↑
        |
        |    ● Nódulo en voxel [59, 256, 300]
        |
        |
        [0,0,0] (esquina del array)
        |________________→ columna (X)
       /
      /
     ↓ fila (Y)

Este es el ARRAY con ÍNDICES discretos (números enteros)
```

**El problema:** Estos dos sistemas NO están alineados automáticamente.

---

## 2. ¿Por qué necesitamos ORIGIN?

El **origin** es el puente entre estos dos sistemas. Te dice: "El voxel [0,0,0] del array corresponde al punto (origin_x, origin_y, origin_z) en milímetros del mundo real"

### Ejemplo visual:

```
MUNDO REAL (mm):                    ARRAY ct_scan:

     -200 mm                             Voxel [0]
       ↓                                    ↓
    ┌──────────────┐                  ┌──────────────┐
-200│              │                  │              │
 mm →│   Región    │                  │  Array de    │
    │   escaneada │                  │   voxels     │
    │              │                  │              │
    └──────────────┘                  └──────────────┘

Origin = (-200, -200, -150) significa:
"El voxel [0,0,0] está en la posición (-200, -200, -150) mm del cuerpo"
```

---

## 3. ¿Por qué necesitamos SPACING?

El **spacing** te dice cuántos milímetros representa cada "paso" de un voxel al siguiente.

### Visualización del Spacing:

```
SLICES (eje Z):

Slice 0  →  Slice 1  →  Slice 2
  |          |          |
  |←─2.5mm──→|←─2.5mm──→|

Spacing Z = 2.5 mm/voxel


PIXELES dentro de un slice (eje X):

Pixel 0  Pixel 1  Pixel 2  Pixel 3
   |       |        |        |
   |←0.7mm→|←0.7mm→|←0.7mm→|

Spacing X = 0.703 mm/pixel
```

---

## 4. Función `world_to_voxel()` - Paso a Paso

### 4.1 ¿Qué hace?

Convierte una posición en **milímetros** (del mundo real) a un **índice de voxel** (del array).

```python
def world_to_voxel(world_coords, origin, spacing):
    voxel_coords = np.rint((world_coords - origin) / spacing).astype(int)
    return voxel_coords
```

### 4.2 La Fórmula Explicada Visualmente

**Fórmula:** `voxel = round((mundo - origin) / spacing)`

Vamos paso por paso con un ejemplo REAL:

**Datos:**
- Nódulo en mundo real: `(-128.7, -175.3, -298.4)` mm
- Origin: `(-200, -200, -150)` mm
- Spacing: `(2.5, 0.703, 0.703)` mm/voxel

#### PASO 1: Restar el Origin

**¿Por qué?** Porque necesitamos saber la distancia RELATIVA desde el punto de referencia (voxel [0,0,0]).

```
Mundo Real (mm):                    Después de restar origin:

     Origin                              Distancia desde [0,0,0]
    (-200, -200, -150)                         (0, 0, 0)
         ↓                                          ↓
    ┌────────────────┐                  ┌────────────────┐
    │                │                  │                │
    │    ● Nódulo    │                  │    ● Nódulo    │
    │  (-128.7, -175.3, -298.4)         │   (71.3, 24.7, -148.4)
    │                │                  │                │
    └────────────────┘                  └────────────────┘

Cálculo:
(-128.7, -175.3, -298.4) - (-200, -200, -150)
= (-128.7+200, -175.3+200, -298.4+150)
= (71.3, 24.7, -148.4) mm desde el voxel [0,0,0]
```

**Interpretación:** El nódulo está a:
- 71.3 mm a la derecha del voxel [0,0,0] (eje X)
- 24.7 mm abajo del voxel [0,0,0] (eje Y)
- -148.4 mm ANTES del voxel [0,0,0] (eje Z negativo)

#### PASO 2: Dividir por Spacing

**¿Por qué?** Para convertir milímetros a "cantidad de voxels".

```
Distancia en mm:          Spacing:         Voxels:
    71.3 mm          ÷   0.703 mm/voxel  =  101.4 voxels
    24.7 mm          ÷   0.703 mm/voxel  =   35.1 voxels
  -148.4 mm          ÷   2.5 mm/voxel    =  -59.4 voxels
```

**Visualización del eje X:**

```
     Voxel:    0     1     2     3    ...   101    102
               |     |     |     |          |      |
Distancia:  0mm  0.7mm 1.4mm 2.1mm  ...  71.0mm 71.7mm
                                            ↑
                              Nódulo en 71.3 mm ≈ voxel 101.4
```

#### PASO 3: Redondear al entero más cercano

**¿Por qué?** Porque los índices de array DEBEN ser enteros (no puedes tener voxel [101.4], debe ser [101] o [102]).

```
(101.4, 35.1, -59.4)  →  round()  →  (101, 35, -59)
```

**Resultado final:**
```
Mundo: (-128.7, -175.3, -298.4) mm  →  Voxel: [101, 35, -59]
```

⚠️ **Nota:** El -59 indica que está FUERA del array (que va de 0 a 132). Esto significa que este nódulo específico no está en el volumen escaneado.

---

## 5. Función `voxel_to_world()` - La Operación Inversa

### 5.1 ¿Qué hace?

Convierte un **índice de voxel** (del array) a una posición en **milímetros** (del mundo real).

```python
def voxel_to_world(voxel_coords, origin, spacing):
    world_coords = spacing * voxel_coords + origin
    return world_coords
```

### 5.2 La Fórmula Explicada

**Fórmula:** `mundo = (voxel × spacing) + origin`

Es exactamente lo contrario de `world_to_voxel`.

**Ejemplo:**

```python
# Datos:
voxel = (59, 256, 300)
spacing = (2.5, 0.703, 0.703)
origin = (-200, -200, -150)

# Paso 1: Multiplicar por spacing (convertir índices a mm relativos)
distancia_relativa = (59, 256, 300) × (2.5, 0.703, 0.703)
                   = (147.5, 180.0, 210.9) mm desde voxel [0,0,0]

# Paso 2: Sumar origin (convertir a coordenadas absolutas)
mundo = (147.5, 180.0, 210.9) + (-200, -200, -150)
      = (-52.5, -20.0, 60.9) mm en el espacio del paciente
```

---

## 6. ¿Por qué es útil `world_to_voxel()`?

### Caso de Uso Principal: **Localizar nódulos anotados en la imagen**

Los radiólogos anotaron nódulos en **coordenadas del mundo real** (mm). Para ver esos nódulos en el array `ct_scan`, necesitas convertir a índices de voxel.

### Ejemplo Práctico Completo:

```python
# PASO 1: El radiólogo anotó un nódulo
# Archivo annotations.csv:
# coordX,coordY,coordZ,diameter_mm
# -128.7,-175.3,-298.4,5.6

# PASO 2: Cargas el CT scan
ct_scan, origin, spacing = loader.load_itk_image(filename)
# ct_scan.shape = (133, 512, 512)

# PASO 3: Quieres VER ese nódulo en la imagen
# Necesitas saber en qué voxel está

# Las coordenadas del CSV están en mm (mundo real):
nod_world = np.array([-298.4, -175.3, -128.7])  # (Z, Y, X) en mm

# PASO 4: Convertir a voxel para acceder al array
nod_voxel = world_to_voxel(nod_world, origin, spacing)
# Resultado: [59, 256, 300]

# PASO 5: Ahora puedes acceder al nódulo en ct_scan
slice_idx, row, col = nod_voxel
nodule_slice = ct_scan[slice_idx]  # Slice 2D con el nódulo

# PASO 6: Extraer región alrededor del nódulo (por ejemplo, 32×32 pixels)
patch = ct_scan[
    slice_idx-5:slice_idx+5,    # 10 slices alrededor
    row-16:row+16,              # 32 pixeles alto
    col-16:col+16               # 32 pixeles ancho
]

# PASO 7: Visualizar
import matplotlib.pyplot as plt
plt.imshow(nodule_slice, cmap='gray')
plt.plot(col, row, 'ro', markersize=10)  # Marcar nódulo
plt.title(f"Nódulo en slice {slice_idx}")
plt.show()
```

**Sin `world_to_voxel()` NO podrías hacer esto** porque solo tienes coordenadas en mm, no índices del array.

---

## 7. ¿Por qué es útil `voxel_to_world()`?

### Caso de Uso Principal: **Reportar detecciones en coordenadas médicas estándar**

Cuando tu algoritmo de IA **detecta** un posible nódulo en el array, necesitas reportarlo en milímetros para que los médicos lo entiendan.

### Ejemplo Práctico:

```python
# PASO 1: Tu modelo de IA detectó algo sospechoso
deteccion_voxel = np.array([75, 280, 310])  # Índices del array

# PASO 2: Convertir a coordenadas del mundo real
deteccion_mundo = voxel_to_world(deteccion_voxel, origin, spacing)
# Resultado: [-62.5, -3.2, 67.9] mm

# PASO 3: Generar reporte médico
print(f"Posible nódulo detectado en:")
print(f"  Coordenadas: X={deteccion_mundo[2]:.1f} mm")
print(f"               Y={deteccion_mundo[1]:.1f} mm")
print(f"               Z={deteccion_mundo[0]:.1f} mm")
print(f"  (Estándar médico compatible con DICOM)")

# PASO 4: El médico puede usar estas coordenadas en CUALQUIER
# software de visualización médica para verificar
```

**Sin `voxel_to_world()`, tu reporte sería:**
- "Nódulo en voxel [75, 280, 310]" ❌ Inútil para médicos

**Con `voxel_to_world()`, tu reporte es:**
- "Nódulo en (-62.5, -3.2, 67.9) mm" ✅ Estándar médico universal

---

## 8. Flujo Completo: Del CSV a la Visualización

```
┌─────────────────────────────────────────────────────────┐
│  PASO 1: Anotaciones del radiólogo (annotations.csv)   │
│  Nódulo en: (-128.7, -175.3, -298.4) mm                │
│  (COORDENADAS MUNDO - milímetros)                       │
└─────────────────────────────────────────────────────────┘
                        ↓
              world_to_voxel()
                        ↓
┌─────────────────────────────────────────────────────────┐
│  PASO 2: Convertir a índices de array                  │
│  Nódulo en voxel: [59, 256, 300]                       │
│  (COORDENADAS VOXEL - índices)                          │
└─────────────────────────────────────────────────────────┘
                        ↓
            ct_scan[59, 256, 300]
                        ↓
┌─────────────────────────────────────────────────────────┐
│  PASO 3: Extraer región del nódulo                     │
│  patch = ct_scan[54:64, 240:272, 284:316]              │
│  (DATOS PARA ENTRENAR IA)                              │
└─────────────────────────────────────────────────────────┘
                        ↓
         Entrenar modelo de IA
                        ↓
┌─────────────────────────────────────────────────────────┐
│  PASO 4: IA detecta nuevo nódulo sospechoso            │
│  En voxel: [82, 301, 245]                              │
│  (COORDENADAS VOXEL - índices)                          │
└─────────────────────────────────────────────────────────┘
                        ↓
              voxel_to_world()
                        ↓
┌─────────────────────────────────────────────────────────┐
│  PASO 5: Reporte para el médico                        │
│  "Posible nódulo en: (21.8, 11.6, 55.0) mm"            │
│  (COORDENADAS MUNDO - milímetros)                       │
└─────────────────────────────────────────────────────────┘
```

---

## 9. Resumen: ¿Cuándo usar cada función?

### `world_to_voxel()`: **De milímetros → índices**

**¿Cuándo?** Cuando tienes coordenadas en mm y necesitas acceder al array

**Casos de uso:**
1. ✅ Leer anotaciones del CSV y visualizarlas en la imagen
2. ✅ Extraer parches (patches) alrededor de nódulos conocidos
3. ✅ Crear máscaras de segmentación para entrenamiento
4. ✅ Navegar a una posición específica reportada por un médico

**Ejemplo:**
```python
# Tengo: coordenadas del médico en mm
# Necesito: ver esa región en ct_scan
voxel_idx = world_to_voxel(coordenadas_mm, origin, spacing)
region = ct_scan[voxel_idx[0], voxel_idx[1], voxel_idx[2]]
```

### `voxel_to_world()`: **De índices → milímetros**

**¿Cuándo?** Cuando tu algoritmo encontró algo en el array y necesitas reportarlo

**Casos de uso:**
1. ✅ Reportar detecciones de IA en coordenadas médicas estándar
2. ✅ Guardar resultados en formato DICOM
3. ✅ Crear informes que otros médicos puedan entender
4. ✅ Calcular distancias reales entre estructuras

**Ejemplo:**
```python
# Tengo: índice donde mi IA detectó algo
# Necesito: reportarlo en mm para el médico
coordenadas_mm = voxel_to_world(indice_deteccion, origin, spacing)
print(f"Nódulo en {coordenadas_mm} mm")
```

---

## 10. Visualización Final: El Sistema Completo

```
MUNDO REAL (Cuerpo del paciente)          ARRAY (ct_scan)
Coordenadas en mm                         Índices de voxel

        Z                                         slice
        ↑                                         ↑
        |                                         |
        |    ● Nódulo                            |    ● Nódulo
        |   (-128, -175, -298) mm                |   [59, 256, 300]
        |                                         |
     Origin                                    [0,0,0]
  (-200,-200,-150)
        |________________→ X                     |________________→ col
       /                                        /
      /                                        /
     ↓ Y                                      ↓ row

     CONTINUO                                 DISCRETO
   (decimales)                              (enteros)

        ↕                                        ↕

  world_to_voxel()  ─────────────→

  voxel_to_world()  ←─────────────
```

---

## Conclusión

**`world_to_voxel()`** es esencial porque:
- Las anotaciones médicas vienen en **mm**
- Pero el array `ct_scan` usa **índices**
- Necesitas la conversión para localizar y extraer datos

**`voxel_to_world()`** es esencial porque:
- Tu IA trabaja con **índices** del array
- Pero los médicos necesitan coordenadas en **mm**
- Necesitas la conversión para reportar resultados

**Ambas son DOS CARAS de la misma moneda:** traducir entre el mundo médico (mm) y el mundo computacional (índices).