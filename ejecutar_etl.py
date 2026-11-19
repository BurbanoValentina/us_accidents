"""
==============================================================================
ORQUESTADOR PRINCIPAL DEL PIPELINE ETL Y ANÁLISIS SQL (US ACCIDENTS)
==============================================================================
Pipeline completo para el procesamiento y análisis de 7.7M de accidentes viales.
Estructura modular dividida en:
  1. Extracción    (extraccion/)
  2. Transformación (transformacion/)
  3. Carga          (carga/)
  4. CSV Final      (csv_limpio_final/)
  5. Consultas SQL  (carga/consultas_sql.py)

Uso:
  python ejecutar_etl.py                     # Ejecuta el pipeline completo (Python/PyArrow)
  python ejecutar_etl.py --fase sql          # Responde las 10 preguntas analíticas con SQL
  python ejecutar_etl.py --fase sql --pregunta 1  # Responde una pregunta específica (1 a 10)
  python ejecutar_etl.py --fase csv          # Exporta el CSV limpio final desde Parquet
  python ejecutar_etl.py --engine pyspark    # Ejecuta el pipeline distribuido con PySpark
==============================================================================
"""

import argparse
import os
import sys
import time

# Asegurar que la raíz del proyecto esté en el sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from extraccion.extractor import ExtractorAccidentes
from transformacion.transformador import TransformadorAccidentes
from carga.cargador import CargadorAlmacenamiento
from carga.consultas_sql import responder_10_preguntas


def parse_args():
    parser = argparse.ArgumentParser(description="Orquestador ETL y Consultas SQL - US Accidents")
    parser.add_argument(
        "--fase",
        choices=["todas", "extraccion", "transformacion", "carga", "csv", "sql"],
        default="todas",
        help="Fase específica a ejecutar: todas, extraccion, transformacion, carga, csv, sql (por defecto: todas)",
    )
    parser.add_argument(
        "--pregunta",
        type=int,
        choices=range(1, 11),
        default=None,
        help="Número de requerimiento analítico específico a responder con SQL (1 al 10)",
    )
    parser.add_argument(
        "--engine",
        choices=["python", "pyspark"],
        default="python",
        help="Motor de procesamiento (python con PyArrow o pyspark)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500_000,
        help="Tamaño de bloque para streaming (por defecto: 500,000 filas)",
    )
    return parser.parse_args()


def ejecutar_pipeline_python(fase="todas", chunk_size=500_000, pregunta=None):
    t_inicio = time.time()

    # Si se solicitan consultas SQL analíticas
    if fase == "sql" or pregunta is not None:
        print("\n" + "=" * 85)
        print("🔍 EJECUTANDO CONSULTAS SQL ANALÍTICAS (SQLite 3)")
        print("=" * 85)
        responder_10_preguntas(filtro_pregunta=pregunta)
        return

    # Si solo se solicitó exportar el CSV limpio final
    if fase == "csv":
        cargador = CargadorAlmacenamiento()
        print("\n=== GENERACIÓN EXCLUSIVA DE CSV LIMPIO FINAL ===")
        cargador.exportar_csv_limpio_desde_parquet()
        print(f"\n✅ Proceso completado en {time.time() - t_inicio:.2f} segundos.")
        return

    print("=" * 80)
    print("🚀 INICIANDO PIPELINE ETL MODULAR (Motor: Python + PyArrow + SQLite)")
    print("=" * 80)

    extractor = ExtractorAccidentes()
    transformador = TransformadorAccidentes()
    cargador = CargadorAlmacenamiento()

    # Cargar tabla demográfica de referencia
    print("\n--- FASE 1: EXTRACCIÓN ---")
    df_demo = extractor.cargar_demografia()
    print(f"[OK] Demografía del Censo cargada ({len(df_demo)} estados/territorios).")

    # Inicializar base de datos SQLite con PRAGMAs y tablas
    if fase in ["todas", "carga"]:
        cargador.inicializar_sqlite(df_demo)

    # Procesar bloques en streaming
    print("\n--- FASE 2 y 3: STREAMING (EXTRACCIÓN -> TRANSFORMACIÓN -> CARGA) ---")
    bloques_generador = extractor.iterar_bloques_accidentes(tamano_bloque=chunk_size)

    for num_bloque, chunk_crudo in bloques_generador:
        t_b0 = time.time()

        # Transformación del bloque
        chunk_limpio = transformador.transformar_bloque(chunk_crudo)

        # Carga en Parquet y SQLite
        if fase in ["todas", "carga"]:
            cargador.cargar_bloque(chunk_limpio)

        print(f"  [Bloque {num_bloque:02d}] Procesadas {len(chunk_limpio):,} filas "
              f"({time.time() - t_b0:.2f}s) | Acumulado: {transformador.metricas['total_filas_transformadas']:,}")

    # Cerrar escritor Parquet y construir índices SQLite
    if fase in ["todas", "carga"]:
        print("\n--- FASE 3 (FINAL): INDEXACIÓN ANALÍTICA ---")
        cargador.cerrar_y_crear_indices()

    # Consolidar métricas de auditoría
    t_total = round(time.time() - t_inicio, 2)
    metricas = {
        **extractor.metricas,
        **transformador.metricas,
        "filas_cargadas": cargador.total_rows_loaded,
        "tiempo_total_segundos": t_total,
    }
    cargador.guardar_auditoria(metricas)

    # Exportar el CSV limpio final
    if fase == "todas":
        print("\n--- GENERACIÓN DE CSV LIMPIO FINAL ---")
        cargador.exportar_csv_limpio_desde_parquet()

    print("\n" + "=" * 80)
    print(f"🎉 PIPELINE ETL FINALIZADO CON ÉXITO EN {t_total} SEGUNDOS")
    print(f"  * Total registros procesados: {metricas['total_filas_transformadas']:,}")
    print(f"  * Parquet limpio:             {cargador.parquet_out}")
    print(f"  * Base de datos SQLite:       {cargador.sqlite_out}")
    print(f"  * CSV Limpio Final:           {cargador.csv_out}")
    print(f"  * Muestra 10k CSV:            {cargador.csv_sample_out}")
    print(f"  * Reporte de Auditoría:       {cargador.audit_json}")
    print("=" * 80)


def ejecutar_pipeline_pyspark():
    from extraccion.extractor_pyspark import crear_spark_session, extraer_datos_spark
    from transformacion.transformador_pyspark import transformar_y_enriquecer_spark

    print("=" * 80)
    print("🚀 INICIANDO PIPELINE ETL DISTRIBUIDO (Motor: Apache PySpark)")
    print("=" * 80)
    t0 = time.time()
    spark = crear_spark_session()

    print("\n--- 1. Extracción PySpark con Esquema Tipado ---")
    df_raw, df_demo = extraer_datos_spark(spark)

    print("\n--- 2. Transformación y Broadcast Join en PySpark ---")
    df_enriched = transformar_y_enriquecer_spark(df_raw, df_demo)
    df_enriched.createOrReplaceTempView("accidents_enriched")

    print("\n--- 3. Verificación de Carga y Esquema ---")
    print(f"[OK] Total columnas enriquecidas: {len(df_enriched.columns)}")
    resumen = spark.sql("""
        SELECT
            COUNT(*) AS total_accidentes,
            COUNT(DISTINCT State) AS estados,
            ROUND(AVG(Severity), 3) AS severidad_media
        FROM accidents_enriched
    """)
    resumen.show()

    spark.stop()
    print(f"\n✅ Pipeline PySpark finalizado en {time.time() - t0:.2f} segundos.")


def main():
    args = parse_args()
    if args.engine == "pyspark":
        ejecutar_pipeline_pyspark()
    else:
        ejecutar_pipeline_python(fase=args.fase, chunk_size=args.chunk_size, pregunta=args.pregunta)


if __name__ == "__main__":
    main()
