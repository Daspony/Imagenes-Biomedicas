# ¿Cómo se define el sistema de coordenadas en imágenes médicas?

## Tu pregunta clave

> "¿Cómo sabe el radiólogo la posición 3D en el mundo real del nódulo?"
> "¿Cómo se define la posición (0,0,0) en el mundo real?"

Estas son preguntas fundamentales que todo el mundo médico necesita responder para que diferentes hospitales, escáneres y médicos puedan compartir información.

---

## 1. El Problema: Necesitamos un Estándar Universal

### 1.1 Imagina este escenario problemático

```
Hospital A:                     Hospital B:
"Nódulo en (50, 30, 20) mm"    "Nódulo en (50, 30, 20) mm"
     ↓                               ↓
¿Es el MISMO nódulo?           ¿O son diferentes?

Sin un estándar, ¡NO SABRÍAMOS!
```

**El problema:** Cada fabricante de escáner CT podría usar su propio sistema de coordenadas:
- GE podría poner el origen en un lugar
- Siemens en otro lugar
- Philips en otro

Sería un caos total. Por eso existe **DICOM**.

---

## 2. El Estándar DICOM - La Solución Universal

**DICOM** (Digital Imaging and Communications in Medicine) es el estándar internacional que define EXACTAMENTE cómo se establecen las coordenadas en imágenes médicas.

### 2.1 El Sistema de Coordenadas del Paciente (Patient Coordinate System)

DICOM define el sistema de coordenadas basado en la **anatomía del paciente**, NO en el escáner.

```
Sistema de Coordenadas del Paciente (DICOM):

        +Z (Superior)
         ↑  Hacia la CABEZA
         |
         |
         |
         0,0,0 ← Centro de referencia
         |________________→ +X (Derecha del paciente)
        /
       /
      ↓ +Y (Posterior)
     Hacia la ESPALDA


Definición DICOM:
- Eje X: Izquierda (-) → Derecha (+) del PACIENTE
- Eje Y: Frente/Anterior (-) → Espalda/Posterior (+) del PACIENTE
- Eje Z: Pies/Inferior (-) → Cabeza/Superior (+) del PACIENTE
```

**Clave:** El sistema está SIEMPRE alineado con el cuerpo del paciente, sin importar:
- Cómo esté acostado
- Qué escáner se use
- En qué hospital esté

---

## 3. ¿Cómo se define el Origen (0,0,0)?

### 3.1 En el Mundo Real: El Isocentro del Escáner

El punto (0,0,0) se define en el **isocentro del escáner CT**.

```
Vista lateral del escáner CT:

                Gantry (anillo)
                    ┌───┐
                    │   │
                    │ ● │ ← Isocentro (0,0,0)
                    │   │    Centro exacto del anillo
                    └───┘

                  [Camilla]
```

**El isocentro es:**
- El centro geométrico del anillo del escáner (gantry)
- Un punto fijo en el espacio del escáner
- El punto (0,0,0) del sistema de coordenadas mundial

### 3.2 ¿Cómo se calibra físicamente?

Los escáneres CT tienen:

1. **Láseres de alineación** que marcan físicamente el isocentro
2. **Marcas en la camilla** que indican dónde estará el centro
3. **Calibración automática** que asegura precisión milimétrica

```
Vista desde arriba - Preparación del paciente:

    Láser vertical
         ↓
    ┌────┼────┐
    │    │    │  Gantry
    │    ●    │  ← Isocentro marcado por láseres
    │    │    │
    └────┼────┘
         ↓
      Paciente acostado aquí
      (centrado según láseres)
```

**Proceso:**
1. El paciente se acuesta en la camilla
2. Los técnicos usan los láseres para centrarlo
3. El escáner registra la posición exacta del paciente relativa al isocentro
4. Todas las medidas se hacen desde ese punto de referencia

---

## 4. ¿Cómo sabe el radiólogo la posición del nódulo?

### 4.1 El Software Médico Hace el Trabajo

Cuando un radiólogo mira una imagen CT en su estación de trabajo:

```
Pantalla del radiólogo:

┌─────────────────────────────────────────────┐
│  Visor DICOM (Ej: OsiriX, Horos, 3D Slicer)│
├─────────────────────────────────────────────┤
│                                             │
│   [Imagen del slice con pulmones]          │
│                                             │
│          ● ← Click aquí                     │
│                                             │
│   Coordenadas: X: -45.3 mm                 │
│                Y:  12.8 mm                  │
│                Z: -67.4 mm                  │
│   Slice: 87/133                            │
└─────────────────────────────────────────────┘
```

**¿Qué pasa cuando hace click en el nódulo?**

1. El software sabe:
   - En qué **pixel** hiciste click (ej: pixel [256, 300])
   - En qué **slice** estás (ej: slice 87)
   - El **Origin** de la imagen (almacenado en metadatos DICOM)
   - El **Spacing** de la imagen (almacenado en metadatos DICOM)

2. El software calcula automáticamente:
   ```python
   # Esto lo hace el software DICOM viewer automáticamente
   voxel_coords = (87, 256, 300)  # donde hiciste click

   # Usa la fórmula voxel_to_world
   world_coords = spacing * voxel_coords + origin

   # Muestra en pantalla: (-45.3, 12.8, -67.4) mm
   ```

3. El radiólogo copia esas coordenadas al archivo CSV

**¡El radiólogo NO calcula nada manualmente!** El software hace toda la matemática.

---

## 5. ¿Qué es el "Origin" exactamente?

El **Origin** es el desplazamiento entre:
- El **isocentro del escáner** (0,0,0 del mundo)
- La **esquina del volumen escaneado** (voxel [0,0,0] del array)

### 5.1 Visualización del Origin

```
ESPACIO DEL ESCÁNER (mundo real en mm):

        Isocentro (0,0,0)
             ↓
             ●━━━━━━━━━━━━━━━→ +X
             ┃
             ┃   ┌──────────────┐
             ┃   │              │
             ┃   │  Región      │
             ┃   │  escaneada   │
             ┃   │              │
             ┃   └──────────────┘
             ┃        ↑
             ┃        └─ Voxel [0,0,0] del array
             ┃           En posición (-200, -200, -150) mm
             ↓
            +Z

Origin = (-200, -200, -150) significa:
"El voxel [0,0,0] del array está a 200mm a la izquierda,
 200mm adelante, y 150mm abajo del isocentro"
```

### 5.2 ¿Por qué el Origin suele ser negativo?

Porque típicamente el **centro del volumen escaneado** está cerca del isocentro, entonces:
- La esquina [0,0,0] del array está **antes** del isocentro (coordenadas negativas)
- El centro del array está **cerca** del isocentro (coordenadas ~0)
- La esquina final está **después** del isocentro (coordenadas positivas)

```
Ejemplo con array de 512×512×133 voxels:

Origin = (-200, -200, -150) mm        ← Voxel [0, 0, 0]

Centro ≈ (-200 + 256×0.7,
          -200 + 256×0.7,
          -150 + 66×2.5)
       = (-20.8, -20.8, 15) mm        ← Voxel [66, 256, 256]
                                        (cerca del isocentro!)

Esquina final = (-200 + 512×0.7,
                 -200 + 512×0.7,
                 -150 + 133×2.5)
              = (158.4, 158.4, 182.5)  ← Voxel [132, 511, 511]
```

---

## 6. El Flujo Completo: Del Escáner al CSV

```
PASO 1: ESCANEO
┌────────────────────────────────────────┐
│  Escáner CT                            │
│  - Isocentro en (0,0,0)                │
│  - Paciente centrado con láseres       │
│  - Escanea región del tórax            │
└────────────────────────────────────────┘
            ↓
         Genera
            ↓
PASO 2: ARCHIVO DICOM
┌────────────────────────────────────────┐
│  Archivo .dcm (DICOM)                  │
│  Metadatos incluyen:                   │
│  - ImagePositionPatient: (-200,-200,-150)│
│    └─ Esto es el Origin                │
│  - PixelSpacing: (0.703, 0.703)        │
│  - SliceThickness: 2.5                 │
│  - Voxels: 512×512×133 números         │
└────────────────────────────────────────┘
            ↓
    Convertir a .mhd/.raw
            ↓
PASO 3: ARCHIVOS LUNA16
┌────────────────────────────────────────┐
│  archivo.mhd                           │
│  Origin = -200 -200 -150               │
│  ElementSpacing = 0.703 0.703 2.5      │
│  DimSize = 512 512 133                 │
│                                        │
│  archivo.raw                           │
│  [34 millones de voxels]               │
└────────────────────────────────────────┘
            ↓
    Radiólogo abre en software
            ↓
PASO 4: ANOTACIÓN
┌────────────────────────────────────────┐
│  Software DICOM Viewer                 │
│  - Muestra la imagen                   │
│  - Radiólogo hace click en nódulo      │
│  - Software calcula:                   │
│    voxel [87, 256, 300]                │
│    → world (-45.3, 12.8, -67.4) mm     │
└────────────────────────────────────────┘
            ↓
  Radiólogo copia coordenadas
            ↓
PASO 5: ARCHIVO CSV
┌────────────────────────────────────────┐
│  annotations.csv                       │
│  seriesuid,coordX,coordY,coordZ,diam   │
│  1.3.6..., -45.3, 12.8, -67.4, 5.6     │
└────────────────────────────────────────┘
```

---

## 7. Respondiendo tus preguntas específicas

### ¿Cómo sabe el radiólogo la posición 3D del nódulo?

**Respuesta:**
1. El radiólogo **NO calcula manualmente** las coordenadas
2. Usa software especializado (DICOM viewer) que:
   - Lee los metadatos (Origin, Spacing)
   - Convierte automáticamente clicks en coordenadas mm
   - Muestra las coordenadas en pantalla
3. El radiólogo simplemente **copia** esas coordenadas al CSV

### ¿Cómo se define el (0,0,0) en el mundo real?

**Respuesta:**
1. El (0,0,0) está en el **isocentro del escáner CT**
2. Es el centro geométrico del anillo (gantry)
3. Se calibra físicamente con:
   - Láseres de alineación
   - Calibración de fábrica del escáner
   - Mantenimiento periódico para asegurar precisión
4. Es un punto **fijo en el espacio del escáner**

---

## 8. ¿Por qué LUNA16 tiene archivos .mhd en lugar de DICOM?

LUNA16 convirtió los archivos DICOM originales a formato .mhd/.raw por varias razones:

### Ventajas de .mhd/.raw:

1. **Más simple** - Archivos de texto + binario plano
2. **Más pequeño** - No incluye todos los metadatos médicos
3. **Más rápido** - Lectura directa sin parser DICOM
4. **Más fácil** - Para investigadores sin experiencia médica

### Mapeo DICOM → .mhd:

```
DICOM                          →    .mhd
────────────────────────────────────────────────
ImagePositionPatient           →    Origin
PixelSpacing + SliceThickness  →    ElementSpacing
Rows × Columns × NumberOfSlices →   DimSize
PixelData                      →    .raw file
```

**Pero la información fundamental (Origin, Spacing) se preserva.**

---

## 9. Ejemplo Práctico Completo

Vamos a seguir un nódulo desde el escaneo hasta el CSV:

```
DÍA 1: ESCANEO
─────────────
Hospital escanea paciente con CT
- Paciente centrado en isocentro (0,0,0)
- Escanea tórax de -200mm a +200mm en cada eje
- Genera archivo DICOM


DÍA 2: ANOTACIÓN
────────────────
Radiólogo abre DICOM en OsiriX:

1. Ve slice 87
2. Identifica nódulo sospechoso
3. Hace click con el mouse en el centro del nódulo
4. El software muestra:

   ┌─────────────────────────┐
   │ Cursor en:              │
   │ X: -45.3 mm            │
   │ Y:  12.8 mm            │
   │ Z: -67.4 mm            │
   │ Slice: 87              │
   └─────────────────────────┘

5. Mide el diámetro con herramienta de medición: 5.6 mm

6. Registra en CSV:
   -45.3, 12.8, -67.4, 5.6


DÍA 3: TU CÓDIGO
────────────────
Tu programa Python:

1. Lee annotations.csv:
   coordX=-45.3, coordY=12.8, coordZ=-67.4

2. Lee archivo.mhd:
   Origin = -200, -200, -150
   Spacing = 0.703, 0.703, 2.5

3. Convierte a voxel:
   voxel = world_to_voxel(
       [-67.4, 12.8, -45.3],  # (Z,Y,X)
       [-150, -200, -200],     # origin
       [2.5, 0.703, 0.703]     # spacing
   )
   # Resultado: [87, 303, 220]

4. Extrae el nódulo:
   ct_scan[87, 303, 220]  # ¡Ahí está!
```

---

## 10. Resumen Visual Final

```
MUNDO REAL                METADATOS              ARRAY
(Espacio físico)         (Conversión)          (Memoria)

    Isocentro                Origin              Voxel [0,0,0]
      (0,0,0) ────────→  (-200,-200,-150) ────→  ct_scan[0,0,0]
        ↓                      ↓                      ↓
   Coordenadas            Desplazamiento         Índices
   absolutas              + Escala               discretos
   en mm                  (Spacing)              (enteros)


Radiólogo click:         Conversión:            Tu código:
Click en nódulo    →    Calcula mm       →     Calcula voxel
  (pixel)                (automático)           (tu script)
                              ↓
                    (-45.3, 12.8, -67.4)
                              ↓
                         CSV guardado
                              ↓
                    Tú lo lees y usas
```

---

## Conclusión

**Para el radiólogo:**
- No hace cálculos manuales
- El software DICOM hace todo automáticamente
- Solo hace click y copia las coordenadas mostradas

**Para el sistema:**
- (0,0,0) = Isocentro del escáner (calibrado físicamente)
- Origin = Desplazamiento del volumen escaneado respecto al isocentro
- Spacing = Escala de conversión mm/voxel

**Para ti (programador):**
- Recibes coordenadas en mm del CSV
- Usas Origin y Spacing para convertir a índices de voxel
- Accedes a los datos en ct_scan

Todo está diseñado para que diferentes hospitales, escáneres y software puedan **compartir e interpretar las mismas coordenadas** de forma consistente. ¡Esa es la magia del estándar DICOM!