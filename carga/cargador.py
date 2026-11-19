"""
Módulo de Carga Analítica, Indexación y Exportación (ETL - Fase 3)
=================================================================
Responsable de:
1. Almacenamiento Columnar: Creación y escritura incremental en formato Apache Parquet
   comprimido con Snappy (carga/almacenamiento_parquet/us_accidents_clean.parquet).
2. Base de Datos Relacional: Carga masiva en SQLite (carga/base_datos/us_accidents.db)
   utilizando PRAGMAs de alto rendimiento y transacciones atómicas por lote.
3. Indexación Analítica: Generación de 8 índices B-Tree para optimización de queries SQL.
4. Exportación del CSV Limpio Final: Generación del CSV ordenado y muestra de inspección
   rápida (csv_limpio_final/).
5. Registro de Auditoría: Guardado de métricas completas de calidad y rendimiento
   (carga/auditoria/00_etl_audit.json y 00_etl_audit.csv).

Tecnologías utilizadas:
- Apache PyArrow 18+ (ParquetWriter con compresión Snappy y pyarrow.csv)
- SQLite 3 (Python sqlite3 con PRAGMAs síncronos en memoria y transacción única por bloque)
- Python standard library (json, time, os)
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
CSV_SAMPLE_PATH = os.path.join(CSV_FINAL_DIR, "us_accidents_limpio_muestra_10k.csv")


class CargadorAlmacenamiento:
    """Administra la carga hacia Parquet, SQLite, CSV final y auditoría."""

    def __init__(self,
                 parquet_out=PARQUET_PATH,
                 sqlite_out=SQLITE_PATH,
                 csv_out=CSV_FULL_PATH,
                 csv_sample_out=CSV_SAMPLE_PATH,
                 audit_json=AUDIT_JSON_PATH,
                 audit_csv=AUDIT_CSV_PATH):
        self.parquet_out = parquet_out
        self.sqlite_out = sqlite_out
        self.csv_out = csv_out
        self.csv_sample_out = csv_sample_out
        self.audit_json = audit_json
        self.audit_csv = audit_csv

        self.parquet_writer = None
        self.sqlite_conn = None
        self.total_rows_loaded = 0

    def inicializar_sqlite(self, df_demo: pd.DataFrame):
        """Inicializa la base de datos SQLite con PRAGMAs optimizados y carga la dimensión demográfica."""
        os.makedirs(os.path.dirname(self.sqlite_out), exist_ok=True)
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

        # Cargar esquema DDL
        if os.path.exists(SQL_SCHEMA_PATH):
            with open(SQL_SCHEMA_PATH, "r", encoding="utf-8") as f:
                ddl = f.read()
            self.sqlite_conn.executescript(ddl)
        else:
            cur = self.sqlite_conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dim_demographics (
                    state TEXT PRIMARY KEY,
                    state_name TEXT,
                    region TEXT,
                    population_2023 INTEGER,
                    area_sqmi INTEGER,
                    density_per_sqmi REAL
                )
            """)

        # Insertar datos demográficos
        demo_cols = df_demo.rename(columns={
            "State": "state",
            "State_Name": "state_name",
            "Region": "region",
            "Population_2023": "population_2023",
            "Area_SqMi": "area_sqmi",
            "Density_Per_SqMi": "density_per_sqmi",
        })
        demo_cols.to_sql("dim_demographics", self.sqlite_conn, if_exists="replace", index=False)
        self.sqlite_conn.commit()
        print(f"[CARGA SQLite] Esquema y tabla dimensional 'dim_demographics' cargados ({len(df_demo)} estados).")

    def cargar_bloque(self, df_chunk: pd.DataFrame):
        """Escribe un bloque transformado hacia Parquet y hacia SQLite."""
        # 1. Escritura Parquet
        table = pa.Table.from_pandas(df_chunk, preserve_index=False)
        if self.parquet_writer is None:
            os.makedirs(os.path.dirname(self.parquet_out), exist_ok=True)
            self.parquet_writer = pq.ParquetWriter(self.parquet_out, table.schema, compression="snappy")
        self.parquet_writer.write_table(table)

        # 2. Carga en SQLite
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
            print(f"[CARGA Parquet] Archivo cerrado con éxito: {self.parquet_out}")

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

    def exportar_csv_limpio_desde_parquet(self, tamano_muestra=10_000):
        """Exporta el dataset limpio final completo a CSV y genera una muestra de 10k filas."""
        if not os.path.exists(self.parquet_out):
            raise FileNotFoundError(f"No existe el archivo Parquet para exportar CSV: {self.parquet_out}")

        os.makedirs(os.path.dirname(self.csv_out), exist_ok=True)
        print(f"[EXPORTACIÓN CSV] Generando CSV limpio final desde Parquet...")
        t0 = time.time()
        pf = pq.ParquetFile(self.parquet_out)
        total_rg = pf.num_row_groups

        # Generar muestra de 10k
        rg0 = pf.read_row_group(0)
        sample_table = rg0.slice(0, min(tamano_muestra, rg0.num_rows))
        pcsv.write_csv(sample_table, self.csv_sample_out)
        print(f"[OK] Muestra rápida exportada: {self.csv_sample_out}")

        # Streaming del CSV completo
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
    print("=== Módulo de Carga Analítica ===")
    c = CargadorAlmacenamiento()
    print(f"Parquet destino: {c.parquet_out} (Existe: {os.path.exists(c.parquet_out)})")
    print(f"SQLite destino:  {c.sqlite_out} (Existe: {os.path.exists(c.sqlite_out)})")
    print(f"CSV destino:     {c.csv_out} (Existe: {os.path.exists(c.csv_out)})")
