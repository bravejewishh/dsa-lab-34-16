import os
import psycopg2
from flask import Flask, request, jsonify

# Удаляем переменные окружения PostgreSQL, чтобы избежать конфликтов кодировки в Windows
for key in ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE', 'PGCLIENTENCODING']:
    os.environ.pop(key, None)

app = Flask(__name__)

# НАСТРОЙКИ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ
DB_CONFIG = {
    "host": "127.0.0.1",      # Локальный хост
    "port": 5432,             # Стандартный порт PostgreSQL
    "user": "postgres",       # Администратор БД
    "password": "postgres",       # Пароль от PostgreSQL
    "database": "currency_db" # Имя базы данных для хранения валют
}

def get_db_connection():
    """Создает и возвращает соединение с БД. При ошибке выбрасывает исключение."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к БД: {e}")
        raise

# КОРНЕВОЙ МАРШРУТ ДЛЯ ПРОВЕРКИ РАБОТОСПОСОБНОСТИ
@app.route('/', methods=['GET'])
def home():
    """Возвращает информацию о доступных эндпоинтах сервиса."""
    return "Currency Converter Microservice is running! Use GET /convert?currency_name=USD&amount=100 or GET /currencies"

# ЭНДПОИНТ ДЛЯ КОНВЕРТАЦИИ ВАЛЮТЫ В РУБЛИ
@app.route('/convert', methods=['GET'])
def convert_currency():
    """
    Конвертирует сумму из указанной валюты в рубли.
    Параметры запроса: currency_name (название валюты), amount (сумма для конвертации)
    Возвращает JSON: {"currency_name": "USD", "amount": 100, "rate": 92.50, "result": 9250.00}
    """
    try:
        # Получаем параметры из URL-запроса
        currency_name = request.args.get('currency_name')
        amount_str = request.args.get('amount')
        
        # Проверяем наличие обязательных параметров
        if not currency_name:
            return jsonify({"error": "Missing parameter: currency_name"}), 400
        
        if not amount_str:
            return jsonify({"error": "Missing parameter: amount"}), 400
        
        # Преобразуем сумму в число
        try:
            amount = float(amount_str)
        except ValueError:
            return jsonify({"error": "Amount must be a number"}), 400
        
        # Проверяем, что сумма положительная
        if amount < 0:
            return jsonify({"error": "Amount must be positive"}), 400
        
        # Подключаемся к БД
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Пункт 1: Проверяем, существует ли валюта в БД
        cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
        result = cur.fetchone()
        
        # Если валюта не найдена, возвращаем ошибку 404
        if not result:
            cur.close()
            conn.close()
            return jsonify({"error": f"Currency {currency_name} not found"}), 404
        
        # Пункт 2: Получаем курс валюты из БД
        rate = float(result[0])
        
        # Пункт 3: Выполняем конвертацию (сумма * курс)
        converted_amount = amount * rate
        
        # Закрываем соединения с БД
        cur.close()
        conn.close()
        
        # Пункт 4: Возвращаем ответ 200 OK с результатом конвертации
        return jsonify({
            "currency_name": currency_name,
            "amount": amount,
            "rate": rate,
            "result": round(converted_amount, 2)  # Округляем до 2 знаков
        }), 200
    
    except Exception as e:
        # Обрабатываем любые непредвиденные ошибки
        return jsonify({"error": str(e)}), 500

# ЭНДПОИНТ ДЛЯ ПОЛУЧЕНИЯ ВСЕХ ВАЛЮТ
@app.route('/currencies', methods=['GET'])
def get_all_currencies():
    """
    Возвращает список всех валют из таблицы currencies.
    Возвращает JSON массив с id, названием и курсом каждой валюты.
    """
    try:
        # Подключаемся к БД
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Выбираем все записи из таблицы currencies, сортируем по id
        cur.execute("SELECT id, currency_name, rate FROM currencies ORDER BY id")
        rows = cur.fetchall()
        
        # Закрываем соединения
        cur.close()
        conn.close()
        
        # Преобразуем результат в список словарей для JSON ответа
        currencies = []
        for row in rows:
            currencies.append({
                "id": row[0],
                "currency_name": row[1],
                "rate": float(row[2])  # Преобразуем Decimal в float для JSON
            })
        
        # Возвращаем массив валют с кодом 200 OK
        return jsonify(currencies), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ЗАПУСК МИКРОСЕРВИСА НА ПОРТУ 5002
if __name__ == '__main__':
    print("Starting Currency Converter Microservice on http://127.0.0.1:5002")
    print(f"Connecting to database: {DB_CONFIG['database']} as user {DB_CONFIG['user']}")
    print("Available endpoints:")
    print("  GET /convert?currency_name=USD&amount=100 - convert currency to RUB")
    print("  GET /currencies - list all currencies")
    
    # host='0.0.0.0' - слушаем все сетевые интерфейсы
    # port=5002 - порт согласно заданию
    # debug=False - отключаем режим отладки для production
    app.run(host='0.0.0.0', port=5002, debug=False)