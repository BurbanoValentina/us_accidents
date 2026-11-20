# 📥 Fase 1: Extracción y Descarga de Datos (ETL)

Esta carpeta contiene el módulo único y centralizado responsable de la **descarga automática desde la URL oficial de Kaggle y la extracción controlada en streaming**.

---

## 🌐 Fuente de Datos Oficial

El pipeline realiza la extracción exclusivamente desde el dataset oficial de Kaggle:

* **Dataset:** US Accidents (2016–2023)
* **URL Oficial:** [https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents)
* **Slug Kaggle:** `sobhanmoosavi/us-accidents`
* **Mecanismo de Descarga:** Descarga pública y anónima automatizada mediante la librería oficial `kagglehub` (sin requerir credenciales manuales ni API key).
* **Archivo Destino:** `extraccion/datos_origen/US_Accidents_March23.csv` (7,728,394 filas, 3.05 GB).

---

## 🛠️ Arquitectura y Tecnologías Utilizadas

* **Único Extractor del Proyecto (`extraccion/extractor.py`):**
  * Implementa la clase `ExtractorAccidentes`.
  * Método `asegurar_archivo_accidentes()`: verifica si el archivo está presente en `extraccion/datos_origen/`. Si no existe, lo descarga directamente desde la URL de Kaggle y lo posiciona automáticamente.
  * **Streaming por Generadores (`chunksize=500_000`):** Lee bloques controlados de 500k filas con Pandas y filtrado de 27 columnas (`usecols=COLUMNAS_EXTRACCION`), manteniendo el consumo de memoria RAM por debajo de 1.5 GB.
  * **Soporte PySpark Integrado (`extraer_spark(spark)`):** Ingesta distribuida tipada bajo demanda sin necesidad de scripts secundarios de extracción.

---

## 🚀 Cómo Ejecutar la Extracción

```bash
# Ejecutar el extractor único de Python
python extraccion/extractor.py
```
