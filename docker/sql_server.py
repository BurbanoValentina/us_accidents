# -*- coding: utf-8 -*-
"""
Servidor Web SQL Interactivo para Docker - US Accidents Analytics.
Corre dentro del contenedor Docker en el puerto 8090 utilizando únicamente la librería estándar de Python.
Permite ejecutar consultas SQL interactivas sobre /data/us_accidents.db con visualización de tablas y exportación.
"""

import http.server
import json
import os
import sqlite3
import time
import urllib.parse

DB_PATH = os.environ.get("DB_PATH", "/data/us_accidents.db")
if not os.path.exists(DB_PATH):
    # Fallback local para pruebas fuera del contenedor
    local_alt = os.path.join(os.path.dirname(__file__), "..", "carga", "base_datos", "us_accidents.db")
    if os.path.exists(local_alt):
        DB_PATH = local_alt

PRELOADED_QUERIES = [
    {
        "id": "q1",
        "name": "1. Top 10 Estados con Más Accidentes",
        "sql": "SELECT state AS Estado, COUNT(*) AS Total, ROUND(AVG(severity), 2) AS Severidad_Media FROM accidents GROUP BY state ORDER BY Total DESC LIMIT 10;"
    },
    {
        "id": "q2",
        "name": "2. Accidentes por Hora del Día (Picos Commuter)",
        "sql": "SELECT hour AS Hora, time_slot AS Franja, COUNT(*) AS Total FROM accidents GROUP BY hour, time_slot ORDER BY hour ASC;"
    },
    {
        "id": "q3",
        "name": "3. Distribución por Nivel de Severidad",
        "sql": "SELECT severity AS Severidad, COUNT(*) AS Total, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM accidents), 2) AS Porcentaje, ROUND(AVG(duration_clean_min), 1) AS Duracion_Promedio_Min FROM accidents GROUP BY severity ORDER BY severity ASC;"
    },
    {
        "id": "q4",
        "name": "4. Top Condiciones Climáticas",
        "sql": "SELECT weather_group AS Clima, COUNT(*) AS Total, ROUND(AVG(severity), 2) AS Severidad_Promedio, ROUND(AVG(visibility_mi), 1) AS Visibilidad_Millas FROM accidents GROUP BY weather_group ORDER BY Total DESC LIMIT 10;"
    },
    {
        "id": "q5",
        "name": "5. Tipos de Vía Más Peligrosos",
        "sql": "SELECT road_type AS Tipo_Via, COUNT(*) AS Total, ROUND(AVG(severity), 2) AS Severidad_Promedio FROM accidents GROUP BY road_type ORDER BY Total DESC;"
    },
    {
        "id": "q6",
        "name": "6. Días de la Semana con Mayor Siniestralidad",
        "sql": "SELECT day_name AS Dia, day_of_week_num AS Num_Dia, COUNT(*) AS Total FROM accidents GROUP BY day_name, day_of_week_num ORDER BY Total DESC;"
    },
    {
        "id": "q7",
        "name": "7. Promedio y Rango de Duración Limpia",
        "sql": "SELECT severity AS Severidad, ROUND(AVG(duration_clean_min), 2) AS Media_Min, ROUND(MIN(duration_clean_min), 2) AS Min_Min, ROUND(MAX(duration_clean_min), 2) AS Max_Min, COUNT(*) AS Total FROM accidents GROUP BY severity;"
    },
    {
        "id": "q8",
        "name": "8. Tendencia por Año y Mes",
        "sql": "SELECT year AS Anio, month AS Mes, COUNT(*) AS Total FROM accidents GROUP BY year, month ORDER BY year ASC, month ASC LIMIT 24;"
    },
    {
        "id": "q9",
        "name": "9. Tipología Vehicular Extraída por NLP",
        "sql": "SELECT vehicle_type AS Tipo_Vehiculo, COUNT(*) AS Total, ROUND(AVG(severity), 2) AS Severidad_Promedio FROM accidents GROUP BY vehicle_type ORDER BY Total DESC;"
    },
    {
        "id": "q10",
        "name": "10. Puntos Críticos Viales con Semáforos",
        "sql": "SELECT state AS Estado, city AS Ciudad, street AS Calle, COUNT(*) AS Total, SUM(traffic_signal) AS Con_Semaforo FROM accidents WHERE street IS NOT NULL AND street != 'Sin dato' GROUP BY state, city, street ORDER BY Total DESC LIMIT 15;"
    }
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>US Accidents SQL Explorer | Docker Container</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #030712; color: #F8FAFC; }
    pre, code, textarea, table { font-family: 'JetBrains Mono', monospace; }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0F172A; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
  </style>
</head>
<body class="min-h-screen p-4 sm:p-8">
  <div class="max-w-7xl mx-auto space-y-6">

    <!-- Header -->
    <header class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-sky-600 flex items-center justify-center font-bold text-white shadow-lg shadow-sky-600/30">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z"/></svg>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-2xl font-bold text-white">US Accidents <span class="text-sky-400">SQL Explorer</span></h1>
            <span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-mono">Docker Active</span>
          </div>
          <p class="text-xs text-slate-400">Base de Datos SQLite: <code>us_accidents.db</code> | Tablas: <code>accidents</code>, <code>us_accidents_limpio</code></p>
        </div>
      </div>
      <div class="flex items-center space-x-3 text-xs font-mono">
        <div class="bg-slate-950 px-3 py-2 rounded-lg border border-slate-800">
          <span class="text-slate-400">CLI Conexión:</span>
          <span class="text-emerald-400">docker exec -it us-accidents-sql sqlite3 /data/us_accidents.db</span>
        </div>
      </div>
    </header>

    <!-- Preloaded Queries Buttons -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <h2 class="text-xs font-bold uppercase tracking-wider text-sky-400 mb-3 flex items-center space-x-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
        <span>Consultas Rápidas del Proyecto (10 Requerimientos)</span>
      </h2>
      <div class="flex flex-wrap gap-2">
        {QUERY_BUTTONS}
      </div>
    </div>

    <!-- SQL Editor -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div class="flex items-center justify-between">
        <label for="sql-input" class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
          <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          <span>Consola SQL Interactiva</span>
        </label>
        <span class="text-xs text-slate-400">Presiona <strong>Ctrl + Enter</strong> para ejecutar</span>
      </div>

      <textarea id="sql-input" rows="5" class="w-full bg-slate-950 text-sky-300 text-xs p-4 rounded-xl border border-slate-800 focus:outline-none focus:border-sky-500 font-mono shadow-inner">{DEFAULT_QUERY}</textarea>

      <div class="flex items-center justify-between">
        <div id="status-bar" class="text-xs font-mono text-slate-400">
          Listo para ejecutar consultas.
        </div>
        <div class="flex items-center space-x-3">
          <button onclick="ejecutarQuery()" id="btn-run" class="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-sky-600/30 transition flex items-center space-x-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <span>Ejecutar Consulta SQL</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Results Table -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div class="flex items-center justify-between pb-2 border-b border-slate-800">
        <h3 class="text-sm font-bold text-white flex items-center space-x-2">
          <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          <span>Resultados de la Consulta</span>
        </h3>
        <span id="results-count" class="text-xs font-mono text-slate-400">0 filas devueltas</span>
      </div>

      <div id="results-container" class="overflow-x-auto max-h-[500px]">
        <div class="text-center py-8 text-xs text-slate-500">
          Haz click en "Ejecutar Consulta SQL" o selecciona uno de los requerimientos superiores.
        </div>
      </div>
    </div>

  </div>

  <script>
    const queries = {QUERIES_JSON};

    function loadQuery(id) {
      const q = queries.find(x => x.id === id);
      if (q) {
        document.getElementById('sql-input').value = q.sql;
        ejecutarQuery();
      }
    }

    document.getElementById('sql-input').addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        ejecutarQuery();
      }
    });

    function ejecutarQuery() {
      const sql = document.getElementById('sql-input').value.trim();
      if (!sql) return;

      const statusBar = document.getElementById('status-bar');
      const container = document.getElementById('results-container');
      const countEl = document.getElementById('results-count');
      const btn = document.getElementById('btn-run');

      statusBar.innerHTML = '<span class="text-sky-400 animate-pulse">Ejecutando consulta en SQLite...</span>';
      btn.disabled = true;

      fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sql: sql })
      })
      .then(res => res.json())
      .then(data => {
        btn.disabled = false;
        if (data.error) {
          statusBar.innerHTML = `<span class="text-red-400">Error: ${data.error}</span>`;
          container.innerHTML = `<div class="bg-red-950/40 border border-red-800 p-4 rounded-xl text-red-300 text-xs font-mono">${data.error}</div>`;
          countEl.innerText = 'Error';
          return;
        }

        statusBar.innerHTML = `<span class="text-emerald-400">✔ Consulta completada en <strong>${data.duration_ms} ms</strong>.</span>`;
        countEl.innerText = `${data.row_count.toLocaleString()} fila(s)`;

        if (data.rows.length === 0) {
          container.innerHTML = '<div class="text-slate-400 text-xs text-center py-6">(Sin registros para mostrar)</div>';
          return;
        }

        let html = '<table class="w-full text-left text-xs border-collapse font-mono">';
        html += '<thead><tr class="border-b border-slate-800 bg-slate-950/80 text-slate-400 uppercase text-[11px]">';
        for (const col of data.columns) {
          html += `<th class="py-2.5 px-3 whitespace-nowrap">${col}</th>`;
        }
        html += '</tr></thead><tbody class="divide-y divide-slate-800/60">';
        for (const row of data.rows) {
          html += '<tr class="hover:bg-slate-800/40 transition">';
          for (const cell of row) {
            html += `<td class="py-2 px-3 whitespace-nowrap text-slate-200">${cell !== null ? cell : '<span class="text-slate-600">NULL</span>'}</td>`;
          }
          html += '</tr>';
        }
        html += '</tbody></table>';
        container.innerHTML = html;
      })
      .catch(err => {
        btn.disabled = false;
        statusBar.innerHTML = `<span class="text-red-400">Error de conexión: ${err.message}</span>`;
      });
    }

    // Auto ejecutar consulta inicial
    window.onload = () => { ejecutarQuery(); };
  </script>
</body>
</html>
"""

class SQLiteHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            buttons_html = []
            for q in PRELOADED_QUERIES:
                buttons_html.append(
                    f'<button onclick="loadQuery(\'{q["id"]}\')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-sky-600 hover:text-white text-slate-300 text-xs font-medium transition border border-slate-700/60">{q["name"]}</button>'
                )
            
            rendered = HTML_TEMPLATE.replace("{QUERY_BUTTONS}", "\\n".join(buttons_html))
            rendered = rendered.replace("{DEFAULT_QUERY}", PRELOADED_QUERIES[0]["sql"])
            rendered = rendered.replace("{QUERIES_JSON}", json.dumps(PRELOADED_QUERIES))

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(rendered.encode("utf-8"))
        elif url.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "database": DB_PATH, "exists": os.path.exists(DB_PATH)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/query":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode("utf-8"))
                sql = payload.get("sql", "").strip()

                if not os.path.exists(DB_PATH):
                    raise FileNotFoundError(f"Base de datos no encontrada en {DB_PATH}")

                t0 = time.time()
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(sql)
                
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall() if cursor.description else []
                conn.close()
                dur_ms = round((time.time() - t0) * 1000, 2)

                response_data = {
                    "columns": columns,
                    "rows": rows[:500],  # Límite a 500 filas en UI para rendimiento
                    "row_count": len(rows),
                    "duration_ms": dur_ms
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))

            except Exception as e:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run(port=8090):
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), SQLiteHandler)
    print(f"🚀 [DOCKER SQL EXPLORER] Servidor iniciado en http://0.0.0.0:{port}")
    print(f"   Base de datos conectada: {DB_PATH}")
    server.serve_forever()

if __name__ == "__main__":
    run()
