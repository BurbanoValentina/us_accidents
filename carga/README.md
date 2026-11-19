# 📤 Fase 3: Carga Analítica, Indexación y Almacenamiento (ETL)

Esta carpeta contiene todos los componentes responsables de la **Fase de Carga** del pipeline ETL, incluyendo bases de datos, almacenamiento columnar, scripts DDL e índices.

---

## 🛠️ Tecnologías y Métodos Utilizados

1. **Almacenamiento Columnar en Apache Parquet (`pyarrow.parquet`)**:
   - Destino: `carga/almacenamiento_parquet/us_accidents_clean.parquet`.
   - **Compresión Snappy**: El dataset crudo de 3.05 GB se redujo a solo **~374 MB** (reducción del 88% en tamaño de disco), manteniendo fidelidad total y lectura columnar ultrarrápida.
   - Escritura por *Row Groups* de 500,000 registros con `pq.ParquetWriter`.

2. **Base de Datos Relacional SQLite 3 (`carga/base_datos/us_accidents.db`)**:
   - Destino: `carga/base_datos/us_accidents.db` (~3.16 GB con índices).
   - **Arquitectura Dimensional en Estrella**:
     - Tabla dimensional: `dim_demographics` (clave primaria: `state`).
     - Tabla de hechos: `accidents` (7,728,394 registros con 40 campos).
   - **Tuning de Rendimiento en Inserción**:
     - `PRAGMA synchronous = OFF`: Deshabilita fsync por cada escritura.
     - `PRAGMA journal_mode = MEMORY`: Bitácora en memoria RAM.
     - `PRAGMA cache_size = -256000`: Buffer de caché de 256 MB.
     - Inserciones en bloque con `executemany()` dentro de una sola transacción `BEGIN ... COMMIT` por chunk de 500k registros.

3. **Estrategia de Indexación B-Tree**:
   - Creación diferida post-carga (se cargan todos los datos primero y luego se generan los índices de una sola vez, lo que es hasta 10 veces más rápido que indexar durante la inserción).
   - 8 índices especializados para consultas analíticas instantáneas:
     - `idx_acc_state` (agrupaciones geográficas)
     - `idx_acc_severity` (filtros por gravedad)
     - `idx_acc_weather` (análisis meteorológico)
     - `idx_acc_ym` (tendencias temporales año/mes)
     - `idx_acc_hour` (patrón horario)
     - `idx_acc_day` (patrón semanal)
     - `idx_acc_road` (análisis de infraestructura vial)
     - `idx_acc_veh` (análisis de tipo de vehículo)

4. **Auditoría Automatizada**:
   - Destino: `carga/auditoria/00_etl_audit.json` y `carga/auditoria/00_etl_audit.csv`.
   - Registro automático de: filas crudas leídas, filas limpias generadas, duplicados eliminados, marcas temporales reparadas, valores atípicos y tiempos de ejecución.

---

## 📂 Contenido de la Carpeta

- `almacenamiento_parquet/`:
  - `us_accidents_clean.parquet`: Archivo columnar optimizado con los 7.7M de registros limpios.
- `base_datos/`:
  - `us_accidents.db`: Base de datos SQLite relacional lista para queries SQL analíticas.
- `sql/`:
  - `esquema_sqlite.sql`: DDL completo de creación de tablas e índices.
- `auditoria/`:
  - `00_etl_audit.json`: Resumen de métricas de calidad en formato JSON.
  - `00_etl_audit.csv`: Resumen tabular de auditoría.
- `cargador.py`: Módulo en Python que implementa la clase `CargadorAlmacenamiento`.
