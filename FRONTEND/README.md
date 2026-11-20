# 🚀 TrafficPulse AI - Frontend Ejecutivo & Dashboard

Frontend interactivo para la visualización ejecutiva del **Proyecto 3: Análisis de Accidentes de Tránsito en Zonas Urbanas de EE.UU.**

---

## 📌 Estructura del Frontend

El frontend cuenta con 3 secciones especializadas:

1. **Sección 1: Preguntas y Respuestas (10 Requerimientos Analíticos)**
   - Despliegue interactivo de las 10 preguntas analíticas.
   - Respuestas de negocio, KPIs clave y hallazgos cuantitativos.
   - Consultas SQL formateadas e indexadas.
   - Las 10 gráficas generadas en alta resolución con visor interactivo (*lightbox modal*).

2. **Sección 2: Análisis Inferencial ANOVA**
   - Formulación matemática de hipótesis ($H_0$ y $H_a$) para `duration_clean_min` y `visibility_mi`.
   - Evaluación rigurosa de supuestos (Teorema del Límite Central y Test de Levene de Homocedasticidad).
   - Tabla comparativa de estadísticos $F$, valores $p$, nivel de significancia (⭐⭐⭐) y tamaño del efecto ($\eta^2$).
   - Resultados de la prueba Post-Hoc de Tukey HSD.
   - Galería de gráficos de distribución y resumen estadístico.

3. **Sección 3: Infografía del Proyecto & Guía de Comandos**
   - Idea de negocio y valor estratégico para autoridades viales y logística.
   - Arquitectura detallada del pipeline ETL por fases (**Extracción**, **Transformación** y **Carga**) con tecnologías utilizadas y justificación de por qué y cómo se hizo.
   - Guía interactiva de comandos con botones de copia con un solo clic.

---

## 💻 Cómo Visualizarlo

### Opción 1: Abrir Directamente en el Navegador
Simplemente haz doble clic sobre el archivo `index.html` en el explorador de archivos de Windows o ejecútalo desde la consola:

```powershell
Start-Process "FRONTEND\index.html"
```

### Opción 2: Iniciar un Servidor Local Ligero
Si deseas servirlo mediante HTTP local:

```powershell
python -m http.server 8080 --directory FRONTEND
```
Luego abre tu navegador en: [http://localhost:8080](http://localhost:8080)
