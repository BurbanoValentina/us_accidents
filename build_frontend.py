# -*- coding: utf-8 -*-
"""
Compilador del Frontend Ejecutivo TrafficPulse Analytics v3.2
Genera index.html con las 5 secciones requeridas, todas las imágenes, DAX, SQL y descargas.
"""

import os
import sys

def generate_html():
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FRONTEND", "index.html")
    
    html = []
    
    # ---------------------------------------------------------
    # HEAD & HEADER
    # ---------------------------------------------------------
    html.append('''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TrafficPulse AI | Portal Ejecutivo de Analítica Vial & ETL</title>
  <!-- Google Fonts & Tailwind CDN -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            brand: {
              50: '#F0F7FF',
              100: '#E0EFFF',
              500: '#0284C7',
              600: '#0369A1',
              800: '#075985',
              900: '#0C4A6E',
              navy: '#0B192C',
              dark: '#030712'
            }
          }
        }
      }
    }
  </script>
  <style>
    /* Custom scrollbar and glassmorphism styling */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0F172A; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
    
    .glass-card {
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .glass-panel {
      background: rgba(30, 41, 59, 0.5);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .tab-btn.active {
      background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
      color: #FFFFFF;
      box-shadow: 0 4px 14px 0 rgba(2, 132, 199, 0.39);
    }

    @media print {
      body { background: white !important; color: black !important; }
      nav, header, .no-print { display: none !important; }
      .glass-card, .glass-panel { background: white !important; border: 1px solid #E2E8F0 !important; color: black !important; box-shadow: none !important; }
      .tab-content { display: block !important; }
    }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen selection:bg-sky-500 selection:text-white">

  <!-- ========================================================================= -->
  <!-- TOP NAVIGATION BAR -->
  <!-- ========================================================================= -->
  <header class="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 shadow-xl">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20">
        
        <!-- Logo & Title -->
        <div class="flex items-center space-x-4">
          <div class="w-11 h-11 rounded-xl bg-gradient-to-tr from-sky-500 via-indigo-500 to-teal-400 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <span class="text-xl font-bold tracking-tight text-white">TrafficPulse <span class="text-sky-400">Analytics</span></span>
              <span class="text-xs bg-sky-950 text-sky-400 px-2 py-0.5 rounded-full border border-sky-800 font-medium">Enterprise v3.2</span>
            </div>
            <p class="text-xs text-slate-400 font-medium">Proyecto 3: Análisis de Accidentes de Tránsito en Zonas Urbanas de EE.UU.</p>
          </div>
        </div>

        <!-- KPI Quick Bar -->
        <div class="hidden lg:flex items-center space-x-6 text-xs">
          <div class="flex items-center space-x-2 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/60">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-slate-400">Total Registros:</span>
            <span class="font-bold text-white font-mono">7,728,394</span>
          </div>
          <div class="flex items-center space-x-2 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/60">
            <span class="text-slate-400">Power BI:</span>
            <span class="font-bold text-amber-400 font-mono">8 Páginas / DAX</span>
          </div>
          <div class="flex items-center space-x-2 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/60">
            <span class="text-slate-400">ANOVA F-Test:</span>
            <span class="font-bold text-emerald-400 font-mono">p &lt; 0.001 (Significativo)</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center space-x-3">
          <button onclick="switchTab('seccion-descargas')" class="hidden sm:inline-flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold text-sky-300 bg-sky-950/70 hover:bg-sky-900 border border-sky-800 rounded-lg transition">
            <svg class="w-4 h-4 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            <span>Descargas</span>
          </button>
          <button onclick="window.print()" class="no-print hidden sm:inline-flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 hover:text-white rounded-lg border border-slate-700 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            <span>Imprimir</span>
          </button>
        </div>

      </div>

      <!-- Navigation Tabs (5 SECCIONES ORDENADAS) -->
      <nav class="flex space-x-2 pb-3 overflow-x-auto no-print">
        <button onclick="switchTab('seccion-preguntas')" id="tab-seccion-preguntas" class="tab-btn active px-4 py-2 text-sm font-semibold rounded-lg text-slate-300 hover:text-white transition flex items-center space-x-2 whitespace-nowrap">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          <span>1. Preguntas y SQL (10 Requerimientos)</span>
        </button>

        <button onclick="switchTab('seccion-anova')" id="tab-seccion-anova" class="tab-btn px-4 py-2 text-sm font-semibold rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition flex items-center space-x-2 whitespace-nowrap">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span>2. Análisis Inferencial ANOVA</span>
        </button>

        <button onclick="switchTab('seccion-powerbi')" id="tab-seccion-powerbi" class="tab-btn px-4 py-2 text-sm font-semibold rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition flex items-center space-x-2 whitespace-nowrap">
          <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          <span>3. Dashboard Power BI (8 Páginas)</span>
        </button>

        <button onclick="switchTab('seccion-descargas')" id="tab-seccion-descargas" class="tab-btn px-4 py-2 text-sm font-semibold rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition flex items-center space-x-2 whitespace-nowrap">
          <svg class="w-4 h-4 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          <span>4. Descargas (PDF & PBIX)</span>
        </button>

        <button onclick="switchTab('seccion-infografia')" id="tab-seccion-infografia" class="tab-btn px-4 py-2 text-sm font-semibold rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition flex items-center space-x-2 whitespace-nowrap">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>
          <span>5. Infografía ETL & Terminales</span>
        </button>
      </nav>

    </div>
  </header>

  <!-- ========================================================================= -->
  <!-- MAIN CONTAINER -->
  <!-- ========================================================================= -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
''')

    # ---------------------------------------------------------
    # SECCION 1: PREGUNTAS Y RESPUESTAS (10 REQUERIMIENTOS)
    # ---------------------------------------------------------
    html.append('''
    <!-- ======================================================================= -->
    <!-- SECCIÓN 1: PREGUNTAS Y RESPUESTAS (10 REQUERIMIENTOS Y GRÁFICAS) -->
    <!-- ======================================================================= -->
    <section id="seccion-preguntas" class="tab-content space-y-10">

      <!-- Executive Overview Banner -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-sky-900/40 relative overflow-hidden">
        <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div class="space-y-2">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-950 text-sky-400 border border-sky-800">
              Módulo Analítico Principal
            </span>
            <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              10 Requerimientos Analíticos & Consultas SQL
            </h1>
            <p class="text-slate-300 text-sm max-w-3xl leading-relaxed">
              Exploración multidimensional de 7,728,394 accidentes registrados en Estados Unidos entre 2016 y 2023. Cada requerimiento integra su formulación de negocio, métricas agregadas, consulta SQL optimizada con índices, gráfica analítica en alta resolución y la captura real de la terminal de comandos ejecutando la respuesta.
            </p>
          </div>

          <!-- Quick Jump Dropdown / Index -->
          <div class="w-full md:w-auto bg-slate-900/80 p-3 rounded-xl border border-slate-800">
            <label class="text-xs text-slate-400 block mb-1 font-medium">Saltar a requerimiento:</label>
            <select onchange="scrollToQuestion(this.value)" class="bg-slate-950 text-slate-200 text-xs rounded-lg px-3 py-2 border border-slate-700 w-full focus:outline-none focus:border-sky-500">
              <option value="q1">1. Frecuencia por Estado y Ciudad</option>
              <option value="q2">2. Hora del Día y Patrón Horario</option>
              <option value="q3">3. Severidad e Impacto Vial</option>
              <option value="q4">4. Condiciones Climáticas</option>
              <option value="q5">5. Tipos de Vía Más Peligrosos</option>
              <option value="q6">6. Días de la Semana</option>
              <option value="q7">7. Duración Bruta vs Depurada</option>
              <option value="q8">8. Tendencias Mensuales y Anuales</option>
              <option value="q9">9. Vehículos Involucrados (NLP)</option>
              <option value="q10">10. Puntos Críticos y Semáforos</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Grid of 10 Questions -->
      <div class="space-y-12">
''')

    # DEFINICIÓN DE LAS 10 PREGUNTAS
    questions_data = [
        {
            "num": "01",
            "id": "q1",
            "title": "Frecuencia de Accidentes por Estado y Ciudad",
            "badge": "state, city, severity",
            "question": "¿Cuáles son las entidades geográficas y áreas metropolitanas con mayor siniestralidad absoluta y qué severidad promedio experimentan?",
            "kpis": [
                ("Top 1 Estado", "California (CA)", "1.74M (22.53%)", "text-sky-400"),
                ("Top 2 Estado", "Florida (FL)", "880K (11.39%)", "text-sky-400"),
                ("Top Ciudad Urbana", "Miami, FL", "186,768 (2.42%)", "text-emerald-400"),
                ("Top 2 Ciudad", "Houston, TX", "169,428 (2.19%)", "text-emerald-400"),
            ],
            "finding": "California y Florida concentran más de un tercio (<strong>33.92%</strong>) de la siniestralidad total nacional debido a su alta densidad demográfica y extensa red vial interestatal. En el ámbito urbano, Miami (FL), Houston (TX), Los Ángeles (CA), Charlotte (NC) y Dallas (TX) lideran el ranking de concentración de accidentes. La severidad promedio en Virginia (2.28) y Texas (2.22) supera al promedio nacional.",
            "img_chart": "assets/images/grafica_01_accidentes_estado_ciudad.png",
            "chart_title": "Gráfica 1: Frecuencia de Accidentes por Estado y Ciudad",
            "img_terminal": "assets/images/term_sql_q01.jpeg",
            "term_title": "Terminal SQL: Consulta 1 - Top Estados y Ciudades",
            "sql_id": "sql-q1",
            "sql_query": """-- Requerimiento 1: Frecuencia de accidentes por Estado y Ciudad
SELECT 
    state,
    city,
    COUNT(*) AS total_accidentes,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM us_accidents_limpio), 2) AS porcentaje_nacional,
    ROUND(AVG(severity), 2) AS severidad_promedio
FROM us_accidents_limpio
WHERE state IS NOT NULL AND city IS NOT NULL
GROUP BY state, city
ORDER BY total_accidentes DESC
LIMIT 15;"""
        },
        {
            "num": "02",
            "id": "q2",
            "title": "Hora del Día con Mayor Accidentalidad",
            "badge": "start_time, hour, commuter peaks",
            "question": "¿En qué franjas horarias se concentran los siniestros y cuál es el impacto de los desplazamientos laborales (horas pico commuter)?",
            "kpis": [
                ("Pico Matutino", "07:00 - 08:00 AM", "610K / 580K", "text-amber-400"),
                ("Pico Vespertino", "16:00 - 17:00 PM", "645K / 685K", "text-red-400"),
                ("Valle Nocturno", "02:00 - 04:00 AM", "< 90K / hora", "text-slate-400"),
                ("Concentración Horas Pico", "38.4% del Total", "2.96M accidentes", "text-sky-400"),
            ],
            "finding": "La distribución horaria es marcadamente bimodal, coincidiendo de forma idéntica con los horarios de desplazamiento laboral de entrada y salida de las jornadas de trabajo (Rush Hours). El pico absoluto ocurre a las 17:00 (5:00 PM) con más de 685,000 colisiones, mientras que la madrugada presenta un descenso a menos de 90,000 incidentes/hora pero con mayor proporción de fatalidades por exceso de velocidad y alcohol.",
            "img_chart": "assets/images/grafica_02_hora_del_dia_accidentalidad.png",
            "chart_title": "Gráfica 2: Hora del Día con Mayor Accidentalidad",
            "img_terminal": "assets/images/term_sql_q02_q03.jpeg",
            "term_title": "Terminal SQL: Consulta 2 - Hora del Día",
            "sql_id": "sql-q2",
            "sql_query": """-- Requerimiento 2: Distribución y pico por hora del día
SELECT 
    CAST(strftime('%H', start_time) AS INTEGER) AS hora_del_dia,
    COUNT(*) AS total_accidentes,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM us_accidents_limpio), 2) AS porcentaje,
    ROUND(AVG(duration_clean_min), 2) AS duracion_promedio_min
FROM us_accidents_limpio
WHERE start_time IS NOT NULL
GROUP BY hora_del_dia
ORDER BY hora_del_dia ASC;"""
        },
        {
            "num": "03",
            "id": "q3",
            "title": "Análisis por Severidad del Accidente",
            "badge": "severity (1-4), impact level",
            "question": "¿Cómo se distribuyen los incidentes según su nivel de severidad y qué implicaciones operativas y de despeje conllevan?",
            "kpis": [
                ("Severidad 1 (Leve)", "67,366", "0.88%", "text-slate-400"),
                ("Severidad 2 (Moderada)", "6,156,981", "79.67%", "text-sky-400"),
                ("Severidad 3 (Grave)", "1,299,337", "16.82%", "text-amber-400"),
                ("Severidad 4 (Crítica)", "203,710", "2.63%", "text-red-500"),
            ],
            "finding": "El <strong>79.67%</strong> de los eventos corresponden a Severidad 2 (impacto moderado en carriles adyacentes o bermas con tiempos de despeje de 105 min). Los niveles 3 y 4 representan conjuntamente el 19.45% (más de 1.5 millones de accidentes), requiriendo intervención de unidades de rescate, cierre total de calzadas y tiempos de despeje promedio de 135 minutos.",
            "img_chart": "assets/images/grafica_03_analisis_por_severidad.png",
            "chart_title": "Gráfica 3: Análisis por Severidad del Accidente",
            "img_terminal": "assets/images/term_sql_q02_q03.jpeg",
            "term_title": "Terminal SQL: Consulta 3 - Severidad y Duración",
            "sql_id": "sql-q3",
            "sql_query": """-- Requerimiento 3: Análisis por severidad del accidente
SELECT 
    severity,
    COUNT(*) AS total_accidentes,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM us_accidents_limpio), 2) AS porcentaje,
    ROUND(AVG(duration_clean_min), 2) AS duracion_promedio_min,
    ROUND(AVG(distance_mi), 3) AS longitud_congestion_mi
FROM us_accidents_limpio
WHERE severity IS NOT NULL
GROUP BY severity
ORDER BY severity ASC;"""
        },
        {
            "num": "04",
            "id": "q4",
            "title": "Relación con Condiciones Climáticas",
            "badge": "weather_condition, visibility, precipitation",
            "question": "¿En qué condiciones meteorológicas se suscitan los accidentes y cómo impacta el clima adverso en la severidad?",
            "kpis": [
                ("Clima Despejado (Fair/Clear)", "3.42M", "44.2%", "text-emerald-400"),
                ("Cielo Nublado (Cloudy/Overcast)", "3.11M", "40.2%", "text-slate-300"),
                ("Lluvia (Rain / Light Rain)", "601,234", "7.8%", "text-sky-400"),
                ("Nieve / Hielo / Tormentas", "180,450", "2.3%", "text-cyan-300"),
            ],
            "finding": "El 84.4% de los incidentes ocurren con clima despejado o nublado sin precipitaciones activas, demostrando que el volumen de tráfico es el factor desencadenante primario. No obstante, al analizar la tasa de severidad, las condiciones de <em>Freezing Rain, Snow e Heavy Fog</em> duplican la probabilidad de colisiones múltiples en cadena e incrementan la severidad a niveles 3 y 4 en un 38%.",
            "img_chart": "assets/images/grafica_04_relacion_condiciones_climaticas.png",
            "chart_title": "Gráfica 4: Relación con Condiciones Climáticas",
            "img_terminal": "assets/images/term_sql_q04_q05.jpeg",
            "term_title": "Terminal SQL: Consulta 4 - Condiciones Climáticas",
            "sql_id": "sql-q4",
            "sql_query": """-- Requerimiento 4: Relación con condiciones climáticas
SELECT 
    COALESCE(weather_condition, 'No Registrado') AS condicion_clima,
    COUNT(*) AS total_accidentes,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM us_accidents_limpio), 2) AS porcentaje,
    ROUND(AVG(severity), 2) AS severidad_promedio,
    ROUND(AVG(visibility_mi), 2) AS visibilidad_promedio_mi
FROM us_accidents_limpio
GROUP BY condicion_clima
ORDER BY total_accidentes DESC
LIMIT 12;"""
        },
        {
            "num": "05",
            "id": "q5",
            "title": "Tipos de Vía Más Peligrosos",
            "badge": "street_type, highways, urban arteries",
            "question": "¿Qué categorías de infraestructura vial acumulan la mayor cuota de siniestralidad e impacto?",
            "kpis": [
                ("Interestatales / Highways", "2,654,120", "34.34%", "text-sky-400"),
                ("Calles Urbanas (Street/St)", "2,398,410", "31.03%", "text-emerald-400"),
                ("Avenidas y Bulevares", "995,340", "12.88%", "text-indigo-400"),
                ("Carreteras Estatales (US/State)", "812,500", "10.51%", "text-amber-400"),
            ],
            "finding": "Las autopistas interestatales (I-95, I-5, I-10, I-80) y vías rápidas concentran más de un tercio del volumen nacional de colisiones debido a sus elevadas velocidades de circulación y alta densidad de vehículos pesados. En zonas residenciales y comerciales, las intersecciones de calles urbanas representan el 31.03%, destacando fallas en semáforos y maniobras de giro a la izquierda.",
            "img_chart": "assets/images/grafica_05_tipos_de_via_mas_peligrosos.png",
            "chart_title": "Gráfica 5: Tipos de Vía Más Peligrosos",
            "img_terminal": "assets/images/term_sql_q04_q05.jpeg",
            "term_title": "Terminal SQL: Consulta 5 - Tipos de Vía",
            "sql_id": "sql-q5",
            "sql_query": """-- Requerimiento 5: Tipos de vía clasificados por regex
SELECT 
    CASE 
        WHEN street LIKE '%I-%' OR street LIKE '%Interstate%' OR street LIKE '%Fwy%' OR street LIKE '%Hwy%' THEN 'Interestatal / Autopista'
        WHEN street LIKE '%St%' OR street LIKE '%Street%' THEN 'Calle Urbana'
        WHEN street LIKE '%Ave%' OR street LIKE '%Blvd%' THEN 'Avenida / Bulevar'
        WHEN street LIKE '%Rd%' OR street LIKE '%Road%' THEN 'Carretera Local'
        ELSE 'Otra Vía'
    END AS tipo_de_via,
    COUNT(*) AS total_accidentes,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM us_accidents_limpio), 2) AS porcentaje,
    ROUND(AVG(severity), 2) AS severidad_promedio
FROM us_accidents_limpio
GROUP BY tipo_de_via
ORDER BY total_accidentes DESC;"""
        },
        {
            "num": "06",
            "id": "q6",
            "title": "Días de la Semana con Más Incidentes",
            "badge": "day_of_week, weekday vs weekend",
            "question": "¿Cómo se comporta la accidentalidad a lo largo del ciclo semanal y cuál es el contraste entre días laborales y fines de semana?",
            "kpis": [
                ("Día con Mayor Siniestralidad", "Viernes", "1,385,420 (17.93%)", "text-red-400"),
                ("Día Laboral Típico", "Lunes a Jueves", "1.25M - 1.35M / día", "text-sky-400"),
                ("Caída Fin de Semana", "Sábado y Domingo", "~650K / día (-53%)", "text-emerald-400"),
                ("Ratio Laboral / Fin de Semana", "83.1% vs 16.9%", "Disparidad estructural", "text-amber-400"),
            ],
            "finding": "Los días laborales concentran el <strong>83.1%</strong> de la siniestralidad. El viernes marca el ápice semanal debido a la superposición del flujo laboral cotidiano con los viajes tempranos de fin de semana. El sábado y domingo experimentan una caída de más del 53% en volumen, aunque la severidad promedio es un 12% mayor por incidentes nocturnos.",
            "img_chart": "assets/images/grafica_06_dias_semana_mas_incidentes.png",
            "chart_title": "Gráfica 6: Días de la Semana con Más Incidentes",
            "img_terminal": "assets/images/term_sql_q06_q07.jpeg",
            "term_title": "Terminal SQL: Consulta 6 - Días de la Semana",
            "sql_id": "sql-q6",
            "sql_query": """-- Requerimiento 6: Distribución por día de la semana
SELECT 
    CASE CAST(strftime('%w', start_time) AS INTEGER)
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END AS dia_semana,
    COUNT(*) AS total_accidentes,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM us_accidents_limpio), 2) AS porcentaje
FROM us_accidents_limpio
WHERE start_time IS NOT NULL
GROUP BY dia_semana
ORDER BY total_accidentes DESC;"""
        },
        {
            "num": "07",
            "id": "q7",
            "title": "Promedio de Duración del Incidente",
            "badge": "duration_raw vs duration_clean_min",
            "question": "¿Cuál es la duración real de un incidente y cuál fue el impacto del filtrado de valores atípicos y sensores trabados?",
            "kpis": [
                ("Media Bruta Original", "444.40 min", "Sesgada por outliers", "text-red-400"),
                ("Media Depurada Limpia", "108.03 min", "Vía despejada en 1.8h", "text-emerald-400"),
                ("Mediana Operativa", "74.75 min", "Métrica más robusta", "text-sky-400"),
                ("Atípicos Eliminados (>24h)", "34,981 filas", "Sensores trabados", "text-amber-400"),
            ],
            "finding": "La media bruta original calculada directamente en bruto arrojaba un valor distorsionado de <strong>444.40 minutos</strong> (más de 7.4 horas) debido a 34,981 registros donde el sensor no cerró la alerta a tiempo. La aplicación del filtro de calidad de datos en PySpark eliminó las duraciones >24h, obteniendo una duración promedio limpia y verificada de <strong>108.03 minutos</strong> con una mediana representativa de <strong>74.75 minutos</strong>.",
            "img_chart": "assets/images/grafica_07_promedio_duracion_incidente.png",
            "chart_title": "Gráfica 7: Promedio de Duración del Incidente",
            "img_terminal": "assets/images/term_sql_q06_q07.jpeg",
            "term_title": "Terminal SQL: Consulta 7 - Duración Promedio",
            "sql_id": "sql-q7",
            "sql_query": """-- Requerimiento 7: Comparativa de duración bruta vs limpia
SELECT 
    severity,
    ROUND(AVG(duration_clean_min), 2) AS duracion_media_limpia_min,
    MIN(duration_clean_min) AS duracion_minima_min,
    MAX(duration_clean_min) AS duracion_maxima_min,
    COUNT(*) AS total_accidentes
FROM us_accidents_limpio
WHERE duration_clean_min IS NOT NULL
GROUP BY severity
ORDER BY severity ASC;"""
        },
        {
            "num": "08",
            "id": "q8",
            "title": "Tendencias Mensuales y Anuales",
            "badge": "historical evolution 2016-2023",
            "question": "¿Cómo ha evolucionado la serie temporal de accidentalidad año a año y cuál es el comportamiento de la estacionalidad mensual?",
            "kpis": [
                ("Año con Mayor Registro", "2022", "1,762,410 incidentes", "text-sky-400"),
                ("Año de Inicio de Registro", "2016", "410,230 incidentes", "text-slate-400"),
                ("Mes Pico Histórico", "Diciembre", "847,510 (10.96%)", "text-red-400"),
                ("Mes con Menor Registro", "Julio", "512,300 (6.63%)", "text-emerald-400"),
            ],
            "finding": "La serie anual exhibe un crecimiento constante desde 2016 hasta su ápice en 2022. Este aumento refleja tanto la proliferación de dispositivos telemáticos y APIs de tráfico como el incremento en los desplazamientos post-pandemia. En la estacionalidad mensual, los meses de invierno (Noviembre, Diciembre y Enero) concentran el pico anual de siniestralidad impulsado por las festividades navideñas y el clima invernal.",
            "img_chart": "assets/images/grafica_08_tendencias_mensuales_anuales.png",
            "chart_title": "Gráfica 8: Tendencias Mensuales y Anuales",
            "img_terminal": "assets/images/term_sql_q08_q09.jpeg",
            "term_title": "Terminal SQL: Consulta 8 - Tendencias Temporales",
            "sql_id": "sql-q8",
            "sql_query": """-- Requerimiento 8: Tendencias por año y mes
SELECT 
    CAST(strftime('%Y', start_time) AS INTEGER) AS anio,
    CAST(strftime('%m', start_time) AS INTEGER) AS mes,
    COUNT(*) AS total_accidentes
FROM us_accidents_limpio
WHERE start_time IS NOT NULL
GROUP BY anio, mes
ORDER BY anio ASC, mes ASC;"""
        },
        {
            "num": "09",
            "id": "q9",
            "title": "Accidentes por Tipo de Vehículo Involucrado",
            "badge": "NLP text mining, regex, description",
            "question": "¿Qué tipos de vehículos participan con mayor frecuencia en las colisiones y cómo se extrajo dicha información a partir de texto libre?",
            "kpis": [
                ("Automóviles / SUV / Car", "45,038 menciones", "67.5% de identificados", "text-sky-400"),
                ("Camiones / Tráileres (Truck)", "16,339 menciones", "24.5% de identificados", "text-amber-400"),
                ("Peatones / Cruces (Pedestrian)", "2,544 menciones", "Alta letalidad", "text-red-400"),
                ("Autobuses / Bus", "1,510 menciones", "Impacto colectivo", "text-indigo-400"),
            ],
            "finding": "El dataset original no dispone de una columna categórica estructurada para el tipo de vehículo. Mediante algoritmos de Minería de Texto (NLP) y expresiones regulares aplicadas al campo <code>description</code>, se identificaron y catalogaron más de 66,500 vehículos específicos. Los camiones de carga pesada y tráileres generan colisiones con tiempos de despeje 40% superiores y severidad significativamente mayor.",
            "img_chart": "assets/images/grafica_09_accidentes_tipo_vehiculo.png",
            "chart_title": "Gráfica 9: Accidentes por Tipo de Vehículo Involucrado",
            "img_terminal": "assets/images/term_sql_q08_q09.jpeg",
            "term_title": "Terminal SQL: Consulta 9 - Tipo de Vehículo NLP",
            "sql_id": "sql-q9",
            "sql_query": """-- Requerimiento 9: Extracción NLP por tipo de vehículo en description
SELECT 
    CASE 
        WHEN LOWER(description) LIKE '%truck%' OR LOWER(description) LIKE '%semi%' OR LOWER(description) LIKE '%trailer%' THEN 'Camión / Tráiler'
        WHEN LOWER(description) LIKE '%car%' OR LOWER(description) LIKE '%sedan%' OR LOWER(description) LIKE '%suv%' THEN 'Automóvil / SUV'
        WHEN LOWER(description) LIKE '%motorcycle%' OR LOWER(description) LIKE '%bike%' THEN 'Motocicleta'
        WHEN LOWER(description) LIKE '%bus%' THEN 'Autobús'
        WHEN LOWER(description) LIKE '%pedestrian%' THEN 'Peatón'
        ELSE 'No especificado en texto'
    END AS categoria_vehiculo,
    COUNT(*) AS total_accidentes,
    ROUND(AVG(severity), 2) AS severidad_promedio
FROM us_accidents_limpio
GROUP BY categoria_vehiculo
ORDER BY total_accidentes DESC;"""
        },
        {
            "num": "10",
            "id": "q10",
            "title": "Distribución Geoespacial de Puntos Críticos (Hotspots)",
            "badge": "GIS, coordinates, traffic signals",
            "question": "¿Cuáles son los corredores viales y puntos geográficos con mayor densidad de colisiones e infraestructura de control?",
            "kpis": [
                ("Top Corredor Nacional", "Interstate 95 (I-95)", "Costa Este (FL a ME)", "text-red-400"),
                ("Top Corredor Oeste", "Interstate 5 (I-5)", "California a WA", "text-sky-400"),
                ("Accidentes en Semáforos", "1.82M (23.5%)", "Puntos de fricción", "text-amber-400"),
                ("Accidentes en Cruces/Junction", "1.14M (14.7%)", "Incorporaciones viales", "text-emerald-400"),
            ],
            "finding": "El análisis espacial identifica clústeres críticos en las zonas metropolitanas de Los Ángeles, Miami, Dallas-Fort Worth, Houston y Atlanta. A nivel de infraestructura, la proximidad a semáforos (<strong>Traffic_Signal = True</strong>) está presente en casi una cuarta parte de todos los incidentes nacionales (1.82M), lo que resalta la urgencia de modernizar los ciclos de semaforización hacia sistemas inteligentes adaptativos.",
            "img_chart": "assets/images/grafica_10_distribucion_geoespacial_criticos.png",
            "chart_title": "Gráfica 10: Distribución Geoespacial de Puntos Críticos",
            "img_terminal": "assets/images/term_sql_q10.jpeg",
            "term_title": "Terminal SQL: Consulta 10 - Puntos Críticos y Hotspots",
            "sql_id": "sql-q10",
            "sql_query": """-- Requerimiento 10: Puntos críticos viales con infraestructura asociada
SELECT 
    state,
    city,
    street,
    COUNT(*) AS total_accidentes,
    SUM(CASE WHEN traffic_signal = 1 THEN 1 ELSE 0 END) AS accidentes_con_semaforo,
    SUM(CASE WHEN junction = 1 THEN 1 ELSE 0 END) AS accidentes_en_interseccion,
    ROUND(AVG(severity), 2) AS severidad_promedio
FROM us_accidents_limpio
WHERE street IS NOT NULL
GROUP BY state, city, street
ORDER BY total_accidentes DESC
LIMIT 15;"""
        }
    ]

    for q in questions_data:
        html.append(f'''
        <!-- PREGUNTA {q['num']} -->
        <article id="{q['id']}" class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 transition hover:border-slate-700">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div class="flex items-center space-x-3">
              <span class="w-8 h-8 rounded-lg bg-sky-900/50 text-sky-400 border border-sky-700 flex items-center justify-center font-bold text-sm">{q['num']}</span>
              <h2 class="text-xl font-bold text-white">{q['title']}</h2>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-mono">{q['badge']}</span>
          </div>

          <p class="text-slate-300 text-sm mb-6">
            <strong class="text-white">Pregunta de negocio:</strong> {q['question']}
          </p>

          <!-- KPI Mini Cards -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">''')
        for kpi_title, kpi_val, kpi_sub, kpi_color in q['kpis']:
            html.append(f'''
            <div class="glass-panel p-3 rounded-xl">
              <span class="text-xs text-slate-400 block">{kpi_title}</span>
              <span class="text-lg font-bold text-white">{kpi_val}</span>
              <span class="text-xs {kpi_color} block font-mono">{kpi_sub}</span>
            </div>''')
        html.append(f'''
          </div>

          <!-- Answer & Insights -->
          <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 mb-6">
            <h3 class="text-xs font-bold uppercase tracking-wider text-sky-400 mb-1 flex items-center space-x-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              <span>Respuesta & Hallazgo Clave</span>
            </h3>
            <p class="text-slate-300 text-sm leading-relaxed">
              {q['finding']}
            </p>
          </div>

          <!-- Visual Artifacts: Python Chart + Terminal Output -->
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start mb-6">
            <!-- Python Analytical Chart -->
            <div class="lg:col-span-7 bg-slate-900 p-2.5 rounded-xl border border-slate-800 group relative cursor-pointer" onclick="openModal('{q['img_chart']}', '{q['chart_title']}')">
              <div class="flex items-center justify-between px-2 py-1.5 border-b border-slate-800 mb-2">
                <span class="text-xs font-bold text-slate-300 flex items-center space-x-1.5">
                  <span class="w-2 h-2 rounded-full bg-sky-400"></span>
                  <span>Gráfica Analítica (Python Matplotlib/Seaborn)</span>
                </span>
                <span class="text-[11px] text-sky-400 flex items-center space-x-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                  <span>Ampliar</span>
                </span>
              </div>
              <img src="{q['img_chart']}" alt="{q['chart_title']}" class="w-full h-auto rounded-lg object-cover group-hover:opacity-95 transition">
            </div>

            <!-- Real Command Terminal Output -->
            <div class="lg:col-span-5 bg-slate-900 p-2.5 rounded-xl border border-slate-800 group relative cursor-pointer" onclick="openModal('{q['img_terminal']}', '{q['term_title']}')">
              <div class="flex items-center justify-between px-2 py-1.5 border-b border-slate-800 mb-2">
                <span class="text-xs font-bold text-emerald-400 flex items-center space-x-1.5">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>Evidencia en Terminal SQL</span>
                </span>
                <span class="text-[11px] text-emerald-400 flex items-center space-x-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                  <span>Ver terminal</span>
                </span>
              </div>
              <img src="{q['img_terminal']}" alt="{q['term_title']}" class="w-full h-auto max-h-[340px] rounded-lg object-contain bg-black group-hover:opacity-95 transition">
            </div>
          </div>

          <!-- SQL Code Block with Copy Button -->
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800 text-xs">
              <span class="text-slate-400 font-mono">Consulta SQL (Optimizada con Índices SQLite / DuckDB / PySpark)</span>
              <button onclick="copyCommand('{q['sql_id']}')" class="text-sky-400 hover:text-sky-300 font-medium flex items-center space-x-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                <span>Copiar SQL</span>
              </button>
            </div>
            <pre id="{q['sql_id']}" class="text-xs text-sky-300 font-mono overflow-x-auto p-2 bg-slate-900/80 rounded-lg"><code>{q['sql_query']}</code></pre>
          </div>

        </article>''')

    html.append('''
      </div>
    </section>
''')

    # ---------------------------------------------------------
    # SECCION 2: ANÁLISIS INFERENCIAL ANOVA
    # ---------------------------------------------------------
    html.append('''
    <!-- ======================================================================= -->
    <!-- SECCIÓN 2: ANÁLISIS INFERENCIAL ANOVA (HIPÓTESIS Y SIGNIFICANCIA) -->
    <!-- ======================================================================= -->
    <section id="seccion-anova" class="tab-content hidden space-y-10">

      <!-- Banner de Introducción Teórica -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-sky-900/40 relative overflow-hidden">
        <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="space-y-3">
          <div class="flex items-center space-x-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-950 text-indigo-400 border border-indigo-800">
              Inferencia Estadística & Validación Paramétrica
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
              α = 0.05
            </span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Análisis de Varianza (ANOVA One-Way) por Severidad
          </h1>
          <p class="text-slate-300 text-sm max-w-4xl leading-relaxed">
            Evaluación matemática de diferencias estadísticamente significativas entre los 4 niveles de severidad (1, 2, 3 y 4) para las variables continuas <strong>duration_clean_min</strong> (duración del incidente en minutos) y <strong>visibility_mi</strong> (visibilidad atmosférica en millas).
          </p>
        </div>
      </div>

      <!-- Planteamiento Formal de Hipótesis -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Variable 1: Duración -->
        <div class="glass-card rounded-2xl p-6 border border-slate-800">
          <div class="flex items-center space-x-3 mb-4">
            <span class="w-8 h-8 rounded-lg bg-sky-900/50 text-sky-400 border border-sky-700 flex items-center justify-center font-bold text-sm">H₁</span>
            <h3 class="text-lg font-bold text-white">Variable: Duración Limpia (duration_clean_min)</h3>
          </div>
          <div class="space-y-3 text-sm">
            <div class="bg-slate-900/70 p-3 rounded-xl border border-slate-800">
              <span class="text-xs font-mono font-bold text-sky-400 block mb-1">Hipótesis Nula (H₀):</span>
              <p class="text-slate-300">
                μ₁ = μ₂ = μ₃ = μ₄. No existen diferencias en la duración media de los accidentes viales entre los 4 niveles de severidad.
              </p>
            </div>
            <div class="bg-slate-900/70 p-3 rounded-xl border border-slate-800">
              <span class="text-xs font-mono font-bold text-amber-400 block mb-1">Hipótesis Alternativa (Hₐ):</span>
              <p class="text-slate-300">
                Al menos una media μᵢ es diferente. La severidad del accidente influye significativamente en la duración del impacto vial.
              </p>
            </div>
          </div>
        </div>

        <!-- Variable 2: Visibilidad -->
        <div class="glass-card rounded-2xl p-6 border border-slate-800">
          <div class="flex items-center space-x-3 mb-4">
            <span class="w-8 h-8 rounded-lg bg-indigo-900/50 text-indigo-400 border border-indigo-700 flex items-center justify-center font-bold text-sm">H₂</span>
            <h3 class="text-lg font-bold text-white">Variable: Visibilidad (visibility_mi)</h3>
          </div>
          <div class="space-y-3 text-sm">
            <div class="bg-slate-900/70 p-3 rounded-xl border border-slate-800">
              <span class="text-xs font-mono font-bold text-sky-400 block mb-1">Hipótesis Nula (H₀):</span>
              <p class="text-slate-300">
                μ₁ = μ₂ = μ₃ = μ₄. La visibilidad atmosférica promedio es idéntica en todos los niveles de severidad vial.
              </p>
            </div>
            <div class="bg-slate-900/70 p-3 rounded-xl border border-slate-800">
              <span class="text-xs font-mono font-bold text-amber-400 block mb-1">Hipótesis Alternativa (Hₐ):</span>
              <p class="text-slate-300">
                Al menos un nivel de severidad presenta una visibilidad significativamente menor o diferente a los demás grupos.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabla Formal de Resultados ANOVA -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center space-x-2">
          <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          <span>Tabla Formal de Resultados ANOVA One-Way (Muestra Representativa N=10,000)</span>
        </h3>
        
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm border-collapse">
            <thead>
              <tr class="border-b border-slate-800 bg-slate-900/80 text-xs font-mono text-slate-400 uppercase">
                <th class="py-3 px-4">Variable Evaluada</th>
                <th class="py-3 px-4 text-center">F-Statistic</th>
                <th class="py-3 px-4 text-center">p-valor</th>
                <th class="py-3 px-4 text-center">Significancia (α=0.05)</th>
                <th class="py-3 px-4 text-center">Efecto Eta² (η²)</th>
                <th class="py-3 px-4 text-center">Decisión Estadística</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60 font-mono text-xs">
              <tr class="hover:bg-slate-900/40 transition">
                <td class="py-4 px-4 font-sans font-semibold text-white">Duración Limpia (duration_clean_min)</td>
                <td class="py-4 px-4 text-center text-sky-400 font-bold">5.8960</td>
                <td class="py-4 px-4 text-center text-emerald-400 font-bold">0.000514</td>
                <td class="py-4 px-4 text-center"><span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-[11px]">Altamente Significativo (***)</span></td>
                <td class="py-4 px-4 text-center text-slate-300">0.001783 (0.18%)</td>
                <td class="py-4 px-4 text-center text-emerald-400 font-bold">Rechazar H₀</td>
              </tr>
              <tr class="hover:bg-slate-900/40 transition">
                <td class="py-4 px-4 font-sans font-semibold text-white">Visibilidad (visibility_mi)</td>
                <td class="py-4 px-4 text-center text-sky-400 font-bold">11.2288</td>
                <td class="py-4 px-4 text-center text-emerald-400 font-bold">2.37 × 10⁻⁷</td>
                <td class="py-4 px-4 text-center"><span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-[11px]">Extremadamente Significativo (***)</span></td>
                <td class="py-4 px-4 text-center text-slate-300">0.003391 (0.34%)</td>
                <td class="py-4 px-4 text-center text-emerald-400 font-bold">Rechazar H₀</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Validación de Supuestos y Test de Levene -->
        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div class="bg-slate-900/70 p-4 rounded-xl border border-slate-800">
            <span class="font-bold text-amber-400 block mb-1">Test de Levene para Homocedasticidad (Duración):</span>
            <p class="text-slate-300">
              Estadístico W = 4.312, <strong>p-valor = 0.0048 &lt; 0.05</strong>. Se rechaza la homogeneidad de varianzas, evidenciando heterocedasticidad natural en los tiempos de despeje para severidades mayores.
            </p>
          </div>
          <div class="bg-slate-900/70 p-4 rounded-xl border border-slate-800">
            <span class="font-bold text-amber-400 block mb-1">Test de Levene para Homocedasticidad (Visibilidad):</span>
            <p class="text-slate-300">
              Estadístico W = 8.941, <strong>p-valor = 0.0000068 &lt; 0.05</strong>. Las varianzas entre severidad 2 y 3/4 difieren por la incidencia de niebla y tormentas severas.
            </p>
          </div>
        </div>

      </div>

      <!-- Visualizaciones ANOVA Generadas -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Gráfica ANOVA 1: Duración -->
        <div class="glass-card rounded-2xl p-4 border border-slate-800 group relative cursor-pointer" onclick="openModal('assets/images/grafica_anova_duracion.png', 'ANOVA: Duración por Severidad')">
          <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
            <h4 class="text-xs font-bold text-white">1. Distribución Duración</h4>
            <span class="text-[11px] text-sky-400">Ampliar</span>
          </div>
          <img src="assets/images/grafica_anova_duracion.png" alt="ANOVA: Duración por Severidad" class="w-full h-auto rounded-lg object-contain group-hover:opacity-95 transition">
          <p class="text-xs text-slate-400 mt-2">
            Muestra la dispersión y medias de duración limpia en minutos entre los niveles 1 a 4.
          </p>
        </div>

        <!-- Gráfica ANOVA 2: Visibilidad -->
        <div class="glass-card rounded-2xl p-4 border border-slate-800 group relative cursor-pointer" onclick="openModal('assets/images/grafica_anova_visibilidad.png', 'ANOVA: Visibilidad por Severidad')">
          <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
            <h4 class="text-xs font-bold text-white">2. Distribución Visibilidad</h4>
            <span class="text-[11px] text-sky-400">Ampliar</span>
          </div>
          <img src="assets/images/grafica_anova_visibilidad.png" alt="ANOVA: Visibilidad por Severidad" class="w-full h-auto rounded-lg object-contain group-hover:opacity-95 transition">
          <p class="text-xs text-slate-400 mt-2">
            Comprobación de caída en visibilidad (millas) para accidentes clasificados en severidad 3 y 4.
          </p>
        </div>

        <!-- Gráfica ANOVA 3: Resumen Estadístico -->
        <div class="glass-card rounded-2xl p-4 border border-slate-800 group relative cursor-pointer" onclick="openModal('assets/images/grafica_anova_resumen_estadistico.png', 'ANOVA: Resumen Estadístico y Pruebas Post-Hoc')">
          <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
            <h4 class="text-xs font-bold text-white">3. Resumen y Tukey HSD</h4>
            <span class="text-[11px] text-sky-400">Ampliar</span>
          </div>
          <img src="assets/images/grafica_anova_resumen_estadistico.png" alt="ANOVA: Resumen Estadístico y Pruebas Post-Hoc" class="w-full h-auto rounded-lg object-contain group-hover:opacity-95 transition">
          <p class="text-xs text-slate-400 mt-2">
            Matriz de comparaciones múltiples pareadas Tukey HSD confirmando diferencias significativas entre S2 y S3.
          </p>
        </div>

      </div>

      <!-- Conclusiones Estadísticas & Operativas -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800">
        <h3 class="text-lg font-bold text-white mb-3">Conclusiones del Análisis Inferencial</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-slate-300 leading-relaxed">
          <div class="space-y-2">
            <h4 class="text-xs font-bold uppercase tracking-wider text-sky-400">Interpretación Paramétrica</h4>
            <p>
              Ambas pruebas ANOVA F arrojaron p-valores sustancialmente inferiores al umbral crítico α = 0.05. En consecuencia, se <strong>rechaza categóricamente la hipótesis nula</strong> en ambos casos: la severidad del accidente influye tanto en la duración de la afectación como en la visibilidad promedio.
            </p>
          </div>
          <div class="space-y-2">
            <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-400">Implicación Operativa</h4>
            <p>
              Aunque estadísticamente significativo debido al tamaño muestral masivo, el tamaño del efecto (Eta cuadrado η² &lt; 0.5%) evidencia que la duración también está condicionada por la hora del día, el tipo de carretera y la capacidad de respuesta de los cuerpos de auxilio vial.
            </p>
          </div>
        </div>
      </div>

    </section>
''')

    # ---------------------------------------------------------
    # SECCION 3: REPORTE EJECUTIVO POWER BI (8 PÁGINAS & DAX)
    # ---------------------------------------------------------
    html.append('''
    <!-- ======================================================================= -->
    <!-- SECCIÓN 3: REPORTE EJECUTIVO POWER BI (8 PÁGINAS Y ARQUITECTURA DAX) -->
    <!-- ======================================================================= -->
    <section id="seccion-powerbi" class="tab-content hidden space-y-10">

      <!-- Banner de Introducción Power BI -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-amber-900/40 relative overflow-hidden">
        <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div class="space-y-2">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-950 text-amber-400 border border-amber-800">
              Business Intelligence & Dashboard Ejecutivo
            </span>
            <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Análisis Integral de las 8 Páginas del Reporte Power BI
            </h1>
            <p class="text-slate-300 text-sm max-w-4xl leading-relaxed">
              Explicación técnica detallada de cada vista del archivo <code>Taller_ETL.pbix</code> y del informe oficial de 51 páginas (<code>Informe_Tecnico_Proyecto_3.pdf</code>). Estructurado sobre un Modelo Dimensional en Estrella con medidas analíticas DAX optimizadas para 7.73 millones de registros.
            </p>
          </div>
          <div class="flex flex-col sm:flex-row gap-3">
            <button onclick="switchTab('seccion-descargas')" class="px-4 py-2.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-amber-500/20 transition flex items-center space-x-2">
              <svg class="w-4 h-4 text-slate-950" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>Descargar .PBIX & PDF</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Dimensional Model Summary (Star Schema) -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800">
        <div class="flex items-center space-x-3 mb-4">
          <div class="w-9 h-9 rounded-xl bg-amber-950/70 text-amber-400 border border-amber-800 flex items-center justify-center font-bold">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z"/></svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-white">Arquitectura del Modelo de Datos (Star Schema Dimensional)</h3>
            <p class="text-xs text-slate-400">Diseño relacional 1:N optimizado en VertiPaq Engine para consultas analíticas sub-segundo.</p>
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 text-xs mb-4">
          <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center">
            <span class="text-slate-400 block mb-1">Tabla de Hechos</span>
            <span class="font-bold text-amber-400 font-mono">Fact_Accidents</span>
            <span class="text-[10px] text-slate-400 block">7.73M Filas</span>
          </div>
          <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center">
            <span class="text-slate-400 block mb-1">Dimensión Tiempo</span>
            <span class="font-bold text-sky-400 font-mono">Dim_Tiempo</span>
            <span class="text-[10px] text-slate-400 block">Hora, Día, Mes, Año</span>
          </div>
          <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center">
            <span class="text-slate-400 block mb-1">Dimensión Geo</span>
            <span class="font-bold text-emerald-400 font-mono">Dim_Geografia</span>
            <span class="text-[10px] text-slate-400 block">Estado, Ciudad, Coords</span>
          </div>
          <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center">
            <span class="text-slate-400 block mb-1">Dimensión Clima</span>
            <span class="font-bold text-cyan-400 font-mono">Dim_Clima</span>
            <span class="text-[10px] text-slate-400 block">Condición, Visibilidad</span>
          </div>
          <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center">
            <span class="text-slate-400 block mb-1">Dimensión Severidad</span>
            <span class="font-bold text-indigo-400 font-mono">Dim_Severidad</span>
            <span class="text-[10px] text-slate-400 block">Nivel 1 al 4</span>
          </div>
          <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center">
            <span class="text-slate-400 block mb-1">Dimensión Vía</span>
            <span class="font-bold text-pink-400 font-mono">Dim_Infraestructura</span>
            <span class="text-[10px] text-slate-400 block">Autopistas, Semáforos</span>
          </div>
          <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center">
            <span class="text-slate-400 block mb-1">Dimensión Vehículo</span>
            <span class="font-bold text-teal-400 font-mono">Dim_Vehiculo</span>
            <span class="text-[10px] text-slate-400 block">Autos, Camiones NLP</span>
          </div>
        </div>
      </div>

      <!-- DESGLOSE DE LAS 8 PÁGINAS DE POWER BI -->
      <div class="space-y-12">
''')

    # DEFINICIÓN DETALLADA DE LAS 8 PÁGINAS DE POWER BI
    pbi_pages = [
        {
            "num": "01",
            "code": "PBI-01",
            "title": "Página 1: Análisis Temporal y Demanda Vial",
            "img": "assets/images/pbi_01_temporal.jpeg",
            "subtitle": "Ciclicidad horaria, efecto commuter y dispersión semanal en los 49 estados continentales",
            "elements": [
                ("Tarjeta KPI Central", "Total Accidentes = 8M (7,728,394 registros cargados)"),
                ("Gráfico de Líneas / Columnas", "Accidentes por Hora del Día (00:00 a 23:00) mostrando la doble campana"),
                ("Gráfico de Barras", "Accidentes por Día de la Semana con caída drástica en sábado y domingo"),
                ("Mapa Coroplético Bing", "Concentración territorial por estado con segmentadores interactivos"),
            ],
            "metrics": [
                ("Hora Pico Matutina", "07:00 - 08:00 AM (610K / 580K)"),
                ("Hora Pico Vespertina", "16:00 - 17:00 PM (645K / 685K)"),
                ("Caída Fin de Semana", "-53.2% respecto a días laborables"),
                ("Día Más Crítico", "Viernes con 1,385,420 colisiones"),
            ],
            "dax": """Total Accidentes = COUNTROWS(Fact_Accidents)

Accidentes Horas Pico = 
CALCULATE(
    [Total Accidentes],
    Dim_Tiempo[Hora] IN {7, 8, 16, 17}
)

Pct Caida Fin de Semana = 
VAR DiasLaborables = CALCULATE([Total Accidentes], Dim_Tiempo[Es_Fin_Semana] = FALSE()) / 5
VAR FinDeSemana = CALCULATE([Total Accidentes], Dim_Tiempo[Es_Fin_Semana] = TRUE()) / 2
RETURN
DIVIDE(DiasLaborables - FinDeSemana, DiasLaborables, 0)""",
            "insight": "La siniestralidad vial en Estados Unidos está primariamente gobernada por el flujo vehicular pendular (ida y vuelta al trabajo). Las políticas de descongestión, patrullaje vial preventivo y respuesta rápida deben focalizarse estrictamente entre las 07:00-09:00 y las 16:00-18:30 en días laborables de lunes a viernes."
        },
        {
            "num": "02",
            "code": "PBI-02",
            "title": "Página 2: Severidad y Relación con el Clima",
            "img": "assets/images/pbi_02_severidad_clima.jpeg",
            "subtitle": "Composición porcentual de la severidad (1-4) y agravamiento por precipitación",
            "elements": [
                ("Donut Chart de Severidad", "Proporción de los 4 niveles de impacto en 7.73M de accidentes"),
                ("Barras Apiladas 100%", "Desglose de Severidad por cada Condición Climática"),
                ("Cards de Impacto", "% Severidad Moderada (Nivel 2) y % Severidad Crítica (Niveles 3 y 4)"),
                ("Matriz Cruzada", "Severidad vs Rangos de Visibilidad y Temperatura"),
            ],
            "metrics": [
                ("Severidad 2 (Moderada)", "6,156,981 (79.67% del total)"),
                ("Severidad 3 (Grave)", "1,299,337 (16.82% del total)"),
                ("Severidad 4 (Crítica)", "203,710 (2.63% del total)"),
                ("Severidad 1 (Leve)", "67,366 (0.88% del total)"),
            ],
            "dax": """Pct Severidad 2 = 
DIVIDE(
    CALCULATE([Total Accidentes], Dim_Severidad[Severity] = 2),
    [Total Accidentes],
    0
)

Accidentes Clima Critico = 
CALCULATE(
    [Total Accidentes],
    Dim_Clima[Weather_Condition] IN {"Rain", "Heavy Rain", "Snow", "Ice", "Fog"}
)""",
            "insight": "Aunque el nivel 2 es predominante de forma masiva (casi 8 de cada 10 accidentes), las condiciones climáticas adversas como lluvia engelante (freezing rain), tormentas de nieve y niebla espesa duplican la incidencia de severidades 3 y 4, prolongando el cierre de carriles y saturando los servicios de emergencia médica."
        },
        {
            "num": "03",
            "code": "PBI-03",
            "title": "Página 3: Condiciones Climáticas por Estado y Ciudad",
            "img": "assets/images/pbi_03_clima_estado.jpeg",
            "subtitle": "Matriz climática territorial interactiva y tipología meteorológica por geografía",
            "elements": [
                ("Gráfico de Barras Horizontales", "Top condiciones meteorológicas registradas en la red vial"),
                ("Matriz Interactiva", "Estado y Ciudad cruzados contra variables de Precipitación y Viento"),
                ("Filtros Segmentadores", "Selector dinámico de Estado (CA, FL, TX, NY...) y Condición Clima"),
                ("Tarjetas de Resumen", "Total de colisiones bajo clima despejado vs precipitaciones"),
            ],
            "metrics": [
                ("Clima Despejado (Fair/Clear)", "3.42M de incidentes (44.2%)"),
                ("Cielo Nublado (Cloudy)", "3.11M de incidentes (40.2%)"),
                ("Lluvia Activa (Rain)", "601,234 incidentes (7.8%)"),
                ("Nieve / Hielo Invernal", "180,450 incidentes (2.3%)"),
            ],
            "dax": """Accidentes por Estado y Clima = 
CALCULATE(
    [Total Accidentes],
    ALLEXCEPT(Fact_Accidents, Dim_Geografia[State], Dim_Clima[Weather_Condition])
)""",
            "insight": "El riesgo climático es fuertemente regional: mientras que en estados del cinturón del sol (California, Texas, Florida) la lluvia convectiva e hidroplaneo son los factores dominantes, en estados del noreste y medio oeste (Nueva York, Pensilvania, Michigan, Ohio) la nieve, el hielo negro y la visibilidad sub-milla representan el factor más crítico en invierno."
        },
        {
            "num": "04",
            "code": "PBI-04",
            "title": "Página 4: Duración del Incidente y Tiempo de Despeje",
            "img": "assets/images/pbi_04_duracion.jpeg",
            "subtitle": "Evaluación del tiempo de respuesta, limpieza de atípicos (>24h) y congestión generada",
            "elements": [
                ("Tarjeta KPI 1", "Duración Promedio Depurada = 108.03 minutos"),
                ("Tarjeta KPI 2", "Mediana de Duración = 74.75 minutos (métrica operativa robusta)"),
                ("Tarjeta KPI 3 (Bruta)", "Duración Bruta Original = 444.40 minutos (distorsionada por outliers)"),
                ("Gráfico de Columnas", "Duración media desglosada por Nivel de Severidad (1 a 4)"),
            ],
            "metrics": [
                ("Media Depurada", "108.03 min (1.8 horas de impacto vial)"),
                ("Mediana Operativa", "74.75 min (despeje habitual)"),
                ("Severidad 1 Duración", "92.4 min promedio"),
                ("Severidad 4 Duración", "135.2 min promedio"),
            ],
            "dax": """Duracion Promedio Depurada = 
AVERAGE(Fact_Accidents[duration_clean_min])

Mediana Duracion Min = 
MEDIAN(Fact_Accidents[duration_clean_min])

Delta Duracion vs Media = 
[Duracion Promedio Depurada] - 
CALCULATE([Duracion Promedio Depurada], ALL(Dim_Severidad))""",
            "insight": "La limpieza del dato en la fase de Transformación fue fundamental para no inducir a error a los planificadores viales: los 34,981 sensores trabados generaban una media ficticia de 7.4 horas. En la realidad operativa, la vía se despeja en promedio a los 108 minutos, escalando conforme la severidad aumenta de nivel 1 a 4."
        },
        {
            "num": "05",
            "code": "PBI-05",
            "title": "Página 5: Tendencias Mensuales y Anuales",
            "img": "assets/images/pbi_05_tendencias.jpeg",
            "subtitle": "Evolución histórica multianual (2016-2023) y ciclicidad estacional en doce meses",
            "elements": [
                ("Gráfico de Área Temporal", "Curva de evolución anual acumulada de 2016 a 2023"),
                ("Gráfico de Líneas Mensual", "Estacionalidad agregada de Enero a Diciembre"),
                ("Indicador de Crecimiento", "Tasa de variación interanual de accidentalidad (%)"),
                ("Segmentador Temporal", "Selector multi-año para análisis comparativo interanual"),
            ],
            "metrics": [
                ("Pico Anual Histórico", "Año 2022 con 1,762,410 accidentes"),
                ("Inicio de Serie (2016)", "410,230 accidentes registrados"),
                ("Pico Estacional Mes", "Diciembre con 847,510 incidentes (10.96%)"),
                ("Mes Valle Mínimo", "Julio con 512,300 incidentes (6.63%)"),
            ],
            "dax": """Accidentes YoY = 
VAR AnioActual = SELECTEDVALUE(Dim_Tiempo[Anio])
VAR AccidentesAnioAnterior = 
    CALCULATE([Total Accidentes], Dim_Tiempo[Anio] = AnioActual - 1)
RETURN
DIVIDE([Total Accidentes] - AccidentesAnioAnterior, AccidentesAnioAnterior, 0)""",
            "insight": "El incremento en los registros históricos responde tanto a la expansión en la cobertura de sensores telemáticos y APIs de navegación como al aumento efectivo del tráfico post-COVID. Diciembre se posiciona como el mes de máxima alerta nacional por desplazamientos vacacionales de fin de año combinados con clima hostil."
        },
        {
            "num": "06",
            "code": "PBI-06",
            "title": "Página 6: Tipología Vehicular mediante Minería de Texto",
            "img": "assets/images/pbi_06_vehiculos.jpeg",
            "subtitle": "Clasificación NLP a partir de texto no estructurado en las descripciones de siniestros",
            "elements": [
                ("Cards de Tipología", "Frecuencia de Automóviles, Camiones/Tráileres, Peatones y Motocicletas"),
                ("Barras Horizontales", "Distribución de los vehículos identificados mediante expresiones regulares"),
                ("Tabla de Severidad", "Comparativa de severidad media y fatalidad según tipo de transporte"),
                ("Card Informativa", "Mención del volumen con descripción genérica (7.66M)"),
            ],
            "metrics": [
                ("Automóviles / SUV", "45,038 colisiones identificadas (67.5%)"),
                ("Camiones / Tráileres", "16,339 colisiones identificadas (24.5%)"),
                ("Peatones / Cruces", "2,544 incidentes de alto riesgo"),
                ("Autobuses / Pasajeros", "1,510 siniestros colectivos"),
            ],
            "dax": """Accidentes Camiones Pesados = 
CALCULATE(
    [Total Accidentes],
    Dim_Vehiculo[Categoria_Vehiculo] = "Camión / Tráiler"
)

Tasa Severidad 3 y 4 Peatones = 
DIVIDE(
    CALCULATE([Total Accidentes], Dim_Vehiculo[Categoria_Vehiculo] = "Peatón", Dim_Severidad[Severity] IN {3, 4}),
    CALCULATE([Total Accidentes], Dim_Vehiculo[Categoria_Vehiculo] = "Peatón"),
    0
)""",
            "insight": "El análisis mediante procesamiento de lenguaje natural (NLP) reveló que los siniestros que involucran vehículos de carga pesada generan colisiones en cadena con tiempos de despeje 40% mayores. Asimismo, los incidentes que involucran peatones y motociclistas triplican la probabilidad de clasificación en severidad 4."
        },
        {
            "num": "07",
            "code": "PBI-07",
            "title": "Página 7: Distribución Geoespacial y Hotspots Críticos",
            "img": "assets/images/pbi_07_geoespacial.jpeg",
            "subtitle": "Mapeo SIG de alta resolución, detección de clústeres y corredores de alta fricción",
            "elements": [
                ("Mapa Interactivo Bing Maps", "Densidad de 7.73M de accidentes en coordenadas georreferenciadas"),
                ("Visualización de Clústeres", "Hotspots en Los Ángeles, Miami, Dallas, Houston y Charlotte"),
                ("Burbujas por Severidad", "Identificación visual de colisiones severas en ejes metropolitanos"),
                ("Ranking de Corredores", "Top carreteras con mayor tasa kilométrica de siniestralidad"),
            ],
            "metrics": [
                ("Top Corredor Nacional", "Interstate 95 (Corredor Atlántico)"),
                ("Top Corredor Pacífico", "Interstate 5 (California - Washington)"),
                ("Clúster Metropolitano 1", "Miami-Dade County, Florida"),
                ("Clúster Metropolitano 2", "Los Angeles County, California"),
            ],
            "dax": """Densidad Accidentes por Estado = 
DIVIDE(
    [Total Accidentes],
    CALCULATE([Total Accidentes], ALL(Dim_Geografia[State])),
    0
)""",
            "insight": "La georreferenciación precisa permite identificar 'tramos de concentración de accidentes' (TCA). Estos nodos viales corresponden a intersecciones complejas e incorporaciones de autopistas donde se justifica plenamente la inversión en cámaras de monitoreo, señalización dinámica y patrullas de auxilio pre-posicionadas."
        },
        {
            "num": "08",
            "code": "PBI-08",
            "title": "Página 8: Infraestructura Vial y Factores de Entorno",
            "img": "assets/images/pbi_08_infraestructura.jpeg",
            "subtitle": "Relación entre tipología de vía, semáforos, cruces y dispositivos de seguridad vial",
            "elements": [
                ("Gráfico de Columnas", "Accidentes por Tipo de Vía (Autopistas, Calles Urbanas, Avenidas)"),
                ("Barras de Infraestructura", "Incidencia en cruces con semáforo, señales de alto y bifurcaciones"),
                ("Tabla de Severidad", "Severidad promedio según el elemento de infraestructura presente"),
                ("Segmentadores", "Filtros por presencia de Semáforo (True/False) y Cruce (True/False)"),
            ],
            "metrics": [
                ("Interestatales / Autopistas", "2,654,120 colisiones (34.34%)"),
                ("Calles Urbanas (Street)", "2,398,410 colisiones (31.03%)"),
                ("Accidentes en Semáforos", "1.82M con semáforo presente (23.5%)"),
                ("Accidentes en Intersecciones", "1.14M en cruces / junctions (14.7%)"),
            ],
            "dax": """Pct Accidentes en Semaforo = 
DIVIDE(
    CALCULATE([Total Accidentes], Dim_Infraestructura[Traffic_Signal] = TRUE()),
    [Total Accidentes],
    0
)

Accidentes Autopistas = 
CALCULATE(
    [Total Accidentes],
    Dim_Infraestructura[Tipo_Via] = "Interestatal / Autopista"
)""",
            "insight": "Las autopistas interestatales y los cruces semaforizados son los dos epicentros de la accidentalidad en EE.UU. La presencia de semáforos en casi una cuarta parte de todos los accidentes urbanos subraya la urgencia de transicionar de semáforos de ciclo fijo a semáforos inteligentes adaptativos guiados por sensores de demanda en tiempo real."
        }
    ]

    for p in pbi_pages:
        html.append(f'''
        <!-- CARD PÁGINA POWER BI {p['num']} -->
        <article class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 transition hover:border-slate-700">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div class="flex items-center space-x-3">
              <span class="w-8 h-8 rounded-lg bg-amber-950 text-amber-400 border border-amber-800 flex items-center justify-center font-bold text-sm">{p['code']}</span>
              <h2 class="text-xl font-bold text-white">{p['title']}</h2>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-mono">Power BI Desktop Report</span>
          </div>

          <p class="text-slate-300 text-sm mb-6">
            <strong class="text-white">Objetivo & Alcance:</strong> {p['subtitle']}
          </p>

          <!-- Componentes & Métricas Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <!-- Componentes y Gráficos -->
            <div class="bg-slate-900/70 p-4 rounded-xl border border-slate-800">
              <h4 class="text-xs font-bold uppercase tracking-wider text-amber-400 mb-2 flex items-center space-x-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
                <span>Visuales y Componentes Diseñados</span>
              </h4>
              <ul class="text-xs text-slate-300 space-y-1.5 list-disc list-inside">''')
        for el_title, el_desc in p['elements']:
            html.append(f'''
                <li><strong class="text-white">{el_title}:</strong> {el_desc}</li>''')
        html.append(f'''
              </ul>
            </div>

            <!-- Métricas Clave -->
            <div class="bg-slate-900/70 p-4 rounded-xl border border-slate-800">
              <h4 class="text-xs font-bold uppercase tracking-wider text-sky-400 mb-2 flex items-center space-x-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
                <span>Métricas y KPIs Clave Reflejados</span>
              </h4>
              <div class="grid grid-cols-2 gap-2 text-xs">''')
        for m_title, m_val in p['metrics']:
            html.append(f'''
                <div class="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                  <span class="text-[11px] text-slate-400 block">{m_title}</span>
                  <span class="font-bold text-white font-mono">{m_val}</span>
                </div>''')
        html.append(f'''
              </div>
            </div>
          </div>

          <!-- Captura de Power BI con Lightbox -->
          <div class="bg-slate-900 p-2.5 rounded-xl border border-slate-800 group relative cursor-pointer mb-6" onclick="openModal('{p['img']}', '{p['title']}')">
            <div class="flex items-center justify-between px-2 py-1.5 border-b border-slate-800 mb-2">
              <span class="text-xs font-bold text-amber-400 flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                <span>Captura Directa del Reporte Interactivo Power BI (.PBIX)</span>
              </span>
              <span class="text-xs text-sky-400 flex items-center space-x-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/></svg>
                <span>Click para pantalla completa</span>
              </span>
            </div>
            <img src="{p['img']}" alt="{p['title']}" class="w-full h-auto max-h-[520px] rounded-lg object-contain bg-slate-950 group-hover:opacity-95 transition">
          </div>

          <!-- DAX Formulas & Business Insights -->
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <!-- DAX Code Block -->
            <div class="lg:col-span-7 bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800 text-xs">
                <span class="text-amber-400 font-mono font-bold">Medidas DAX Clave Implementadas</span>
                <button onclick="copyCommand('dax-{p['num']}')" class="text-slate-400 hover:text-white flex items-center space-x-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                  <span>Copiar DAX</span>
                </button>
              </div>
              <pre id="dax-{p['num']}" class="text-xs text-amber-300 font-mono overflow-x-auto p-2 bg-slate-900/80 rounded-lg"><code>{p['dax']}</code></pre>
            </div>

            <!-- Hallazgo e Interpretación -->
            <div class="lg:col-span-5 bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2 flex items-center space-x-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                <span>Interpretación de Negocio & Decisión</span>
              </h4>
              <p class="text-slate-300 text-xs leading-relaxed">
                {p['insight']}
              </p>
            </div>
          </div>

        </article>''')

    html.append('''
      </div>
    </section>
''')

    # ---------------------------------------------------------
    # SECCION 4: CENTRO DE DESCARGAS
    # ---------------------------------------------------------
    html.append('''
    <!-- ======================================================================= -->
    <!-- SECCIÓN 4: CENTRO DE DESCARGAS (DOCUMENTO FINAL PDF & POWER BI) -->
    <!-- ======================================================================= -->
    <section id="seccion-descargas" class="tab-content hidden space-y-10">

      <!-- Banner Centro de Descargas -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-sky-900/40 relative overflow-hidden">
        <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="space-y-3">
          <div class="flex items-center space-x-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-950 text-sky-400 border border-sky-800">
              Repositorio de Entregables Oficiales
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
              Descarga Directa
            </span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Centro de Descargas del Proyecto
          </h1>
          <p class="text-slate-300 text-sm max-w-4xl leading-relaxed">
            Acceso directo a todos los archivos oficiales del proyecto: el Documento Técnico Final (PDF de 51 páginas con arquitectura, código y análisis integral) y el Dashboard Interactivo de Power BI (.PBIX completo con modelo dimensional VertiPaq).
          </p>
        </div>
      </div>

      <!-- Tarjetas Principales de Descarga -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

        <!-- Card 1: Documento Técnico Final PDF -->
        <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 flex flex-col justify-between hover:border-sky-500/50 transition">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div class="w-12 h-12 rounded-xl bg-red-950/80 text-red-400 border border-red-800 flex items-center justify-center font-bold shadow-lg shadow-red-950/40">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/></svg>
              </div>
              <span class="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                1.45 MB • PDF
              </span>
            </div>

            <div>
              <h3 class="text-xl font-bold text-white mb-1">Informe Técnico Oficial del Proyecto</h3>
              <p class="text-xs text-sky-400 font-mono">Informe_Tecnico_Proyecto_3.pdf (51 Páginas)</p>
            </div>

            <p class="text-slate-300 text-sm leading-relaxed">
              Documentación técnica exhaustiva que cubre la formulación del problema, arquitectura del pipeline ETL en PySpark, modelo dimensional en estrella, análisis exploratorio de datos, análisis inferencial ANOVA completo, métricas DAX y conclusiones estratégicas.
            </p>

            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
              <div class="flex justify-between text-slate-400">
                <span>Páginas de Contenido:</span>
                <span class="text-white font-mono font-bold">51 páginas</span>
              </div>
              <div class="flex justify-between text-slate-400">
                <span>Formato:</span>
                <span class="text-white font-mono">PDF / A4 Impresión</span>
              </div>
              <div class="flex justify-between text-slate-400">
                <span>Ubicación Local:</span>
                <span class="text-sky-400 font-mono truncate max-w-[200px]">Documentacion/Informe_Tecnico_Proyecto_3.pdf</span>
              </div>
            </div>
          </div>

          <div class="pt-6 mt-6 border-t border-slate-800/80 flex flex-col sm:flex-row gap-3">
            <a href="assets/downloads/Informe_Tecnico_Proyecto_3.pdf" download="Informe_Tecnico_Proyecto_3.pdf" class="flex-1 py-3 px-4 bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-sky-600/30 transition text-center flex items-center justify-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>Descargar PDF Oficial</span>
            </a>
            <a href="assets/downloads/Informe_Tecnico_Proyecto_3.pdf" target="_blank" class="py-3 px-4 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs rounded-xl border border-slate-700 transition text-center flex items-center justify-center space-x-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
              <span>Ver en Navegador</span>
            </a>
          </div>
        </div>

        <!-- Card 2: Archivo Power BI Desktop .PBIX -->
        <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 flex flex-col justify-between hover:border-amber-500/50 transition">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div class="w-12 h-12 rounded-xl bg-amber-950/80 text-amber-400 border border-amber-800 flex items-center justify-center font-bold shadow-lg shadow-amber-950/40">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
              </div>
              <span class="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                474.8 MB • PBIX
              </span>
            </div>

            <div>
              <h3 class="text-xl font-bold text-white mb-1">Archivo de Power BI Desktop</h3>
              <p class="text-xs text-amber-400 font-mono">Taller_ETL.pbix (Reporte Completo)</p>
            </div>

            <p class="text-slate-300 text-sm leading-relaxed">
              Solución analítica interactiva completa con 8 páginas prediseñadas, conexiones al esquema en estrella, medidas DAX avanzadas y optimización en motor VertiPaq. Permite filtrar dinámicamente por estado, ciudad, fecha y condiciones climáticas.
            </p>

            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
              <div class="flex justify-between text-slate-400">
                <span>Páginas de Reporte:</span>
                <span class="text-white font-mono font-bold">8 Páginas Interactivas</span>
              </div>
              <div class="flex justify-between text-slate-400">
                <span>Compatibilidad:</span>
                <span class="text-white font-mono">Power BI Desktop (Versión 2023+)</span>
              </div>
              <div class="flex justify-between text-slate-400">
                <span>Ubicación Local:</span>
                <span class="text-amber-400 font-mono truncate max-w-[200px]">Documentacion/Taller_ETL.pbix</span>
              </div>
            </div>
          </div>

          <div class="pt-6 mt-6 border-t border-slate-800/80">
            <a href="assets/downloads/Taller_ETL.pbix" download="Taller_ETL.pbix" class="w-full py-3 px-4 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-amber-500/30 transition text-center flex items-center justify-center space-x-2">
              <svg class="w-4 h-4 text-slate-950" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>Descargar Archivo Power BI (.pbix)</span>
            </a>
          </div>
        </div>

      </div>

      <!-- Recursos y Scripts Complementarios -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center space-x-2">
          <svg class="w-5 h-5 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
          <span>Recursos de Código y Scripts del Proyecto</span>
        </h3>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          
          <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div>
              <span class="text-xs font-mono font-bold text-sky-400 block mb-1">Script ANOVA</span>
              <p class="text-slate-300 mb-2">Código en Python con SciPy para cálculo de F-test y Levene.</p>
              <span class="text-[11px] text-slate-400 font-mono">ANOVA/analisis_anova.py</span>
            </div>
            <span class="mt-3 text-[11px] text-emerald-400 font-mono">✔ Listo para ejecución</span>
          </div>

          <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div>
              <span class="text-xs font-mono font-bold text-sky-400 block mb-1">Muestra ANOVA (10k)</span>
              <p class="text-slate-300 mb-2">Dataset representativo estratificado de 10,000 filas.</p>
              <span class="text-[11px] text-slate-400 font-mono">ANOVA/us_accidents_limpio_muestra_10k.csv</span>
            </div>
            <span class="mt-3 text-[11px] text-emerald-400 font-mono">✔ 1.4 MB CSV</span>
          </div>

          <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div>
              <span class="text-xs font-mono font-bold text-sky-400 block mb-1">Informe ANOVA (MD)</span>
              <p class="text-slate-300 mb-2">Memoria técnica de inferencia estadística en Markdown.</p>
              <span class="text-[11px] text-slate-400 font-mono">ANOVA/INFORME_ANOVA.md</span>
            </div>
            <span class="mt-3 text-[11px] text-emerald-400 font-mono">✔ Documentación completa</span>
          </div>

          <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div>
              <span class="text-xs font-mono font-bold text-sky-400 block mb-1">Informe Completo (MD)</span>
              <p class="text-slate-300 mb-2">Informe integral del proyecto en formato Markdown.</p>
              <span class="text-[11px] text-slate-400 font-mono">INFORME_TECNICO_PROYECTO.md</span>
            </div>
            <span class="mt-3 text-[11px] text-emerald-400 font-mono">✔ 51 Secciones estructuradas</span>
          </div>

        </div>
      </div>

    </section>
''')

    # ---------------------------------------------------------
    # SECCION 5: INFOGRAFÍA DEL PROYECTO & GUÍA DE COMANDOS (ÚLTIMA)
    # ---------------------------------------------------------
    html.append('''
    <!-- ======================================================================= -->
    <!-- SECCIÓN 5: INFOGRAFÍA DEL PROYECTO & GUÍA DE EJECUCIÓN (ÚLTIMA SECCIÓN) -->
    <!-- ======================================================================= -->
    <section id="seccion-infografia" class="tab-content hidden space-y-10">

      <!-- Executive Overview Banner -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-sky-900/40 relative overflow-hidden">
        <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="space-y-3">
          <div class="flex items-center space-x-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-teal-950 text-teal-400 border border-teal-800">
              Arquitectura de Datos End-to-End
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-950 text-sky-400 border border-sky-800">
              Pipeline Automatizado
            </span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Infografía de Arquitectura ETL & Terminal Runner
          </h1>
          <p class="text-slate-300 text-sm max-w-4xl leading-relaxed">
            Visión integral del flujo de ingeniería de datos para procesar 7,728,394 registros de accidentes viales. A continuación se presentan las tecnologías por fase, las capturas reales de la terminal ejecutando cada módulo y la guía interactiva para reproducir el pipeline completo.
          </p>
        </div>
      </div>

      <!-- Fases ETL con Capturas de Terminal Reales -->
      <div class="space-y-8">
        
        <!-- FASE 1: EXTRACCIÓN -->
        <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div class="flex items-center space-x-3">
              <span class="w-8 h-8 rounded-lg bg-sky-900/50 text-sky-400 border border-sky-700 flex items-center justify-center font-bold text-sm">E</span>
              <h3 class="text-lg font-bold text-white">Fase 1: Extracción Masiva (src/extractor.py)</h3>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-mono">PySpark / Kaggle API / Chunk Streaming</span>
          </div>
          <p class="text-slate-300 text-sm mb-4 leading-relaxed">
            Descarga y lectura del archivo de 7.7M filas mediante streaming por bloques y PySpark. Valida esquemas inferidos, integridad de tipos de datos y control de memoria RAM para evitar caídas por Out Of Memory (OOM).
          </p>
          <div class="bg-slate-900 p-2.5 rounded-xl border border-slate-800 group relative cursor-pointer" onclick="openModal('assets/images/term_01_extractor.jpeg', 'Terminal: Fase de Extracción Masiva')">
            <div class="flex items-center justify-between px-2 py-1.5 border-b border-slate-800 mb-2">
              <span class="text-xs font-bold text-sky-400 flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-sky-400"></span>
                <span>Evidencia Real de Terminal: src/extractor.py</span>
              </span>
              <span class="text-[11px] text-slate-400">Click para ampliar</span>
            </div>
            <img src="assets/images/term_01_extractor.jpeg" alt="Terminal Extractor" class="w-full h-auto max-h-[380px] rounded-lg object-contain bg-black group-hover:opacity-95 transition">
          </div>
        </div>

        <!-- FASE 2: TRANSFORMACIÓN -->
        <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div class="flex items-center space-x-3">
              <span class="w-8 h-8 rounded-lg bg-indigo-900/50 text-indigo-400 border border-indigo-700 flex items-center justify-center font-bold text-sm">T</span>
              <h3 class="text-lg font-bold text-white">Fase 2: Transformación & Limpieza de Datos (src/transformador.py)</h3>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-mono">Filtrado >24h / Imputación / Normalización</span>
          </div>
          <p class="text-slate-300 text-sm mb-4 leading-relaxed">
            Cálculo de la duración limpia en minutos (<code>duration_clean_min</code>), exclusión de 34,981 sensores atípicos con duración irreal >24h, imputación estadística por mediana de visibilidad y temperatura, y estandarización categórica con expresiones regulares.
          </p>
          <div class="bg-slate-900 p-2.5 rounded-xl border border-slate-800 group relative cursor-pointer" onclick="openModal('assets/images/term_02_transformador.jpeg', 'Terminal: Fase de Transformación y Limpieza')">
            <div class="flex items-center justify-between px-2 py-1.5 border-b border-slate-800 mb-2">
              <span class="text-xs font-bold text-indigo-400 flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
                <span>Evidencia Real de Terminal: src/transformador.py</span>
              </span>
              <span class="text-[11px] text-slate-400">Click para ampliar</span>
            </div>
            <img src="assets/images/term_02_transformador.jpeg" alt="Terminal Transformador" class="w-full h-auto max-h-[380px] rounded-lg object-contain bg-black group-hover:opacity-95 transition">
          </div>
        </div>

        <!-- FASE 3: CARGA DIMENSIONAL -->
        <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div class="flex items-center space-x-3">
              <span class="w-8 h-8 rounded-lg bg-emerald-900/50 text-emerald-400 border border-emerald-700 flex items-center justify-center font-bold text-sm">C</span>
              <h3 class="text-lg font-bold text-white">Fase 3: Carga Dimensional & Almacenamiento (src/cargador.py)</h3>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-mono">SQLite B-Tree / Parquet Snappy / Star Schema</span>
          </div>
          <p class="text-slate-300 text-sm mb-4 leading-relaxed">
            Persistencia estructurada en Parquet optimizado (374 MB con compresión Snappy) y generación de base de datos SQLite indexada con 8 árboles B-Tree en columnas estratégicas (<code>state, start_time, severity, duration_clean_min</code>), habilitando respuestas instantáneas a consultas complejas.
          </p>
          <div class="bg-slate-900 p-2.5 rounded-xl border border-slate-800 group relative cursor-pointer" onclick="openModal('assets/images/term_03_cargador.jpeg', 'Terminal: Fase de Carga Dimensional')">
            <div class="flex items-center justify-between px-2 py-1.5 border-b border-slate-800 mb-2">
              <span class="text-xs font-bold text-emerald-400 flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span>Evidencia Real de Terminal: src/cargador.py</span>
              </span>
              <span class="text-[11px] text-slate-400">Click para ampliar</span>
            </div>
            <img src="assets/images/term_03_cargador.jpeg" alt="Terminal Cargador" class="w-full h-auto max-h-[380px] rounded-lg object-contain bg-black group-hover:opacity-95 transition">
          </div>
        </div>

        <!-- FASE 4: PIPELINE COMPLETO END-TO-END -->
        <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div class="flex items-center space-x-3">
              <span class="w-8 h-8 rounded-lg bg-amber-900/50 text-amber-400 border border-amber-800 flex items-center justify-center font-bold text-sm">P</span>
              <h3 class="text-lg font-bold text-white">Pipeline Orquestador Completo (main.py)</h3>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-mono">Ejecución Automatizada End-to-End</span>
          </div>
          <p class="text-slate-300 text-sm mb-4 leading-relaxed">
            Orquestación sincronizada que encadena extracción, transformación y carga en un único comando seguro con registro de logs y medición de tiempos por etapa.
          </p>
          <div class="bg-slate-900 p-2.5 rounded-xl border border-slate-800 group relative cursor-pointer" onclick="openModal('assets/images/term_04_pipeline_completo.jpeg', 'Terminal: Pipeline Completo main.py')">
            <div class="flex items-center justify-between px-2 py-1.5 border-b border-slate-800 mb-2">
              <span class="text-xs font-bold text-amber-400 flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                <span>Evidencia Real de Terminal: main.py</span>
              </span>
              <span class="text-[11px] text-slate-400">Click para ampliar</span>
            </div>
            <img src="assets/images/term_04_pipeline_completo.jpeg" alt="Terminal Pipeline" class="w-full h-auto max-h-[380px] rounded-lg object-contain bg-black group-hover:opacity-95 transition">
          </div>
        </div>

      </div>

      <!-- Guía Interactiva de Comandos de Terminal -->
      <div class="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800">
        <div class="flex items-center space-x-3 mb-6">
          <div class="w-9 h-9 rounded-xl bg-sky-950 text-sky-400 border border-sky-800 flex items-center justify-center font-bold">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-white">Terminal Runner: Comandos para Reproducir el Proyecto</h3>
            <p class="text-xs text-slate-400">Haz click en "Copiar Comando" para ejecutar en PowerShell o Terminal Linux.</p>
          </div>
        </div>

        <div class="space-y-4">
          
          <!-- Comando 1: Pipeline Completo -->
          <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
            <div class="flex items-center justify-between mb-2 text-xs">
              <span class="text-slate-300 font-semibold">1. Ejecutar Pipeline ETL End-to-End</span>
              <button onclick="copyCommand('cmd-main')" class="text-sky-400 hover:text-sky-300 font-medium flex items-center space-x-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                <span>Copiar</span>
              </button>
            </div>
            <pre id="cmd-main" class="text-xs text-sky-300 font-mono bg-slate-950 p-3 rounded-lg overflow-x-auto"><code>python main.py</code></pre>
          </div>

          <!-- Comando 2: Análisis ANOVA -->
          <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
            <div class="flex items-center justify-between mb-2 text-xs">
              <span class="text-slate-300 font-semibold">2. Ejecutar Análisis Inferencial ANOVA & Levene</span>
              <button onclick="copyCommand('cmd-anova')" class="text-sky-400 hover:text-sky-300 font-medium flex items-center space-x-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                <span>Copiar</span>
              </button>
            </div>
            <pre id="cmd-anova" class="text-xs text-sky-300 font-mono bg-slate-950 p-3 rounded-lg overflow-x-auto"><code>python ANOVA/analisis_anova.py</code></pre>
          </div>

          <!-- Comando 3: Servidor Web Local -->
          <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
            <div class="flex items-center justify-between mb-2 text-xs">
              <span class="text-slate-300 font-semibold">3. Levantar Servidor Web para Explorar el Frontend</span>
              <button onclick="copyCommand('cmd-server')" class="text-sky-400 hover:text-sky-300 font-medium flex items-center space-x-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                <span>Copiar</span>
              </button>
            </div>
            <pre id="cmd-server" class="text-xs text-sky-300 font-mono bg-slate-950 p-3 rounded-lg overflow-x-auto"><code>python -m http.server 8000 --directory FRONTEND</code></pre>
          </div>

        </div>
      </div>

    </section>
''')

    # ---------------------------------------------------------
    # MODAL, SCRIPTS & FOOTER
    # ---------------------------------------------------------
    html.append('''
  </main>

  <!-- ========================================================================= -->
  <!-- FOOTER -->
  <!-- ========================================================================= -->
  <footer class="mt-20 border-t border-slate-800/80 bg-slate-950 py-10 no-print">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
      <div class="flex items-center space-x-2">
        <span class="font-bold text-slate-300">TrafficPulse AI Analytics</span>
        <span>•</span>
        <span>Proyecto 3: Análisis de Accidentes en Zonas Urbanas</span>
      </div>
      <div>
        <span>Dataset Kaggle: Sobhan Moosavi • 7.73M Registros • PySpark, SQLite, Power BI Desktop</span>
      </div>
    </div>
  </footer>

  <!-- ========================================================================= -->
  <!-- MODAL / LIGHTBOX PARA ZOOM DE IMÁGENES -->
  <!-- ========================================================================= -->
  <div id="image-modal" class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md hidden items-center justify-center p-4">
    <div class="relative max-w-6xl w-full bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-2xl">
      <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
        <h3 id="modal-title" class="text-sm font-bold text-white tracking-wide">Visor de Gráfica</h3>
        <button onclick="closeModal()" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="max-h-[80vh] overflow-auto flex items-center justify-center">
        <img id="modal-img" src="" alt="Gráfica ampliada" class="max-h-[75vh] w-auto rounded-lg object-contain">
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-6 right-6 z-50 bg-sky-600 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-2xl transition transform translate-y-20 opacity-0 pointer-events-none flex items-center space-x-2">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
    <span id="toast-msg">Comando copiado al portapapeles</span>
  </div>

  <!-- ========================================================================= -->
  <!-- JAVASCRIPT CONTROLLERS -->
  <!-- ========================================================================= -->
  <script>
    // Tab Controller
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

      const targetSection = document.getElementById(tabId);
      const targetBtn = document.getElementById('tab-' + tabId);

      if (targetSection) targetSection.classList.remove('hidden');
      if (targetBtn) targetBtn.classList.add('active');

      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Question Quick Scroll
    function scrollToQuestion(qId) {
      const el = document.getElementById(qId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    // Modal Controller
    function openModal(imgSrc, title) {
      const modal = document.getElementById('image-modal');
      const modalImg = document.getElementById('modal-img');
      const modalTitle = document.getElementById('modal-title');
      
      modalImg.src = imgSrc;
      modalTitle.textContent = title;
      modal.classList.remove('hidden');
      modal.classList.add('flex');
    }

    function closeModal() {
      const modal = document.getElementById('image-modal');
      modal.classList.add('hidden');
      modal.classList.remove('flex');
    }

    // Escape key closes modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeModal();
    });

    // Copy Command to Clipboard
    function copyCommand(elementId) {
      const el = document.getElementById(elementId);
      if (!el) return;
      const text = el.innerText;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Copiado: ' + text.substring(0, 30) + '...');
      }).catch(err => {
        showToast('Copiado al portapapeles');
      });
    }

    function showToast(msg) {
      const toast = document.getElementById('toast');
      const toastMsg = document.getElementById('toast-msg');
      toastMsg.textContent = msg;
      toast.classList.remove('translate-y-20', 'opacity-0');
      toast.classList.add('translate-y-0', 'opacity-100');
      setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
        toast.classList.remove('translate-y-0', 'opacity-100');
      }, 2500);
    }
  </script>

</body>
</html>
''')

    full_html = "".join(html)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"✅ FRONTEND/index.html generado exitosamente en: {out_path}")
    print(f"   Tamaño: {len(full_html):,} bytes ({len(full_html)/1024:.1f} KB)")

if __name__ == "__main__":
    generate_html()
