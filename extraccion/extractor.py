"""
Módulo de Extracción de Datos (ETL - Fase 1)
===========================================
Responsable de la ingesta controlada de datos crudos:
1. Dataset de accidentes de tránsito (US_Accidents_March23.csv) ~3.05 GB.
2. Dataset demográfico de referencia del Censo de EE.UU. 2023 (us_state_demographics.csv).

Tecnologías utilizadas:
- Python 3.13
- Pandas (motor de streaming con chunksize para control estricto de memoria RAM)
- Manejo de esquemas y tipos de datos en streaming
"""

import os
import time
import pandas as pd

# Rutas estándar del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_ACCIDENTS_CSV = os.path.join(BASE_DIR, "extraccion", "datos_origen", "US_Accidents_March23.csv")
RAW_DEMOGRAPHICS_CSV = os.path.join(BASE_DIR, "extraccion", "datos_origen", "us_state_demographics.csv")

# Columnas relevantes seleccionadas para la extracción
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
    """Clase para la extracción por bloques (streaming) de las fuentes de datos."""

    def __init__(self, ruta_accidentes=RAW_ACCIDENTS_CSV, ruta_demografia=RAW_DEMOGRAPHICS_CSV):
        self.ruta_accidentes = ruta_accidentes
        self.ruta_demografia = ruta_demografia
        self.metricas = {
            "total_filas_crudas": 0,
            "nulos_calle": 0,
            "nulos_ciudad": 0,
            "nulos_clima": 0,
            "nulos_temperatura": 0,
            "nulos_visibilidad": 0,
        }

    def cargar_demografia(self) -> pd.DataFrame:
        """Carga la tabla de referencia demográfica del Censo de EE.UU."""
        if not os.path.exists(self.ruta_demografia):
            raise FileNotFoundError(f"Archivo demográfico no encontrado en: {self.ruta_demografia}")
        df_demo = pd.read_csv(self.ruta_demografia)
        return df_demo

    def iterar_bloques_accidentes(self, tamano_bloque=500_000):
        """
        Generador que extrae los datos crudos en streaming por bloques (chunks),
        evitando saturar la memoria RAM con el archivo de 3.05 GB.
        """
        if not os.path.exists(self.ruta_accidentes):
            raise FileNotFoundError(f"Archivo de accidentes no encontrado en: {self.ruta_accidentes}")

        print(f"[EXTRACCIÓN] Iniciando streaming desde: {self.ruta_accidentes}")
        print(f"             Tamaño de bloque: {tamano_bloque:,} filas | Columnas: {len(COLUMNAS_EXTRACCION)}")

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


if __name__ == "__main__":
    t0 = time.time()
    extractor = ExtractorAccidentes()
    print("=== Probando Módulo de Extracción ===")
    demo = extractor.cargar_demografia()
    print(f"[OK] Demografía cargada con éxito: {len(demo)} registros (Estados/Territorios).")

    # Muestra de lectura del primer bloque
    for num_bloque, chunk in extractor.iterar_bloques_accidentes(tamano_bloque=10_000):
        print(f"[OK] Bloque {num_bloque} extraído exitosamente con {len(chunk):,} filas y {len(chunk.columns)} columnas.")
        break
    print(f"[COMPLETADO] Prueba de extracción finalizada en {time.time() - t0:.2f} segundos.")
