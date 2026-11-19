# ⚙️ Pipeline ETL: Análisis de Accidentes de Tránsito en Zonas Urbanas (EE.UU., 2016–2023)

Repositorio exclusivo y especializado en el proceso de **Extracción, Transformación y Carga (ETL)** para el dataset masivo de accidentes viales de Estados Unidos (**7,728,394 registros** de [Kaggle US Accidents](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents)) enriquecido con datos demográficos del **Censo de EE.UU. 2023**.

Todo el frontend, diapositivas, documentos y tableros externos han sido removidos, dejando una **arquitectura de datos limpia, modular y de alto rendimiento**.

---

## 📁 Estructura del Repositorio Organizado

```text
tallerpyspark/
├── 1. extraccion/                       # FASE 1: INGESTA Y EXTRACCIÓN CONTROLADA
│   ├── datos_origen/                    # Fuentes de datos crudas en bruto
│   │   ├── US_Accidents_March23.csv     # Dataset crudo original (7,728,394 filas, 3.05 GB)
│   │   └── us_state_demographics.csv    # Tabla demográfica del Censo EE.UU. 2023
│   ├── extractor.py                     # Extractor en streaming con Pandas (bloques de 500k)
│   ├── extractor_pyspark.py             # Extractor distribuido PySpark con esquema tipado (StructType)
│   └── README.md                        # Documentación técnica de la fase de extracción
│
├── 2. transformacion/                   # FASE 2: LIMPIEZA, DERIVACIÓN Y ENRIQUECIMIENTO
│   ├── transformador.py                 # Lógica de limpieza, regex RE2 C++, NLP y enriquecimiento
│   ├── transformador_pyspark.py         # Transformaciones distribuidas en Spark SQL y Broadcast Join
│   └── README.md                        # Documentación técnica de la fase de transformación
│
├── 3. carga/                            # FASE 3: ALMACENAMIENTO, INDEXACIÓN Y AUDITORÍA
│   ├── almacenamiento_parquet/          # Almacenamiento columnar optimizado
│   │   └── us_accidents_clean.parquet   # Parquet limpio comprimido Snappy (~374 MB)
│   ├── base_datos/                      # Base de datos relacional analítica
│   │   └── us_accidents.db              # SQLite 3 con esquema estrella y 8 índices B-Tree (3.16 GB)
│   ├── sql/                             # Scripts DDL de base de datos
│   │   └── esquema_sqlite.sql           # Definición formal de tablas e índices
│   ├── auditoria/                       # Métricas de ejecución y calidad del dato
│   │   ├── 00_etl_audit.json            # Métricas en JSON (filas, nulos, outliers, tiempos)
│   │   └── 00_etl_audit.csv             # Métricas en formato tabular CSV
│   ├── cargador.py                      # Módulo de carga masiva, indexación y exportación
│   └── README.md                        # Documentación técnica de la fase de carga
│
├── 4. csv_limpio_final/                 # APARTADO EXCLUSIVO: DATASET FINAL DEPURADO EN CSV
│   ├── us_accidents_limpio.csv          # CSV LIMPIO FINAL COMPLETO (7.73M filas, 40 cols, 2.22 GB)
│   ├── us_accidents_limpio_muestra_10k.csv # Muestra rápida de 10,000 filas para Excel / inspección
│   └── README.md                        # Diccionario de datos formal de las 40 columnas
│
├── ejecutar_etl.py                      # Orquestador maestro CLI del pipeline completo
├── requirements.txt                     # Dependencias estrictas del ETL (Pandas, PyArrow, PySpark)
└── .gitignore                           # Exclusión de archivos pesados binarios
```

---

## 🔍 Detalle Técnico por Fase del ETL

### 1. ¿Qué se utilizó para hacer la EXTRACCIÓN?

La fase de extracción resolvió el desafío de ingerir un archivo CSV de **3.05 GB** con **7,728,394 filas** y 46 columnas sin desbordar la memoria RAM.

* **Tecnología Principal:** **Python 3.13 + Pandas (`chunksize=500_000`, `low_memory=False`)**.
  * **Patrón Streaming por Generadores:** En lugar de cargar los 3 GB en memoria de una sola vez, se implementó un generador en `extraccion/extractor.py` que lee bloques controlados de 500,000 registros, manteniendo el uso de memoria RAM por debajo de 1.5 GB en todo momento.
  * **Filtrado Vertical de Columnas (`usecols`):** Se extrajeron exactamente 27 columnas críticas requeridas para el análisis, descartando campos redundantes en la lectura inicial y reduciendo en un 40% el tiempo de I/O de disco.
* **Tecnología Alternativa:** **Apache Spark / PySpark 3.5+ (`extraccion/extractor_pyspark.py`)**.
  * **Esquema Estructurado Explícito (`StructType` con 46 campos):** Se definió un esquema tipado exacto (`StringType`, `IntegerType`, `DoubleType`, `BooleanType`), anulando la necesidad de `inferSchema=True` (el cual requeriría dos pasadas completas sobre los 3 GB de datos crudos).
* **Fuentes Extraídas (`extraccion/datos_origen/`):**
  1. `US_Accidents_March23.csv`: Datos de telemetría de tráfico recopilados de múltiples proveedores (MapQuest, Bing).
  2. `us_state_demographics.csv`: Datos oficiales del Censo de EE.UU. 2023 (población, superficie en millas cuadradas y densidad por estado).

---

### 2. ¿Qué se utilizó para hacer la TRANSFORMACIÓN?

La fase de transformación limpia, estandariza, normaliza tipos y enriquece semánticamente los registros.

* **Tecnologías Utilizadas:**
  * **Apache PyArrow 18+ (`pyarrow.compute` con motor RE2 en C++):** Utilizado para evaluación de expresiones regulares de alta velocidad compiladas en C++. Procesa patrones de texto sobre cientos de miles de filas en milisegundos, superando en más de 20x al motor `re` nativo de Python.
  * **Pandas 2.2+:** Manejo de estructuras tabulares, imputación y transformaciones de series de tiempo.
  * **NumPy (`np.select`):** Vectorización condicional multivariable para categorización en una sola pasada.
  * **PySpark SQL (`pyspark.sql.functions`):** Transformaciones distribuidas nativas y **Broadcast Join** (`F.broadcast(df_demo)`) que distribuye la dimensión demográfica a todos los ejecutores evitando *shuffles* por la red.
* **Transformaciones y Reglas de Negocio Implementadas:**
  1. **Deduplicación Global:** Seguimiento incremental mediante un conjunto hash (`set()`) del identificador único `ID` a través de todos los bloques.
  2. **Estandarización de Fechas y Nanosegundos:** Corrección de **743,166 registros** que contenían precisión sub-segundo con nanosegundos (`.000000000`), normalizándolos a marcas ISO 8601 uniformes (`YYYY-MM-DD HH:MM:SS`).
  3. **Duración y Tratamiento de Outliers:**
     * Cálculo de duración en minutos `(End_Time - Start_Time)`.
     * Detección y tratamiento de marcas negativas (fechas inconsistentes).
     * Detección de **34,981 eventos atípicos** con duraciones superiores a 24 horas (1,440 minutos), creando una columna limpia `duration_clean_min` para evitar sesgar los análisis estadísticos.
  4. **Derivaciones Temporales:** Extracción de año, mes, nombre de mes en español (`Enero` a `Diciembre`), año-mes (`YYYY-MM`), hora (0-23), día de la semana numérico (1=Domingo..7=Sábado), nombre de día en español, indicador de fin de semana (`is_weekend`), y franjas horarias operativas (`Madrugada`, `Pico Mañana`, `Mediodía`, `Pico Tarde`, `Noche`).
  5. **Clasificación Meteorológica Semántica:** Agrupación con PyArrow RE2 de más de 100 condiciones climáticas crudas en 6 categorías estándar en español: `Despejado`, `Nublado`, `Lluvia`, `Niebla`, `Nieve/Hielo` y `Otro`.
  6. **Clasificación de Infraestructura y Vías:** Identificación mediante expresiones regulares RE2 de 5 tipos de vía sobre el nombre de calle: `Autopista / Interstate`, `Carretera / Highway`, `Avenida / Boulevard`, `Calle / Vía Urbana` y `Otra Vía`.
  7. **Minería de Texto / NLP sobre Descripción para Tipo de Vehículo:** Extracción de 7 tipos de vehículos (`Camión / Tráiler`, `Motocicleta`, `Autobús`, `Bicicleta`, `Peatón involucrado`, `SUV / Van / Pickup`, `Automóvil / Multivehículo`), con filtrado estricto de falsos positivos toponímicos (ej. descartando líneas viales como `"I-80 Bus"` o calles como `"Van Ness Ave"`).
  8. **Downcasting y Optimización de Memoria:** Reducción de tipos a enteros pequeños (`int8`, `Int16`), números flotantes de precisión simple (`float32`) y strings limpios.

---

### 3. ¿Qué se utilizó para hacer la CARGA?

La fase de carga vuelca la información transformada en tres destinos de almacenamiento según su caso de uso analítico.

* **Destino 1: Almacenamiento Columnar en Apache Parquet (`carga/almacenamiento_parquet/`)**
  * **Tecnología:** `pyarrow.parquet.ParquetWriter` con compresión **Snappy**.
  * **Ventaja:** El dataset crudo de 3.05 GB se comprimió a solo **374 MB** (reducción del 88% de espacio en disco), optimizado para lectura columnar rápida en motores analíticos (DuckDB, Spark, Polars, Pandas).
* **Destino 2: Base de Datos Relacional SQLite 3 (`carga/base_datos/us_accidents.db`)**
  * **Tecnología:** Motor relacional SQLite 3 con Python `sqlite3`.
  * **Diseño Dimensional:** Esquema en estrella compuesto por `dim_demographics` (dimensión de estados) y `accidents` (tabla de hechos de 7,728,394 filas).
  * **Optimizaciones de Rendimiento:**
    * Inserción por lotes con `executemany()` dentro de transacciones atómicas explícitas (`BEGIN ... COMMIT`).
    * Directivas PRAGMA de alta velocidad: `PRAGMA synchronous = OFF`, `PRAGMA journal_mode = MEMORY`, `PRAGMA temp_store = MEMORY` y memoria caché de 256 MB (`PRAGMA cache_size = -256000`).
  * **Estrategia de Indexación:** Creación diferida de **8 índices B-Tree especializados** tras la inserción de datos:
    * `idx_acc_state` (consultas por Estado)
    * `idx_acc_severity` (consultas por Severidad)
    * `idx_acc_weather` (consultas por Clima)
    * `idx_acc_ym` (consultas por Año y Mes)
    * `idx_acc_hour` (consultas por Hora)
    * `idx_acc_day` (consultas por Día de semana)
    * `idx_acc_road` (consultas por Tipo de vía)
    * `idx_acc_veh` (consultas por Tipo de vehículo)
* **Destino 3: Auditoría y Métricas de Calidad (`carga/auditoria/`)**
  * Exportación automática de `00_etl_audit.json` y `00_etl_audit.csv` con métricas de trazabilidad y auditoría:
    * Total filas crudas: `7,728,394`
    * Total filas limpias cargadas: `7,728,394`
    * Timestamps corregidos con nanosegundos: `743,166`
    * Outliers mayores a 24 horas tratados: `34,981`

---

## 📊 Apartado de CSV Limpio Final (`csv_limpio_final/`)

Ubicado en la carpeta [`csv_limpio_final/`](csv_limpio_final/):

1. **`us_accidents_limpio.csv` (2.22 GB):**
   * Archivo CSV final completo, depurado, con **7,728,394 filas** y **40 columnas** listas para su consumo inmediato en cualquier software analítico.
2. **`us_accidents_limpio_muestra_10k.csv` (3.0 MB):**
   * Muestra representativa de los primeros 10,000 registros limpios, ideal para abrir en Microsoft Excel, Google Sheets o editores de texto livianos sin sobrecargar el equipo.
3. **Diccionario de Datos:**
   * En [`csv_limpio_final/README.md`](csv_limpio_final/README.md) se encuentra la descripción detallada, tipo de dato y valores permitidos para cada una de las 40 columnas.

---

## 🚀 Guía de Ejecución

### 1. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar el Pipeline Completo (Extracción -> Transformación -> Carga)

```bash
# Ejecutar todo el pipeline modular con Python + PyArrow + SQLite
python ejecutar_etl.py
```

### 3. Ejecutar Fases Específicas

```bash
# Exportar únicamente el CSV limpio final desde el archivo Parquet
python ejecutar_etl.py --fase csv

# Probar solo la extracción
python extraccion/extractor.py

# Probar solo la transformación
python transformacion/transformador.py

# Probar el cargador y bases de datos
python carga/cargador.py
```

### 4. Ejecutar con Apache PySpark (Distribuido)

```bash
python ejecutar_etl.py --engine pyspark
```

### 5. Responder las 10 Preguntas Analíticas con Consultas SQL en Python

```bash
# Responder todas las 10 preguntas analíticas ejecutando SQL sobre us_accidents.db
python ejecutar_etl.py --fase sql

# Responder una pregunta analítica específica (ej. pregunta 1, 2, ..., 10)
python ejecutar_etl.py --fase sql --pregunta 1
```
