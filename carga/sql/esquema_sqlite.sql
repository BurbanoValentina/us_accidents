-- ==============================================================================
-- DDL DE BASE DE DATOS ANALÍTICA (SQLite 3 / SQL Estándar)
-- Ubicación: carga/base_datos/us_accidents.db
-- Tabla de Hechos de Accidentes Viales (7,728,394 registros) + 8 Índices B-Tree
-- ==============================================================================

CREATE TABLE IF NOT EXISTS accidents (
    id TEXT,
    source TEXT,
    severity INTEGER,
    start_time TEXT,
    end_time TEXT,
    year INTEGER,
    month INTEGER,
    month_name TEXT,
    year_month TEXT,
    hour INTEGER,
    day_of_week_num INTEGER,
    day_name TEXT,
    is_weekend INTEGER,
    time_slot TEXT,
    duration_raw_min REAL,
    duration_clean_min REAL,
    distance_mi REAL,
    start_lat REAL,
    start_lng REAL,
    street TEXT,
    road_type TEXT,
    city TEXT,
    county TEXT,
    state TEXT,
    temperature_f REAL,
    humidity_pct REAL,
    visibility_mi REAL,
    wind_speed_mph REAL,
    precipitation_in REAL,
    weather_raw TEXT,
    weather_group TEXT,
    sunrise_sunset TEXT,
    traffic_signal INTEGER,
    junction INTEGER,
    crossing INTEGER,
    stop INTEGER,
    station INTEGER,
    railway INTEGER,
    roundabout INTEGER,
    vehicle_type TEXT
);

CREATE INDEX IF NOT EXISTS idx_acc_state ON accidents(state);
CREATE INDEX IF NOT EXISTS idx_acc_severity ON accidents(severity);
CREATE INDEX IF NOT EXISTS idx_acc_weather ON accidents(weather_group);
CREATE INDEX IF NOT EXISTS idx_acc_ym ON accidents(year, month);
CREATE INDEX IF NOT EXISTS idx_acc_hour ON accidents(hour);
CREATE INDEX IF NOT EXISTS idx_acc_day ON accidents(day_of_week_num);
CREATE INDEX IF NOT EXISTS idx_acc_road ON accidents(road_type);
CREATE INDEX IF NOT EXISTS idx_acc_veh ON accidents(vehicle_type);