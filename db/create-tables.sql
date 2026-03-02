CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age INTEGER CHECK (age >= 0 AND age <= 120),
    weight_kg DECIMAL(5,2) CHECK (weight_kg > 0),
    height_cm INTEGER CHECK (height_cm > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workouts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    steps INTEGER NOT NULL CHECK (steps >= 0),
    heart_rate_avg INTEGER NOT NULL CHECK (heart_rate_avg >= 40 AND heart_rate_avg <= 220),
    calories_burned INTEGER NOT NULL CHECK (calories_burned >= 0),
    distance_km DECIMAL(6,2) CHECK (distance_km >= 0),
    intensity TEXT CHECK (intensity IN ('низкая', 'средняя', 'высокая')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_workouts INTEGER DEFAULT 0,
    total_calories INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    total_distance DECIMAL(10,2) DEFAULT 0,
    avg_heart_rate DECIMAL(5,2) DEFAULT 0,
    last_activity TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE OR REPLACE VIEW v_workout_summary AS
SELECT 
    activity_type,
    COUNT(*) as total_sessions,
    AVG(duration_minutes) as avg_duration,
    AVG(calories_burned) as avg_calories,
    AVG(heart_rate_avg) as avg_heart_rate,
    SUM(steps) as total_steps,
    SUM(distance_km) as total_distance
FROM workouts
GROUP BY activity_type;

CREATE OR REPLACE VIEW v_daily_stats AS
SELECT 
    DATE(start_time) as day,
    COUNT(*) as workouts_count,
    SUM(calories_burned) as total_calories,
    SUM(steps) as total_steps,
    AVG(heart_rate_avg) as avg_heart_rate
FROM workouts
GROUP BY DATE(start_time);