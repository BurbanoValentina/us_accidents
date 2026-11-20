"""
Módulo Único de Transformación, Limpieza y Enriquecimiento (ETL - Fase 2)
========================================================================
Responsable unificado de:
1. Deduplicación global incremental por ID.
2. Normalización de marcas temporales con precisión de nanosegundos (.000000000).
3. Detección y tratamiento de anomalías temporales (duraciones negativas y outliers > 24h).
4. Ingeniería de características temporales (año, mes, nombre mes español, hora, día semana español, franja horaria).
5. Agrupación semántica de condiciones climáticas (PyArrow RE2 en C++ y Spark SQL).
6. Clasificación de infraestructura vial y tipo de vía (Autopistas, Carreteras, Avenidas, Calles).
7. Minería de texto / NLP sobre descripciones para extracción de tipos de vehículo con filtrado de falsos positivos toponímicos.
8. Optimización estricta de tipos de datos en memoria (Downcasting a int8, float32, categóricos).
9. Soporte dual: motor Pandas/PyArrow (para streaming de bajo consumo) y motor PySpark (distribuido).

Tecnologías utilizadas:
- Python 3.13
- Pandas 2.2+
- Apache PyArrow 18+ (PyArrow Compute RE2 para expresiones regulares de alto rendimiento compiladas en C++)
- NumPy (np.select para vectorización condicional)
- Apache PySpark (transformaciones distribuidas con funciones nativas de Spark SQL)
"""

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

DIAS_ES = {
    1: "Domingo", 2: "Lunes", 3: "Martes", 4: "Miércoles",
    5: "Jueves", 6: "Viernes", 7: "Sábado",
}


# ==============================================================================
# MOTOR 1: TRANSFORMACIÓN CON PANDAS / PYARROW (STREAMING EN BLOQUES)
# ==============================================================================

class TransformadorAccidentes:
    """Aplica las reglas de negocio, limpieza, derivación y enriquecimiento a cada bloque."""

    def __init__(self):
        self.seen_ids = set()
        self.metricas = {
            "duplicados_eliminados": 0,
            "timestamps_con_nanosegundos_corregidos": 0,
            "timestamps_invalidos": 0,
            "duraciones_negativas": 0,
            "outliers_duracion_gt_24h": 0,
            "total_filas_transformadas": 0,
        }

    @staticmethod
    def clasificar_clima(series_weather: pd.Series) -> pd.Series:
        """Agrupación semántica de Weather_Condition en 6 categorías en español con PyArrow RE2."""
        arr = pa.array(series_weather.fillna("").astype(str))
        is_empty = pc.equal(arr, "")
        is_snow = pc.match_substring_regex(arr, r"(?i)(snow|ice|sleet|hail|wintry|freezing)")
        is_rain = pc.match_substring_regex(arr, r"(?i)(rain|drizzle|shower|thunder|t-storm|storm)")
        is_fog = pc.match_substring_regex(arr, r"(?i)(fog|mist|haze|smoke|dust|ash)")
        is_cloud = pc.match_substring_regex(arr, r"(?i)(cloud|overcast)")
        is_clear = pc.match_substring_regex(arr, r"(?i)(clear|fair)")

        conds = [
            is_empty.to_numpy(zero_copy_only=False),
            is_snow.to_numpy(zero_copy_only=False),
            is_rain.to_numpy(zero_copy_only=False),
            is_fog.to_numpy(zero_copy_only=False),
            is_cloud.to_numpy(zero_copy_only=False),
            is_clear.to_numpy(zero_copy_only=False),
        ]
        choices = ["Otro", "Nieve/Hielo", "Lluvia", "Niebla", "Nublado", "Despejado"]
        return pd.Series(np.select(conds, choices, default="Otro"), index=series_weather.index)

    @staticmethod
    def clasificar_tipo_via(series_street: pd.Series) -> pd.Series:
        """Clasifica el tipo de vía usando patrones RE2 en C++ sobre Street."""
        arr = pa.array(series_street.fillna("").astype(str))
        is_empty = pc.equal(arr, "")
        is_interstate = pc.match_substring_regex(
            arr, r"(?i)\b(I-\d+|INTERSTATE|FWY|FREEWAY|EXPY|EXPRESSWAY|PKWY|PARKWAY|TPKE|TURNPIKE)\b"
        )
        is_highway = pc.match_substring_regex(
            arr, r"(?i)\b(US-\d+|SR-\d+|STATE ROUTE|STATE HWY|HWY|HIGHWAY|RT-\d+|COUNTY RD|CR-\d+)\b"
        )
        is_blvd = pc.match_substring_regex(arr, r"(?i)\b(BLVD|BOULEVARD|AVE|AVENUE)\b")
        is_urban = pc.match_substring_regex(arr, r"(?i)\b(ST|STREET|RD|ROAD|DR|DRIVE|LN|LANE|WAY|CT|PL|CIR)\b")

        conds = [
            is_empty.to_numpy(zero_copy_only=False),
            is_interstate.to_numpy(zero_copy_only=False),
            is_highway.to_numpy(zero_copy_only=False),
            is_blvd.to_numpy(zero_copy_only=False),
            is_urban.to_numpy(zero_copy_only=False),
        ]
        choices = [
            "Sin dato",
            "Autopista / Interstate",
            "Carretera / Highway",
            "Avenida / Boulevard",
            "Calle / Vía Urbana",
        ]
        return pd.Series(np.select(conds, choices, default="Otra Vía"), index=series_street.index)

    @staticmethod
    def extraer_tipo_vehiculo(series_desc: pd.Series) -> pd.Series:
        """
        Extrae el tipo de vehículo involucrado desde Description mediante PyArrow RE2.
        Filtra falsos positivos toponímicos (ej. 'I-80 Bus', 'Van Ness Ave', 'Truck Route').
        """
        arr = pa.array(series_desc.fillna("").astype(str))

        is_suv_van = pc.match_substring_regex(
            arr, r"(?i)\b(suv|minivan|pickup|pickup truck|cargo van|sprinter|van involved|van fire|van overturned)\b"
        )
        is_truck = pc.and_not(
            pc.match_substring_regex(arr, r"(?i)\b(semi|tractor|18-wheeler|tanker|trailer|big rig|box truck|dump truck|truck)\b"),
            pc.match_substring_regex(arr, r"(?i)\b(truck route|truck stop|truck plaza|truck center|trailer park|pickup truck)\b"),
        )
        is_moto = pc.match_substring_regex(arr, r"(?i)\b(motorcycle|motorbike|moped|scooter)\b")
        is_bus = pc.match_substring_regex(
            arr, r"(?i)\b(school bus|transit bus|city bus|charter bus|shuttle bus|bus involved|bus accident|bus crash)\b"
        )
        is_bike = pc.match_substring_regex(arr, r"(?i)\b(bicycle|bicyclist|cyclist)\b")
        is_ped = pc.match_substring_regex(arr, r"(?i)\bpedestrian\b")
        is_car = pc.match_substring_regex(
            arr,
            r"(?i)\b(multi-?vehicle|multivehicle|two-?vehicle|three-?vehicle|multiple vehicles|car accident|car crash|car fire|car involved|a car|sedan|coupe|hatchback|vehicle involved|vehicle fire|overturned vehicle|disabled vehicle|stalled vehicle)\b",
        )

        conds = [
            is_truck.to_numpy(zero_copy_only=False),
            is_moto.to_numpy(zero_copy_only=False),
            is_bus.to_numpy(zero_copy_only=False),
            is_bike.to_numpy(zero_copy_only=False),
            is_ped.to_numpy(zero_copy_only=False),
            is_suv_van.to_numpy(zero_copy_only=False),
            is_car.to_numpy(zero_copy_only=False),
        ]
        choices = [
            "Camión / Tráiler",
            "Motocicleta",
            "Autobús",
            "Bicicleta",
            "Peatón involucrado",
            "SUV / Van / Pickup",
            "Automóvil / Multivehículo",
        ]
        return pd.Series(np.select(conds, choices, default="No especificado"), index=series_desc.index)

    @staticmethod
    def asignar_franja_horaria(series_hour: pd.Series) -> pd.Series:
        """Categoriza las 24 horas del día en 5 franjas operativas estándar."""
        conds = [
            (series_hour >= 0) & (series_hour < 6),
            (series_hour >= 6) & (series_hour < 10),
            (series_hour >= 10) & (series_hour < 15),
            (series_hour >= 15) & (series_hour < 20),
            (series_hour >= 20) & (series_hour <= 23),
        ]
        choices = [
            "1. Madrugada (00-05h)",
            "2. Pico Mañana (06-09h)",
            "3. Mediodía (10-14h)",
            "4. Pico Tarde (15-19h)",
            "5. Noche (20-23h)",
        ]
        return pd.Series(np.select(conds, choices, default="Sin dato"), index=series_hour.index)

    def transformar_bloque(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Aplica la totalidad de transformaciones vectorizadas a un bloque."""
        # 1. Deduplicación por ID
        mask_new = ~chunk["ID"].isin(self.seen_ids)
        if not mask_new.all():
            self.metricas["duplicados_eliminados"] += int((~mask_new).sum())
            chunk = chunk[mask_new].copy()
        self.seen_ids.update(chunk["ID"].tolist())

        # 2. Normalización de timestamps y corrección de nanosegundos (.000000000)
        st_str = chunk["Start_Time"].astype(str)
        et_str = chunk["End_Time"].astype(str)
        self.metricas["timestamps_con_nanosegundos_corregidos"] += int(st_str.str.contains(".", regex=False).sum())

        start_dt = pd.to_datetime(st_str.str.slice(0, 19), format="%Y-%m-%d %H:%M:%S", errors="coerce")
        end_dt = pd.to_datetime(et_str.str.slice(0, 19), format="%Y-%m-%d %H:%M:%S", errors="coerce")
        self.metricas["timestamps_invalidos"] += int(start_dt.isna().sum())

        # 3. Duración en minutos y detección de anomalías
        dur_raw = (end_dt - start_dt).dt.total_seconds() / 60.0
        neg_mask = dur_raw < 0
        self.metricas["duraciones_negativas"] += int(neg_mask.sum())
        dur_raw = dur_raw.mask(neg_mask, np.nan).round(2)

        outlier_mask = dur_raw > 1440.0
        self.metricas["outliers_duracion_gt_24h"] += int(outlier_mask.sum())
        dur_clean = dur_raw.mask(outlier_mask, np.nan)

        # 4. Derivaciones temporales
        dow_num = ((start_dt.dt.dayofweek + 1) % 7) + 1  # 1=Domingo..7=Sábado

        # 5. DataFrame final normalizado con tipos compactos
        out = pd.DataFrame({
            "id": chunk["ID"].astype(str),
            "source": chunk["Source"].fillna("Sin dato").astype(str),
            "severity": chunk["Severity"].astype("int8"),
            "start_time": start_dt.dt.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_dt.dt.strftime("%Y-%m-%d %H:%M:%S"),
            "year": start_dt.dt.year.astype("Int16"),
            "month": start_dt.dt.month.astype("Int8"),
            "month_name": start_dt.dt.month.map(MESES_ES).fillna("Sin dato"),
            "year_month": start_dt.dt.strftime("%Y-%m"),
            "hour": start_dt.dt.hour.astype("Int8"),
            "day_of_week_num": dow_num.astype("Int8"),
            "day_name": dow_num.map(DIAS_ES).fillna("Sin dato"),
            "is_weekend": dow_num.isin([1, 7]).astype("int8"),
            "time_slot": self.asignar_franja_horaria(start_dt.dt.hour.fillna(-1)),
            "duration_raw_min": dur_raw.astype("float32"),
            "duration_clean_min": dur_clean.astype("float32"),
            "distance_mi": pd.to_numeric(chunk["Distance(mi)"], errors="coerce").round(3).astype("float32"),
            "start_lat": pd.to_numeric(chunk["Start_Lat"], errors="coerce").round(5).astype("float32"),
            "start_lng": pd.to_numeric(chunk["Start_Lng"], errors="coerce").round(5).astype("float32"),
            "street": chunk["Street"].fillna("Sin dato").astype(str).str.strip(),
            "road_type": self.clasificar_tipo_via(chunk["Street"]),
            "city": chunk["City"].fillna("Sin dato").astype(str).str.strip(),
            "county": chunk["County"].fillna("Sin dato").astype(str).str.strip(),
            "state": chunk["State"].fillna("Sin dato").astype(str).str.strip(),
            "temperature_f": pd.to_numeric(chunk["Temperature(F)"], errors="coerce").astype("float32"),
            "humidity_pct": pd.to_numeric(chunk["Humidity(%)"], errors="coerce").astype("float32"),
            "visibility_mi": pd.to_numeric(chunk["Visibility(mi)"], errors="coerce").astype("float32"),
            "wind_speed_mph": pd.to_numeric(chunk["Wind_Speed(mph)"], errors="coerce").astype("float32"),
            "precipitation_in": pd.to_numeric(chunk["Precipitation(in)"], errors="coerce").astype("float32"),
            "weather_raw": chunk["Weather_Condition"].fillna("Sin dato").astype(str).str.strip(),
            "weather_group": self.clasificar_clima(chunk["Weather_Condition"]),
            "sunrise_sunset": chunk["Sunrise_Sunset"].fillna("Sin dato").astype(str),
            "traffic_signal": chunk["Traffic_Signal"].fillna(False).astype("int8"),
            "junction": chunk["Junction"].fillna(False).astype("int8"),
            "crossing": chunk["Crossing"].fillna(False).astype("int8"),
            "stop": chunk["Stop"].fillna(False).astype("int8"),
            "station": chunk["Station"].fillna(False).astype("int8"),
            "railway": chunk["Railway"].fillna(False).astype("int8"),
            "roundabout": chunk["Roundabout"].fillna(False).astype("int8"),
            "vehicle_type": self.extraer_tipo_vehiculo(chunk["Description"]),
        })

        self.metricas["total_filas_transformadas"] += len(out)
        return out


# ==============================================================================
# MOTOR 2: TRANSFORMACIÓN DISTRIBUIDA CON APACHE PYSPARK (SPARK SQL)
# ==============================================================================

def transformar_spark(df_raw):
    """
    Aplica las mismas transformaciones y reglas de negocio sobre un DataFrame distribuido
    utilizando funciones optimizadas de Spark SQL.
    """
    from pyspark.sql import functions as F

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
    return df


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 PROBANDO MÓDULO ÚNICO DE TRANSFORMACIÓN (Pandas/PyArrow + PySpark)")
    print("=" * 80)

    t = TransformadorAccidentes()
    sample_df = pd.DataFrame({
        "ID": ["A-1", "A-2"],
        "Source": ["Source1", "Source2"],
        "Severity": [2, 3],
        "Start_Time": ["2022-01-01 08:30:00.000000000", "2022-06-15 17:45:00"],
        "End_Time": ["2022-01-01 09:15:00.000000000", "2022-06-15 18:30:00"],
        "Distance(mi)": [0.5, 1.2],
        "Description": ["Accident involving a semi truck on I-95", "Car accident near traffic light"],
        "Street": ["I-95 N", "Main St"],
        "City": ["Miami", "Orlando"],
        "County": ["Miami-Dade", "Orange"],
        "State": ["FL", "FL"],
        "Temperature(F)": [75.0, 82.0],
        "Humidity(%)": [80.0, 65.0],
        "Visibility(mi)": [10.0, 9.0],
        "Wind_Speed(mph)": [5.0, 10.0],
        "Precipitation(in)": [0.0, 0.1],
        "Weather_Condition": ["Clear", "Light Rain"],
        "Traffic_Signal": [False, True],
        "Junction": [True, False],
        "Crossing": [False, True],
        "Stop": [False, False],
        "Station": [False, False],
        "Railway": [False, False],
        "Roundabout": [False, False],
        "Sunrise_Sunset": ["Day", "Day"],
        "Start_Lat": [25.77, 28.53],
        "Start_Lng": [-80.19, -81.37],
    })

    res = t.transformar_bloque(sample_df)
    print(f"\n[OK] Transformación con Pandas/PyArrow exitosa: {len(res)} filas, {len(res.columns)} columnas.")
    print("Columnas resultantes:", list(res.columns[:8]), "...")
    print(res[["id", "time_slot", "weather_group", "road_type", "vehicle_type"]].to_string())
