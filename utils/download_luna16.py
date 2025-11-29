"""
Módulo para descargar automáticamente el dataset LUNA16 desde Zenodo

LUNA16 (LUng Nodule Analysis 2016) es un dataset público de imágenes CT pulmonares.
Dataset completo: ~130GB dividido en 10 subsets

Fuente: https://zenodo.org/record/3723295
"""

import os
import zipfile
import requests
from pathlib import Path
from tqdm import tqdm


# URLs de Zenodo para LUNA16
ZENODO_URLS = {
    'subset0':      'https://zenodo.org/record/3723295/files/subset0.zip',
    'subset1':      'https://zenodo.org/record/3723295/files/subset1.zip',
    'subset2':      'https://zenodo.org/record/3723295/files/subset2.zip',
    'subset3':      'https://zenodo.org/record/3723295/files/subset3.zip',
    'subset4':      'https://zenodo.org/record/3723295/files/subset4.zip',
    'subset5':      'https://zenodo.org/record/3723295/files/subset5.zip',
    'subset6':      'https://zenodo.org/record/3723295/files/subset6.zip',
    'subset7':      'https://zenodo.org/record/3723299/files/subset7.zip',
    'subset8':      'https://zenodo.org/record/3723299/files/subset8.zip',
    'subset9':      'https://zenodo.org/record/3723299/files/subset9.zip',
    'annotations':  'https://zenodo.org/record/3723295/files/annotations.csv',
    'candidates':   'https://zenodo.org/record/3723295/files/candidates.csv'
}


def download_file_with_progress(url, dest_path, chunk_size=8192, timeout=60, overwrite=False):
    """
    Descarga archivo con barra de progreso usando requests + tqdm

    Args:
        url: URL del archivo a descargar
        dest_path: Ruta de destino donde guardar el archivo
        chunk_size: Tamaño de los chunks de descarga (en bytes)
        timeout: Timeout de la conexión (en segundos)
        overwrite: Si True, sobrescribe archivos existentes

    Returns:
        bool: True si la descarga fue exitosa, False en caso de error
    """
    dest_path = Path(dest_path)

    # Si ya existe y no queremos sobrescribir, retornar True
    if dest_path.exists() and not overwrite:
        print(f"[INFO] Archivo ya existe: {dest_path.name}")
        return True

    try:
        # Hacer request con stream
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        # Obtener tamaño total del archivo
        total_size = int(response.headers.get('content-length', 0))

        # Crear barra de progreso
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=dest_path.name) as pbar:
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # filtrar keep-alive chunks
                        f.write(chunk)
                        pbar.update(len(chunk))

        print(f"[OK] Descarga completada: {dest_path.name}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error al descargar {url}: {e}")
        # Eliminar archivo parcial si existe
        if dest_path.exists():
            dest_path.unlink()
        return False
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False


def _download_luna16_batch(file_keys, download_dir):
    """
    Descarga y descomprime una lista de recursos de LUNA16

    Args:
        file_keys: lista de claves presentes en ZENODO_URLS
                  ejemplo: ['subset0', 'annotations', 'candidates']
        download_dir: Directorio donde descargar los archivos

    Returns:
        bool: True si todo fue exitoso
    """
    download_dir = Path(download_dir)
    total_files = len(file_keys)

    for idx, file_key in enumerate(file_keys, start=1):
        url = ZENODO_URLS[file_key]

        # Decidir nombre de archivo en disco
        if file_key.startswith("subset"):
            filename = f"{file_key}.zip"
            dest_path = download_dir / filename
            extracted_dir = download_dir / file_key  # carpeta descomprimida
        else:
            filename = f"{file_key}.csv"
            dest_path = download_dir / filename
            extracted_dir = None

        # Verificar si ya existe
        if file_key.startswith("subset"):
            # Para subsets: verificar que la carpeta extraída existe y tiene archivos .mhd
            if extracted_dir and extracted_dir.exists():
                mhd_files = list(extracted_dir.glob("*.mhd"))
                if len(mhd_files) > 0:
                    print(f"[OK] {file_key} ya existe ({len(mhd_files)} archivos .mhd), saltando")
                    continue
        else:
            # Para CSV: verificar que existe y tiene contenido
            if dest_path.exists() and dest_path.stat().st_size > 0:
                print(f"[OK] {file_key} ya existe, saltando")
                continue

        print(f"\n[{idx}/{total_files}] Descargando {filename}...")
        success = download_file_with_progress(url, dest_path, overwrite=True)

        if not success:
            print(f"[ERROR] Error descargando {filename}")
            return False

        # Descomprimir si es un .zip
        if file_key.startswith("subset"):
            print(f"Descomprimiendo {filename}...")

            try:
                with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                    # Obtener lista de archivos
                    members = zip_ref.namelist()

                    # Detectar si el zip tiene una carpeta raíz (ej: subset1/archivo.mhd)
                    # Si todos los archivos empiezan con "subsetX/", extraer al directorio padre
                    has_root_folder = all(m.startswith(f"{file_key}/") or m == f"{file_key}" for m in members if m)

                    if has_root_folder:
                        # Extraer directamente a download_dir (el zip ya tiene la carpeta)
                        extract_to = download_dir
                        print(f"[INFO] Zip contiene carpeta {file_key}/, extrayendo a {download_dir}")
                    else:
                        # El zip no tiene carpeta raíz, crear extracted_dir
                        extracted_dir.mkdir(parents=True, exist_ok=True)
                        extract_to = extracted_dir
                        print(f"[INFO] Zip sin carpeta raíz, extrayendo a {extracted_dir}")

                    # Descomprimir con barra de progreso
                    for member in tqdm(members, desc=f"Extrayendo {file_key}", unit="archivo"):
                        zip_ref.extract(member, extract_to)

                print(f"[OK] {file_key} descomprimido correctamente")

                # Opcional: eliminar el .zip después de extraer para ahorrar espacio
                dest_path.unlink()
                print(f"[INFO] Archivo .zip eliminado: {filename}")

            except zipfile.BadZipFile:
                print(f"[ERROR] {filename} está corrupto o no es un archivo zip válido")
                return False
            except Exception as e:
                print(f"[ERROR] Error al descomprimir {filename}: {e}")
                return False

    return True


def download_luna16(subsets=0, include_csv=True, download_dir=None):
    """
    Descarga datos del dataset LUNA16 de forma paramétrica
    Compatible con Google Colab y ejecución local

    Args:
        subsets: Subsets a descargar. Puede ser:
                - int: un subset específico (ej: 0)
                - list: lista de subsets (ej: [0, 1, 2])
                - 'all': todos los subsets (0-9)
                - None: equivalente a 0
        include_csv: Si True, descarga annotations.csv y candidates.csv
        download_dir: Directorio de destino. Si None, usa './LUNA16'

    Returns:
        bool: True si todo fue exitoso

    Ejemplos:
        >>> download_luna16()                        # subset0 + CSV (por defecto)
        >>> download_luna16(subsets=0)               # idem anterior
        >>> download_luna16(subsets=[0,1,2])         # subset0,1,2 + CSV
        >>> download_luna16(subsets='all')           # todos los subsets 0-9 + CSV
        >>> download_luna16(subsets='all', include_csv=False)  # solo imágenes
    """
    # Determinar directorio de descarga
    if download_dir is None:
        download_dir = Path("./LUNA16")
    else:
        download_dir = Path(download_dir)

    # Crear directorio si no existe
    download_dir.mkdir(parents=True, exist_ok=True)

    # Normalizar parámetro subsets a lista de índices [0..9]
    if subsets is None or subsets == 0:
        subset_ids = [0]
    elif subsets == "all":
        subset_ids = list(range(10))
    elif isinstance(subsets, int):
        subset_ids = [subsets]
    elif isinstance(subsets, list):
        subset_ids = subsets
    else:
        print(f"[ERROR] Parámetro 'subsets' inválido: {subsets}")
        return False

    # Validar que los índices estén en rango [0..9]
    if not all(0 <= s <= 9 for s in subset_ids):
        print(f"[ERROR] Índices de subset deben estar en [0..9]: {subset_ids}")
        return False

    # Construir lista de archivos a descargar
    file_keys = [f"subset{i}" for i in subset_ids]

    if include_csv:
        file_keys.extend(['annotations', 'candidates'])

    # Mostrar resumen
    print("="*70)
    print("DESCARGA DE LUNA16 DESDE ZENODO")
    print("="*70)
    print(f"Directorio de destino: {download_dir.absolute()}")
    print(f"Subsets a descargar: {subset_ids}")
    if include_csv:
        print("Incluyendo: annotations.csv y candidates.csv")
    print("="*70 + "\n")

    # Llamar al helper de descarga
    success = _download_luna16_batch(file_keys, download_dir)

    if success:
        print("\n" + "="*70)
        print("[SUCCESS] DESCARGA COMPLETADA")
        print("="*70)
        print(f"Datos disponibles en: {download_dir.absolute()}")

        # Mostrar estadísticas
        for subset_id in subset_ids:
            subset_path = download_dir / f"subset{subset_id}"
            if subset_path.exists():
                mhd_files = list(subset_path.glob("*.mhd"))
                print(f"  - subset{subset_id}: {len(mhd_files)} archivos .mhd")

        return True
    else:
        print("\n" + "="*70)
        print("[ERROR] DESCARGA INCOMPLETA")
        print("="*70)
        return False


if __name__ == "__main__":
    # Ejemplo de uso
    print("Script de descarga automática de LUNA16\n")

    # Descargar subset0 + CSV por defecto
    success = download_luna16()

    if success:
        print("\n[INFO] Dataset listo para usar")
    else:
        print("\n[ERROR] Hubo problemas durante la descarga")
