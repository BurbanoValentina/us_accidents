# 🔄 Fase 2: Transformación, Limpieza y Enriquecimiento (ETL)

Esta carpeta contiene todos los módulos y algoritmos responsables de la **Fase de Transformación** de los datos de accidentes de tránsito en EE.UU.

---

## 🛠️ Tecnologías y Métodos Utilizados

1. **Python 3.13 + Pandas 2.2+**:
   - Deduplicación global incremental por `ID` utilizando un conjunto de hash (`set()`) en memoria para garantizar unicidad a lo largo de todos los chunks.
   - Vectorización de operaciones numéricas y lógicas para máximo rendimiento.

2. **Apache PyArrow 18+ (Motor RE2 compilado en C++)**:
   - `pyarrow.compute.match_substring_regex`: Procesamiento ultra-rápido de expresiones regulares directamente sobre buffers de memoria C++, superando en más de 20x la velocidad del módulo `re` estándar de Python.
   - Clasificación semántica de más de 100 condiciones climáticas crudas en 6 categorías canónicas en español (`Despejado`, `Nublado`, `Lluvia`, `Niebla`, `Nieve/Hielo`, `Otro`).
   - Categorización jerárquica de tipos de vía en base al nombre de calle (`Autopista / Interstate`, `Carretera / Highway`, `Avenida / Boulevard`, `Calle / Vía Urbana`, `Otra Vía`).
   - Minería de texto / NLP sobre el campo `Description` para clasificar 7 tipos de vehículos, incorporando filtros negativos para descartar falsos positivos toponímicos (por ejemplo: la línea de autobús o autopista `"I-80 Bus"`, avenidas como `"Van Ness Ave"` o `"Van Buren St"` que no corresponden a camionetas/vans).

3. **NumPy (`np.select`)**:
   - Asignación condicional multivariable vectorizada para franjas horarias y variables derivadas, evitando bucles iterativos `for` o `apply()` lentos.

4. **Apache Spark / PySpark**:
   - Transformaciones nativas distribuidas con `pyspark.sql.functions` (`F.when`, `F.regexp_extract`, `F.to_timestamp`).
   - **Broadcast Join**: Como la tabla demográfica de 51 estados es pequeña (2 KB), se utiliza `F.broadcast(df_demo)` para enviarla a todos los nodos de trabajo, evitando costosos *shuffles* por la red.

---

## 🧼 Reglas de Limpieza y Derivaciones de Negocio

| Variable Derivada | Regla de Negocio / Transformación Aplicada | Propósito Analítico |
|---|---|---|
| `start_time` / `end_time` | Parseo estricto ISO 8601 truncando a los primeros 19 caracteres para corregir 743,166 registros con nanosegundos (`.000000000`). | Estandarización temporal uniforme. |
| `duration_raw_min` | `(end_ts - start_ts)` en minutos. Detección y corrección de marcas negativas. | Métrica de duración real del bloqueo vial. |
| `duration_clean_min` | Truncamiento de *outliers* extremos mayores a 24 horas (1,440 min) identificados como incidencias de registro administrativo. | Evitar distorsión de promedios en análisis. |
| `time_slot` | División en 5 franjas: Madrugada (00-05h), Pico Mañana (06-09h), Mediodía (10-14h), Pico Tarde (15-19h) y Noche (20-23h). | Análisis de congestión urbana. |
| `weather_group` | Expresiones regulares RE2 agrupando condiciones atmosféricas en español. | Cruce de severidad vs meteorología. |
| `road_type` | Expresiones regulares RE2 identificando autopistas interestatales, rutas estatales, bulevares y calles locales. | Identificación de infraestructura crítica. |
| `vehicle_type` | Extracción NLP RE2 desde `Description` filtrando falsos positivos viales. | Tipo de vehículo involucrado. |
| `is_weekend` | Flag booleano (1 si es Sábado o Domingo, 0 día de semana). | Comparación laboral vs fin de semana. |

---

## 🚀 Cómo Ejecutar la Transformación Individualmente

```bash
# Probar el transformador con datos simulados
python transformacion/transformador.py
```
