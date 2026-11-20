"""
Módulo de Carga Analítica, Indexación y Exportación (ETL - Fase 3)
=================================================================
Responsable de:
1. Almacenamiento Columnar: Creación y escritura incremental en formato Apache Parquet
   comprimido con Snappy (carga/almacenamiento_parquet/us_accidents_clean.parquet).
2. Base de Datos Relacional: Carga masiva en SQLite (carga/base_datos/us_accidents.db)
   utilizando PRAGMAs de alto rendimiento y transacciones atómicas por lote.
3. Indexación Analítica: Generación diferida de 8 índices B-Tree para optimización de queries SQL.
4. Exportación del CSV Limpio Final: Generación del dataset limpio completo (csv_limpio_final/us_accidents_limpio.csv).
5. Registro de Auditoría: Guardado de métricas completas de calidad y rendimiento
   (carga/auditoria/00_etl_audit.json y 00_etl_audit.csv).
6. Resiliencia: Reconstrucción automática de esquemas DDL y directorios si son eliminados.

Tecnologías utilizadas:
- Apache PyArrow 18+ (ParquetWriter con compresión Snappy y pyarrow.csv)
- SQLite 3 (Python sqlite3 con PRAGMAs síncronos en memoria y transacción única por bloque)
- Python standard library (json, time, os, shutil)
"""

import json
import os
import sqlite3
import time
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pcsv
import pyarrow.parquet as pq

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARQUET_PATH = os.path.join(BASE_DIR, "carga", "almacenamiento_parquet", "us_accidents_clean.parquet")
SQLITE_PATH = os.path.join(BASE_DIR, "carga", "base_datos", "us_accidents.db")
SQL_SCHEMA_PATH = os.path.join(BASE_DIR, "carga", "sql", "esquema_sqlite.sql")
AUDIT_JSON_PATH = os.path.join(BASE_DIR, "carga", "auditoria", "00_etl_audit.json")
AUDIT_CSV_PATH = os.path.join(BASE_DIR, "carga", "auditoria", "00_etl_audit.csv")
CSV_FINAL_DIR = os.path.join(BASE_DIR, "csv_limpio_final")
CSV_FULL_PATH = os.path.join(CSV_FINAL_DIR, "us_accidents_limpio.csv")

# Definición DDL de contingencia embebida (se autogenera si se elimina el archivo SQL)
DDL_ACCIDENTS_SQL = """-- ==============================================================================
-- DDL DE BASE DE DATOS ANALÍTICA (SQLite 3 / SQL Estándar)
-- Ubicación: carga/base_datos/us_accidents.db
-- Tabla de Hechos de Accidentes Viales (7,728,394 registros) + 8 Índices B-Tree
-- ==============================================================================

CREATE TABLE IF NOT EXISTS accidents (
    id TEXT,
    source TEXT,
    severity INTEGER,
    start_time TEXT,
    end_time TEXT,
    year INTEGER,
    month INTEGER,
    month_name TEXT,
    year_month TEXT,
    hour INTEGER,
    day_of_week_num INTEGER,
    day_name TEXT,
    is_weekend INTEGER,
    time_slot TEXT,
    duration_raw_min REAL,
    duration_clean_min REAL,
    distance_mi REAL,
    start_lat REAL,
    start_lng REAL,
    street TEXT,
    road_type TEXT,
    city TEXT,
    county TEXT,
    state TEXT,
    temperature_f REAL,
    humidity_pct REAL,
    visibility_mi REAL,
    wind_speed_mph REAL,
    precipitation_in REAL,
    weather_raw TEXT,
    weather_group TEXT,
    sunrise_sunset TEXT,
    traffic_signal INTEGER,
    junction INTEGER,
    crossing INTEGER,
    stop INTEGER,
    station INTEGER,
    railway INTEGER,
    roundabout INTEGER,
    vehicle_type TEXT
);

CREATE INDEX IF NOT EXISTS idx_acc_state ON accidents(state);
CREATE INDEX IF NOT EXISTS idx_acc_severity ON accidents(severity);
CREATE INDEX IF NOT EXISTS idx_acc_weather ON accidents(weather_group);
CREATE INDEX IF NOT EXISTS idx_acc_ym ON accidents(year, month);
CREATE INDEX IF NOT EXISTS idx_acc_hour ON accidents(hour);
CREATE INDEX IF NOT EXISTS idx_acc_day ON accidents(day_of_week_num);
CREATE INDEX IF NOT EXISTS idx_acc_road ON accidents(road_type);
CREATE INDEX IF NOT EXISTS idx_acc_veh ON accidents(vehicle_type);
"""


class CargadorAlmacenamiento:
    """Administra la carga hacia Parquet, SQLite, CSV final y auditoría."""

    def __init__(self,
                 parquet_out=PARQUET_PATH,
                 sqlite_out=SQLITE_PATH,
                 csv_out=CSV_FULL_PATH,
                 audit_json=AUDIT_JSON_PATH,
                 audit_csv=AUDIT_CSV_PATH):
        self.parquet_out = parquet_out
        self.sqlite_out = sqlite_out
        self.csv_out = csv_out
        self.audit_json = audit_json
        self.audit_csv = audit_csv

        self.parquet_writer = None
        self.sqlite_conn = None
        self.total_rows_loaded = 0

    def inicializar_sqlite(self):
        """
        Inicializa la base de datos SQLite con PRAGMAs optimizados y crea la tabla 'accidents'.
        Si el archivo de esquema SQL fue borrado, lo autogenera inmediatamente.
        """
        os.makedirs(os.path.dirname(self.sqlite_out), exist_ok=True)
        os.makedirs(os.path.dirname(SQL_SCHEMA_PATH), exist_ok=True)

        if os.path.exists(self.sqlite_out):
            try:
                os.remove(self.sqlite_out)
            except PermissionError:
                pass

        self.sqlite_conn = sqlite3.connect(self.sqlite_out)
        self.sqlite_conn.execute("PRAGMA synchronous = OFF")
        self.sqlite_conn.execute("PRAGMA journal_mode = MEMORY")
        self.sqlite_conn.execute("PRAGMA temp_store = MEMORY")
        self.sqlite_conn.execute("PRAGMA cache_size = -256000")

        # Cargar o regenerar el esquema DDL
        if os.path.exists(SQL_SCHEMA_PATH):
            with open(SQL_SCHEMA_PATH, "r", encoding="utf-8") as f:
                ddl = f.read()
        else:
            ddl = DDL_ACCIDENTS_SQL.strip()
            with open(SQL_SCHEMA_PATH, "w", encoding="utf-8") as f:
                f.write(ddl)
            print(f"[CARGA SQLite] Esquema regenerado automáticamente en: {SQL_SCHEMA_PATH}")

        self.sqlite_conn.executescript(ddl)
        self.sqlite_conn.commit()
        print(f"[CARGA SQLite] Base de datos y tabla 'accidents' inicializadas correctamente.")

    def cargar_bloque(self, df_chunk: pd.DataFrame):
        """Escribe un bloque transformado hacia Parquet y hacia SQLite."""
        # 1. Escritura Parquet incremental
        table = pa.Table.from_pandas(df_chunk, preserve_index=False)
        if self.parquet_writer is None:
            os.makedirs(os.path.dirname(self.parquet_out), exist_ok=True)
            self.parquet_writer = pq.ParquetWriter(self.parquet_out, table.schema, compression="snappy")
        self.parquet_writer.write_table(table)

        # 2. Carga en SQLite en lote único
        if self.sqlite_conn is not None:
            cols_list = list(df_chunk.columns)
            placeholders = ",".join(["?"] * len(cols_list))
            insert_sql = f"INSERT INTO accidents ({','.join(cols_list)}) VALUES ({placeholders})"
            col_arrays = []
            for col_name in cols_list:
                s_col = df_chunk[col_name]
                if pd.api.types.is_integer_dtype(s_col):
                    if s_col.isna().any():
                        col_arrays.append([None if pd.isna(v) else int(v) for v in s_col.tolist()])
                    else:
                        col_arrays.append(s_col.astype(int).tolist())
                elif pd.api.types.is_float_dtype(s_col):
                    vals = s_col.astype(float).tolist()
                    col_arrays.append([None if (v != v) else v for v in vals])
                else:
                    col_arrays.append([None if pd.isna(v) else str(v) for v in s_col.tolist()])

            self.sqlite_conn.execute("BEGIN")
            self.sqlite_conn.executemany(insert_sql, zip(*col_arrays))
            self.sqlite_conn.commit()

        self.total_rows_loaded += len(df_chunk)

    def cerrar_y_crear_indices(self):
        """Cierra el escritor Parquet y construye los 8 índices B-Tree en SQLite."""
        if self.parquet_writer is not None:
            self.parquet_writer.close()
            self.parquet_writer = None
            print(f"[CARGA Parquet] Archivo Parquet completado: {self.parquet_out}")

        if self.sqlite_conn is not None:
            print("[CARGA SQLite] Generando 8 índices B-Tree para optimización de consultas...")
            t_idx = time.time()
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_acc_state ON accidents(state)",
                "CREATE INDEX IF NOT EXISTS idx_acc_severity ON accidents(severity)",
                "CREATE INDEX IF NOT EXISTS idx_acc_weather ON accidents(weather_group)",
                "CREATE INDEX IF NOT EXISTS idx_acc_ym ON accidents(year, month)",
                "CREATE INDEX IF NOT EXISTS idx_acc_hour ON accidents(hour)",
                "CREATE INDEX IF NOT EXISTS idx_acc_day ON accidents(day_of_week_num)",
                "CREATE INDEX IF NOT EXISTS idx_acc_road ON accidents(road_type)",
                "CREATE INDEX IF NOT EXISTS idx_acc_veh ON accidents(vehicle_type)",
            ]
            for idx_sql in indices:
                self.sqlite_conn.execute(idx_sql)
            self.sqlite_conn.commit()
            self.sqlite_conn.close()
            self.sqlite_conn = None
            print(f"[CARGA SQLite] Índices creados exitosamente en {time.time() - t_idx:.2f} segundos.")

    def exportar_csv_limpio_desde_parquet(self):
        """Exporta el dataset limpio final completo a CSV directamente desde Parquet por streaming."""
        if not os.path.exists(self.parquet_out):
            raise FileNotFoundError(f"No existe el archivo Parquet para exportar CSV: {self.parquet_out}")

        os.makedirs(os.path.dirname(self.csv_out), exist_ok=True)
        print(f"[EXPORTACIÓN CSV] Generando CSV limpio final desde Parquet...")
        t0 = time.time()
        pf = pq.ParquetFile(self.parquet_out)
        total_rg = pf.num_row_groups

        # Streaming del CSV completo por grupos de filas
        with open(self.csv_out, "wb") as f_out:
            write_options = pcsv.WriteOptions(include_header=True)
            for i in range(total_rg):
                table_rg = pf.read_row_group(i)
                pcsv.write_csv(table_rg, f_out, write_options=write_options)
                write_options = pcsv.WriteOptions(include_header=False)

        size_gb = os.path.getsize(self.csv_out) / (1024 ** 3)
        print(f"[OK] CSV Limpio Final generado: {self.csv_out} ({size_gb:.2f} GB) en {time.time() - t0:.2f}s")

    def guardar_auditoria(self, metricas_completas: dict):
        """Guarda las métricas del pipeline en JSON y CSV."""
        os.makedirs(os.path.dirname(self.audit_json), exist_ok=True)
        with open(self.audit_json, "w", encoding="utf-8") as f:
            json.dump(metricas_completas, f, indent=2, ensure_ascii=False)
        pd.DataFrame([metricas_completas]).to_csv(self.audit_csv, index=False)
        print(f"[AUDITORÍA] Métricas consolidadas guardadas en {self.audit_json} y {self.audit_csv}")


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 PROBANDO MÓDULO DE CARGA (Validación de estructura y base de datos)")
    print("=" * 80)

    c = CargadorAlmacenamiento()

    # 1. Asegurar directorios de destino
    os.makedirs(os.path.dirname(c.parquet_out), exist_ok=True)
    os.makedirs(os.path.dirname(c.sqlite_out), exist_ok=True)
    os.makedirs(os.path.dirname(c.csv_out), exist_ok=True)
    os.makedirs(os.path.dirname(c.audit_json), exist_ok=True)

    # 2. Inicializar base de datos y esquema
    c.inicializar_sqlite()

    # 3. Cargar un bloque mínimo de prueba para verificar escritura
    sample_df = pd.DataFrame({
        "id": ["TEST-1"],
        "source": ["Source1"],
        "severity": [2],
        "start_time": ["2023-01-01 12:00:00"],
        "end_time": ["2023-01-01 13:00:00"],
        "year": [2023],
        "month": [1],
        "month_name": ["Enero"],
        "year_month": ["2023-01"],
        "hour": [12],
        "day_of_week_num": [1],
        "day_name": ["Domingo"],
        "is_weekend": [1],
        "time_slot": ["3. Mediodía (10-14h)"],
        "duration_raw_min": [60.0],
        "duration_clean_min": [60.0],
        "distance_mi": [0.5],
        "start_lat": [25.77],
        "start_lng": [-80.19],
        "street": ["I-95"],
        "road_type": ["Autopista / Interstate"],
        "city": ["Miami"],
        "county": ["Miami-Dade"],
        "state": ["FL"],
        "temperature_f": [75.0],
        "humidity_pct": [60.0],
        "visibility_mi": [10.0],
        "wind_speed_mph": [5.0],
        "precipitation_in": [0.0],
        "weather_raw": ["Clear"],
        "weather_group": ["Despejado"],
        "sunrise_sunset": ["Day"],
        "traffic_signal": [0],
        "junction": [1],
        "crossing": [0],
        "stop": [0],
        "station": [0],
        "railway": [0],
        "roundabout": [0],
        "vehicle_type": ["Automóvil / Multivehículo"]
    })

    c.cargar_bloque(sample_df)
    c.cerrar_y_crear_indices()

    print(f"\n[OK] Verificación completada exitosamente:")
    print(f"  * Base de datos SQLite creada:   {c.sqlite_out} (Existe: {os.path.exists(c.sqlite_out)})")
    print(f"  * Archivo Parquet creado:       {c.parquet_out} (Existe: {os.path.exists(c.parquet_out)})")
    print(f"  * Directorio CSV preparado:     {os.path.dirname(c.csv_out)}")
    print(f"\nℹ️ Para ejecutar la carga masiva completa de los 7.7 millones de registros:")
    print(f"   python ejecutar_etl.py --modo etl")
