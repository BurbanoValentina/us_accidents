"""
==============================================================================
PROYECTO 3: ANÁLISIS DE ACCIDENTES DE TRÁNSITO EN ZONAS URBANAS
ORQUESTADOR DEL PIPELINE ETL Y CONSULTAS SQL ANALÍTICAS
==============================================================================
Estructura lógica del archivo:
  1. FUNCIONES Y EJECUCIÓN DEL PIPELINE ETL (Extracción -> Transformación -> Carga).
  2. CONSULTAS SQL ANALÍTICAS Y RESPUESTAS A LAS 10 PREGUNTAS DEL PROYECTO.
  3. FUNCIÓN PRINCIPAL / ENTRADA CLI (main).

Uso:
  python ejecutar_etl.py                     # Ejecuta y responde las 10 preguntas con consultas SQL
  python ejecutar_etl.py --pregunta 1        # Responde una pregunta analítica específica (del 1 al 10)
  python ejecutar_etl.py --modo etl          # Reejecuta el pipeline ETL completo desde los datos crudos
  python ejecutar_etl.py --modo csv          # Exporta el CSV limpio final desde Parquet
  python ejecutar_etl.py --engine pyspark    # Ejecuta el pipeline distribuido con Apache PySpark
==============================================================================
"""

import argparse
import os
import sqlite3
import sys
import time

# Configuración de rutas base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DB_PATH = os.path.join(BASE_DIR, "carga", "base_datos", "us_accidents.db")


# ==============================================================================
# BLOQUE 1: FUNCIONES Y ORQUESTACIÓN DEL PIPELINE ETL
# (Extracción -> Transformación -> Carga en Parquet / SQLite / CSV)
# ==============================================================================

def ejecutar_pipeline_etl(chunk_size=500_000):
    """
    Ejecuta el ciclo de vida completo del ETL:
      - Fase 1: Extracción en streaming de los datos crudos (3.05 GB) y demografía.
      - Fase 2: Transformación, limpieza de timestamps, deduplicación y derivaciones NLP.
      - Fase 3: Carga incremental en Parquet y base relacional SQLite + 8 índices B-Tree.
      - Exportación del CSV limpio final.
    """
    from extraccion.extractor import ExtractorAccidentes
    from transformacion.transformador import TransformadorAccidentes
    from carga.cargador import CargadorAlmacenamiento

    t_inicio = time.time()
    print("=" * 90)
    print("🚀 EJECUTANDO PIPELINE ETL COMPLETO (Extracción -> Transformación -> Carga)")
    print("=" * 90)

    extractor = ExtractorAccidentes()
    transformador = TransformadorAccidentes()
    cargador = CargadorAlmacenamiento()

    # 1. Extracción y Streaming
    print("\n--- FASE 1 y 2: EXTRACCIÓN Y STREAMING DESDE KAGGLE ---")
    cargador.inicializar_sqlite()
    bloques = extractor.iterar_bloques_accidentes(tamano_bloque=chunk_size)

    for num_bloque, chunk_crudo in bloques:
        t_b0 = time.time()
        chunk_limpio = transformador.transformar_bloque(chunk_crudo)
        cargador.cargar_bloque(chunk_limpio)
        print(f"  [Bloque {num_bloque:02d}] Procesadas {len(chunk_limpio):,} filas "
              f"({time.time() - t_b0:.2f}s) | Acumulado: {transformador.metricas['total_filas_transformadas']:,}")

    # 2. Indexación Analítica en SQLite
    print("\n--- FASE 3 (FINAL): INDEXACIÓN ANALÍTICA B-TREE ---")
    cargador.cerrar_y_crear_indices()

    # 4. Auditoría y Métricas
    t_total = round(time.time() - t_inicio, 2)
    metricas = {
        **extractor.metricas,
        **transformador.metricas,
        "filas_cargadas": cargador.total_rows_loaded,
        "tiempo_total_segundos": t_total,
    }
    cargador.guardar_auditoria(metricas)

    # 5. Generación del CSV Limpio Final
    print("\n--- GENERACIÓN DE CSV LIMPIO FINAL ---")
    cargador.exportar_csv_limpio_desde_parquet()

    print("\n" + "=" * 90)
    print(f"🎉 PIPELINE ETL FINALIZADO CON ÉXITO EN {t_total} SEGUNDOS")
    print(f"  * Total registros limpios: {metricas['total_filas_transformadas']:,}")
    print(f"  * Parquet limpio:          {cargador.parquet_out}")
    print(f"  * Base de datos SQLite:    {cargador.sqlite_out}")
    print(f"  * CSV Limpio Final:        {cargador.csv_out}")
    print("=" * 90)


def ejecutar_pipeline_pyspark():
    """Ejecuta el pipeline distribuido equivalente utilizando Apache PySpark y Spark SQL."""
    from extraccion.extractor import ExtractorAccidentes
    from transformacion.transformador import transformar_spark
    from pyspark.sql import SparkSession

    print("=" * 90)
    print("🚀 INICIANDO PIPELINE ETL DISTRIBUIDO (Motor: Apache PySpark)")
    print("=" * 90)
    t0 = time.time()
    spark = (
        SparkSession.builder
        .appName("ETL_Distribuido_US_Accidents")
        .master("local[*]")
        .config("spark.driver.memory", "4g")
        .config("spark.sql.shuffle.partitions", "16")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    print("\n--- 1. Extracción PySpark desde URL de Kaggle ---")
    extractor = ExtractorAccidentes()
    df_raw = extractor.extraer_spark(spark)

    print("\n--- 2. Transformación en PySpark ---")
    df_clean = transformar_spark(df_raw)
    df_clean.createOrReplaceTempView("accidents")

    print("\n--- 3. Verificación de Carga y Esquema ---")
    resumen = spark.sql("""
        SELECT 
            COUNT(*) AS total_accidentes, 
            COUNT(DISTINCT State) AS estados, 
            ROUND(AVG(Severity), 3) AS severidad_media
        FROM accidents
    """)
    resumen.show()

    spark.stop()
    print(f"\n✅ Pipeline PySpark finalizado en {time.time() - t0:.2f} segundos.")


def exportar_solo_csv():
    """Exporta de forma independiente el CSV limpio final desde el archivo Parquet procesado."""
    from carga.cargador import CargadorAlmacenamiento
    print("\n=== GENERACIÓN EXCLUSIVA DE CSV LIMPIO FINAL ===")
    c = CargadorAlmacenamiento()
    c.exportar_csv_limpio_desde_parquet()


# ==============================================================================
# BLOQUE 2: FORMATEADOR Y MOTOR DE CONSULTAS SQL ANALÍTICAS (10 PREGUNTAS)
# ==============================================================================

def formatear_tabla(columnas, filas):
    """Genera una tabla visual limpia en texto con alineación de tipos."""
    if not filas:
        return "(Sin resultados)"
    anchos = [len(str(c)) for c in columnas]
    for fila in filas:
        for idx, valor in enumerate(fila):
            val_str = f"{valor:,}" if isinstance(valor, int) else (f"{valor:.2f}" if isinstance(valor, float) else str(valor))
            if len(val_str) > anchos[idx]:
                anchos[idx] = len(val_str)
    sep = "+" + "+".join(["-" * (w + 2) for w in anchos]) + "+"
    cabecera = "|" + "|".join([f" {str(col).center(anchos[i])} " for i, col in enumerate(columnas)]) + "|"
    lineas = [sep, cabecera, sep]
    for fila in filas:
        fila_str = []
        for i, val in enumerate(fila):
            if isinstance(val, (int, float)):
                v_repr = f"{val:,}" if isinstance(val, int) else f"{val:.2f}"
                fila_str.append(f" {v_repr.rjust(anchos[i])} ")
            else:
                fila_str.append(f" {str(val).ljust(anchos[i])} ")
        lineas.append("|" + "|".join(fila_str) + "|")
    lineas.append(sep)
    return "\n".join(lineas)


# Catálogo completo de las 10 Preguntas y Consultas SQL Analíticas
CONSULTAS_ANALITICAS = [
    {
        "num": 1,
        "titulo": "Frecuencia de accidentes por estado y ciudad",
        "descripcion": "¿Cuáles son los estados y ciudades con mayor accidentalidad absoluta y severidad promedio?",
        "sql_principal": """
SELECT 
    state AS Estado,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Nacional,
    ROUND(AVG(severity), 3) AS Severidad_Promedio
FROM accidents
GROUP BY state
ORDER BY Total_Accidentes DESC
LIMIT 10;
        """,
        "sql_ciudades": """
SELECT 
    city AS Ciudad,
    state AS Estado,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Nacional,
    ROUND(AVG(severity), 3) AS Severidad_Promedio
FROM accidents
WHERE city != 'Sin dato' AND city != ''
GROUP BY city, state
ORDER BY Total_Accidentes DESC
LIMIT 10;
        """,
        "conclusion": "California (1.74M, 22.53%) y Florida (880K, 11.39%) lideran ampliamente la accidentalidad vial a nivel nacional, seguidos por Texas (582K, 7.54%). En cuanto a ciudades urbanas, Miami, FL (186,768) y Houston, TX (169,428) encabezan la siniestralidad."
    },
    {
        "num": 2,
        "titulo": "Hora del día con mayor accidentalidad (Patrón Horario y Franjas)",
        "descripcion": "¿En qué horas del día y franjas horarias ocurren más accidentes?",
        "sql_principal": """
SELECT 
    hour AS Hora_24h,
    time_slot AS Franja_Horaria,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Nacional,
    ROUND(AVG(severity), 3) AS Severidad_Promedio
FROM accidents
WHERE hour IS NOT NULL AND hour >= 0
GROUP BY hour, time_slot
ORDER BY Total_Accidentes DESC;
        """,
        "conclusion": "Patrón bimodal laboral claro: las horas críticas son las 07:00h (587,472, 7.6%) y 16:00h–17:00h (1.15M, ~15%), coincidiendo con la entrada y salida laboral. La madrugada (00-05h) concentra menor volumen pero mayor severidad relativa."
    },
    {
        "num": 3,
        "titulo": "Análisis por severidad del accidente (Distribución y duración)",
        "descripcion": "¿Cómo se distribuyen los niveles de gravedad y qué impacto vial generan?",
        "sql_principal": """
SELECT 
    severity AS Nivel_Severidad,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Total,
    ROUND(AVG(duration_clean_min), 2) AS Duracion_Media_Min,
    ROUND(AVG(distance_mi), 3) AS Distancia_Media_Mi,
    ROUND(AVG(visibility_mi), 2) AS Visibilidad_Media_Mi
FROM accidents
WHERE severity IS NOT NULL
GROUP BY severity
ORDER BY severity ASC;
        """,
        "conclusion": "El 79.67% de los incidentes son de Severidad 2 (moderados). Sin embargo, los eventos de Severidad 4 (críticos, 2.65%) generan un cierre vial promedio de más de 3 horas (185.9 min) y afectan 1.5 millas de calzada."
    },
    {
        "num": 4,
        "titulo": "Relación con condiciones climáticas",
        "descripcion": "¿Cómo influyen los grupos meteorológicos en la frecuencia y severidad?",
        "sql_principal": """
SELECT 
    weather_group AS Categoria_Clima,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Total,
    ROUND(AVG(severity), 3) AS Severidad_Promedio,
    SUM(CASE WHEN severity >= 3 THEN 1 ELSE 0 END) AS Accidentes_Graves_S3_S4,
    ROUND(SUM(CASE WHEN severity >= 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Pct_Graves,
    ROUND(AVG(temperature_f), 1) AS Temp_Prom_F,
    ROUND(AVG(visibility_mi), 2) AS Visibilidad_Prom_Mi
FROM accidents
GROUP BY weather_group
ORDER BY Total_Accidentes DESC;
        """,
        "conclusion": "Despejado (44.1%) y Nublado (40.9%) dominan en volumen por exposición al tráfico. No obstante, la Lluvia dispara la tasa de siniestros graves al 22.76% (severidad 2.25), mientras la Nieve/Hielo y Niebla reducen la visibilidad por debajo de 3 millas."
    },
    {
        "num": 5,
        "titulo": "Tipos de vía más peligrosos (Jerarquía Vial y Vías Críticas)",
        "descripcion": "¿Qué tipos de infraestructura vial presentan mayor peligrosidad y volumen de accidentes graves?",
        "sql_principal": """
SELECT 
    road_type AS Tipo_Via,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Total,
    ROUND(AVG(severity), 3) AS Severidad_Promedio,
    SUM(CASE WHEN severity >= 3 THEN 1 ELSE 0 END) AS Incidentes_Graves,
    ROUND(SUM(CASE WHEN severity >= 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Pct_Graves,
    ROUND(AVG(duration_clean_min), 2) AS Duracion_Promedio_Min
FROM accidents
GROUP BY road_type
ORDER BY Total_Accidentes DESC;
        """,
        "sql_top_calles": """
SELECT 
    street AS Nombre_Via,
    COUNT(*) AS Total_Accidentes,
    ROUND(AVG(severity), 3) AS Severidad_Promedio
FROM accidents
WHERE street != 'Sin dato' AND street != ''
GROUP BY street
ORDER BY Total_Accidentes DESC
LIMIT 5;
        """,
        "conclusion": "Las Autopistas / Interstates son las vías más peligrosas: concentran el 34.3% del total, la mayor severidad (2.34) y un tercio de todos los siniestros graves nacionales (32.44% en S3-S4). Las vías con mayor volumen individual son la I-95 N (78,430) y la I-95 S (74,528)."
    },
    {
        "num": 6,
        "titulo": "Días de la semana con más incidentes",
        "descripcion": "¿Qué días de la semana registran mayor concentración de siniestros y cómo varía la gravedad?",
        "sql_principal": """
SELECT 
    day_of_week_num AS Num_Dia,
    day_name AS Dia_Semana,
    CASE WHEN is_weekend = 1 THEN 'Fin de semana' ELSE 'Laboral' END AS Tipo_Dia,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Total,
    ROUND(AVG(severity), 3) AS Severidad_Promedio,
    ROUND(AVG(duration_clean_min), 2) AS Duracion_Promedio_Min
FROM accidents
WHERE day_of_week_num IS NOT NULL
GROUP BY day_of_week_num, day_name, is_weekend
ORDER BY Total_Accidentes DESC;
        """,
        "conclusion": "El Viernes es el día con más accidentes (1.37M, 17.68%). En el fin de semana el volumen cae a casi la mitad, pero la severidad promedio aumenta notablemente (Domingo con severidad 2.26 y Sábado con duración media de 116 min)."
    },
    {
        "num": 7,
        "titulo": "Promedio de duración del incidente (Bruta vs Depurada <= 24h)",
        "descripcion": "¿Cuál es la duración promedio real del incidente y cuál es el impacto de los valores atípicos?",
        "sql_principal": """
SELECT 
    severity AS Nivel_Severidad,
    COUNT(*) AS Total_Accidentes,
    ROUND(AVG(duration_raw_min), 2) AS Duracion_Bruta_Prom_Min,
    ROUND(AVG(duration_clean_min), 2) AS Duracion_Depurada_Prom_Min,
    SUM(CASE WHEN duration_raw_min > 1440 THEN 1 ELSE 0 END) AS Outliers_gt_24h,
    ROUND(SUM(CASE WHEN duration_raw_min > 1440 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Pct_Outliers
FROM accidents
GROUP BY severity
ORDER BY severity ASC;
        """,
        "conclusion": "La duración bruta global es de 444.4 min (~7.4h) debido a 34,981 eventos atípicos mayores a 24 horas producto de cierres administrativos prolongados. Depurando estos outliers, la duración media real es de 108.0 min (45.7 min en Severidad 1 vs 185.9 min en Severidad 4)."
    },
    {
        "num": 8,
        "titulo": "Tendencias mensuales y anuales (Serie Histórica y Estacionalidad)",
        "descripcion": "¿Cómo ha evolucionado la accidentalidad entre 2016 y 2023 y qué meses son más riesgosos?",
        "sql_principal": """
SELECT 
    year AS Anio,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Total,
    ROUND(AVG(severity), 3) AS Severidad_Promedio
FROM accidents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year ASC;
        """,
        "sql_mes": """
SELECT 
    month AS Mes_Num,
    month_name AS Mes,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Total,
    ROUND(AVG(severity), 3) AS Severidad_Promedio
FROM accidents
WHERE month IS NOT NULL
GROUP BY month, month_name
ORDER BY month ASC;
        """,
        "conclusion": "Crecimiento continuo en la captura del registro desde 2016 (410K) hasta el máximo de 2022 (1.76M, 22.8%). Estacionalmente, Diciembre lidera con 847,343 accidentes (10.96%), seguido de Noviembre (9.84%) y Enero (9.73%), coincidiendo con la temporada invernal y festiva."
    },
    {
        "num": 9,
        "titulo": "Accidentes por tipo de vehículo involucrado (Minería de Texto / NLP)",
        "descripcion": "¿Qué tipos de vehículos participan en accidentes y cuál genera mayor gravedad y duración?",
        "sql_principal": """
SELECT 
    vehicle_type AS Tipo_Vehiculo,
    COUNT(*) AS Total_Accidentes,
    ROUND(COUNT(*) * 100.0 / 7728394, 2) AS Pct_Total,
    ROUND(AVG(severity), 3) AS Severidad_Promedio,
    SUM(CASE WHEN severity >= 3 THEN 1 ELSE 0 END) AS Accidentes_Graves,
    ROUND(SUM(CASE WHEN severity >= 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Pct_Graves,
    ROUND(AVG(duration_clean_min), 2) AS Duracion_Prom_Min
FROM accidents
GROUP BY vehicle_type
ORDER BY Total_Accidentes DESC;
        """,
        "conclusion": "El algoritmo NLP identificó 68,252 menciones de vehículos descartando toponimias viales falsas. Los accidentes de Camión / Tráiler registran la mayor severidad (2.52) y duración de despeje (124.95 min), mientras que Automóvil / Multivehículo presenta la mayor tasa de siniestros graves (43.02%)."
    },
    {
        "num": 10,
        "titulo": "Distribución geoespacial de puntos críticos (Hotspots y Elementos Viales)",
        "descripcion": "¿Dónde se concentran los clústeres geográficos de mayor riesgo y qué infraestructura vial está presente?",
        "sql_principal": """
SELECT 
    ROUND(start_lat, 1) AS Lat_Grid,
    ROUND(start_lng, 1) AS Lng_Grid,
    state AS Estado,
    city AS Ciudad_Cercana,
    COUNT(*) AS Total_Accidentes,
    ROUND(AVG(severity), 3) AS Severidad_Promedio
FROM accidents
WHERE start_lat IS NOT NULL AND start_lng IS NOT NULL
GROUP BY Lat_Grid, Lng_Grid
ORDER BY Total_Accidentes DESC
LIMIT 10;
        """,
        "sql_infra": """
SELECT 
    SUM(traffic_signal) AS Con_Semaforo,
    SUM(crossing) AS Cruce_Peatonal,
    SUM(junction) AS Enlace_Autopista,
    SUM(stop) AS Senal_Pare,
    SUM(station) AS Estacion_Transporte,
    SUM(railway) AS Paso_Nivel_Tren
FROM accidents;
        """,
        "conclusion": "Los principales puntos críticos urbanos se concentran en las zonas metropolitanas de Miami, FL (53,220 en Lat 25.9 / Lng -80.2), Los Ángeles, CA (39,838 en Lat 34.0 / Lng -118.2), Charlotte, NC y Dallas, TX. A nivel de infraestructura, más de 1.14M de accidentes ocurren en semáforos y 873K en cruces peatonales."
    }
]


def ejecutar_consultas_sql(pregunta_num=None, db_path=DB_PATH):
    """Ejecuta las consultas SQL analíticas directamente sobre la base de datos de SQLite."""
    if not os.path.exists(db_path):
        print(f"\n[ERROR] No se encontró la base de datos en: {db_path}")
        print("Ejecuta primero: python ejecutar_etl.py --modo etl")
        return

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA cache_size = -256000")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA mmap_size = 30000000000")
    cur = conn.cursor()

    print("=" * 90)
    print("🎯 PROYECTO 3: CONSULTAS SQL Y RESPUESTAS ANALÍTICAS (US ACCIDENTS)")
    print(f"   Base de Datos Relacional: {db_path}")
    print("=" * 90)

    for item in CONSULTAS_ANALITICAS:
        num = item["num"]
        if pregunta_num is not None and pregunta_num != num:
            continue

        print(f"\n{'=' * 90}")
        print(f"📌 REQUERIMIENTO {num}: {item['titulo']}")
        print(f"   Pregunta analítica: {item['descripcion']}")
        print(f"{'=' * 90}")

        # Mostrar el comando SQL principal
        print("\n🔹 CONSULTA SQL PRINCIPAL:")
        print(item["sql_principal"].strip())
        print("-" * 90)

        # Ejecutar y mostrar tabla
        t0 = time.time()
        cur.execute(item["sql_principal"])
        cols = [d[0] for d in cur.description]
        filas = cur.fetchall()
        t_elap = time.time() - t0
        print(f"Resultado ({len(filas)} filas) obtenido en {t_elap:.2f} segundos:")
        print(formatear_tabla(cols, filas))

        # Consultas complementarias si existen
        for k in ["sql_ciudades", "sql_top_calles", "sql_mes", "sql_infra"]:
            if k in item:
                print(f"\n🔹 CONSULTA SQL COMPLEMENTARIA ({k}):")
                print(item[k].strip())
                print("-" * 90)
                t0_sub = time.time()
                cur.execute(item[k])
                sub_cols = [d[0] for d in cur.description]
                sub_filas = cur.fetchall()
                print(f"Resultado complementario ({len(sub_filas)} filas) [{time.time() - t0_sub:.2f}s]:")
                print(formatear_tabla(sub_cols, sub_filas))

        # Conclusión analítica
        print("\n💡 RESPUESTA / CONCLUSIÓN ANALÍTICA:")
        print(f"   {item['conclusion']}")
        print("-" * 90)

    conn.close()
    print("\n" + "=" * 90)
    print("✅ Consultas SQL y respuestas completadas exitosamente.")
    print("=" * 90 + "\n")


# ==============================================================================
# BLOQUE 3: ENTRADA PRINCIPAL Y CONFIGURACIÓN DE ARGUMENTOS CLI
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Proyecto 3: Orquestador ETL y Consultas SQL Analíticas"
    )
    parser.add_argument(
        "--modo",
        choices=["sql", "etl", "csv"],
        default="sql" if os.path.exists(DB_PATH) else "etl",
        help="Modo de ejecución: 'sql' (consultas analíticas), 'etl' (ejecuta el pipeline de datos), 'csv' (exporta el CSV final). Por defecto ejecuta 'sql' si la base ya existe.",
    )
    parser.add_argument(
        "--pregunta",
        type=int,
        choices=range(1, 11),
        default=None,
        help="Número de pregunta específica a responder con SQL (1 al 10)",
    )
    parser.add_argument(
        "--engine",
        choices=["python", "pyspark"],
        default="python",
        help="Motor para el ETL (python con PyArrow o pyspark)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500_000,
        help="Tamaño de bloque en streaming para el ETL (por defecto: 500,000)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.engine == "pyspark":
        ejecutar_pipeline_pyspark()
    elif args.modo == "etl":
        ejecutar_pipeline_etl(chunk_size=args.chunk_size)
    elif args.modo == "csv":
        exportar_solo_csv()
    else:
        # Por defecto corre las consultas SQL y muestra preguntas y respuestas
        ejecutar_consultas_sql(pregunta_num=args.pregunta)


if __name__ == "__main__":
    main()
