# app.py
import json
import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# настройка лимитера
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day"]  # общий лимит: 100 запросов в сутки
)

# путь к файлу с данными
DATA_FILE = 'data.json'

# загружаем данные при старте
data = {}
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}

# сохраняем данные в файл
def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# POST /set — сохранить ключ-значение
@app.route('/set', methods=['POST'])
@limiter.limit("10 per minute")  # отдельный лимит для записи
def set_value():
    req = request.get_json()
    key = req.get('key')
    value = req.get('value')
    
    if not key:
        return jsonify({'error': 'key is required'}), 400
    
    data[key] = value
    save_data()
    return jsonify({'status': 'ok', 'key': key}), 200

# GET /get/<key> — получить значение по ключу
@app.route('/get/<key>', methods=['GET'])
def get_value(key):
    if key in data:
        return jsonify({'key': key, 'value': data[key]}), 200
    return jsonify({'error': 'key not found'}), 404

# DELETE /delete/<key> — удалить ключ
@app.route('/delete/<key>', methods=['DELETE'])
@limiter.limit("10 per minute")  # отдельный лимит для удаления
def delete_value(key):
    if key in data:
        del data[key]
        save_data()
        return jsonify({'status': 'deleted', 'key': key}), 200
    return jsonify({'error': 'key not found'}), 404

# GET /exists/<key> — проверить наличие ключа
@app.route('/exists/<key>', methods=['GET'])
def exists_key(key):
    return jsonify({'key': key, 'exists': key in data}), 200

if __name__ == '__main__':
    app.run(debug=True)