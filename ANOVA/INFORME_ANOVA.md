# 📊 Informe Técnico del Análisis ANOVA: Accidentes Viales en Zonas Urbanas de EE.UU.

Este documento presenta la formulación matemática, verificación de supuestos, resultados inferenciales e interpretación analítica del análisis de varianza (**ANOVA unidireccional**) aplicado sobre el conjunto de datos de accidentes de tránsito en Estados Unidos (*US Accidents Dataset*).

---

## 1. Objetivos del Análisis

Determinar mediante evidencia estadística formal si la gravedad o nivel de impacto de un accidente (**Severidad**, clasificada en niveles ordinales del 1 al 4) produce diferencias estadísticamente significativas en dos métricas operativas y ambientales clave:
1. **`duration_clean_min`**: Duración efectiva del incidente en minutos (tiempo de cierre y despeje vial, sin valores atípicos administrativos $>24$ h).
2. **`visibility_mi`**: Visibilidad meteorológica registrada al momento del siniestro en millas terrestres.

---

## 2. Formulación de Hipótesis Estadísticas

Para cada una de las variables analizadas, se plantea una prueba de hipótesis global con nivel de significancia $\alpha = 0.05$:

### Variable 1: Duración del Accidente (`duration_clean_min`)
* **Hipótesis Nula ($H_0$):** No existen diferencias entre las duraciones medias de despeje vial para los cuatro niveles de severidad.
  $$\mu_{\text{dur}, 1} = \mu_{\text{dur}, 2} = \mu_{\text{dur}, 3} = \mu_{\text{dur}, 4}$$
* **Hipótesis Alternativa ($H_a$):** Al menos un nivel de severidad presenta una duración media significativamente diferente a los demás.
  $$\exists\ i \neq j \quad \text{tal que} \quad \mu_{\text{dur}, i} \neq \mu_{\text{dur}, j}$$

### Variable 2: Visibilidad Meteorológica (`visibility_mi`)
* **Hipótesis Nula ($H_0$):** La visibilidad meteorológica promedio es idéntica en todos los niveles de severidad.
  $$\mu_{\text{vis}, 1} = \mu_{\text{vis}, 2} = \mu_{\text{vis}, 3} = \mu_{\text{vis}, 4}$$
* **Hipótesis Alternativa ($H_a$):** Al menos un nivel de severidad difiere significativamente en su visibilidad promedio.
  $$\exists\ i \neq j \quad \text{tal que} \quad \mu_{\text{vis}, i} \neq \mu_{\text{vis}, j}$$

---

## 3. Validación de Supuestos Estadísticos

Para la aplicación válida del estadístico $F$ de Snedecor en ANOVA, se evaluaron los supuestos fundamentales:

### A. Supuesto de Independencia
* **Validación:** Cada registro corresponde a un evento de siniestralidad vial geolocalizado con identificador único (`id`), verificado durante la fase de transformación con deduplicación por clave primaria. Se asume independencia entre observaciones.

### B. Supuesto de Normalidad
* **Evaluación:** En muestras masivas ($N = 10,000$ en muestra de prueba y $N = 7,728,394$ en la población), el **Teorema del Límite Central (TLC)** garantiza que la distribución muestral de las medias converge asintóticamente a una distribución normal.
* La variable `duration_clean_min` presenta asimetría positiva típica de los tiempos de espera y despeje, por lo que se reportan tanto medias como medianas paramétricas y no paramétricas.

### C. Supuesto de Homogeneidad de Varianzas (Homocedasticidad)
Se evaluó mediante la **Prueba de Levene** centrada en la mediana:

| Variable | Estadístico $F$ (Levene) | Valor $p$ | Condición ($\alpha = 0.05$) | Conclusión del Supuesto |
| :--- | :---: | :---: | :---: | :--- |
| **`duration_clean_min`** | $5.8896$ | $0.000518$ | $p < 0.05$ | Varianzas **heterocedásticas** |
| **`visibility_mi`** | $7.8478$ | $0.000032$ | $p < 0.05$ | Varianzas **heterocedásticas** |

> **Nota Metodológica:** Al rechazarse la igualdad de varianzas en ambas variables ($p < 0.05$), se ratifican las conclusiones mediante comparaciones robustas y la prueba post-hoc de **Tukey HSD**, la cual mantiene un control estricto sobre el error Tipo I ($\alpha$).

---

## 4. Estadísticas Descriptivas por Nivel de Severidad

| Severidad | Descripción Operativa | $N$ (Muestra 10k) | Media Duración (min) | Mediana Duración (min) | Desv. Est. (min) | Media Visibilidad (mi) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Nivel 1** | Impacto mínimo en flujo | 6 | 37.50 | 37.50 | 8.22 | 9.00 |
| **Nivel 2** | Retraso moderado urbano | 5,976 | 42.97 | 30.00 | 28.95 | 8.79 |
| **Nivel 3** | Obstrucción carril / autopista | 3,916 | 46.05 | 30.00 | 45.16 | 9.10 |
| **Nivel 4** | Cierre vial total / catástrofe | 6 | 35.38 | 30.00 | 8.53 | 9.33 |

*(En el dataset nacional completo de 7.7M filas, la severidad 4 alcanza un promedio nacional de **185.9 minutos** debido a los complejos operativos de rescate pericial).*

---

## 5. Resultados de la Prueba ANOVA $F$

### 1. Severidad $\rightarrow$ Duración (`duration_clean_min`)
* **Estadístico $F$:** $5.8960$
* **Valor $p$:** $0.0005136543$ ($p < 0.001$)
* **Decisión:** **Rechazar $H_0$**
* **Significancia:** **Altamente Significativo (⭐⭐⭐)**
* **Interpretación:** Existe una diferencia estadísticamente significativa en la duración promedio del incidente entre los diferentes niveles de severidad vial.

### 2. Severidad $\rightarrow$ Visibilidad (`visibility_mi`)
* **Estadístico $F$:** $11.2288$
* **Valor $p$:** $0.0000002370$ ($2.37 \times 10^{-7}$)
* **Decisión:** **Rechazar $H_0$**
* **Significancia:** **Altamente Significativo (⭐⭐⭐)**
* **Interpretación:** La visibilidad atmosférica varía de forma significativa entre los niveles de severidad del accidente.

---

## 6. Tamaño del Efecto ($\eta^2$, Eta-Squared)

El estadístico Eta-cuadrado cuantifica el porcentaje de la varianza total de la variable dependiente explicado por la severidad:

$$\eta^2 = \frac{\text{SS}_{\text{between}}}{\text{SS}_{\text{total}}}$$

* **`duration_clean_min`:** $\eta^2 = 0.001783$ ($0.18\%$) $\rightarrow$ Efecto pequeño/sutil a nivel poblacional individual, aunque con alto impacto agregado sobre millones de vehículos.
* **`visibility_mi`:** $\eta^2 = 0.003391$ ($0.34\%$) $\rightarrow$ Efecto pequeño; la visibilidad es un catalizador ambiental que interactúa de manera multivariada con la velocidad y el tipo de vía.

---

## 7. Comparaciones Múltiples Pareadas (Prueba Post-Hoc de Tukey HSD)

Para identificar qué pares de grupos presentan las diferencias significativas:

| Comparación de Severidad | Variable: Duración ($p$-value) | Conclusión Duración | Variable: Visibilidad ($p$-value) | Conclusión Visibilidad |
| :---: | :---: | :---: | :---: | :---: |
| **Nivel 1 vs Nivel 2** | $0.982740$ | No significativo | $0.997276$ | No significativo |
| **Nivel 1 vs Nivel 3** | $0.938716$ | No significativo | $0.999703$ | No significativo |
| **Nivel 1 vs Nivel 4** | $0.999628$ | No significativo | $0.995986$ | No significativo |
| **Nivel 2 vs Nivel 3** | **$0.000206$** | **✓ Significativo ($p < 0.001$)** | **$0.000000$** | **✓ Significativo ($p < 0.001$)** |
| **Nivel 2 vs Nivel 4** | $0.956030$ | No significativo | $0.955425$ | No significativo |
| **Nivel 3 vs Nivel 4** | $0.888732$ | No significativo | $0.996039$ | No significativo |

**Hallazgo Crítico:** La frontera más influyente del tráfico se ubica en la transición entre el **Nivel 2** (incidentes urbanos típicos) y el **Nivel 3** (bloqueos mayores en autopistas e interstates), donde se produce un salto cuantitativo y estadísticamente significativo tanto en tiempo de retención como en condiciones meteorológicas asociadas.

---

## 8. Visualizaciones Generadas

Las siguientes figuras gráficas generadas acompañan este reporte:
1. `grafica_anova_duracion.png`: Diagrama de cajas (IQR) y medias con intervalos de confianza al 95% para `duration_clean_min`.
2. `grafica_anova_visibilidad.png`: Distribución y variación paramétrica de `visibility_mi` por severidad.
3. `grafica_anova_resumen_estadistico.png`: Panel integrado con pruebas $F$, test de Levene y conclusiones analíticas.

---

## 9. Modo de Ejecución del Script

Para ejecutar el análisis ANOVA en la terminal:

```powershell
# Opción 1: Ejecución estándar usando la muestra de 10,000 registros (tiempo: ~1s)
python ANOVA/analisis_anova.py

# Opción 2: Ejecución sobre el dataset nacional completo de 7.7 millones de filas
$env:USE_FULL_DATASET="1"; python ANOVA/analisis_anova.py
```
