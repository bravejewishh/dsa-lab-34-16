import psycopg2

DB_CONFIG = {
    "dbname": "finance_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def init_database():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            sum NUMERIC(10, 2) NOT NULL,
            chat_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            type_operation VARCHAR(20) NOT NULL CHECK (type_operation IN ('income', 'expense'))
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Таблицы успешно созданы или уже существуют")

