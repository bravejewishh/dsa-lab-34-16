# -*- coding: utf-8 -*-
import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="lab5",
        user="postgres", 
        password="postgres"  # впишите пароль вручную с клавиатуры
    )
    print("✅ подключение успешно")
    conn.close()
except UnicodeDecodeError as e:
    print(f"❌ unicode-ошибка: {e}")
    print("💡 проблема в кодировке файла или драйвере")
except Exception as e:
    print(f"❌ другая ошибка: {e}")