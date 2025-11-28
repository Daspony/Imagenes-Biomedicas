# Módulo de Carga de Datos LUNA16 - Explicación Detallada

## Introducción para Usuarios No Técnicos

Este documento explica en detalle cómo funciona el módulo de carga de datos del pipeline de detección de nódulos pulmonares, pensado especialmente para personas sin experiencia previa en procesamiento de imágenes biomédicas.

---

## 1. ¿Qué es un Tomografía Computarizada (CT)?

Antes de entender el código, necesitas comprender qué son los datos que estamos manejando:

### 1.1 ¿Cómo se obtiene una imagen CT?

Una tomografía computarizada (CT scan) es como tomar múltiples "fotografías" de rayos X del cuerpo desde diferentes ángulos y luego usar una computadora para combinarlas en imágenes detalladas de cortes transversales.

**Analogía simple:**
- Imagina que tienes un pan de molde
- Cada rebanada del pan sería un "slice" (corte) de la tomografía
- Si apilas todas las rebanadas, obtienes el pan completo (el volumen 3D)

### 1.1.1 ¿Cómo se toman las "rebanadas"? ¿360° o de pies a cabeza?

Esta es una pregunta clave para entender la geometría de un CT scan. La respuesta es **AMBAS COSAS**, pero en dos pasos diferentes:

#### Paso 1: Cada SLICE se captura girando 360° alrededor del paciente

Para crear **UNA SOLA REBANADA** (un slice):

```
Vista desde arriba del paciente acostado:

                  Tubo de rayos X
                        ↓
                    [Fuente]
                        |
                        |
        ┌───────────────●───────────────┐
        │                               │ ← Gantry (anillo que gira)
        │          👤 Paciente          │
        │         (acostado)            │
        │                               │
        └───────────────●───────────────┘
                        |
                        |
                   [Detectores]
                        ↑
              Detectores de rayos X

El anillo completo GIRA 360° alrededor del paciente
```

**¿Qué pasa durante un giro completo de 360°?**

1. El tubo de rayos X dispara desde múltiples ángulos (por ejemplo, 1000 posiciones diferentes)
2. Los detectores al otro lado capturan cuántos rayos X pasaron a través del cuerpo
3. La computadora usa estas 1000+ mediciones para **reconstruir** una imagen 2D de ese corte transversal

**Analogía del pastel:**
- Es como si tomaras fotos de una rebanada de pastel desde todos los lados
- La computadora combina todas esas vistas para crear una imagen completa del interior de la rebanada
- Esto te permite ver qué hay DENTRO sin abrirla

#### Paso 2: Luego la camilla se mueve para capturar el siguiente slice

Una vez que se completa la imagen de una rebanada, la camilla se mueve un poco (por ejemplo, 2.5 mm) y el proceso se repite:

```
Vista lateral del escáner:

Camilla móvil →

Gantry (fijo)
    ║
    ║  Slice 1  ← Paciente en posición 1, gira 360°
    ║
    ║  Slice 2  ← Camilla avanza 2.5 mm, gira 360° otra vez
    ║
    ║  Slice 3  ← Camilla avanza 2.5 mm, gira 360° otra vez
    ║
    ║  Slice 4
    ║
    ║   ...
    ║
    ║  Slice 133 ← Último slice

El paciente se mueve a través del anillo (de pies a cabeza o viceversa)
```

**Resumen:**
- **360° de rotación** → Crea UNA rebanada (slice) 2D
- **Movimiento de pies a cabeza** → Crea MÚLTIPLES rebanadas apiladas (volumen 3D)

#### 1.1.2 Visualización completa del proceso

```
PROCESO COMPLETO DE ADQUISICIÓN CT:

1. Paciente se acuesta en la camilla

   [Camilla]──→ 👤 ──→ [Gantry circular]

2. Para cada posición Z (cada 2.5 mm):

   a) El anillo gira 360° alrededor del paciente

      Ángulo 0°:    Fuente → 👤 → Detectores
      Ángulo 90°:   Detectores ↑ 👤 ↓ Fuente
      Ángulo 180°:  Detectores ← 👤 ← Fuente
      Ángulo 270°:  Fuente ↑ 👤 ↓ Detectores

   b) Se capturan 1000+ mediciones desde todos los ángulos

   c) La computadora RECONSTRUYE una imagen 2D del corte transversal

      Resultado: SLICE #1 (512×512 pixeles)

3. La camilla avanza 2.5 mm

4. Se repite el proceso → SLICE #2

5. Se repite → SLICE #3

... (133 veces en total)

6. Resultado final: VOLUMEN 3D = 133 slices apilados
```

#### 1.1.3 ¿En qué dirección se apilan los slices?

Para un CT de tórax (pulmones) como LUNA16:

```
Vista del paciente:

        👤 Cabeza
        │
        ├─── Slice 132 (superior) ← Cerca del cuello
        ├─── Slice 100
        ├─── Slice 80
        ├─── Slice 60  ← Nivel del corazón
        ├─── Slice 40
        ├─── Slice 20
        ├─── Slice 0 (inferior) ← Cerca del abdomen
        │
        👤 Pies

Los slices se apilan de ABAJO (pies) hacia ARRIBA (cabeza)
O de ARRIBA (cabeza) hacia ABAJO (pies)
Depende de cómo el técnico configure el escáner
```

**Eje Z en coordenadas:**
- El eje Z generalmente va de pies → cabeza (o viceversa)
- Cada slice está separado 2.5 mm en este eje
- Es el eje de menor resolución (spacing más grande)

#### 1.1.4 ¿Por qué cada slice es un "corte transversal"?

Cada slice es perpendicular al eje del cuerpo:

```
Si cortas el cuerpo horizontalmente (como rebanar un salami):

Vista desde arriba (mirando hacia abajo):

     ╔═════════════════╗
     ║  Pulmón Izq  ║ Pulmón Der ║  ← Este es un slice
     ║      ♥ Corazón  ║
     ╚═════════════════╝
           Espalda

Puedes ver:
- Los dos pulmones (áreas oscuras = aire)
- El corazón (en el medio)
- Las costillas (huesos blancos en el borde)
- La columna vertebral (atrás)

TODO EN UN SOLO PLANO HORIZONTAL
```

#### 1.1.5 Comparación con otros tipos de cortes

Aunque los CT normalmente usan cortes transversales (axiales), existen otras orientaciones:

**Corte Axial (Transversal) - El estándar en CT:**
```
     Cabeza
        ↑
        │
    ────┼──── ← Plano de corte (horizontal)
        │
        ↓
      Pies
```
- Como rebanar un pan horizontalmente
- Es lo que hace el escáner CT
- **LUNA16 usa este tipo**

**Corte Sagital (de lado):**
```
  Frente
     ↑
     │
     ┼──→ Lado derecho
     │
     ↓
  Espalda
```
- Como cortar el cuerpo por la mitad de izquierda a derecha
- Se puede generar después a partir de los cortes axiales

**Corte Coronal (frontal):**
```
  Cabeza
     ↑
     │
     ┼──→ Lado derecho
     │
     ↓
   Pies
```
- Como cortar el cuerpo de frente a espalda
- También se genera después a partir de los cortes axiales

**Nota importante:** El escáner CT físicamente solo captura cortes **axiales (transversales)**. Los cortes sagitales y coronales se crean después mediante software, reorganizando los datos 3D.

### 1.2 ¿Qué información contiene?

Cada punto en la imagen CT (llamado **voxel**, equivalente 3D de un pixel) contiene un número que representa la **densidad del tejido** en esa ubicación. Este número se mide en **Unidades Hounsfield (HU)**:

- **Aire**: -1000 HU (muy oscuro en la imagen)
- **Pulmón**: -500 a -900 HU (oscuro/gris oscuro)
- **Tejido blando**: -100 a 100 HU (gris)
- **Hueso**: +400 a +1000 HU (blanco brillante)
- **Metal**: +1000+ HU (blanco muy brillante)

---

## 2. Formatos de Archivo: .mhd y .raw

### 2.1 ¿Por qué dos archivos?

El dataset LUNA16 almacena cada escaneo CT en **DOS archivos** que trabajan juntos:

#### Archivo .mhd (MetaImage Header)
Es un archivo de texto pequeño que contiene la "receta" o "manual de instrucciones":

```
ObjectType = Image
NDims = 3
DimSize = 512 512 133
ElementSpacing = 0.703125 0.703125 2.5
ElementType = MET_SHORT
ElementDataFile = archivo.raw
```

**Traducción de cada línea:**

1. **`ObjectType = Image`**: "Esto es una imagen médica"

2. **`NDims = 3`**: "La imagen tiene 3 dimensiones" (ancho × alto × profundidad)

3. **`DimSize = 512 512 133`**:
   - 512 pixeles de ancho (eje X)
   - 512 pixeles de alto (eje Y)
   - 133 slices de profundidad (eje Z)
   - **Total**: Es como tener 133 imágenes de 512×512 pixeles apiladas

4. **`ElementSpacing = 0.703125 0.703125 2.5`**:
   - Cada pixel mide 0.703125 mm en el eje X
   - Cada pixel mide 0.703125 mm en el eje Y
   - Cada slice está separado 2.5 mm en el eje Z
   - **Importante**: ¡Esto convierte pixeles a milímetros en el mundo real!

5. **`ElementType = MET_SHORT`**: "Los números se guardan como enteros cortos (16 bits)"

6. **`ElementDataFile = archivo.raw`**: "Los datos reales están en archivo.raw"

#### Archivo .raw (Datos Binarios)

Es un archivo binario que contiene **TODOS los números** de densidad (valores HU) de cada voxel:

- **Tamaño**: Para una imagen de 512×512×133, tendríamos:
  - 512 × 512 × 133 = 34,865,152 voxels
  - Si cada número ocupa 2 bytes (MET_SHORT): ~66 MB

- **Formato**: Los números están escritos uno tras otro, como una larga lista:
  ```
  -1024, -1020, -1015, -980, ... [34 millones de números más]
  ```

**¿Por qué separar la información?**
- El .mhd es legible por humanos (podemos abrirlo con un editor de texto)
- El .raw es compacto y eficiente para almacenar millones de números
- Es como tener un libro (manual) separado de los datos (archivo de datos)

---

## 3. La Clase LUNA16DataLoader - Explicación Línea por Línea

```python
class LUNA16DataLoader:
    """
    Cargador de datos para el dataset LUNA16
    """
```

**¿Qué es una clase?**
- Una "clase" es como un molde o plantilla para crear objetos
- Este "molde" contendrá todas las herramientas para trabajar con datos LUNA16

---

### 3.1 Constructor: `__init__`

```python
def __init__(self, data_path, annotations_path=None):
    self.data_path = data_path
    self.annotations = None

    if annotations_path and os.path.exists(annotations_path):
        self.annotations = pd.read_csv(annotations_path)
        print(f"Anotaciones cargadas: {len(self.annotations)} nódulos")
```

**¿Qué hace?**
Cuando creas un nuevo cargador, esto es lo primero que se ejecuta:

1. **`self.data_path = data_path`**: Guarda la ruta donde están los archivos .mhd/.raw
   - Ejemplo: `"./LUNA16/subset0"`

2. **`self.annotations = None`**: Inicialmente, no hay anotaciones cargadas

3. **Si existe `annotations.csv`**:
   - Lo carga en una tabla (DataFrame de pandas)
   - Esta tabla contiene información de dónde están los nódulos:
     ```
     seriesuid                    | coordX | coordY | coordZ | diameter_mm
     1.3.6.1.4...105756658...     | -128.6 | -175.3 | -298.4 | 5.651471
     ```
   - Cada fila = un nódulo confirmado por radiólogos

---

### 3.2 Cargar Imagen: `load_itk_image`

```python
def load_itk_image(self, filename):
    """
    Carga imagen en formato MetaImage (.mhd)
    """
    itkimage = sitk.ReadImage(filename)
    ct_scan = sitk.GetArrayFromImage(itkimage)
    origin = np.array(list(reversed(itkimage.GetOrigin())))
    spacing = np.array(list(reversed(itkimage.GetSpacing())))

    return ct_scan, origin, spacing
```

#### 3.2.1 `sitk.ReadImage(filename)` - El Lector Mágico

**SimpleITK (sitk)** es una biblioteca especializada en leer imágenes médicas.

**IMPORTANTE:** El parámetro `filename` apunta al archivo **.mhd** (metadatos), NO al archivo .raw:

```python
# Correcto ✓
sitk.ReadImage("archivo.mhd")

# Incorrecto ✗ - No se lee directamente el .raw
sitk.ReadImage("archivo.raw")
```

**¿Por qué solo pasamos el .mhd?**

Porque el archivo .mhd contiene una línea que dice:
```
ElementDataFile = archivo.raw
```

SimpleITK es lo suficientemente inteligente para:
1. Leer el .mhd que le pasaste
2. Ver que dice "ElementDataFile = archivo.raw"
3. Automáticamente buscar y abrir archivo.raw en la misma carpeta
4. Cargar ambos archivos juntos

**Analogía:**
- Es como darle a alguien solo el índice de un libro
- El índice dice "Los datos están en el Capítulo 5"
- La persona automáticamente va y lee el Capítulo 5
- Tú no necesitas decirle explícitamente "también lee el Capítulo 5"

**¿Qué hace `sitk.ReadImage`?**

1. **Lee el archivo .mhd** que especificaste en `filename`
2. **Extrae el nombre del .raw** de la línea `ElementDataFile`
3. **Busca y lee el archivo .raw** automáticamente
4. **Los combina** en un objeto especial que contiene:
   - Los voxels (densidades del .raw)
   - Los metadatos (del .mhd: dimensiones, espaciado, origen)

**Proceso interno (simplificado):**

```
1. Abrir archivo.mhd
2. Leer: DimSize = 512 512 133
3. Leer: ElementSpacing = 0.703 0.703 2.5
4. Leer: ElementDataFile = archivo.raw
5. Abrir archivo.raw
6. Leer 34,865,152 números
7. Organizar en estructura 3D: [133 slices][512 filas][512 columnas]
8. Guardar metadatos (spacing, origin, etc.)
9. Retornar objeto ITKImage
```

**Analogía:**
- Es como tener un manual de LEGO (archivo .mhd) que te dice cómo armar las piezas
- Y una bolsa con todas las piezas sueltas (archivo .raw)
- `ReadImage` lee el manual, toma las piezas, y construye el modelo completo

---

#### 3.2.2 `sitk.GetArrayFromImage(itkimage)` - Convertir a Números

**¿Qué hace?**
Convierte el objeto ITKImage en un **array de NumPy** (una tabla multidimensional de números).

**¿Por qué convertir?**
- El objeto ITKImage es complejo y especializado
- Un array de NumPy es más simple y compatible con librerías científicas de Python
- Es como convertir un archivo PDF a un documento de Word editable

**IMPORTANTE: ¿Qué información usa y qué NO usa?**

`GetArrayFromImage()` **SOLO** extrae los voxels (los números de densidad). **NO** lee ni usa:
- ❌ `ElementSpacing` - Se descarta aquí
- ❌ `Origin` - Se descarta aquí
- ❌ `TransformMatrix` - Se descarta aquí
- ✅ `DimSize` - Usa esto para saber las dimensiones del array
- ✅ Los datos del .raw - Usa estos números

**¿Qué pasa con ElementSpacing y Origin?**

Aunque `GetArrayFromImage()` no los usa directamente, **NO se pierden**. Siguen guardados en el objeto `itkimage` y los obtenemos con:
```python
spacing = itkimage.GetSpacing()  # Lee ElementSpacing del .mhd
origin = itkimage.GetOrigin()    # Lee Origin del .mhd
```

**¿Cómo encuentra el array?**

El objeto ITKImage ya tiene los datos en memoria después de `ReadImage()`. `GetArrayFromImage` simplemente:

1. **Accede a los voxels** que están en memoria (los 34 millones de números del .raw)
2. **Lee DimSize** para saber que debe crear un array de (512, 512, 133)
3. **Los reorganiza** en formato NumPy
4. **IMPORTANTE**: Cambia el orden de los ejes de (X, Y, Z) → (Z, Y, X)
5. **Descarta** spacing, origin y otros metadatos (pero quedan en `itkimage`)

**¿Por qué `Shape: [slices, height, width]`?**

SimpleITK usa convención médica: **(X, Y, Z)** donde Z = slices
NumPy/Python prefiere: **(Z, Y, X)** para facilitar iterar por slices

**Ejemplo visual:**

```
Archivo .raw (una dimensión):
[-1024, -1020, -1015, ..., +50, +60, +70]

Después de ReadImage (orden médico X,Y,Z):
Dimensiones: (512 ancho, 512 alto, 133 profundidad)

Después de GetArrayFromImage (orden NumPy Z,Y,X):
Shape: (133, 512, 512)
        ↑    ↑    ↑
     slices alto ancho
```

**Razón práctica:**
Con `shape = (133, 512, 512)` puedes hacer:
```python
slice_0 = ct_scan[0]      # Primer slice: imagen 512×512
slice_50 = ct_scan[50]    # Slice 50: otra imagen 512×512
```

Es más intuitivo iterar por slices de esta manera.

---

#### 3.2.3 `origin` - El Punto de Referencia

```python
origin = np.array(list(reversed(itkimage.GetOrigin())))
```

**¿Qué es el origen?**

El **origen** es el punto (0, 0, 0) del sistema de coordenadas del paciente en milímetros.

**Ejemplo:**
```
Origin = (-200.0, -200.0, -150.0)
```

Esto significa que:
- El voxel [0,0,0] en la imagen corresponde al punto (-200mm, -200mm, -150mm) en el espacio del paciente
- Es como el punto de partida en un mapa

**¿Por qué se invierte con `reversed()`?**
- ITK devuelve el origen en orden (X, Y, Z)
- Lo invertimos a (Z, Y, X) para que coincida con el array NumPy

**Utilidad:**
Permite convertir posiciones de pixeles a posiciones reales en milímetros.

---

#### 3.2.4 `spacing` - La Escala

```python
spacing = np.array(list(reversed(itkimage.GetSpacing())))
```

**¿Qué es el espaciado?**

El **spacing** indica cuántos milímetros mide cada voxel en cada dimensión.

**Ejemplo:**
```
Spacing = (2.5, 0.703125, 0.703125)  # después de reversed
          ↑    ↑         ↑
         mm   mm        mm
       entre  alto     ancho
      slices  pixel    pixel
```

**Interpretación:**
- Cada slice está separado 2.5 mm del siguiente
- Cada pixel dentro de un slice mide 0.703 mm × 0.703 mm

**Analogía:**
- Es como la escala en un mapa: "1 cm = 10 km"
- Aquí: "1 pixel = 0.703 mm"

**¿Por qué es importante?**

Si un nódulo mide 10 pixeles de diámetro:
- Diámetro real = 10 × 0.703 = 7.03 mm
- ¡Los doctores necesitan medidas en milímetros, no en pixeles!

---

### 3.3 Conversión de Coordenadas

#### 3.3.1 Coordenadas Mundo vs Coordenadas Voxel

Hay DOS sistemas de coordenadas:

**Coordenadas Mundo (World Coordinates):**
- Unidades: **milímetros**
- Sistema de referencia: El cuerpo del paciente
- Ejemplo: "El nódulo está en (−128.6, −175.3, −298.4) mm"
- Usado en: Anotaciones médicas, informes

**Coordenadas Voxel (Voxel Coordinates):**
- Unidades: **índices de array** (enteros)
- Sistema de referencia: La matriz de imagen
- Ejemplo: "El nódulo está en el voxel [120, 256, 300]"
- Usado en: Procesamiento de imágenes, extracción de datos

---

#### 3.3.2 `world_to_voxel` - De Milímetros a Pixeles

```python
def world_to_voxel(self, world_coords, origin, spacing):
    """
    Convierte coordenadas mundo (mm) a coordenadas voxel (índices)
    """
    voxel_coords = np.rint((world_coords - origin) / spacing).astype(int)
    return voxel_coords
```

**¿Qué hace?**

Convierte una posición en milímetros a una posición en pixeles.

**Fórmula:**
```
voxel_coords = round((world_coords - origin) / spacing)
```

**Ejemplo paso a paso:**

Datos:
- Posición del nódulo: `world_coords = (-128.6, -175.3, -298.4)` mm
- Origin: `(-200.0, -200.0, -150.0)` mm
- Spacing: `(2.5, 0.703125, 0.703125)` mm/voxel

Cálculo:

```python
# Paso 1: Restar el origen (ajustar al punto de referencia)
relative_coords = world_coords - origin
                = (-128.6, -175.3, -298.4) - (-200.0, -200.0, -150.0)
                = (71.4, 24.7, -148.4) mm

# Paso 2: Dividir por spacing (convertir mm a voxels)
voxel_coords = relative_coords / spacing
             = (71.4, 24.7, -148.4) / (2.5, 0.703125, 0.703125)
             = (28.56, 35.13, -211.06)

# Paso 3: Redondear al entero más cercano
voxel_coords = round(28.56, 35.13, -211.06)
             = (29, 35, -211)
```

**Resultado:** El nódulo está en el voxel [29, 35, -211] del array.

**Analogía:**
- Es como convertir coordenadas GPS (latitud/longitud) a una celda específica en una cuadrícula de mapa

---

#### 3.3.3 `voxel_to_world` - De Pixeles a Milímetros

```python
def voxel_to_world(self, voxel_coords, origin, spacing):
    """
    Convierte coordenadas voxel a coordenadas mundo (mm)
    """
    world_coords = spacing * voxel_coords + origin
    return world_coords
```

**¿Qué hace?**

Es la operación inversa: convierte índices de pixel a posición en milímetros.

**Fórmula:**
```
world_coords = (voxel_coords × spacing) + origin
```

**Ejemplo:**

```python
# Datos
voxel_coords = (29, 35, -211)
spacing = (2.5, 0.703125, 0.703125)
origin = (-200.0, -200.0, -150.0)

# Paso 1: Multiplicar por spacing
relative_coords = voxel_coords × spacing
                = (29, 35, -211) × (2.5, 0.703125, 0.703125)
                = (72.5, 24.609, -148.359) mm

# Paso 2: Sumar el origen
world_coords = relative_coords + origin
             = (72.5, 24.609, -148.359) + (-200.0, -200.0, -150.0)
             = (-127.5, -175.391, -298.359) mm
```

**Uso:**
Si detectamos un nódulo en el voxel [100, 250, 300], podemos reportar su posición real en milímetros para el médico.

---

### 3.4 Normalización: `normalize_hu`

```python
def normalize_hu(self, image, min_hu=-1000, max_hu=400):
    """
    Normaliza valores Hounsfield Units a rango [0, 1]

    Ventana pulmonar típica: [-1000, 400] HU
    """
    image = np.clip(image, min_hu, max_hu)
    image = (image - min_hu) / (max_hu - min_hu)
    return image.astype(np.float32)
```

**¿Por qué normalizar?**

Los valores HU van desde -1024 hasta +3000 o más. Los algoritmos de machine learning funcionan mejor con números pequeños en el rango [0, 1].

**¿Qué hace el código?**

**Paso 1: `np.clip(image, min_hu, max_hu)`**

Recorta valores fuera del rango de interés:

```python
Valor original HU  →  Después de clip(-1000, 400)
-1500              →  -1000  (muy bajo, se ajusta)
-800               →  -800   (dentro del rango, sin cambio)
300                →  300    (dentro del rango, sin cambio)
2000               →  400    (muy alto, se ajusta)
```

**Paso 2: Normalizar a [0, 1]**

```python
normalized = (valor - min_hu) / (max_hu - min_hu)
           = (valor - (-1000)) / (400 - (-1000))
           = (valor + 1000) / 1400
```

**Ejemplos:**

```python
HU = -1000  →  (-1000 + 1000) / 1400 = 0.0     (aire, mínimo)
HU = -300   →  (-300 + 1000) / 1400  = 0.5     (pulmón, medio)
HU = +400   →  (400 + 1000) / 1400   = 1.0     (tejido denso, máximo)
```

**¿Por qué [-1000, 400]?**

Esta es la **ventana pulmonar** estándar que permite ver bien:
- Aire en los pulmones: -1000 HU
- Tejido pulmonar: -700 a -500 HU
- Nódulos: -100 a +400 HU

Todo lo que está fuera de este rango no nos interesa para detectar nódulos pulmonares.

---

### 3.5 Obtener Anotaciones: `get_annotations_for_scan`

```python
def get_annotations_for_scan(self, seriesuid):
    """
    Obtiene anotaciones de nódulos para un escaneo específico
    """
    if self.annotations is None:
        return None

    scan_annotations = self.annotations[self.annotations['seriesuid'] == seriesuid]
    return scan_annotations
```

**¿Qué hace?**

Filtra las anotaciones para obtener solo los nódulos de un escaneo específico.

**Ejemplo:**

Tabla `annotations.csv` completa:
```
seriesuid                              | coordX  | coordY  | coordZ  | diameter_mm
1.3.6.1.4.1...105756658...            | -128.6  | -175.3  | -298.4  | 5.65
1.3.6.1.4.1...105756658...            | 103.8   | -211.9  | -227.1  | 4.22
1.3.6.1.4.1...108197895...            | 69.6    | -140.9  | -175.4  | 8.14
```

Si llamas:
```python
annotations = loader.get_annotations_for_scan("1.3.6.1.4.1...105756658...")
```

Retorna solo las filas que coinciden:
```
seriesuid                              | coordX  | coordY  | coordZ  | diameter_mm
1.3.6.1.4.1...105756658...            | -128.6  | -175.3  | -298.4  | 5.65
1.3.6.1.4.1...105756658...            | 103.8   | -211.9  | -227.1  | 4.22
```

Esto te dice: "Este escaneo tiene 2 nódulos en estas posiciones"

---

## 4. Ejemplo Completo de Uso

```python
# Crear el cargador
loader = LUNA16DataLoader(
    data_path="./LUNA16/subset0",
    annotations_path="./LUNA16/annotations.csv"
)

# Cargar un escaneo
filename = "./LUNA16/subset0/1.3.6.1.4.1.14519.5.2.1.6279.6001.105756658031515062000744821260.mhd"
ct_volume, origin, spacing = loader.load_itk_image(filename)

# Ver información
print(f"Forma del volumen: {ct_volume.shape}")        # (133, 512, 512)
print(f"Origen: {origin}")                            # (-200.0, -200.0, -150.0)
print(f"Espaciado: {spacing}")                        # (2.5, 0.703, 0.703)

# Normalizar valores
ct_normalized = loader.normalize_hu(ct_volume)
print(f"Rango de valores: [{ct_normalized.min()}, {ct_normalized.max()}]")  # [0.0, 1.0]

# Obtener anotaciones de este escaneo
seriesuid = "1.3.6.1.4.1.14519.5.2.1.6279.6001.105756658031515062000744821260"
nodule_annotations = loader.get_annotations_for_scan(seriesuid)
print(f"Número de nódulos anotados: {len(nodule_annotations)}")

# Convertir posición de un nódulo a coordenadas voxel
for idx, row in nodule_annotations.iterrows():
    world_coords = np.array([row['coordZ'], row['coordY'], row['coordX']])
    voxel_coords = loader.world_to_voxel(world_coords, origin, spacing)
    print(f"Nódulo en {world_coords} mm → voxel {voxel_coords}")
```

---

## 5. Resumen Visual: Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                   ARCHIVOS EN DISCO                          │
├─────────────────────────────────────────────────────────────┤
│  archivo.mhd (texto)          archivo.raw (binario)         │
│  ├── DimSize = 512 512 133   ├── -1024, -1020, -1015, ...   │
│  ├── Spacing = 0.7 0.7 2.5   │   [34 millones de números]   │
│  └── Origin = -200 -200 -150 │                              │
└─────────────────────────────────────────────────────────────┘
                        ↓
               sitk.ReadImage(filename)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              OBJETO ITKImage (en memoria)                    │
├─────────────────────────────────────────────────────────────┤
│  • Voxels organizados en 3D                                 │
│  • Metadatos (spacing, origin, etc.)                        │
└─────────────────────────────────────────────────────────────┘
                        ↓
          sitk.GetArrayFromImage(itkimage)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│            NUMPY ARRAY (procesable)                          │
├─────────────────────────────────────────────────────────────┤
│  Shape: (133, 512, 512)                                     │
│  [[[−1024, −1020, ...], [...]], ...]                        │
│                                                              │
│  ct_volume[0]     → Primer slice (512×512)                  │
│  ct_volume[50]    → Slice 50 (512×512)                      │
│  ct_volume[132]   → Último slice (512×512)                  │
└─────────────────────────────────────────────────────────────┘
                        ↓
             normalize_hu(ct_volume)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│           ARRAY NORMALIZADO (listo para ML)                  │
├─────────────────────────────────────────────────────────────┤
│  Shape: (133, 512, 512)                                     │
│  Valores: [0.0, 1.0]                                        │
│  • 0.0 = aire (-1000 HU)                                    │
│  • 0.5 = pulmón (~-300 HU)                                  │
│  • 1.0 = tejido denso (+400 HU)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Entendiendo las Coordenadas de los Nódulos

### 6.1 ¿En qué unidades están las coordenadas?

**Respuesta corta:** Las coordenadas de los nódulos en el archivo `annotations.csv` están en **MILÍMETROS**, NO en pixeles.

**Explicación detallada:**

Cuando abres el archivo `annotations.csv`, verás algo como esto:

```csv
seriesuid,coordX,coordY,coordZ,diameter_mm
1.3.6.1.4.1.14519.5.2.1.6279.6001.105756658...,-128.699421965317,-175.319272783189,-298.387506856739,5.651470635
```

**Todas estas coordenadas son MILÍMETROS:**
- `coordX = -128.699` mm
- `coordY = -175.319` mm
- `coordZ = -298.387` mm
- `diameter_mm = 5.651` mm

### 6.2 ¿Por qué en milímetros y no en pixeles?

**Razón médica importante:**

Los radiólogos (médicos que leen las tomografías) siempre hablan en **medidas reales del cuerpo humano** (milímetros o centímetros), nunca en pixeles.

**Ejemplo del mundo real:**

Un radiólogo escribe en su informe:
> "Nódulo de 5.6 mm de diámetro localizado en el lóbulo superior derecho, coordenadas: (-128.7, -175.3, -298.4) mm"

El radiólogo **NO** escribiría:
> "Nódulo de 8 pixeles localizado en voxel (120, 256, 300)" ❌

**¿Por qué?**
- Las dimensiones en milímetros son **estándares médicos** universales
- Los pixeles cambian según la resolución del escáner
- Un nódulo de 5 mm es peligroso, ¡sin importar cuántos pixeles ocupe!

### 6.3 ¿Las coordenadas son 2D o 3D?

**Respuesta:** Las coordenadas (X, Y, Z) son **TRIDIMENSIONALES (3D)** y representan una posición única en todo el volumen del pecho del paciente.

**Visualización:**

```
        Z (profundidad/slices)
        ↑
        |     Nódulo en (-128.7, -175.3, -298.4) mm
        |        ●
        |
        |________________→ X (ancho)
       /
      /
     ↓ Y (alto)
```

**Desglose de cada coordenada:**

- **X (ancho):** Posición de izquierda a derecha del paciente (-128.7 mm)
- **Y (alto):** Posición de arriba a abajo (-175.3 mm)
- **Z (profundidad):** Posición de adelante hacia atrás (-298.4 mm)

**Las 3 coordenadas juntas definen UN ÚNICO PUNTO en el espacio 3D del tórax.**

### 6.4 ¿Cómo se relaciona con las imágenes 2D?

Aquí está la clave para entender:

**El volumen CT completo:**
- Es **3D**: tiene 133 slices apilados
- Cada slice es una imagen **2D** de 512×512 pixeles

**Cuando tienes coordenadas 3D de un nódulo:**

```python
# Coordenadas del nódulo en mm
world_coords = (-128.7, -175.3, -298.4)  # (X, Y, Z) en milímetros

# Convertir a coordenadas voxel (pixeles 3D)
voxel_coords = world_to_voxel(world_coords, origin, spacing)
# Resultado ejemplo: (120, 256, 300) → (slice_index, fila, columna)
```

**Interpretación:**
- **Slice 120**: El nódulo está en el slice número 120 de los 133 totales
- **Fila 256**: Dentro de ese slice 2D, está en la fila 256 (eje Y)
- **Columna 300**: Y en la columna 300 (eje X)

**Analogía del edificio:**

Imagina un edificio de 133 pisos (= 133 slices):

```
Coordenadas 3D del nódulo: (120, 256, 300)
                            ↓    ↓    ↓
                         Piso  Fila  Columna

- Ir al piso 120 del edificio       → Slice 120
- Caminar hasta la fila 256         → Coordenada Y
- Buscar la columna 300             → Coordenada X
- ¡Ahí está el nódulo! ●
```

### 6.5 Ejemplo Completo Paso a Paso

Vamos a localizar un nódulo desde el archivo `annotations.csv` hasta verlo en la imagen:

**Paso 1: Leer las coordenadas del CSV**

```csv
coordX,coordY,coordZ,diameter_mm
-128.699,-175.319,-298.387,5.651
```

Estas son coordenadas en **milímetros** en el espacio 3D del paciente.

**Paso 2: Cargar la imagen CT**

```python
ct_volume, origin, spacing = loader.load_itk_image(filename)
# ct_volume tiene forma (133, 512, 512) → 133 slices de 512×512
# origin = (-200.0, -200.0, -150.0) mm
# spacing = (2.5, 0.703125, 0.703125) mm/voxel
```

**Paso 3: Convertir coordenadas mundo (mm) → voxel (pixeles)**

```python
world_coords = np.array([-298.387, -175.319, -128.699])  # (Z, Y, X) en mm
voxel_coords = world_to_voxel(world_coords, origin, spacing)

# Cálculo:
# Z: (-298.387 - (-150.0)) / 2.5 = -59.35... ≈ -59 ← ¡Negativo!
# Esto indica que está ANTES del origen en Z
```

**Nota importante sobre coordenadas negativas:**

Las coordenadas en milímetros pueden ser negativas porque el **origen** es un punto de referencia arbitrario en el cuerpo. No significa que algo esté "mal".

**Paso 4: Acceder al voxel específico**

Una vez que tienes las coordenadas voxel válidas, por ejemplo `(59, 256, 300)`:

```python
# El nódulo está en el slice 59
slice_with_nodule = ct_volume[59]  # Imagen 2D de 512×512

# El centro del nódulo está en el pixel (256, 300) de ese slice
nodule_pixel_value = slice_with_nodule[256, 300]

print(f"Valor HU en el centro del nódulo: {nodule_pixel_value}")
# Ejemplo de salida: -50 HU (densidad típica de un nódulo)
```

**Paso 5: Visualizar el slice con el nódulo**

```python
import matplotlib.pyplot as plt

plt.imshow(slice_with_nodule, cmap='gray')
plt.plot(300, 256, 'ro', markersize=10)  # Marcar el nódulo en rojo
plt.title(f"Slice 59 - Nódulo en pixel (256, 300)")
plt.show()
```

### 6.6 Tabla Comparativa: Coordenadas Mundo vs Voxel

| Aspecto | Coordenadas Mundo | Coordenadas Voxel |
|---------|-------------------|-------------------|
| **Unidades** | Milímetros (mm) | Pixeles (índices enteros) |
| **Rango de valores** | Pueden ser negativos | Siempre 0 o positivos |
| **Ejemplo** | (-128.7, -175.3, -298.4) | (59, 256, 300) |
| **Dónde se usan** | Archivos CSV médicos | Acceso a arrays NumPy |
| **Sistema de referencia** | Cuerpo del paciente | Matriz de imagen |
| **Precisión** | Números decimales | Solo enteros |
| **Uso clínico** | Informes médicos ✓ | No, solo programación |
| **Depende del escáner** | NO (estándar) | SÍ (varía según resolución) |

### 6.7 ¿Qué pasa con nódulos entre slices?

**Pregunta:** Si un nódulo tiene coordenada Z = -298.387 mm y esto da voxel Z = 59.35, ¿está en el slice 59 o 60?

**Respuesta:** Los nódulos son objetos **3D** que ocupan múltiples voxels:

```
Nódulo de 5.6 mm de diámetro con spacing Z = 2.5 mm:

Ocupa ≈ 5.6 / 2.5 ≈ 2.2 slices

Si el centro está en slice 59.35:
- Slice 58: Parte del nódulo ●
- Slice 59: Centro del nódulo ⬤ ← coordenada redondeada
- Slice 60: Parte del nódulo ●
- Slice 61: Posible borde del nódulo ·
```

Por eso usamos `np.rint()` (redondear al entero más cercano) para obtener el **slice central** del nódulo.

### 6.8 Resumen Visual Completo

```
┌─────────────────────────────────────────────────────────────┐
│                  ARCHIVO annotations.csv                     │
│                                                              │
│  coordX,coordY,coordZ,diameter_mm                           │
│  -128.7, -175.3, -298.4, 5.651                              │
│    ↑       ↑       ↑       ↑                                │
│   mm      mm      mm      mm                                │
│  (ancho) (alto) (prof) (diámetro)                           │
│                                                              │
│  COORDENADAS 3D EN MILÍMETROS                               │
└─────────────────────────────────────────────────────────────┘
                        ↓
                world_to_voxel()
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              COORDENADAS VOXEL (pixeles)                     │
│                                                              │
│  (59, 256, 300)                                             │
│   ↑   ↑    ↑                                                │
│   Z   Y    X                                                │
│  slice fila columna                                         │
│                                                              │
│  ÍNDICES PARA ACCEDER AL ARRAY                              │
└─────────────────────────────────────────────────────────────┘
                        ↓
           ct_volume[59, 256, 300]
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                   VOXEL ESPECÍFICO                           │
│                                                              │
│  Valor: -50 HU                                              │
│  Interpretación: Tejido de densidad de nódulo               │
│                                                              │
│  UBICACIÓN EXACTA DEL CENTRO DEL NÓDULO                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Preguntas Frecuentes

**P: ¿Por qué necesitamos ambos archivos .mhd y .raw?**

R: Separar metadatos (dimensiones, espaciado) de los datos puros (voxels) hace el sistema más flexible y eficiente. Puedes leer la información básica sin cargar millones de números.

---

**P: ¿Qué pasa si pierdo el archivo .mhd pero tengo el .raw?**

R: No podrías interpretar correctamente el .raw porque no sabrías:
- Cuántos slices tiene
- Qué tamaño tiene cada slice
- Cuánto mide cada pixel en milímetros
- Dónde está el origen

---

**P: ¿Por qué el array es (133, 512, 512) y no (512, 512, 133)?**

R: Por convención de programación en Python:
- Queremos iterar fácilmente por slices: `for slice in ct_volume`
- El primer índice debe ser el que cambia más rápido
- Así `ct_volume[i]` te da el slice i completo

---

**P: ¿Qué pasa si el spacing no es uniforme?**

R: Es común que el espaciado entre slices (eje Z) sea mayor que dentro del slice (ejes X, Y). Por ejemplo:
- Spacing = (2.5, 0.7, 0.7) mm
- Los slices están más separados (2.5 mm) que los pixeles dentro de ellos (0.7 mm)

Esto afecta los cálculos de distancia y volumen, por eso siempre usamos el spacing en las conversiones.

---

## 7. Conclusión

El módulo `LUNA16DataLoader` es esencialmente un **traductor** que:

1. **Lee** archivos médicos especializados (.mhd/.raw)
2. **Convierte** los datos a formato Python estándar (NumPy arrays)
3. **Traduce** entre dos sistemas de coordenadas (mm ↔ pixeles)
4. **Normaliza** los valores para algoritmos de machine learning
5. **Conecta** las imágenes con sus anotaciones médicas

Todo esto permite que el resto del pipeline trabaje con datos consistentes y procesables.