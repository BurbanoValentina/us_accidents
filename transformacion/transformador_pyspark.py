"""
Módulo de Transformación Distribuida con Apache PySpark (ETL - Fase 2)
======================================================================
Responsable de:
1. Deduplicación distribuida por ID y filtrado de nulos críticos.
2. Parseo y normalización de timestamps con funciones de Spark SQL.
3. Derivación de duración y detección de valores atípicos (> 24h).
4. Clasificación semántica de clima, tipo de vía y NLP de vehículos en Spark.
5. Enriquecimiento demográfico mediante Broadcast Join (optimizando la red del clúster).

Tecnologías utilizadas:
- Apache PySpark 3.5+
- Spark SQL Functions (F.when, F.regexp_extract, F.to_timestamp, F.broadcast)
- Spark SQL Window Functions para ordenamiento y particiones analíticas
"""

from pyspark.sql import functions as F
from pyspark.sql import Window


def transformar_y_enriquecer_spark(df_raw, df_demo):
    """Aplica las transformaciones distribuidas sobre los DataFrames de PySpark."""
    df = (
        df_raw
        .filter(F.col("ID").isNotNull() & F.col("State").isNotNull())
        .dropDuplicates(["ID"])
        .withColumn("start_ts", F.to_timestamp(F.substring("Start_Time", 1, 19), "yyyy-MM-dd HH:mm:ss"))
        .withColumn("end_ts", F.to_timestamp(F.substring("End_Time", 1, 19), "yyyy-MM-dd HH:mm:ss"))
        .withColumn(
            "duration_raw_min",
            F.when(
                (F.col("end_ts").isNotNull()) & (F.col("start_ts").isNotNull()) & (F.col("end_ts") >= F.col("start_ts")),
                F.round((F.unix_timestamp("end_ts") - F.unix_timestamp("start_ts")) / 60.0, 2)
            ).otherwise(None)
        )
        .withColumn(
            "duration_clean_min",
            F.when(F.col("duration_raw_min") <= 1440.0, F.col("duration_raw_min")).otherwise(None)
        )
        .withColumn("year", F.year("start_ts"))
        .withColumn("month", F.month("start_ts"))
        .withColumn("hour", F.hour("start_ts"))
        .withColumn("day_of_week_num", F.dayofweek("start_ts"))
        .withColumn("weather_group", F.when(
            F.col("Weather_Condition").isin("Fair", "Clear"), "Despejado"
        ).when(
            F.col("Weather_Condition").isin("Mostly Cloudy", "Cloudy", "Partly Cloudy", "Overcast"), "Nublado"
        ).when(
            F.lower(F.col("Weather_Condition")).rlike("rain|drizzle|shower|thunder|t-storm|storm"), "Lluvia"
        ).when(
            F.lower(F.col("Weather_Condition")).rlike("fog|mist|haze|smoke|dust"), "Niebla"
        ).when(
            F.lower(F.col("Weather_Condition")).rlike("snow|ice|sleet|hail|wintry|freezing"), "Nieve/Hielo"
        ).otherwise("Otro"))
        .withColumn(
            "road_type",
            F.when(F.upper(F.col("Street")).rlike(r"\bI-\d+|INTERSTATE|FWY|EXPY|PKWY|TPKE"), "Autopista / Interstate")
            .when(F.upper(F.col("Street")).rlike(r"\bUS-\d+|\bSR-\d+|HWY|HIGHWAY|STATE ROUTE"), "Carretera / Highway")
            .when(F.upper(F.col("Street")).rlike(r"\bBLVD\b|\bAVE\b"), "Avenida / Boulevard")
            .when(F.upper(F.col("Street")).rlike(r"\bST\b|\bRD\b|\bDR\b|\bLN\b|\bWAY\b"), "Calle / Vía Urbana")
            .otherwise("Otra Vía")
        )
        .withColumn(
            "vehicle_kw",
            F.lower(F.regexp_extract(
                F.coalesce(F.col("Description"), F.lit("")),
                r"\b(suv|minivan|pickup|cargo van|van involved|semi|tractor|18-wheeler|tanker|trailer|truck|motorcycle|motorbike|scooter|school bus|transit bus|city bus|bus involved|bus accident|bicycle|bicyclist|cyclist|pedestrian|multi-?vehicle|car fire|car involved|car accident|sedan|vehicle involved|vehicle fire)\b",
                1
            ))
        )
        .withColumn(
            "vehicle_type",
            F.when(F.col("vehicle_kw").isin("suv", "minivan", "pickup", "cargo van", "van involved"), "SUV / Van / Pickup")
            .when(F.col("vehicle_kw").isin("semi", "tractor", "18-wheeler", "tanker", "trailer", "truck"), "Camión / Tráiler")
            .when(F.col("vehicle_kw").isin("motorcycle", "motorbike", "scooter"), "Motocicleta")
            .when(F.col("vehicle_kw").isin("school bus", "transit bus", "city bus", "bus involved", "bus accident"), "Autobús")
            .when(F.col("vehicle_kw").isin("bicycle", "bicyclist", "cyclist"), "Bicicleta")
            .when(F.col("vehicle_kw") == "pedestrian", "Peatón involucrado")
            .when(F.col("vehicle_kw") != "", "Automóvil / Multivehículo")
            .otherwise("No especificado")
        )
    )

    # Enriquecimiento demográfico por State mediante Broadcast Join
    df_enriched = df.join(F.broadcast(df_demo), on="State", how="left")
    return df_enriched
