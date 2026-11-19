"""
Módulo de Extracción Distribuida con Apache PySpark (ETL - Fase 1)
==================================================================
Responsable de la ingesta distribuida con esquema fuertemente tipado:
1. Definición explícita de StructType para las 46 columnas originales del dataset.
2. Ingesta de fuentes CSV mediante SparkSession con lectura distribuida.

Tecnologías utilizadas:
- Apache Spark 3.5+ / PySpark
- Spark SQL DataFrame Reader
- Esquemas tipados StructType / StructField (evita el costo de inferSchema en 3 GB)
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, BooleanType
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_ACCIDENTS_CSV = os.path.join(BASE_DIR, "extraccion", "datos_origen", "US_Accidents_March23.csv")
RAW_DEMOGRAPHICS_CSV = os.path.join(BASE_DIR, "extraccion", "datos_origen", "us_state_demographics.csv")


def obtener_esquema_accidentes():
    """Retorna el esquema tipado explícito para optimizar la velocidad de ingesta."""
    return StructType([
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


def crear_spark_session(app_name="ETL_Extraccion_US_Accidents"):
    """Crea e inicializa una sesión local de Spark optimizada para la máquina."""
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", "4g")
        .config("spark.sql.shuffle.partitions", "16")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def extraer_datos_spark(spark, path_accidents=RAW_ACCIDENTS_CSV, path_demo=RAW_DEMOGRAPHICS_CSV):
    """Extrae las fuentes en DataFrames de PySpark."""
    schema_acc = obtener_esquema_accidentes()

    df_raw = (
        spark.read.format("csv")
        .option("header", "true")
        .option("escape", '"')
        .schema(schema_acc)
        .load(path_accidents)
    )

    df_demo = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load(path_demo)
    )

    return df_raw, df_demo


if __name__ == "__main__":
    print("=== Probando Extracción con PySpark ===")
    spark = crear_spark_session()
    df_raw, df_demo = extraer_datos_spark(spark)
    print(f"[OK] DataFrame Accidentes conectado. Columnas: {len(df_raw.columns)}")
    print(f"[OK] DataFrame Demografía conectado. Columnas: {len(df_demo.columns)}")
    spark.stop()
