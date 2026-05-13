import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

# Убираем влияние переменных окружения, которые часто вызывают UnicodeDecodeError в Windows
for key in ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE', 'PGCLIENTENCODING', 'PGSERVICE', 'PGAPPNAME']:
    os.environ.pop(key, None)

# НАСТРОЙКИ 
DB_HOST = "127.0.0.1"
DB_PORT = 5432
ADMIN_USER = "postgres"
ADMIN_PASS = "postgres"

NEW_USER = "currency_app_user"
NEW_PASS = "SecurePass123!"
NEW_DB = "currency_db"

def setup_postgres():
    print("Подключение к PostgreSQL...")
    try:
        conn_admin = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=ADMIN_USER,
            password=ADMIN_PASS,
            database="postgres",
            connect_timeout=5
        )
        print("Подключение успешно.")
    except psycopg2.OperationalError as e:
        print("ОШИБКА ПОДКЛЮЧЕНИЯ: Сервер PostgreSQL не отвечает.")
        print("1. Запущена ли служба postgresql-x64-XX в services.msc?")
        print("2. Верно ли указан пароль?")
        return
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return

    conn_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn_admin.cursor()

    try:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (NEW_USER,))
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s").format(sql.Identifier(NEW_USER)), (NEW_PASS,))
            print("Пользователь создан.")
        else:
            print("Пользователь уже существует.")

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (NEW_DB,))
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(
                sql.Identifier(NEW_DB),
                sql.Identifier(NEW_USER)
            ))
            print("База данных создана.")
        else:
            print("База данных уже существует.")
    except Exception as e:
        print(f"Ошибка создания объектов: {e}")
    finally:
        cur.close()
        conn_admin.close()

    try:
        print(f"Подключение к базе {NEW_DB}...")
        conn_db = psycopg2.connect(
            host=DB_HOST, port=DB_PORT,
            user=NEW_USER, password=NEW_PASS,
            database=NEW_DB,
            connect_timeout=5
        )
        cur_db = conn_db.cursor()
        cur_db.execute("""
            CREATE TABLE IF NOT EXISTS currencies (
                id INTEGER PRIMARY KEY,
                currency_name VARCHAR,
                rate NUMERIC
            )
        """)
        conn_db.commit()
        print("Таблица 'currencies' успешно создана.")
    except psycopg2.Error as e:
        print(f"Ошибка работы с таблицей: {e}")
    finally:
        if 'cur_db' in locals(): cur_db.close()
        if 'conn_db' in locals(): conn_db.close()

if __name__ == "__main__":
    setup_postgres()