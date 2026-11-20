"""
==============================================================================
GENERADOR DE GRÁFICAS ANALÍTICAS (SQL) - PROYECTO 3: ACCIDENTES EN EE.UU.
==============================================================================
Genera 10 visualizaciones de nivel ejecutivo a partir de los datos analíticos
obtenidos de las consultas SQL / Parquet de las 10 preguntas analíticas.
==============================================================================
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Configurar directorio de trabajo y rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_JSON_PATH = os.path.join(PROJECT_ROOT, "datos_analiticos_10_preguntas.json")
OUTPUT_DIR = BASE_DIR

# Estilo visual ejecutivo
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

COLORS = {
    'primary': '#1E3A8A',    # Navy blue
    'secondary': '#0284C7',  # Sky blue
    'accent': '#0D9488',     # Teal
    'danger': '#DC2626',     # Red / Critical
    'warning': '#D97706',    # Amber
    'purple': '#7C3AED',     # Violet
    'dark': '#0F172A',       # Slate 900
    'light_bg': '#F8FAFC',   # Slate 50
    'card_bg': '#FFFFFF'
}


def cargar_datos():
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def guardar_grafica(fig, filename):
    out_path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"✅ Generada: {filename}")


# ------------------------------------------------------------------------------
# 1. FRECUENCIA POR ESTADO Y CIUDAD
# ------------------------------------------------------------------------------
def plot_q1(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('REQUERIMIENTO 1: Frecuencia de Accidentes por Estado y Ciudad Urbana', 
                 fontsize=16, fontweight='bold', color=COLORS['dark'], y=1.02)
    
    # Estados
    states = data['q1']['states']
    names_st = [s['state'] for s in reversed(states)]
    totals_st = [s['total'] / 1000.0 for s in reversed(states)]
    pcts_st = [s['pct'] for s in reversed(states)]
    sevs_st = [s['avg_sev'] for s in reversed(states)]
    
    bars1 = ax1.barh(names_st, totals_st, color=COLORS['primary'], alpha=0.85, edgecolor=COLORS['dark'], height=0.65)
    ax1.set_title('Top 10 Estados con Mayor Siniestralidad Vial', fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel('Total Accidentes (Miles)', fontsize=11)
    ax1.grid(axis='x', linestyle='--', alpha=0.6)
    
    for bar, pct, sev in zip(bars1, pcts_st, sevs_st):
        w = bar.get_width()
        ax1.text(w + 20, bar.get_y() + bar.get_height()/2, 
                 f'{w:,.0f}k ({pct}%) | Sev: {sev}', 
                 va='center', ha='left', fontsize=9, fontweight='semibold', color='#334155')
    ax1.set_xlim(0, max(totals_st) * 1.25)
    
    # Ciudades
    cities = data['q1']['cities']
    names_ci = [f"{c['city']}, {c['state']}" for c in reversed(cities)]
    totals_ci = [c['total'] / 1000.0 for c in reversed(cities)]
    pcts_ci = [c['pct'] for c in reversed(cities)]
    
    bars2 = ax2.barh(names_ci, totals_ci, color=COLORS['secondary'], alpha=0.85, edgecolor='#0369A1', height=0.65)
    ax2.set_title('Top 10 Ciudades Urbanas con Mayor Concentración', fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel('Total Accidentes (Miles)', fontsize=11)
    ax2.grid(axis='x', linestyle='--', alpha=0.6)
    
    for bar, pct in zip(bars2, pcts_ci):
        w = bar.get_width()
        ax2.text(w + 3, bar.get_y() + bar.get_height()/2, 
                 f'{w:,.1f}k ({pct}%)', 
                 va='center', ha='left', fontsize=9, fontweight='semibold', color='#334155')
    ax2.set_xlim(0, max(totals_ci) * 1.22)
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_01_accidentes_estado_ciudad.png')


# ------------------------------------------------------------------------------
# 2. HORA DEL DÍA Y FRANJAS
# ------------------------------------------------------------------------------
def plot_q2(data):
    fig, ax1 = plt.subplots(figsize=(14, 6.5))
    
    hours_data = data['q2']['by_hour']
    hours = [h['hour'] for h in hours_data]
    totals = [h['total'] / 1000.0 for h in hours_data]
    sevs = [h['avg_sev'] for h in hours_data]
    
    ax1.plot(hours, totals, color=COLORS['primary'], linewidth=3, marker='o', markersize=6, label='Accidentes (Miles)')
    ax1.fill_between(hours, totals, color=COLORS['secondary'], alpha=0.15)
    ax1.set_title('REQUERIMIENTO 2: Patrón Horario Bimodal y Severidad por Hora del Día', 
                  fontsize=15, fontweight='bold', color=COLORS['dark'], pad=15)
    ax1.set_xlabel('Hora del Día (00:00 - 23:00)', fontsize=11, labelpad=8)
    ax1.set_ylabel('Total de Accidentes (Miles)', fontsize=11, color=COLORS['primary'])
    ax1.set_xticks(range(0, 24))
    ax1.set_xticklabels([f"{h:02d}:00" for h in range(0, 24)], rotation=45)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Anotaciones de picos
    max_am_idx = 7
    ax1.annotate('Pico Matutino (07:00h - 08:00h)\nEntrada Laboral (587k)', 
                 xy=(7, totals[7]), xytext=(3, totals[7] + 80),
                 arrowprops=dict(facecolor=COLORS['primary'], shrink=0.08, width=1.5, headwidth=7),
                 fontweight='bold', fontsize=9, color=COLORS['primary'])
    
    max_pm_idx = 16
    ax1.annotate('Pico Vespertino (16:00h - 17:00h)\nSalida Laboral (1.15M)', 
                 xy=(16, totals[16]), xytext=(12, totals[16] + 70),
                 arrowprops=dict(facecolor=COLORS['danger'], shrink=0.08, width=1.5, headwidth=7),
                 fontweight='bold', fontsize=9, color=COLORS['danger'])
    
    # Eje secundario para Severidad
    ax2 = ax1.twinx()
    ax2.plot(hours, sevs, color=COLORS['danger'], linewidth=2.5, linestyle='--', marker='s', markersize=5, label='Severidad Promedio')
    ax2.set_ylabel('Severidad Promedio (Escala 1 - 4)', fontsize=11, color=COLORS['danger'])
    ax2.set_ylim(2.0, 2.45)
    ax2.grid(False)
    
    # Destacar madrugada
    ax2.annotate('Peligrosidad de Madrugada\n(00:00 - 04:00h) Severidad > 2.28', 
                 xy=(2, sevs[2]), xytext=(0.5, 2.38),
                 arrowprops=dict(facecolor=COLORS['danger'], shrink=0.08, width=1.2, headwidth=6),
                 fontweight='bold', fontsize=8.5, color=COLORS['danger'])
    
    # Leyenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_02_hora_del_dia_accidentalidad.png')


# ------------------------------------------------------------------------------
# 3. ANÁLISIS POR SEVERIDAD
# ------------------------------------------------------------------------------
def plot_q3(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    fig.suptitle('REQUERIMIENTO 3: Distribución por Severidad e Impacto en Duración y Vía', 
                 fontsize=15, fontweight='bold', color=COLORS['dark'], y=1.02)
    
    sev_data = data['q3']
    labels = [f"Nivel {s['severity']}" for s in sev_data]
    totals = [s['total'] for s in sev_data]
    pcts = [s['pct'] for s in sev_data]
    durations = [s['avg_duration'] for s in sev_data]
    distances = [s['avg_distance'] for s in sev_data]
    
    sev_colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
    
    # Donut Chart
    wedges, texts, autotexts = ax1.pie(totals, labels=labels, autopct='%1.1f%%',
                                       startangle=140, colors=sev_colors, 
                                       wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
                                       textprops=dict(color=COLORS['dark'], fontweight='bold', fontsize=10))
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color('white')
    ax1.set_title('Proporción del Volumen de Accidentes', fontsize=12, fontweight='bold', pad=10)
    
    # Texto central del Donut
    ax1.text(0, 0, '7.73M\nTotal', ha='center', va='center', fontsize=14, fontweight='bold', color=COLORS['dark'])
    
    # Barras de Duración Promedio y Distancia
    x = np.arange(len(labels))
    width = 0.35
    
    rects1 = ax2.bar(x - width/2, durations, width, label='Duración Media (Minutos)', color=COLORS['primary'], alpha=0.85)
    ax2.set_ylabel('Duración Media de Cierre (Minutos)', fontsize=11, color=COLORS['primary'])
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=10, fontweight='bold')
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Eje secundario para distancia
    ax2_dist = ax2.twinx()
    rects2 = ax2_dist.bar(x + width/2, distances, width, label='Distancia Afectada (Millas)', color=COLORS['warning'], alpha=0.85)
    ax2_dist.set_ylabel('Longitud de Congestión Vial (Millas)', fontsize=11, color=COLORS['warning'])
    ax2_dist.grid(False)
    ax2_dist.set_ylim(0, max(distances)*1.3)
    
    # Anotaciones
    for r in rects1:
        h = r.get_height()
        ax2.text(r.get_x() + r.get_width()/2., h + 3, f'{h:.1f}m', ha='center', va='bottom', fontsize=9, fontweight='bold')
    for r in rects2:
        h = r.get_height()
        ax2_dist.text(r.get_x() + r.get_width()/2., h + 0.04, f'{h:.2f}mi', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    ax2.set_title('Impacto Operativo: Tiempo de Despeje vs Longitud Afectada', fontsize=12, fontweight='bold', pad=10)
    
    lines1, lab1 = ax2.get_legend_handles_labels()
    lines2, lab2 = ax2_dist.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, lab1 + lab2, loc='upper left')
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_03_analisis_por_severidad.png')


# ------------------------------------------------------------------------------
# 4. RELACIÓN CON CONDICIONES CLIMÁTICAS
# ------------------------------------------------------------------------------
def plot_q4(data):
    fig, ax1 = plt.subplots(figsize=(13, 6.5))
    
    weather = data['q4']
    cats = [w['weather_group'] for w in weather]
    totals = [w['total'] / 1000.0 for w in weather]
    pct_graves = [w['pct_graves'] for w in weather]
    vis = [w['avg_vis'] for w in weather]
    
    x = np.arange(len(cats))
    width = 0.45
    
    bars = ax1.bar(x, totals, width, color=COLORS['secondary'], alpha=0.85, edgecolor='#0284C7', label='Total Accidentes (Miles)')
    ax1.set_title('REQUERIMIENTO 4: Influencia de Condiciones Meteorológicas en Volumen y Severidad', 
                  fontsize=14, fontweight='bold', color=COLORS['dark'], pad=15)
    ax1.set_xlabel('Categoría Meteorológica Consolidada', fontsize=11, labelpad=8)
    ax1.set_ylabel('Total de Accidentes (Miles)', fontsize=11, color=COLORS['primary'])
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats, rotation=20, ha='right', fontsize=10, fontweight='semibold')
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 25, f'{h:,.0f}k', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax1.set_ylim(0, max(totals)*1.15)
    
    # Eje secundario para tasa de accidentes graves
    ax2 = ax1.twinx()
    ax2.plot(x, pct_graves, color=COLORS['danger'], marker='D', markersize=7, linewidth=2.5, label='% Accidentes Graves (S3-S4)')
    ax2.set_ylabel('Tasa de Siniestros Graves (Severidad 3 o 4 %)', fontsize=11, color=COLORS['danger'])
    ax2.set_ylim(10, 30)
    ax2.grid(False)
    
    for i, txt in enumerate(pct_graves):
        ax2.annotate(f"{txt}%", (x[i], pct_graves[i] + 0.6), ha='center', fontsize=9, fontweight='bold', color=COLORS['danger'])
        
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_04_relacion_condiciones_climaticas.png')


# ------------------------------------------------------------------------------
# 5. TIPOS DE VÍA MÁS PELIGROSOS
# ------------------------------------------------------------------------------
def plot_q5(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    fig.suptitle('REQUERIMIENTO 5: Jerarquía Vial y Peligrosidad en la Red de Transporte', 
                 fontsize=15, fontweight='bold', color=COLORS['dark'], y=1.02)
    
    roads = data['q5']['by_road']
    names = [r['road_type'] for r in reversed(roads)]
    totals = [r['total'] / 1000.0 for r in reversed(roads)]
    pcts = [r['pct'] for r in reversed(roads)]
    pct_graves = [r['pct_graves'] for r in reversed(roads)]
    sevs = [r['avg_sev'] for r in reversed(roads)]
    
    bars1 = ax1.barh(names, totals, color=COLORS['primary'], alpha=0.85, height=0.6)
    ax1.set_title('Distribución por Tipo de Infraestructura Vial', fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel('Accidentes (Miles)', fontsize=11)
    ax1.grid(axis='x', linestyle='--', alpha=0.6)
    
    for bar, pct in zip(bars1, pcts):
        w = bar.get_width()
        ax1.text(w + 30, bar.get_y() + bar.get_height()/2, f'{w:,.0f}k ({pct}%)', 
                 va='center', ha='left', fontsize=9, fontweight='bold')
    ax1.set_xlim(0, max(totals) * 1.25)
    
    # Severidad y % Graves
    bars2 = ax2.barh(names, pct_graves, color=COLORS['danger'], alpha=0.8, height=0.6)
    ax2.set_title('Tasa de Siniestros Graves por Tipo de Vía (% S3-S4)', fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel('% Incidentes con Severidad 3 o 4', fontsize=11)
    ax2.grid(axis='x', linestyle='--', alpha=0.6)
    
    for bar, sev in zip(bars2, sevs):
        w = bar.get_width()
        ax2.text(w + 0.8, bar.get_y() + bar.get_height()/2, f'{w:.1f}% | Sev Prom: {sev}', 
                 va='center', ha='left', fontsize=9, fontweight='bold')
    ax2.set_xlim(0, max(pct_graves) * 1.3)
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_05_tipos_de_via_mas_peligrosos.png')


# ------------------------------------------------------------------------------
# 6. DÍAS DE LA SEMANA
# ------------------------------------------------------------------------------
def plot_q6(data):
    fig, ax1 = plt.subplots(figsize=(13, 6))
    
    days_data = data['q6']
    day_names = [d['day_name'] for d in days_data]
    totals = [d['total'] / 1000.0 for d in days_data]
    sevs = [d['avg_sev'] for d in days_data]
    is_weekend = [d['is_weekend'] for d in days_data]
    
    colors_bars = [COLORS['secondary'] if not w else COLORS['warning'] for w in is_weekend]
    
    x = np.arange(len(day_names))
    bars = ax1.bar(x, totals, width=0.55, color=colors_bars, alpha=0.85, edgecolor=COLORS['dark'])
    ax1.set_title('REQUERIMIENTO 6: Accidentalidad Semanal: Volumen vs Severidad Fin de Semana', 
                  fontsize=14, fontweight='bold', color=COLORS['dark'], pad=15)
    ax1.set_xlabel('Día de la Semana', fontsize=11)
    ax1.set_ylabel('Total de Accidentes (Miles)', fontsize=11, color=COLORS['primary'])
    ax1.set_xticks(x)
    ax1.set_xticklabels(day_names, fontsize=10, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    
    for bar, d in zip(bars, days_data):
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 15, f"{h:,.0f}k\n({d['pct']}%)", 
                 ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax1.set_ylim(0, max(totals) * 1.18)
    
    # Línea de severidad
    ax2 = ax1.twinx()
    ax2.plot(x, sevs, color=COLORS['danger'], marker='o', markersize=8, linewidth=2.5, linestyle='-', label='Severidad Promedio')
    ax2.set_ylabel('Severidad Promedio', fontsize=11, color=COLORS['danger'])
    ax2.set_ylim(2.10, 2.30)
    ax2.grid(False)
    
    for i, txt in enumerate(sevs):
        ax2.annotate(f"{txt:.2f}", (x[i], sevs[i] + 0.008), ha='center', fontsize=9, fontweight='bold', color=COLORS['danger'])
        
    # Anotación Viernes
    ax1.annotate('Pico Máximo de Accidentes\n(Viernes 1.37M)', xy=(4, totals[4]), xytext=(2.6, totals[4] + 90),
                 arrowprops=dict(facecolor=COLORS['primary'], shrink=0.08, width=1.2, headwidth=6),
                 fontweight='bold', fontsize=9, color=COLORS['primary'])
    
    # Anotación Domingo
    ax2.annotate('Mayor Severidad (2.26)\nFines de Semana', xy=(6, sevs[6]), xytext=(4.8, 2.28),
                 arrowprops=dict(facecolor=COLORS['danger'], shrink=0.08, width=1.2, headwidth=6),
                 fontweight='bold', fontsize=9, color=COLORS['danger'])
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_06_dias_semana_mas_incidentes.png')


# ------------------------------------------------------------------------------
# 7. PROMEDIO DE DURACIÓN BRUTA VS DEPURADA
# ------------------------------------------------------------------------------
def plot_q7(data):
    fig, ax = plt.subplots(figsize=(13, 6.5))
    
    dur_data = data['q7']
    labels = [f"Severidad {d['severity']}" for d in dur_data]
    raw_avgs = [d['raw_avg'] for d in dur_data]
    clean_avgs = [d['clean_avg'] for d in dur_data]
    outliers = [d['outliers'] for d in dur_data]
    pct_out = [d['pct_outliers'] for d in dur_data]
    
    x = np.arange(len(labels))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, raw_avgs, width, label='Duración Bruta con Outliers (Minutos)', color='#CBD5E1', edgecolor='#94A3B8')
    rects2 = ax.bar(x + width/2, clean_avgs, width, label='Duración Depurada (<= 24h, Minutos)', color=COLORS['primary'], edgecolor='#1E293B')
    
    ax.set_title('REQUERIMIENTO 7: Duración Promedio del Incidente: Impacto de Outliers Administrativos', 
                 fontsize=14, fontweight='bold', color=COLORS['dark'], pad=15)
    ax.set_xlabel('Nivel de Severidad', fontsize=11)
    ax.set_ylabel('Duración Media de Cierre Vial (Minutos)', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    for r in rects1:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2., h + 10, f'{h:.1f}m\n(~{h/60:.1f}h)', 
                ha='center', va='bottom', fontsize=8.5, color='#64748B', fontweight='bold')
        
    for r, o, p in zip(rects2, outliers, pct_out):
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2., h + 10, f'{h:.1f}m\n({p}% out)', 
                ha='center', va='bottom', fontsize=9, color=COLORS['primary'], fontweight='bold')
        
    ax.set_ylim(0, max(raw_avgs) * 1.25)
    
    ax.text(0.68, 0.72, '⚡ 34,981 incidentes reportaron > 24 horas\npor retraso administrativo en el cierre del ticket.\nLa depuración restaura el tiempo operacional real.', 
            transform=ax.transAxes, fontsize=9.5, bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEF3C7', edgecolor='#F59E0B'))
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_07_promedio_duracion_incidente.png')


# ------------------------------------------------------------------------------
# 8. TENDENCIAS MENSUALES Y ANUALES
# ------------------------------------------------------------------------------
def plot_q8(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('REQUERIMIENTO 8: Serie Histórica Anual (2016-2023) y Estacionalidad Mensual', 
                 fontsize=15, fontweight='bold', color=COLORS['dark'], y=1.02)
    
    # Anual
    years_data = data['q8']['by_year']
    years = [str(y['year']) for y in years_data]
    totals_yr = [y['total'] / 1000.0 for y in years_data]
    
    bars_yr = ax1.bar(years, totals_yr, color=COLORS['primary'], alpha=0.85, width=0.6, edgecolor=COLORS['dark'])
    ax1.plot(years, totals_yr, color=COLORS['danger'], marker='o', linewidth=2)
    ax1.set_title('Evolución Anual del Registro de Accidentes', fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel('Año', fontsize=11)
    ax1.set_ylabel('Total de Accidentes (Miles)', fontsize=11)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    
    for bar in bars_yr:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 25, f'{h:,.0f}k', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax1.set_ylim(0, max(totals_yr) * 1.18)
    
    # Mensual
    months_data = data['q8']['by_month']
    m_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    totals_mo = [m['total'] / 1000.0 for m in months_data]
    pcts_mo = [m['pct'] for m in months_data]
    
    ax2.plot(m_names, totals_mo, color=COLORS['secondary'], marker='s', linewidth=2.5, markersize=6)
    ax2.fill_between(m_names, totals_mo, color=COLORS['secondary'], alpha=0.15)
    ax2.set_title('Estacionalidad Mensual (Pico Festivo e Invernal en Diciembre)', fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel('Mes', fontsize=11)
    ax2.set_ylabel('Total de Accidentes (Miles)', fontsize=11)
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    # Destacar diciembre
    ax2.annotate('Pico Invernal (Diciembre)\n847k (10.96%)', xy=(11, totals_mo[11]), xytext=(8, totals_mo[11] + 40),
                 arrowprops=dict(facecolor=COLORS['danger'], shrink=0.08, width=1.2, headwidth=6),
                 fontweight='bold', fontsize=9, color=COLORS['danger'])
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_08_tendencias_mensuales_anuales.png')


# ------------------------------------------------------------------------------
# 9. TIPO DE VEHÍCULO INVOLUCRADO (NLP)
# ------------------------------------------------------------------------------
def plot_q9(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('REQUERIMIENTO 9: Accidentes por Tipo de Vehículo Involucrado (Clasificación NLP)', 
                 fontsize=15, fontweight='bold', color=COLORS['dark'], y=1.02)
    
    veh_data = data['q9']
    # Filtrar solo vehículos identificados específicamente
    identified = [v for v in veh_data if v['vehicle_type'] != 'No especificado']
    names = [v['vehicle_type'] for v in identified]
    totals = [v['total'] for v in identified]
    sevs = [v['avg_sev'] for v in identified]
    durations = [v['avg_duration'] for v in identified]
    graves = [v['pct_graves'] for v in identified]
    
    # Gráfica 1: Frecuencia de mención
    bars1 = ax1.bar(names, totals, color=COLORS['primary'], alpha=0.85, width=0.55, edgecolor=COLORS['dark'])
    ax1.set_title('Incidentes Específicos Identificados por NLP', fontsize=12, fontweight='bold', pad=10)
    ax1.set_ylabel('Total de Menciones Confirmadas', fontsize=11)
    ax1.set_xticklabels(names, rotation=15, ha='right', fontsize=9.5, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    
    for bar in bars1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 400, f'{h:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax1.set_ylim(0, max(totals) * 1.18)
    
    # Gráfica 2: Severidad y Duración
    x = np.arange(len(names))
    width = 0.35
    
    ax2.bar(x - width/2, sevs, width, label='Severidad Promedio', color=COLORS['danger'], alpha=0.85)
    ax2.set_ylabel('Severidad Promedio (1 - 4)', fontsize=11, color=COLORS['danger'])
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=15, ha='right', fontsize=9.5, fontweight='bold')
    ax2.set_ylim(1.5, 3.0)
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    
    ax2_dur = ax2.twinx()
    ax2_dur.bar(x + width/2, durations, width, label='Duración Promedio (Min)', color=COLORS['warning'], alpha=0.85)
    ax2_dur.set_ylabel('Duración de Despeje (Minutos)', fontsize=11, color=COLORS['warning'])
    ax2_dur.set_ylim(0, 150)
    ax2_dur.grid(False)
    
    lines1, lab1 = ax2.get_legend_handles_labels()
    lines2, lab2 = ax2_dur.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, lab1 + lab2, loc='upper left')
    ax2.set_title('Gravedad y Complejidad de Rescate por Categoría', fontsize=12, fontweight='bold', pad=10)
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_09_accidentes_tipo_vehiculo.png')


# ------------------------------------------------------------------------------
# 10. DISTRIBUCIÓN GEOESPACIAL Y PUNTOS CRÍTICOS
# ------------------------------------------------------------------------------
def plot_q10(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5))
    fig.suptitle('REQUERIMIENTO 10: Hotspots Geoespaciales Urbanos e Infraestructura Crítica', 
                 fontsize=15, fontweight='bold', color=COLORS['dark'], y=1.02)
    
    # Hotspots Macro
    hotspots = data['q10']['hotspots']
    labels_hs = [f"{h['city']}, {h['state']}\n({h['lat_grid']:.1f}, {h['lng_grid']:.1f})" for h in reversed(hotspots)]
    totals_hs = [h['total'] / 1000.0 for h in reversed(hotspots)]
    sevs_hs = [h['avg_sev'] for h in reversed(hotspots)]
    
    bars1 = ax1.barh(labels_hs, totals_hs, color=COLORS['danger'], alpha=0.85, height=0.65)
    ax1.set_title('Top 10 Macro-Clústeres Urbanos (Cuadrículas de 0.1°)', fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel('Accidentes Concentrados (Miles)', fontsize=11)
    ax1.grid(axis='x', linestyle='--', alpha=0.6)
    
    for bar, sev in zip(bars1, sevs_hs):
        w = bar.get_width()
        ax1.text(w + 0.8, bar.get_y() + bar.get_height()/2, f'{w:.1f}k | Sev: {sev}', 
                 va='center', ha='left', fontsize=8.5, fontweight='bold')
    ax1.set_xlim(0, max(totals_hs) * 1.25)
    
    # Infraestructura Vial
    infra = data['q10']['infra']
    infra_labels = [
        'Semáforos\n(Traffic Signal)',
        'Cruces Peatonales\n(Crossing)',
        'Enlaces Autopista\n(Junction)',
        'Señales de Pare\n(Stop)',
        'Estaciones Tránsito\n(Station)',
        'Pasos Tren\n(Railway)'
    ]
    infra_vals = [
        infra['Semaforos'] / 1000.0,
        infra['Cruces_Peatonales'] / 1000.0,
        infra['Enlaces_Autopista'] / 1000.0,
        infra['Senales_Pare'] / 1000.0,
        infra['Estaciones_Transporte'] / 1000.0,
        infra['Pasos_Nivel_Tren'] / 1000.0
    ]
    
    bars2 = ax2.bar(infra_labels, infra_vals, color=COLORS['accent'], alpha=0.85, width=0.55, edgecolor=COLORS['dark'])
    ax2.set_title('Incidentes Asociados a Elementos de Infraestructura Vial', fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylabel('Total Accidentes (Miles)', fontsize=11)
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    ax2.set_xticklabels(infra_labels, rotation=20, ha='right', fontsize=9, fontweight='semibold')
    
    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., h + 20, f'{h:,.0f}k', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax2.set_ylim(0, max(infra_vals) * 1.18)
    
    plt.tight_layout()
    guardar_grafica(fig, 'grafica_10_distribucion_geoespacial_criticos.png')


def main():
    print("=" * 80)
    print("🚀 GENERANDO LAS 10 GRÁFICAS ANALÍTICAS (SQL / PROYECTO 3)")
    print(f"   Destino: {OUTPUT_DIR}")
    print("=" * 80)
    
    data = cargar_datos()
    plot_q1(data)
    plot_q2(data)
    plot_q3(data)
    plot_q4(data)
    plot_q5(data)
    plot_q6(data)
    plot_q7(data)
    plot_q8(data)
    plot_q9(data)
    plot_q10(data)
    
    print("=" * 80)
    print("🎉 TODAS LAS 10 GRÁFICAS HAN SIDO GENERADAS EXITOSAMENTE EN ALTA RESOLUCIÓN.")
    print("=" * 80)


if __name__ == "__main__":
    main()
