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
    return "Currency Microservice is running! Use POST /load, POST /update_currency, POST /delete"

# ЭНДПОИНТ ДЛЯ ДОБАВЛЕНИЯ НОВОЙ ВАЛЮТЫ
@app.route('/load', methods=['POST'])
def load_currency():
    """
    Добавляет новую валюту в БД.
    Ожидает JSON: {"currency_name": "USD", "rate": 92.50}
    Возвращает 200 при успехе, 409 если валюта уже существует.
    """
    try:
        # Извлекаем JSON из тела запроса
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data"}), 400
        
        # Получаем название валюты и курс
        name = data.get('currency_name')
        rate = data.get('rate')
        
        # Проверяем, что оба поля присутствуют
        if not name or rate is None:
            return jsonify({"error": "Missing currency_name or rate"}), 400
        
        # Устанавливаем соединение с БД
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Пункт 1: Проверяем, существует ли уже такая валюта
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
        if cur.fetchone():
            cur.close()
            conn.close()
            # Возвращаем 409 Conflict, так как валюта уже есть
            return jsonify({"error": f"Currency {name} already exists"}), 409
        
        # Пункт 2: Сохраняем валюту в таблицу
        # Автоматически генерируем новый ID (максимальный существующий + 1)
        cur.execute("SELECT COALESCE(MAX(id), 0) FROM currencies")
        max_id = cur.fetchone()[0]
        new_id = max_id + 1
        
        # Вставляем новую запись
        cur.execute(
            "INSERT INTO currencies (id, currency_name, rate) VALUES (%s, %s, %s)",
            (new_id, name, float(rate))
        )
        conn.commit()  # Фиксируем изменения
        
        # Закрываем соединения
        cur.close()
        conn.close()
        
        # Пункт 3: Возвращаем ответ 200 OK
        return jsonify({"message": f"Currency {name} added successfully", "id": new_id}), 200
    
    except Exception as e:
        # Обрабатываем любые непредвиденные ошибки
        return jsonify({"error": str(e)}), 500

# ЭНДПОИНТ ДЛЯ ОБНОВЛЕНИЯ КУРСА ВАЛЮТЫ
@app.route('/update_currency', methods=['POST'])
def update_currency():
    """
    Обновляет курс существующей валюты.
    Ожидает JSON: {"currency_name": "USD", "rate": 93.75}
    Возвращает 200 при успехе, 404 если валюта не найдена.
    """
    try:
        # Извлекаем данные из запроса
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data"}), 400
        
        name = data.get('currency_name')
        rate = data.get('rate')
        
        # Валидация входных данных
        if not name or rate is None:
            return jsonify({"error": "Missing currency_name or rate"}), 400
        
        # Подключаемся к БД
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Пункт 1: Проверяем, существует ли валюта в БД
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            # Возвращаем 404 Not Found, так как валюта не существует
            return jsonify({"error": f"Currency {name} not found"}), 404
        
        # Пункт 2: Обновляем курс валюты
        cur.execute(
            "UPDATE currencies SET rate = %s WHERE currency_name = %s",
            (float(rate), name)
        )
        conn.commit()  # Фиксируем изменения
        
        # Закрываем соединения
        cur.close()
        conn.close()
        
        # Пункт 3: Возвращаем ответ 200 OK
        return jsonify({"message": f"Rate for {name} updated to {rate}"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ЭНДПОИНТ ДЛЯ УДАЛЕНИЯ ВАЛЮТЫ
@app.route('/delete', methods=['POST'])
def delete_currency():
    """
    Удаляет валюту из БД.
    Ожидает JSON: {"currency_name": "USD"}
    Возвращает 200 при успехе, 404 если валюта не найдена.
    """
    try:
        # Извлекаем данные из запроса
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data"}), 400
        
        name = data.get('currency_name')
        
        # Проверяем, что название валюты указано
        if not name:
            return jsonify({"error": "Missing currency_name"}), 400
        
        # Подключаемся к БД
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Пункт 1: Проверяем, существует ли валюта в БД
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            # Возвращаем 404 Not Found, если валюты нет
            return jsonify({"error": f"Currency {name} not found"}), 404
        
        # Пункт 2: Удаляем валюту из таблицы
        cur.execute("DELETE FROM currencies WHERE currency_name = %s", (name,))
        conn.commit()  # Фиксируем изменения
        
        # Закрываем соединения
        cur.close()
        conn.close()
        
        # Пункт 3: Возвращаем ответ 200 OK
        return jsonify({"message": f"Currency {name} deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ДОПОЛНИТЕЛЬНЫЙ ЭНДПОИНТ ДЛЯ ПРОСМОТРА ВСЕХ ВАЛЮТ (УДОБНО ДЛЯ ТЕСТИРОВАНИЯ)
@app.route('/currencies', methods=['GET'])
def list_currencies():
    """
    Возвращает список всех валют из БД.
    Не требуется по заданию, но полезен для отладки.
    """
    try:
        # Подключаемся к БД
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Выбираем все записи из таблицы currencies
        cur.execute("SELECT id, currency_name, rate FROM currencies ORDER BY id")
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Преобразуем результат в список словарей
        currencies = []
        for row in rows:
            currencies.append({
                "id": row[0],
                "currency_name": row[1],
                "rate": float(row[2])  # Преобразуем Decimal в float для JSON
            })
        
        return jsonify(currencies), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ЗАПУСК МИКРОСЕРВИСА
if __name__ == '__main__':
    print("Starting Currency Microservice on http://127.0.0.1:5001")
    print(f"Connecting to database: {DB_CONFIG['database']} as user {DB_CONFIG['user']}")
    # host='0.0.0.0' - слушаем все сетевые интерфейсы
    # port=5001 - порт согласно заданию
    # debug=False - отключаем режим отладки для production
    app.run(host='0.0.0.0', port=5001, debug=False)