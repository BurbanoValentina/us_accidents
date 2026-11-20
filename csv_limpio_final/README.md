# 📊 Apartado de CSV Limpio Final (Dataset Depurado)

Esta carpeta contiene el resultado final depurado, normalizado y enriquecido del proceso ETL sobre el dataset de accidentes de tráfico en Estados Unidos.

---

## 📁 Archivos Disponibles

1. **`us_accidents_limpio.csv`** (~2.22 GB):
   - **Dataset completo final**: Contiene la totalidad de los **7,728,394 registros** y **40 columnas** procesadas, sin registros duplicados y con tipos de datos estandarizados. Listo para consumo analítico.

---

## 📖 Diccionario de Datos (40 Columnas Finales)

| # | Columna | Tipo de Dato | Descripción y Valores Permitidos |
|---|---|---|---|
| 1 | `id` | `VARCHAR(16)` | Identificador alfanumérico único del accidente (ej. `A-1`, `A-7728394`). Clave primaria. |
| 2 | `source` | `VARCHAR(32)` | Fuente original del reporte del incidente (`Source1`, `Source2`, `Source3`). |
| 3 | `severity` | `TINYINT (1-4)` | Nivel de gravedad del accidente: 1 (Menor impacto) a 4 (Cierre vial crítico). |
| 4 | `start_time` | `DATETIME` | Fecha y hora de inicio estandarizada (`YYYY-MM-DD HH:MM:SS`), libre de nanosegundos. |
| 5 | `end_time` | `DATETIME` | Fecha y hora de finalización del evento vial (`YYYY-MM-DD HH:MM:SS`). |
| 6 | `year` | `SMALLINT` | Año de ocurrencia (rango: 2016 a 2023). |
| 7 | `month` | `TINYINT` | Mes numérico de ocurrencia (1 a 12). |
| 8 | `month_name` | `VARCHAR(16)` | Nombre del mes en español (`Enero` a `Diciembre`). |
| 9 | `year_month` | `VARCHAR(7)` | Identificador mensual en formato `YYYY-MM`. |
| 10 | `hour` | `TINYINT` | Hora del día en formato 24 horas (0 a 23). |
| 11 | `day_of_week_num` | `TINYINT` | Día de la semana numérico (1=Domingo, 2=Lunes, ..., 7=Sábado). |
| 12 | `day_name` | `VARCHAR(16)` | Nombre del día de la semana en español (`Lunes` a `Domingo`). |
| 13 | `is_weekend` | `TINYINT (0/1)` | Flag booleano: 1 si es fin de semana (Sábado/Domingo), 0 día laborable. |
| 14 | `time_slot` | `VARCHAR(32)` | Franja horaria: `1. Madrugada`, `2. Pico Mañana`, `3. Mediodía`, `4. Pico Tarde`, `5. Noche`. |
| 15 | `duration_raw_min` | `FLOAT` | Duración bruta calculada en minutos `(end_time - start_time)`. |
| 16 | `duration_clean_min` | `FLOAT` | Duración depurada: nula para valores negativos o atípicos extremos (> 1,440 min / 24h). |
| 17 | `distance_mi` | `FLOAT` | Longitud en millas del tramo de vía afectado por el accidente. |
| 18 | `start_lat` | `FLOAT` | Latitud GPS del punto de inicio del incidente. |
| 19 | `start_lng` | `FLOAT` | Longitud GPS del punto de inicio del incidente. |
| 20 | `street` | `VARCHAR(128)` | Nombre de la calle o tramo de vía donde ocurrió el siniestro. |
| 21 | `road_type` | `VARCHAR(32)` | Clasificación vial: `Autopista / Interstate`, `Carretera / Highway`, `Avenida / Boulevard`, `Calle / Vía Urbana`, `Otra Vía`. |
| 22 | `city` | `VARCHAR(64)` | Ciudad donde se registró el accidente. |
| 23 | `county` | `VARCHAR(64)` | Condado administrativo del incidente. |
| 24 | `state` | `VARCHAR(2)` | Código postal oficial de dos letras del estado de EE.UU. (ej. `CA`, `FL`, `TX`). |
| 25 | `temperature_f` | `FLOAT` | Temperatura ambiental registrada en grados Fahrenheit. |
| 26 | `humidity_pct` | `FLOAT` | Porcentaje de humedad relativa en el ambiente. |
| 27 | `visibility_mi` | `FLOAT` | Distancia de visibilidad horizontal medida en millas. |
| 28 | `wind_speed_mph` | `FLOAT` | Velocidad del viento registrada en millas por hora. |
| 29 | `precipitation_in`| `FLOAT` | Nivel de precipitación acumulada en pulgadas. |
| 30 | `weather_raw` | `VARCHAR(64)` | Condición meteorológica original reportada en inglés. |
| 31 | `weather_group` | `VARCHAR(32)` | Categoría climática en español: `Despejado`, `Nublado`, `Lluvia`, `Niebla`, `Nieve/Hielo`, `Otro`. |
| 32 | `sunrise_sunset` | `VARCHAR(8)` | Indicador de ciclo de luz: `Day` (Día) o `Night` (Noche). |
| 33 | `traffic_signal` | `TINYINT (0/1)` | Presencia de semáforo en el punto del accidente (1=Sí, 0=No). |
| 34 | `junction` | `TINYINT (0/1)` | Presencia de enlace vial o intersección de autopista (1=Sí, 0=No). |
| 35 | `crossing` | `TINYINT (0/1)` | Presencia de cruce peatonal marcado (1=Sí, 0=No). |
| 36 | `stop` | `TINYINT (0/1)` | Presencia de señal de Pare / Stop (1=Sí, 0=No). |
| 37 | `station` | `TINYINT (0/1)` | Proximidad a estación de transporte público (1=Sí, 0=No). |
| 38 | `railway` | `TINYINT (0/1)` | Proximidad a vía férrea o paso a nivel (1=Sí, 0=No). |
| 39 | `roundabout` | `TINYINT (0/1)` | Proximidad a glorieta / rotonda vial (1=Sí, 0=No). |
| 40 | `vehicle_type` | `VARCHAR(32)` | Tipo de vehículo extraído mediante NLP: `Camión / Tráiler`, `Motocicleta`, `Autobús`, `Bicicleta`, `Peatón involucrado`, `SUV / Van / Pickup`, `Automóvil / Multivehículo`, `No especificado`. |
