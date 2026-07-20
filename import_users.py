import os
import sys
import secrets
import subprocess
import random
from datetime import datetime, timedelta

# 1. Автоматическая проверка и установка зависимостей
def check_dependencies(use_postgres):
    dependencies = ["bcrypt"]
    if use_postgres:
        dependencies.append("psycopg2-binary")
        
    for dep in dependencies:
        import_name = "bcrypt" if dep == "bcrypt" else "psycopg2"
        try:
            __import__(import_name)
        except ImportError:
            print(f"Пакет '{dep}' не найден. Устанавливаю через pip...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"Успешно установлен '{dep}'.")
            except Exception as e:
                print(f"Не удалось установить '{dep}' автоматически: {e}")
                sys.exit(1)

# 2. Простой парсер .env
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    os.environ[key] = val

load_env()
database_url = os.environ.get("DATABASE_URL")
use_postgres = bool(database_url)

check_dependencies(use_postgres)

import bcrypt

# Password pool variables
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%*&"

def generate_recovery_key():
    random_hex = secrets.token_hex(4).upper()
    parts = [random_hex[i:i+4] for i in range(0, len(random_hex), 4)]
    return 'RF-' + '-'.join(parts)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

# Helper to generate random registration date between April 20, 2026 and today
def generate_random_created_at():
    start_date = datetime(2026, 4, 20, 0, 0, 0)
    end_date = datetime.now()
    
    delta = end_date - start_date
    delta_seconds = delta.total_seconds()
    
    random_seconds = random.uniform(0, delta_seconds)
    random_date = start_date + timedelta(seconds=random_seconds)
    
    return random_date.strftime('%Y-%m-%d %H:%M:%S')

# Transliteration dictionary for Russian names to generate clean emails
trans_dict = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z',
    'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
}

def transliterate(text):
    return "".join(trans_dict.get(c, c) for c in text.lower())

# 3. Расширенный генератор на нужное количество уникальных пользователей
def generate_needed_users(count, passwords_pool, hashes_pool):
    # Узбекские мужские имена и фамилии
    uz_names = [
        "Otabek", "Sardor", "Umid", "Jasur", "Bekzod", "Anvar", "Rustam", "Dilshod", "Sanjar", "Sherzod", 
        "Nodir", "Bobur", "Aziz", "Alisher", "Javlon", "Farrux", "Shoxrux", "Ulugbek", "Abror", "Bahodir",
        "Diyor", "Eldor", "Asadbek", "Jahongir", "Mirali", "Sirojiddin", "Ismoil", "Ilyos", "Zafar", "Xurshid",
        "Muzaffar", "Oybek", "Bunyod", "Doniyor", "Suxrob", "Mansur", "Komil", "Jamshid", "Olim", "Ramazon",
        "Tohir", "Sobir", "Shavkat", "Erkin", "Akmal", "Ilhom", "Hasan", "Husan", "Botir", "Xasan"
    ]
    uz_surnames = [
        "Karimov", "Xasanov", "Abdullayev", "Sattorov", "Ismoilov", "Rahimov", "Yusupov", "Ergashev", "Yoldashev", 
        "Xoshimov", "Nazarov", "Boboyev", "Qodirov", "Xolmatov", "Mirzayev", "Saidov", "Tursunov", "Jo'rayev",
        "Ne'matov", "Rashidov", "Abduvaliyev", "Sultanov", "Axmedov", "Toshpulatov", "Raxmonov", "Normatov",
        "Murodov", "Mamatov", "Umarov", "Usmanov", "Sharipov", "Alimov", "Isakov", "Niyazov", "Xamroyev"
    ]
    
    # Узбекские женские имена и фамилии
    uz_fem_names = [
        "Dildora", "Gulnora", "Malika", "Madina", "Kamola", "Shahnoza", "Nigora", "Zarina", "Nilufar", "Yulduz", 
        "Iroda", "Muxlisa", "Ozoda", "Sitora", "Rayhona", "Feruza", "Sevara", "Dilnoza", "Shaxzoda", "Guli",
        "Lola", "Nargiza", "Sora", "Zilola", "Ruxshona", "Asal", "Nodira", "Shirin", "Mohira", "Gozal",
        "Charos", "Kumush", "Oydin", "Gulsanam", "Zuhra", "Fatima", "Barno", "Shaxnoza", "Munisa", "Rano"
    ]
    uz_fem_surnames = [s.replace("ov", "va") if s.endswith("ov") else s + "a" for s in uz_surnames]

    # Русские мужские имена и фамилии
    ru_names = [
        "Александр", "Иван", "Алексей", "Дмитрий", "Сергей", "Андрей", "Роман", "Никита", "Егор", "Илья", 
        "Павел", "Олег", "Максим", "Виктор", "Денис", "Владимир", "Михаил", "Артем", "Антон", "Игорь",
        "Владислав", "Ярослав", "Даниил", "Кирилл", "Евгений", "Николай", "Константин", "Юрий", "Анатолий", "Виталий",
        "Валерий", "Станислав", "Руслан", "Артур", "Вадим", "Тимур", "Глеб", "Матвей", "Федор", "Grigoriy"
    ]
    ru_surnames = [
        "Иванов", "Петров", "Смирнов", "Кузнецов", "Попов", "Соколов", "Лебедев", "Козлов", "Новиков", "Соловьёв", 
        "Воробьёв", "Богданов", "Волков", "Павлов", "Васильев", "Зайцев", "Голубев", "Виноградов", "Морозов", "Степанов",
        "Николаев", "Егоров", "Орлов", "Ковалёв", "Макаров", "Федоров", "Яковлев", "Белов", "Антонов", "Тарасов",
        "Никитин", "Поляков", "Ткачёв", "Баранов", "Фролов", "Алексеев", "Жуков", "Киселёв", "Кудрявцев", "Семенов"
    ]
    
    # Русские женские имена и фамилии
    ru_fem_names = [
        "Екатерина", "Анастасия", "Мария", "Анна", "Юлия", "Алина", "Кристина", "Марина", "Наталья", "Ольга", 
        "Светлана", "Ксения", "Татьяна", "Валентина", "Ирина", "Елена", "Дарья", "Виктория", "Полина", "Вероника",
        "Алена", "Елизавета", "София", "Валерия", "Яна", "Милана", "Маргарита", "Ангелина", "Инна", "Алла",
        "Надежда", "Любовь", "Вера", "Лидия", "Галина", "Нина", "Тамара", "Лариса", "Евгения", "Диана"
    ]
    ru_fem_surnames = [s + "a" if not s.endswith("ёв") else s.replace("ёв", "ёва") for s in ru_surnames]

    domains = ["gmail.com", "mail.ru", "yandex.ru"]
    
    generated = []
    seen_emails = set()
    
    print(f"Генерирую структуру для {count} уникальных пользователей в памяти...")
    
    while len(generated) < count:
        lang = random.choice(["uz", "ru"])
        gender = random.choice(["male", "female"])
        
        if lang == "uz":
            first = random.choice(uz_names) if gender == "male" else random.choice(uz_fem_names)
            last = random.choice(uz_surnames) if gender == "male" else random.choice(uz_fem_surnames)
            last_clean = last.lower().replace("'", "")
            email_prefix = f"{first.lower()}.{last_clean}{random.randint(100, 999999)}"
        else:
            first = random.choice(ru_names) if gender == "male" else random.choice(ru_fem_names)
            last = random.choice(ru_surnames) if gender == "male" else random.choice(ru_fem_surnames)
            
            # Базовый транслит для генерации почты из русских имён
            trans_first = transliterate(first)
            trans_last = transliterate(last)
            email_prefix = f"{trans_first}.{trans_last}{random.randint(100, 999999)}"
            
        email = f"{email_prefix}@{random.choice(domains)}"
        
        # Защита от дубликатов email
        if email in seen_emails:
            continue
            
        seen_emails.add(email)
        
        # Выбираем пароль и его готовый хеш из пула
        pass_idx = random.randint(0, len(passwords_pool) - 1)
        password = passwords_pool[pass_idx]
        hashed_pwd = hashes_pool[pass_idx]
        
        generated.append({
            "first_name": first,
            "last_name": last,
            "language": lang,
            "email": email,
            "password": password,
            "hashed_pwd": hashed_pwd,
            "created_at": generate_random_created_at()
        })
        
    return generated

# Создаем пул паролей и хешируем их один раз, чтобы сэкономить процессорное время
print("Подготовка пула хешированных паролей...")
passwords_pool = ["".join(random.choice(chars) for _ in range(12)) for _ in range(25)]
hashes_pool = [hash_password(p) for p in passwords_pool]

def process_sqlite(target_count):
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'readforge.db')
    print(f"Подключение к базе SQLite: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Инициализируем таблицы если они отсутствуют
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            surname     TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            password    TEXT NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            recovery_key TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type        TEXT NOT NULL,
            topic       TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    
    # 1. Очистка счетчиков генераций
    cursor.execute("DELETE FROM generations")
    print("Очищена таблица generations (счетчики генераций сброшены).")
    conn.commit()
    
    # 2. Получение текущего количества пользователей
    cursor.execute("SELECT COUNT(*) FROM users")
    current_count = cursor.fetchone()[0]
    print(f"Текущее количество пользователей в SQLite: {current_count}")
    
    needed = target_count - current_count
    if needed <= 0:
        print("Пользователей в базе уже достаточно.")
        conn.close()
        return 0, current_count
        
    print(f"Необходимо добавить пользователей: {needed}")
    
    # Генерация пользователей
    users = generate_needed_users(needed, passwords_pool, hashes_pool)
    
    # Считываем все существующие email за раз
    cursor.execute("SELECT email FROM users")
    existing_emails = {row[0].lower() for row in cursor.fetchall()}
    
    success_count = 0
    batch_size = 500
    batch = []
    
    for index, u in enumerate(users):
        first_name = u["first_name"]
        last_name = u["last_name"]
        email = u["email"].lower()
        
        if email in existing_emails:
            continue
            
        hashed_pwd = u["hashed_pwd"]
        recovery_key = generate_recovery_key()
        created_at = u["created_at"]
        
        batch.append((first_name, last_name, email, hashed_pwd, recovery_key, created_at))
        
        if len(batch) >= batch_size:
            cursor.executemany("""
                INSERT INTO users (name, surname, email, password, recovery_key, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, batch)
            success_count += len(batch)
            batch = []
            print(f"[Прогресс SQLite] Добавлено: {success_count} / {needed} пользователей...")
            conn.commit()
            
    if batch:
        cursor.executemany("""
            INSERT INTO users (name, surname, email, password, recovery_key, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, batch)
        success_count += len(batch)
        conn.commit()
        
    cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    final_count = cursor.fetchone()[0]
    conn.close()
    return success_count, final_count

def process_postgres(target_count, url):
    import psycopg2
    from psycopg2.extras import execute_batch
    print("Подключение к PostgreSQL (Supabase)...")
    conn = psycopg2.connect(url)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          SERIAL PRIMARY KEY,
            name        VARCHAR(255) NOT NULL,
            surname     VARCHAR(255) NOT NULL,
            email       VARCHAR(255) NOT NULL UNIQUE,
            password    VARCHAR(255) NOT NULL,
            created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            recovery_key VARCHAR(255)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id          SERIAL PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type        VARCHAR(50) NOT NULL,
            topic       VARCHAR(255),
            created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # 1. Очистка счетчиков генераций
    cursor.execute("DELETE FROM generations")
    print("Очищена таблица generations (счетчики генераций сброшены).")
    conn.commit()
    
    # 2. Получение текущего количества пользователей
    cursor.execute("SELECT COUNT(*) FROM users")
    current_count = cursor.fetchone()[0]
    print(f"Текущее количество пользователей в PostgreSQL: {current_count}")
    
    needed = target_count - current_count
    if needed <= 0:
        print("Пользователей в базе уже достаточно.")
        conn.close()
        return 0, current_count
        
    print(f"Необходимо добавить пользователей: {needed}")
    
    # Генерация пользователей
    users = generate_needed_users(needed, passwords_pool, hashes_pool)
    
    # Считываем все существующие email
    cursor.execute("SELECT email FROM users")
    existing_emails = {row[0].lower() for row in cursor.fetchall()}
    
    success_count = 0
    batch_size = 500
    batch = []
    
    for index, u in enumerate(users):
        first_name = u["first_name"]
        last_name = u["last_name"]
        email = u["email"].lower()
        
        if email in existing_emails:
            continue
            
        hashed_pwd = u["hashed_pwd"]
        recovery_key = generate_recovery_key()
        created_at = u["created_at"]
        
        batch.append((first_name, last_name, email, hashed_pwd, recovery_key, created_at))
        
        if len(batch) >= batch_size:
            execute_batch(cursor, """
                INSERT INTO users (name, surname, email, password, recovery_key, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, batch, page_size=100)
            success_count += len(batch)
            batch = []
            print(f"[Прогресс PostgreSQL] Добавлено: {success_count} / {needed} пользователей...")
            conn.commit()
            
    if batch:
        execute_batch(cursor, """
            INSERT INTO users (name, surname, email, password, recovery_key, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, batch, page_size=100)
        success_count += len(batch)
        conn.commit()
        
    cursor.execute("SELECT COUNT(*) FROM users")
    final_count = cursor.fetchone()[0]
    conn.close()
    return success_count, final_count

def main():
    TARGET_USER_COUNT = 11862
    print(f"Запуск процесса наполнения базы до {TARGET_USER_COUNT} пользователей...")
    if use_postgres:
        success, final = process_postgres(TARGET_USER_COUNT, database_url)
    else:
        success, final = process_sqlite(TARGET_USER_COUNT)
        
    print("\n--- Финальные Итоги Импорта ---")
    print(f"Успешно добавлено: {success}")
    print(f"Итоговое количество пользователей в базе: {final}")
    print("--------------------------------")

if __name__ == "__main__":
    main()