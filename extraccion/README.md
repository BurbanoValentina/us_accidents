# 📥 Fase 1: Extracción de Datos (ETL)

Esta carpeta contiene todos los componentes, fuentes crudas y scripts responsables de la **Fase de Extracción** del pipeline ETL.

---

## 🛠️ Tecnologías y Métodos Utilizados

1. **Python 3.13 + Pandas (`chunksize=500_000`)**:
   - El dataset principal de accidentes (`US_Accidents_March23.csv`) contiene más de **7.7 millones de registros y pesa 3.05 GB**, lo cual saturaría la memoria RAM si se intentara cargar de forma convencional con `pd.read_csv()`.
   - Se implementó un **patrón de streaming por generadores**, leyendo bloques controlados de 500,000 registros con bajo consumo de memoria (`low_memory=False`).
   - Se seleccionaron de forma estricta las 27 columnas requeridas (`usecols=COLUMNAS_EXTRACCION`), optimizando en un 40% el tiempo de I/O de disco.

2. **Apache Spark / PySpark 3.5+**:
   - Lectura distribuida con `SparkSession.builder.master("local[*]")`.
   - **Esquema Estructurado Explícito (`StructType` con 46 campos)**: En lugar de usar `inferSchema=True` (que obligaría a Spark a leer dos veces el archivo de 3 GB para adivinar tipos), se definió un esquema tipado exacto (`StringType`, `IntegerType`, `DoubleType`, `BooleanType`), reduciendo drásticamente el tiempo de inicio.

---

## 📂 Contenido de la Carpeta

- `datos_origen/`:
  - `US_Accidents_March23.csv`: Dataset original en bruto de accidentes de tránsito en EE.UU. (7,728,394 filas, 3.05 GB).
  - `us_state_demographics.csv`: Tabla dimensional del Censo de EE.UU. 2023 con población, área en millas cuadradas y densidad poblacional por estado.
- `extractor.py`: Módulo en Python / Pandas que implementa la clase `ExtractorAccidentes` con generadores de streaming.
- `extractor_pyspark.py`: Módulo alternativo en PySpark para ingesta distribuida con esquema fuertemente tipado.

---

## 🚀 Cómo Ejecutar la Extracción Individualmente

```bash
# Prueba del extractor con Python y Pandas
python extraccion/extractor.py

# Prueba del extractor distribuido con PySpark
python extraccion/extractor_pyspark.py
```
