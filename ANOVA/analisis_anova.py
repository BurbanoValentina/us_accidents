#!/usr/bin/env python
"""
==============================================================================
ANÁLISIS ANOVA - ACCIDENTES VIALES
==============================================================================
Script para realizar pruebas ANOVA (Analysis of Variance) determinando 
valores p para analizar si hay diferencias significativas entre grupos 
de severidad para las variables:
  - duration_clean_min (duración del accidente en minutos)
  - visibility_mi (visibilidad en millas)

Objetivo: Determinar si la severidad del accidente afecta significativamente
la duración y visibilidad usando ANOVA.
"""

import pandas as pd
import numpy as np
import os
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# Configuración de rutas (soporte para ejecución directa o desde subcarpeta)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

# Rutas posibles
POSSIBLE_SAMPLE_PATHS = [
    os.path.join(BASE_DIR, "csv_limpio_final", "us_accidents_limpio_muestra_10k.csv"),
    os.path.join(PARENT_DIR, "csv_limpio_final", "us_accidents_limpio_muestra_10k.csv"),
]
POSSIBLE_FULL_PATHS = [
    os.path.join(BASE_DIR, "csv_limpio_final", "us_accidents_limpio.csv"),
    os.path.join(PARENT_DIR, "csv_limpio_final", "us_accidents_limpio.csv"),
]

CSV_PATH = next((p for p in POSSIBLE_SAMPLE_PATHS if os.path.exists(p)), POSSIBLE_SAMPLE_PATHS[0])
FULL_CSV_PATH = next((p for p in POSSIBLE_FULL_PATHS if os.path.exists(p)), POSSIBLE_FULL_PATHS[0])

# Intentar usar archivo completo si se desea, o por defecto la muestra optimizada
# NOTA: Si usas el dataset completo (7.7M filas, 2.4 GB), descomentar si dispones de >8GB RAM libre.
# Para ejecución ágil de validación estadística, la muestra de 10k o el dataset completo son compatibles.
if os.path.exists(FULL_CSV_PATH) and os.environ.get("USE_FULL_DATASET", "0") == "1":
    CSV_TO_USE = FULL_CSV_PATH
    DATASET_NAME = "COMPLETO (7.7M registros)"
elif os.path.exists(CSV_PATH):
    CSV_TO_USE = CSV_PATH
    DATASET_NAME = "MUESTRA (10k registros)"
elif os.path.exists(FULL_CSV_PATH):
    CSV_TO_USE = FULL_CSV_PATH
    DATASET_NAME = "COMPLETO (7.7M registros)"
else:
    CSV_TO_USE = CSV_PATH
    DATASET_NAME = "MUESTRA (10k registros)"


def cargar_datos():
    """Carga los datos del CSV limpio."""
    if not os.path.exists(CSV_TO_USE):
        print(f"❌ Error: Archivo CSV no encontrado en {CSV_TO_USE}")
        return None
    
    print(f"\n[CARGA] Datos: {DATASET_NAME}")
    df = pd.read_csv(CSV_TO_USE, low_memory=False)
    print(f"   OK Registros cargados: {len(df):,}")
    print(f"   OK Columnas: {len(df.columns)}")
    
    return df


def validar_variables(df):
    """Valida que las variables requeridas existan."""
    variables_requeridas = ['severity', 'duration_clean_min', 'visibility_mi']
    
    print("\n[VALIDACION] Variables requeridas:")
    for var in variables_requeridas:
        if var in df.columns:
            print(f"   OK {var:25s} - Presente ({df[var].dtype})")
        else:
            print(f"   ERROR {var:25s} - NO ENCONTRADO")
            return False
    
    return True


def estadisticas_descriptivas(df):
    """Calcula estadísticas descriptivas por grupo de severidad."""
    
    print("\n" + "="*90)
    print("[ESTADISTICAS] DESCRIPTIVAS POR SEVERIDAD")
    print("="*90)
    
    severidades = sorted(df['severity'].dropna().unique())
    
    print("\n[1] VARIABLE: duration_clean_min (Duracion en minutos)")
    print("-" * 90)
    print(f"{'Severidad':<12} {'N':>8} {'Media':>12} {'Mediana':>12} {'Desv.Est':>12} {'Min':>12} {'Max':>12}")
    print("-" * 90)
    
    duration_grupos = {}
    for severity in severidades:
        grupo = df[df['severity'] == severity]['duration_clean_min'].dropna()
        duration_grupos[severity] = grupo.values
        
        print(f"Nivel {severity:<8d} {len(grupo):>8,d} {grupo.mean():>12.2f} {grupo.median():>12.2f} "
              f"{grupo.std():>12.2f} {grupo.min():>12.2f} {grupo.max():>12.2f}")
    
    print("\n[2] VARIABLE: visibility_mi (Visibilidad en millas)")
    print("-" * 90)
    print(f"{'Severidad':<12} {'N':>8} {'Media':>12} {'Mediana':>12} {'Desv.Est':>12} {'Min':>12} {'Max':>12}")
    print("-" * 90)
    
    visibility_grupos = {}
    for severity in severidades:
        grupo = df[df['severity'] == severity]['visibility_mi'].dropna()
        visibility_grupos[severity] = grupo.values
        
        print(f"Nivel {severity:<8d} {len(grupo):>8,d} {grupo.mean():>12.2f} {grupo.median():>12.2f} "
              f"{grupo.std():>12.2f} {grupo.min():>12.2f} {grupo.max():>12.2f}")
    
    return duration_grupos, visibility_grupos


def test_normalidad_levene(duration_grupos, visibility_grupos):
    """Realiza test de Levene para homogeneidad de varianzas."""
    
    print("\n" + "="*90)
    print("[TEST DE LEVENE] Homogeneidad de Varianzas")
    print("="*90)
    print("\nH0: Las varianzas son iguales entre grupos")
    print("Ha: Las varianzas NO son iguales entre grupos")
    print("Nivel de significancia: α = 0.05\n")
    
    # Test de Levene para duration_clean_min
    stat_duration, p_levene_duration = stats.levene(*duration_grupos.values())
    print(f"[*] duration_clean_min:")
    print(f"   Estadistico F (Levene): {stat_duration:.4f}")
    print(f"   Valor p: {p_levene_duration:.6f}")
    if p_levene_duration > 0.05:
        print(f"   OK Resultado: Varianzas HOMOGENEAS (p > 0.05)")
    else:
        print(f"   ALERTA Resultado: Varianzas NO HOMOGENEAS (p < 0.05)")
    
    # Test de Levene para visibility_mi
    stat_visibility, p_levene_visibility = stats.levene(*visibility_grupos.values())
    print(f"\n[*] visibility_mi:")
    print(f"   Estadistico F (Levene): {stat_visibility:.4f}")
    print(f"   Valor p: {p_levene_visibility:.6f}")
    if p_levene_visibility > 0.05:
        print(f"   OK Resultado: Varianzas HOMOGENEAS (p > 0.05)")
    else:
        print(f"   ALERTA Resultado: Varianzas NO HOMOGENEAS (p < 0.05)")
    
    return p_levene_duration, p_levene_visibility


def anova_test(duration_grupos, visibility_grupos):
    """Realiza prueba ANOVA F para cada variable."""
    
    print("\n" + "="*90)
    print("[PRUEBA ANOVA F] Analysis of Variance")
    print("="*90)
    print("\nH0: Las medias de los grupos son iguales")
    print("Ha: Al menos una media de los grupos es diferente")
    print("Nivel de significancia: alfa = 0.05\n")
    
    # ANOVA para duration_clean_min
    f_stat_duration, p_value_duration = stats.f_oneway(*duration_grupos.values())
    
    print("[1] ANOVA: Severidad -> duration_clean_min")
    print("-" * 90)
    print(f"   Estadístico F: {f_stat_duration:.4f}")
    print(f"   ⭐ VALOR P: {p_value_duration:.10f}")
    
    if p_value_duration < 0.001:
        significance = "ALTAMENTE SIGNIFICATIVO (p < 0.001) ⭐⭐⭐"
    elif p_value_duration < 0.01:
        significance = "MUY SIGNIFICATIVO (p < 0.01) ⭐⭐"
    elif p_value_duration < 0.05:
        significance = "SIGNIFICATIVO (p < 0.05) ⭐"
    else:
        significance = "NO SIGNIFICATIVO (p ≥ 0.05)"
    
    print(f"   Interpretación: {significance}")
    
    if p_value_duration < 0.05:
        print(f"\n   [CONCLUSION] Resultado:")
        print(f"   Existe diferencia SIGNIFICATIVA en la duracion promedio entre")
        print(f"   los diferentes niveles de severidad. La severidad del accidente")
        print(f"   SI afecta la duracion del mismo.")
    else:
        print(f"\n   [CONCLUSION] Resultado:")
        print(f"   NO existe diferencia significativa en la duracion promedio entre")
        print(f"   los diferentes niveles de severidad. La severidad del accidente")
        print(f"   NO afecta significativamente la duracion.")
    
    # ANOVA para visibility_mi
    f_stat_visibility, p_value_visibility = stats.f_oneway(*visibility_grupos.values())
    
    print("\n[2] ANOVA: Severidad -> visibility_mi")
    print("-" * 90)
    print(f"   Estadístico F: {f_stat_visibility:.4f}")
    print(f"   ⭐ VALOR P: {p_value_visibility:.10f}")
    
    if p_value_visibility < 0.001:
        significance = "ALTAMENTE SIGNIFICATIVO (p < 0.001) ⭐⭐⭐"
    elif p_value_visibility < 0.01:
        significance = "MUY SIGNIFICATIVO (p < 0.01) ⭐⭐"
    elif p_value_visibility < 0.05:
        significance = "SIGNIFICATIVO (p < 0.05) ⭐"
    else:
        significance = "NO SIGNIFICATIVO (p ≥ 0.05)"
    
    print(f"   Interpretación: {significance}")
    
    if p_value_visibility < 0.05:
        print(f"\n   [CONCLUSION] Resultado:")
        print(f"   Existe diferencia SIGNIFICATIVA en la visibilidad promedio entre")
        print(f"   los diferentes niveles de severidad. La severidad del accidente")
        print(f"   SI afecta la visibilidad.")
    else:
        print(f"\n   [CONCLUSION] Resultado:")
        print(f"   NO existe diferencia significativa en la visibilidad promedio entre")
        print(f"   los diferentes niveles de severidad. La severidad del accidente")
        print(f"   NO afecta significativamente la visibilidad.")
    
    return f_stat_duration, p_value_duration, f_stat_visibility, p_value_visibility


def effect_size_eta_squared(df, variable, grouping_var):
    """Calcula eta-squared (tamaño del efecto)."""
    
    # Media general
    grand_mean = df[variable].mean()
    
    # Suma de cuadrados total
    sst = ((df[variable] - grand_mean) ** 2).sum()
    
    # Suma de cuadrados entre grupos
    ssb = 0
    for group in df[grouping_var].unique():
        group_data = df[df[grouping_var] == group][variable]
        group_mean = group_data.mean()
        n_group = len(group_data)
        ssb += n_group * (group_mean - grand_mean) ** 2
    
    # Eta-squared
    eta_squared = ssb / sst
    
    return eta_squared


def tamaño_efecto(df):
    """Calcula tamaño del efecto (eta-squared) para ambas variables."""
    
    print("\n" + "="*90)
    print("[TAMANIO DEL EFECTO] Eta-squared")
    print("="*90)
    print("\nInterpretacion:")
    print("  eta² < 0.01   : Efecto muy pequeño")
    print("  0.01-0.06     : Efecto pequeño")
    print("  0.06-0.14     : Efecto mediano")
    print("  eta² > 0.14   : Efecto grande\n")
    
    # Eta-squared para duration_clean_min
    eta_duration = effect_size_eta_squared(df, 'duration_clean_min', 'severity')
    print(f"[*] duration_clean_min:")
    print(f"   eta² = {eta_duration:.6f} ({eta_duration*100:.4f}%)")
    
    if eta_duration < 0.01:
        effect_interp = "Efecto muy pequeño"
    elif eta_duration < 0.06:
        effect_interp = "Efecto pequeño"
    elif eta_duration < 0.14:
        effect_interp = "Efecto mediano"
    else:
        effect_interp = "Efecto grande"
    
    print(f"   Interpretacion: {effect_interp}")
    
    # Eta-squared para visibility_mi
    eta_visibility = effect_size_eta_squared(df, 'visibility_mi', 'severity')
    print(f"\n[*] visibility_mi:")
    print(f"   eta² = {eta_visibility:.6f} ({eta_visibility*100:.4f}%)")
    
    if eta_visibility < 0.01:
        effect_interp = "Efecto muy pequeño"
    elif eta_visibility < 0.06:
        effect_interp = "Efecto pequeño"
    elif eta_visibility < 0.14:
        effect_interp = "Efecto mediano"
    else:
        effect_interp = "Efecto grande"
    
    print(f"   Interpretacion: {effect_interp}")
    
    return eta_duration, eta_visibility


def prueba_post_hoc(df):
    """Realiza prueba post-hoc de Tukey para comparaciones pareadas."""
    
    print("\n" + "="*90)
    print("[POST-HOC] Comparaciones Pareadas (Tukey HSD)")
    print("="*90)
    
    try:
        from scipy.stats import tukey_hsd
        
        severidades = sorted(df['severity'].dropna().unique())
        
        print("\n[1] Tukey HSD: Severidad -> duration_clean_min")
        print("-" * 90)
        
        grupos_duration = [df[df['severity'] == s]['duration_clean_min'].dropna().values 
                          for s in severidades]
        res_duration = tukey_hsd(*grupos_duration)
        
        print(f"Comparación de pares de severidad:")
        for i, s1 in enumerate(severidades):
            for j, s2 in enumerate(severidades):
                if i < j:
                    p_val = res_duration.pvalue[i, j]
                    print(f"   Severidad {s1} vs {s2}: p-value = {p_val:.6f} ", end="")
                    print("✓ Significativo" if p_val < 0.05 else "✗ No significativo")
        
        print("\n[2] Tukey HSD: Severidad -> visibility_mi")
        print("-" * 90)
        
        grupos_visibility = [df[df['severity'] == s]['visibility_mi'].dropna().values 
                            for s in severidades]
        res_visibility = tukey_hsd(*grupos_visibility)
        
        print(f"Comparación de pares de severidad:")
        for i, s1 in enumerate(severidades):
            for j, s2 in enumerate(severidades):
                if i < j:
                    p_val = res_visibility.pvalue[i, j]
                    print(f"   Severidad {s1} vs {s2}: p-value = {p_val:.6f} ", end="")
                    print("✓ Significativo" if p_val < 0.05 else "✗ No significativo")
    
    except ImportError:
        print("\n[ALERTA] Nota: scipy.stats.tukey_hsd requiere scipy >= 1.7.0")
        print("   Usando metodo alternativo (pairwise t-tests con correccion Bonferroni)")
        
        from scipy.stats import ttest_ind
        
        severidades = sorted(df['severity'].dropna().unique())
        n_comparaciones = len(severidades) * (len(severidades) - 1) / 2
        alpha_corregido = 0.05 / n_comparaciones
        
        print(f"\n   Nivel de significancia corregido (Bonferroni): {alpha_corregido:.6f}\n")
        
        print("[1] T-tests pareados: Severidad -> duration_clean_min")
        print("-" * 90)
        
        for i, s1 in enumerate(severidades):
            for j, s2 in enumerate(severidades):
                if i < j:
                    grupo1 = df[df['severity'] == s1]['duration_clean_min'].dropna()
                    grupo2 = df[df['severity'] == s2]['duration_clean_min'].dropna()
                    t_stat, p_val = ttest_ind(grupo1, grupo2)
                    print(f"   Severidad {s1} vs {s2}: p-value = {p_val:.6f} ", end="")
                    print("OK Significativo" if p_val < alpha_corregido else "NO Significativo")
        
        print("\n[2] T-tests pareados: Severidad -> visibility_mi")
        print("-" * 90)
        
        for i, s1 in enumerate(severidades):
            for j, s2 in enumerate(severidades):
                if i < j:
                    grupo1 = df[df['severity'] == s1]['visibility_mi'].dropna()
                    grupo2 = df[df['severity'] == s2]['visibility_mi'].dropna()
                    t_stat, p_val = ttest_ind(grupo1, grupo2)
                    print(f"   Severidad {s1} vs {s2}: p-value = {p_val:.6f} ", end="")
                    print("OK Significativo" if p_val < alpha_corregido else "NO Significativo")


def resumen_ejecutivo(p_duration, p_visibility, eta_duration, eta_visibility):
    """Imprime resumen ejecutivo de resultados."""
    
    print("\n" + "="*90)
    print("[RESUMEN EJECUTIVO]")
    print("="*90)
    
    print("\n[KEY] HALLAZGOS PRINCIPALES:\n")
    
    print(f"[1] VARIABLE: duration_clean_min (Duracion del accidente)")
    print(f"   - Valor p ANOVA: {p_duration:.10f}")
    if p_duration < 0.05:
        print(f"   - Resultado: OK SIGNIFICATIVO (Rechazar H0)")
        print(f"   - Interpretacion: La severidad afecta SIGNIFICATIVAMENTE la duracion")
    else:
        print(f"   - Resultado: ERROR NO SIGNIFICATIVO (Fallar en rechazar H0)")
        print(f"   - Interpretacion: La severidad NO afecta significativamente la duracion")
    print(f"   - Tamaño del efecto (eta²): {eta_duration:.6f} ({eta_duration*100:.4f}%)")
    
    print(f"\n[2] VARIABLE: visibility_mi (Visibilidad)")
    print(f"   • Valor p ANOVA: {p_visibility:.10f}")
    if p_visibility < 0.05:
        print(f"   • Resultado: ✅ SIGNIFICATIVO (Rechazar H0)")
        print(f"   • Interpretación: La severidad afecta SIGNIFICATIVAMENTE la visibilidad")
    else:
        print(f"   • Resultado: ❌ NO SIGNIFICATIVO (Fallar en rechazar H0)")
        print(f"   • Interpretación: La severidad NO afecta significativamente la visibilidad")
    print(f"   • Tamaño del efecto (η²): {eta_visibility:.6f} ({eta_visibility*100:.4f}%)")
    
    print("\n" + "="*90)


def main():
    """Función principal."""
    
    print("\n" + "="*90)
    print("[ANALISIS ANOVA] - ACCIDENTES VIALES")
    print("="*90)
    
    # Cargar datos
    df = cargar_datos()
    if df is None:
        return
    
    # Validar variables
    if not validar_variables(df):
        return
    
    # Eliminar filas con NaN en variables críticas
    df_clean = df[['severity', 'duration_clean_min', 'visibility_mi']].dropna()
    print(f"\n   OK Registros para analisis: {len(df_clean):,}")
    
    # Estadísticas descriptivas
    duration_grupos, visibility_grupos = estadisticas_descriptivas(df_clean)
    
    # Test de Levene
    test_normalidad_levene(duration_grupos, visibility_grupos)
    
    # ANOVA
    f_stat_duration, p_value_duration, f_stat_visibility, p_value_visibility = anova_test(duration_grupos, visibility_grupos)
    
    # Tamaño del efecto
    eta_duration, eta_visibility = tamaño_efecto(df_clean)
    
    # Prueba post-hoc
    prueba_post_hoc(df_clean)
    
    # Resumen ejecutivo
    resumen_ejecutivo(p_value_duration, p_value_visibility, eta_duration, eta_visibility)
    
    print("\n✅ Análisis completado.\n")


if __name__ == "__main__":
    main()
