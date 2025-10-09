-- TimescaleDB initialization script for AirPuff
-- This script sets up the database schema and TimescaleDB extensions

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create airports table
CREATE TABLE IF NOT EXISTS airports (
    id SERIAL PRIMARY KEY,
    icao VARCHAR(4) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    elevation_ft INTEGER,
    atis_phone VARCHAR(20),
    tower_phone VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on ICAO code
CREATE INDEX IF NOT EXISTS idx_airports_icao ON airports(icao);

-- Create weather observations table
CREATE TABLE IF NOT EXISTS weather_observations (
    icao_code VARCHAR(4) NOT NULL,
    observed_time TIMESTAMP WITH TIME ZONE NOT NULL,
    flight_category VARCHAR(4),
    temp_c DECIMAL(4,1),
    dewpoint_c DECIMAL(4,1),
    wind_dir_degrees INTEGER,
    wind_speed_kt INTEGER,
    visibility_mi DECIMAL(4,1),
    altimeter_in_hg DECIMAL(5,2),
    sky_cover VARCHAR(10),
    raw_text TEXT,
    PRIMARY KEY (icao_code, observed_time)
);

-- Create TimescaleDB hypertable for weather observations
SELECT create_hypertable('weather_observations', 'observed_time', if_not_exists => TRUE);

-- Set data retention policy (keep 1 year of data)
SELECT add_retention_policy('weather_observations', INTERVAL '1 year', if_not_exists => TRUE);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_weather_icao_time ON weather_observations(icao_code, observed_time DESC);
CREATE INDEX IF NOT EXISTS idx_weather_flight_category ON weather_observations(flight_category);
CREATE INDEX IF NOT EXISTS idx_weather_temp ON weather_observations(temp_c);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url VARCHAR(500),
    provider VARCHAR(50) NOT NULL,
    provider_id VARCHAR(255) NOT NULL,
    units VARCHAR(10) DEFAULT 'imperial',
    default_airports TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    api_key VARCHAR(64) UNIQUE
);

-- Create routes table
CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create route airports association table
CREATE TABLE IF NOT EXISTS route_airports (
    route_id INTEGER NOT NULL REFERENCES routes(id),
    airport_id INTEGER NOT NULL REFERENCES airports(id),
    order INTEGER NOT NULL,
    notes TEXT,
    is_waypoint BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (route_id, airport_id)
);

-- Create scheduled messages table
CREATE TABLE IF NOT EXISTS scheduled_messages (
    id SERIAL PRIMARY KEY,
    route_id INTEGER NOT NULL REFERENCES routes(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    schedule_time VARCHAR(50) NOT NULL,
    last_sent TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    recipient_imessage_id VARCHAR(255)
);

-- Insert sample airports
INSERT INTO airports (icao, name, latitude, longitude, elevation_ft, city, state, country) VALUES
('KSFO', 'San Francisco International Airport', 37.6213, -122.3790, 13, 'San Francisco', 'CA', 'USA'),
('KLAX', 'Los Angeles International Airport', 33.9425, -118.4081, 125, 'Los Angeles', 'CA', 'USA'),
('KJFK', 'John F. Kennedy International Airport', 40.6413, -73.7781, 13, 'New York', 'NY', 'USA'),
('KORD', 'Chicago O''Hare International Airport', 41.9786, -87.9048, 672, 'Chicago', 'IL', 'USA'),
('KDFW', 'Dallas/Fort Worth International Airport', 32.8968, -97.0380, 607, 'Dallas', 'TX', 'USA'),
('KATL', 'Hartsfield-Jackson Atlanta International Airport', 33.6407, -84.4277, 1026, 'Atlanta', 'GA', 'USA'),
('KSEA', 'Seattle-Tacoma International Airport', 47.4502, -122.3088, 433, 'Seattle', 'WA', 'USA'),
('KDEN', 'Denver International Airport', 39.8561, -104.6737, 5431, 'Denver', 'CO', 'USA'),
('KMIA', 'Miami International Airport', 25.7959, -80.2870, 8, 'Miami', 'FL', 'USA'),
('KBOS', 'Logan International Airport', 42.3656, -71.0096, 20, 'Boston', 'MA', 'USA')
ON CONFLICT (icao) DO NOTHING;

-- Insert sample weather observations
INSERT INTO weather_observations (icao_code, observed_time, flight_category, temp_c, dewpoint_c, wind_dir_degrees, wind_speed_kt, visibility_mi, altimeter_in_hg, sky_cover, raw_text) VALUES
('KSFO', NOW() - INTERVAL '1 hour', 'VFR', 15.0, 10.0, 270, 12, 10.0, 30.15, 'FEW', 'KSFO 091800Z 27012KT 10SM FEW030 15/10 A3015'),
('KLAX', NOW() - INTERVAL '30 minutes', 'MVFR', 18.0, 12.0, 180, 8, 6.0, 29.98, 'SCT', 'KLAX 091830Z 18008KT 6SM SCT025 18/12 A2998'),
('KJFK', NOW() - INTERVAL '45 minutes', 'IFR', 8.0, 5.0, 360, 15, 2.0, 30.22, 'OVC', 'KJFK 091815Z 36015KT 2SM OVC010 08/05 A3022'),
('KORD', NOW() - INTERVAL '15 minutes', 'VFR', 12.0, 8.0, 240, 10, 15.0, 30.05, 'CLR', 'KORD 091845Z 24010KT 15SM CLR 12/08 A3005'),
('KDFW', NOW() - INTERVAL '20 minutes', 'MVFR', 22.0, 18.0, 200, 6, 5.0, 29.92, 'BKN', 'KDFW 091840Z 20006KT 5SM BKN020 22/18 A2992')
ON CONFLICT (icao_code, observed_time) DO NOTHING;

-- Create views for Grafana dashboards
CREATE OR REPLACE VIEW weather_summary AS
SELECT 
    wo.icao_code,
    a.name as airport_name,
    a.city,
    a.state,
    a.country,
    wo.observed_time,
    wo.flight_category,
    wo.temp_c,
    wo.dewpoint_c,
    wo.wind_dir_degrees,
    wo.wind_speed_kt,
    wo.visibility_mi,
    wo.altimeter_in_hg,
    wo.sky_cover,
    CASE 
        WHEN wo.flight_category = 'VFR' THEN 1
        WHEN wo.flight_category = 'MVFR' THEN 2
        WHEN wo.flight_category = 'IFR' THEN 3
        WHEN wo.flight_category = 'LIFR' THEN 4
        ELSE 0
    END as flight_category_numeric
FROM weather_observations wo
JOIN airports a ON wo.icao_code = a.icao
ORDER BY wo.observed_time DESC;

-- Create view for weather trends
CREATE OR REPLACE VIEW weather_trends AS
SELECT 
    icao_code,
    observed_time,
    temp_c,
    wind_speed_kt,
    visibility_mi,
    altimeter_in_hg,
    flight_category_numeric
FROM weather_summary
WHERE observed_time >= NOW() - INTERVAL '24 hours';

-- Grant permissions for Grafana
GRANT USAGE ON SCHEMA public TO grafana;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO grafana;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafana;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO grafana;
