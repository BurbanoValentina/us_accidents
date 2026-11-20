"""
Módulo Único de Extracción y Descarga de Datos (ETL - Fase 1)
=============================================================
Responsable exclusivo de:
1. Descarga y extracción automática del dataset de accidentes viales desde la URL de Kaggle:
   https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents
2. Almacenamiento local del archivo 'US_Accidents_March23.csv' en 'extraccion/datos_origen/'.
3. Ingesta controlada en streaming con Pandas (chunksize=500,000) para no saturar memoria RAM.
4. Soporte opcional de lectura distribuida con Apache PySpark si se requiere motor distribuido.

Tecnologías utilizadas:
- Python 3.13
- KaggleHub (descarga pública y anónima directa desde la URL de Kaggle sin credenciales manuales)
- Pandas (motor de streaming por bloques)
- Apache PySpark (lectura tipada bajo demanda)
"""

import os
import shutil
import sys
import time
import pandas as pd

# Rutas estándar del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_DATOS_ORIGEN = os.path.join(BASE_DIR, "extraccion", "datos_origen")
RAW_ACCIDENTS_CSV = os.path.join(DIR_DATOS_ORIGEN, "US_Accidents_March23.csv")

# URL Oficial de Kaggle
URL_KAGGLE_ACCIDENTS = "https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents"
KAGGLE_DATASET_SLUG = "sobhanmoosavi/us-accidents"

# Columnas relevantes seleccionadas para la extracción (27 de 46)
COLUMNAS_EXTRACCION = [
    "ID", "Source", "Severity", "Start_Time", "End_Time",
    "Start_Lat", "Start_Lng", "Distance(mi)", "Description",
    "Street", "City", "County", "State",
    "Temperature(F)", "Humidity(%)", "Visibility(mi)",
    "Wind_Speed(mph)", "Precipitation(in)", "Weather_Condition",
    "Crossing", "Junction", "Railway", "Roundabout",
    "Station", "Stop", "Traffic_Signal", "Sunrise_Sunset",
]


class ExtractorAccidentes:
    """Clase única para la descarga desde URL y extracción del dataset de Kaggle."""

    def __init__(self, ruta_accidentes=RAW_ACCIDENTS_CSV):
        self.ruta_accidentes = ruta_accidentes
        self.metricas = {
            "total_filas_crudas": 0,
            "nulos_calle": 0,
            "nulos_ciudad": 0,
            "nulos_clima": 0,
            "nulos_temperatura": 0,
            "nulos_visibilidad": 0,
        }

    def asegurar_archivo_accidentes(self):
        """
        Garantiza que el dataset exista en 'extraccion/datos_origen/US_Accidents_March23.csv'.
        Si no existe, lo descarga y extrae automáticamente desde la URL oficial de Kaggle:
        https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents
        """
        os.makedirs(DIR_DATOS_ORIGEN, exist_ok=True)

        if os.path.exists(self.ruta_accidentes) and os.path.getsize(self.ruta_accidentes) > 100_000_000:
            return

        print("=" * 80)
        print("📥 DESCARGA AUTOMÁTICA DEL DATASET DESDE KAGGLE")
        print(f"   URL: {URL_KAGGLE_ACCIDENTS}")
        print(f"   Slug: {KAGGLE_DATASET_SLUG}")
        print("   Descargando directamente con KaggleHub (público y anónimo)...")
        print("=" * 80)

        # 1. Verificar si ya existe en la caché local de KaggleHub para evitar descargas duplicadas
        user_home = os.path.expanduser("~")
        cache_dir = os.path.join(user_home, ".cache", "kagglehub", "datasets", "sobhanmoosavi", "us-accidents")
        csv_en_cache = None

        if os.path.exists(cache_dir):
            for root, _, files in os.walk(cache_dir):
                for f in files:
                    if f.lower().endswith(".csv") and "accident" in f.lower():
                        candidato = os.path.join(root, f)
                        if os.path.getsize(candidato) > 100_000_000:
                            csv_en_cache = candidato
                            break
                if csv_en_cache:
                    break

        if csv_en_cache and os.path.exists(csv_en_cache):
            print(f"[EXTRACCIÓN] Dataset localizado en caché: {csv_en_cache}")
            print(f"[EXTRACCIÓN] Copiando hacia: {self.ruta_accidentes} ...")
            t0 = time.time()
            shutil.copyfile(csv_en_cache, self.ruta_accidentes)
            print(f"[EXTRACCIÓN] [OK] Copiado exitosamente en {time.time() - t0:.2f}s ({os.path.getsize(self.ruta_accidentes):,} bytes).")
            return

        # 2. Descargar desde la URL de Kaggle utilizando la librería kagglehub
        try:
            import kagglehub
        except ImportError:
            print("[EXTRACCIÓN] Instalando librería requerida 'kagglehub'...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "kagglehub"])
            import kagglehub

        t_descarga = time.time()
        print(f"[EXTRACCIÓN] Descargando desde URL de Kaggle ({KAGGLE_DATASET_SLUG})...")
        path_descargado = kagglehub.dataset_download(KAGGLE_DATASET_SLUG)
        print(f"[EXTRACCIÓN] Descarga completada en {time.time() - t_descarga:.2f}s.")
        print(f"[EXTRACCIÓN] Carpeta de descarga: {path_descargado}")

        # Localizar el archivo CSV descomprimido
        csv_encontrado = None
        for root, _, files in os.walk(path_descargado):
            for f in files:
                if f.lower().endswith(".csv"):
                    csv_encontrado = os.path.join(root, f)
                    break
            if csv_encontrado:
                break

        if not csv_encontrado:
            raise FileNotFoundError(f"No se encontró un archivo CSV dentro de la descarga de Kaggle en: {path_descargado}")

        print(f"[EXTRACCIÓN] Posicionando {csv_encontrado} en {self.ruta_accidentes} ...")
        shutil.copyfile(csv_encontrado, self.ruta_accidentes)
        print(f"[EXTRACCIÓN] [OK] Dataset listo para procesamiento ({os.path.getsize(self.ruta_accidentes):,} bytes).")

    def iterar_bloques_accidentes(self, tamano_bloque=500_000):
        """
        Asegura la existencia del dataset e itera los datos crudos en streaming por bloques (chunks),
        manteniendo el consumo de RAM por debajo de 1.5 GB para los 3.05 GB.
        """
        self.asegurar_archivo_accidentes()

        print(f"[EXTRACCIÓN] Iniciando streaming desde: {self.ruta_accidentes}")
        print(f"             Tamaño de bloque: {tamano_bloque:,} filas | Columnas seleccionadas: {len(COLUMNAS_EXTRACCION)}")

        lector = pd.read_csv(
            self.ruta_accidentes,
            usecols=COLUMNAS_EXTRACCION,
            chunksize=tamano_bloque,
            low_memory=False
        )

        for i, bloque in enumerate(lector):
            filas_bloque = len(bloque)
            self.metricas["total_filas_crudas"] += filas_bloque
            self.metricas["nulos_calle"] += int(bloque["Street"].isna().sum())
            self.metricas["nulos_ciudad"] += int(bloque["City"].isna().sum())
            self.metricas["nulos_clima"] += int(bloque["Weather_Condition"].isna().sum())
            self.metricas["nulos_temperatura"] += int(bloque["Temperature(F)"].isna().sum())
            self.metricas["nulos_visibilidad"] += int(bloque["Visibility(mi)"].isna().sum())

            yield i + 1, bloque

    def extraer_spark(self, spark):
        """
        Método unificado para ingesta distribuida con Apache PySpark
        utilizando esquema tipado explícito.
        """
        from pyspark.sql.types import (
            StructType, StructField, StringType, IntegerType, DoubleType, BooleanType
        )

        self.asegurar_archivo_accidentes()

        schema = StructType([
            StructField("ID", StringType(), True),
            StructField("Source", StringType(), True),
            StructField("Severity", IntegerType(), True),
            StructField("Start_Time", StringType(), True),
            StructField("End_Time", StringType(), True),
            StructField("Start_Lat", DoubleType(), True),
            StructField("Start_Lng", DoubleType(), True),
            StructField("End_Lat", DoubleType(), True),
            StructField("End_Lng", DoubleType(), True),
            StructField("Distance(mi)", DoubleType(), True),
            StructField("Description", StringType(), True),
            StructField("Street", StringType(), True),
            StructField("City", StringType(), True),
            StructField("County", StringType(), True),
            StructField("State", StringType(), True),
            StructField("Zipcode", StringType(), True),
            StructField("Country", StringType(), True),
            StructField("Timezone", StringType(), True),
            StructField("Airport_Code", StringType(), True),
            StructField("Weather_Timestamp", StringType(), True),
            StructField("Temperature(F)", DoubleType(), True),
            StructField("Wind_Chill(F)", DoubleType(), True),
            StructField("Humidity(%)", DoubleType(), True),
            StructField("Pressure(in)", DoubleType(), True),
            StructField("Visibility(mi)", DoubleType(), True),
            StructField("Wind_Direction", StringType(), True),
            StructField("Wind_Speed(mph)", DoubleType(), True),
            StructField("Precipitation(in)", DoubleType(), True),
            StructField("Weather_Condition", StringType(), True),
            StructField("Amenity", BooleanType(), True),
            StructField("Bump", BooleanType(), True),
            StructField("Crossing", BooleanType(), True),
            StructField("Give_Way", BooleanType(), True),
            StructField("Junction", BooleanType(), True),
            StructField("No_Exit", BooleanType(), True),
            StructField("Railway", BooleanType(), True),
            StructField("Roundabout", BooleanType(), True),
            StructField("Station", BooleanType(), True),
            StructField("Stop", BooleanType(), True),
            StructField("Traffic_Calming", BooleanType(), True),
            StructField("Traffic_Signal", BooleanType(), True),
            StructField("Turning_Loop", BooleanType(), True),
            StructField("Sunrise_Sunset", StringType(), True),
            StructField("Civil_Twilight", StringType(), True),
            StructField("Nautical_Twilight", StringType(), True),
            StructField("Astronomical_Twilight", StringType(), True),
        ])

        df_spark = (
            spark.read.format("csv")
            .option("header", "true")
            .option("escape", '"')
            .schema(schema)
            .load(self.ruta_accidentes)
        )
        return df_spark


if __name__ == "__main__":
    t0 = time.time()
    print("=" * 80)
    print("🚀 EJECUTANDO EXTRACTOR ÚNICO (Descarga desde URL de Kaggle y Streaming)")
    print("=" * 80)

    extractor = ExtractorAccidentes()
    print("\n--- 1. Asegurar descarga desde URL de Kaggle ---")
    extractor.asegurar_archivo_accidentes()

    print("\n--- 2. Muestra de Lectura en Streaming (Primer bloque) ---")
    for num_bloque, chunk in extractor.iterar_bloques_accidentes(tamano_bloque=10_000):
        print(f"[OK] Bloque {num_bloque} extraído exitosamente:")
        print(f"     Total filas en bloque: {len(chunk):,}")
        print(f"     Columnas extraídas ({len(chunk.columns)}): {list(chunk.columns[:6])} ...")
        break

    print(f"\n✅ Extractor finalizado exitosamente en {time.time() - t0:.2f} segundos.")
