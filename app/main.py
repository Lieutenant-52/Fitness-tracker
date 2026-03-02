import os
import time
import random
from datetime import datetime, timezone, timedelta
import psycopg2
from faker import Faker

fake = Faker('ru_RU')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'fitness'),
    'user': os.getenv('DB_USER', 'fitness_user'),
    'password': os.getenv('DB_PASSWORD', 'fitness_password')
}

ACTIVITIES = ['бег', 'ходьба', 'велосипед', 'плавание', 'тренажерный зал', 'йога']

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def wait_for_database():
    print("Ожидание базы данных...")
    for i in range(20):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            print("База данных готова")
            return True
        except:
            print(f"Попытка {i+1}/20")
            time.sleep(3)
    return False

def initialize_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        print("Создаем тестовых пользователей...")
        for i in range(15):
            cur.execute("""
                INSERT INTO users (name, email, age, weight_kg, height_cm)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                fake.name(),
                fake.email(),
                random.randint(18, 65),
                round(random.uniform(50.0, 100.0), 2),
                random.randint(150, 200)
            ))
        print("Создано 15 пользователей")
    
    cur.execute("""
        INSERT INTO user_stats (user_id)
        SELECT id FROM users
        ON CONFLICT (user_id) DO NOTHING
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def generate_workout():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM users ORDER BY RANDOM() LIMIT 1")
        user_id = cur.fetchone()[0]
        
        activity = random.choice(ACTIVITIES)
        duration = random.randint(15, 120)
        
        if activity in ['бег', 'ходьба']:
            steps = random.randint(duration * 100, duration * 150)
        else:
            steps = 0
        
        if activity == 'бег':
            heart_rate = random.randint(140, 180)
        elif activity == 'велосипед':
            heart_rate = random.randint(120, 160)
        elif activity == 'плавание':
            heart_rate = random.randint(110, 150)
        else:
            heart_rate = random.randint(90, 130)
        
        calories_base = {
            'бег': 12, 'велосипед': 8, 'плавание': 10,
            'тренажерный зал': 7, 'ходьба': 5, 'йога': 3
        }
        calories = int(calories_base[activity] * duration * random.uniform(0.8, 1.2))
        
        if activity == 'бег':
            distance = round(duration * random.uniform(0.15, 0.20), 2)
        elif activity == 'ходьба':
            distance = round(duration * random.uniform(0.07, 0.10), 2)
        elif activity == 'велосипед':
            distance = round(duration * random.uniform(0.25, 0.35), 2)
        else:
            distance = 0.0
        
        if heart_rate > 160:
            intensity = 'высокая'
        elif heart_rate > 130:
            intensity = 'средняя'
        else:
            intensity = 'низкая'
        
        start_time = datetime.now(timezone.utc) - timedelta(minutes=duration)
        end_time = datetime.now(timezone.utc)
        
        cur.execute("""
            INSERT INTO workouts 
            (user_id, activity_type, start_time, end_time, duration_minutes,
             steps, heart_rate_avg, calories_burned, distance_km, intensity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, activity, start_time, end_time, duration,
              steps, heart_rate, calories, distance, intensity))
        
        cur.execute("""
            UPDATE user_stats 
            SET total_workouts = total_workouts + 1,
                total_calories = total_calories + %s,
                total_steps = total_steps + %s,
                total_distance = total_distance + %s,
                avg_heart_rate = ((avg_heart_rate * total_workouts) + %s) / (total_workouts + 1),
                last_activity = %s
            WHERE user_id = %s
        """, (calories, steps, distance, heart_rate, end_time, user_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {activity}: {duration} мин, {calories} калорий, {steps} шагов")
        
    except Exception as e:
        print(f"Ошибка при создании тренировки: {e}")

def main():
    print("Запуск фитнес-трекера...")
    
    if not wait_for_database():
        print("Не удалось подключиться к базе данных")
        return
    
    initialize_data()
    
    print("Генерация данных начата...")
    
    while True:
        try:
            if random.random() < 0.6:
                generate_workout()
            
            time.sleep(random.uniform(2, 5))
            
        except KeyboardInterrupt:
            print("Симуляция остановлена")
            break
        except Exception as e:
            print(f"Ошибка в основном цикле: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()