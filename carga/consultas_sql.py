"""
Módulo de Consultas SQL Analíticas (Proyecto 3: US Accidents)
============================================================
Responde a los 10 requerimientos analíticos del proyecto ejecutando
consultas SQL sobre la base de datos relacional (carga/base_datos/us_accidents.db).

Tablas:
  - accidents: Tabla de hechos enriquecida (7,728,394 registros)
  - dim_demographics: Dimensión demográfica Censo EE.UU. 2023 (51 estados)
"""

import os
import sqlite3
import time

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "carga", "base_datos", "us_accidents.db")


def formatear_tabla(columnas, filas):
    """Genera una tabla visual en texto con formato limpio."""
    if not filas:
        return "(Sin resultados)"
    
    # Calcular anchos de columna
    anchos = [len(str(c)) for c in columnas]
    for fila in filas:
        for idx, valor in enumerate(fila):
            val_str = f"{valor:,}" if isinstance(valor, int) else (f"{valor:.2f}" if isinstance(valor, float) else str(valor))
            if len(val_str) > anchos[idx]:
                anchos[idx] = len(val_str)
    
    # Encabezado
    sep = "+" + "+".join(["-" * (w + 2) for w in anchos]) + "+"
    cabecera = "|" + "|".join([f" {str(col).center(anchos[i])} " for i, col in enumerate(columnas)]) + "|"
    lineas = [sep, cabecera, sep]
    
    # Filas
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


def responder_10_preguntas(db_path=DB_PATH, filtro_pregunta=None):
    """Ejecuta y responde las 10 preguntas analíticas mediante consultas SQL."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Base de datos no encontrada en: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA cache_size = -256000")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA mmap_size = 30000000000")
    cur = conn.cursor()

    preguntas = [
        {
            "num": 1,
            "titulo": "Frecuencia de accidentes por estado y ciudad (+ tasa demográfica x 100k hab)",
            "sql": """
                WITH estado_agg AS (
                    SELECT 
                        state, 
                        COUNT(*) AS total_accidentes,
                        ROUND(AVG(severity), 3) AS severidad_media
                    FROM accidents
                    GROUP BY state
                )
                SELECT 
                    ea.state AS Estado,
                    d.state_name AS Nombre_Estado,
                    d.region AS Region,
                    d.population_2023 AS Poblacion_2023,
                    ea.total_accidentes AS Total_Accidentes,
                    ROUND(ea.total_accidentes * 100.0 / 7728394, 2) AS Pct_Nacional,
                    ROUND(ea.total_accidentes * 100000.0 / d.population_2023, 2) AS Tasa_x_100k_Hab,
                    ea.severidad_media AS Severidad_Promedio
                FROM estado_agg ea
                LEFT JOIN dim_demographics d ON ea.state = d.state
                ORDER BY ea.total_accidentes DESC
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
            """
        },
        {
            "num": 2,
            "titulo": "Hora del día con mayor accidentalidad (Patrón Horario y Franjas)",
            "sql": """
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
            """
        },
        {
            "num": 3,
            "titulo": "Análisis por severidad del accidente (Distribución y duración)",
            "sql": """
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
            """
        },
        {
            "num": 4,
            "titulo": "Relación con condiciones climáticas",
            "sql": """
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
            """
        },
        {
            "num": 5,
            "titulo": "Tipos de vía más peligrosos (Jerarquía Vial y Top Vías Críticas)",
            "sql": """
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
            """
        },
        {
            "num": 6,
            "titulo": "Días de la semana con más incidentes",
            "sql": """
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
            """
        },
        {
            "num": 7,
            "titulo": "Promedio de duración del incidente (Bruta vs Depurada <= 24h)",
            "sql": """
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
            """
        },
        {
            "num": 8,
            "titulo": "Tendencias mensuales y anuales (Serie Histórica y Estacionalidad)",
            "sql": """
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
            """
        },
        {
            "num": 9,
            "titulo": "Accidentes por tipo de vehículo involucrado (Minería de Texto / NLP)",
            "sql": """
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
            """
        },
        {
            "num": 10,
            "titulo": "Distribución geoespacial de puntos críticos (Hotspots y Elementos Viales)",
            "sql": """
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
            """
        }
    ]

    print("=" * 85)
    print("🎯 PROYECTO 3: RESPUESTAS ANALÍTICAS CON CONSULTAS SQL EN PYTHON")
    print("   Base de Datos Relacional: carga/base_datos/us_accidents.db")
    print("=" * 85)

    resultados_dict = {}

    for item in preguntas:
        p_num = item["num"]
        if filtro_pregunta is not None and filtro_pregunta != p_num:
            continue

        print(f"\n{'='*85}")
        print(f"📌 REQUERIMIENTO {p_num}: {item['titulo']}")
        print(f"{'='*85}")
        
        t0 = time.time()
        cur.execute(item["sql"])
        cols = [d[0] for d in cur.description]
        filas = cur.fetchall()
        t_elap = time.time() - t0
        print(f"Consulta SQL principal ejecutada en {t_elap:.2f} segundos:")
        print(formatear_tabla(cols, filas))

        resultados_dict[f"p{p_num}_principal"] = (cols, filas)

        # Si hay subconsultas complementarias
        for extra_key in ["sql_ciudades", "sql_top_calles", "sql_mes", "sql_infra"]:
            if extra_key in item:
                t0_sub = time.time()
                cur.execute(item[extra_key])
                sub_cols = [d[0] for d in cur.description]
                sub_filas = cur.fetchall()
                print(f"\n  Detalle complementario ({extra_key}) [{time.time() - t0_sub:.2f}s]:")
                print(formatear_tabla(sub_cols, sub_filas))
                resultados_dict[f"p{p_num}_{extra_key}"] = (sub_cols, sub_filas)

    conn.close()
    print(f"\n{'='*85}")
    print("✅ Todas las consultas SQL analíticas han sido resueltas exitosamente.")
    print(f"{'='*85}\n")
    return resultados_dict


if __name__ == "__main__":
    responder_10_preguntas()
