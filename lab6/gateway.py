import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Адреса целевых микросервисов
CURRENCY_MANAGER_URL = "http://127.0.0.1:5001"  # Микросервис управления валютами
DATA_MANAGER_URL = "http://127.0.0.1:5002"      # Микросервис данных и конвертации

# ---------- Прокси-эндпоинты (перенаправление запросов на целевые микросервисы) ----------

@app.route('/api/load', methods=['POST'])
def proxy_load():
    """Прокси для добавления новой валюты. Перенаправляет POST /api/load на currency-manager"""
    data = request.get_json()
    resp = requests.post(f"{CURRENCY_MANAGER_URL}/load", json=data)
    return jsonify(resp.json()), resp.status_code

@app.route('/api/update', methods=['POST'])
def proxy_update():
    """Прокси для обновления курса валюты. Перенаправляет POST /api/update на currency-manager"""
    data = request.get_json()
    resp = requests.post(f"{CURRENCY_MANAGER_URL}/update_currency", json=data)
    return jsonify(resp.json()), resp.status_code

@app.route('/api/delete', methods=['POST'])
def proxy_delete():
    """Прокси для удаления валюты. Перенаправляет POST /api/delete на currency-manager"""
    data = request.get_json()
    resp = requests.post(f"{CURRENCY_MANAGER_URL}/delete", json=data)
    return jsonify(resp.json()), resp.status_code

@app.route('/api/currencies', methods=['GET'])
def proxy_currencies():
    """Прокси для получения списка валют. Перенаправляет GET /api/currencies на data-manager"""
    resp = requests.get(f"{DATA_MANAGER_URL}/currencies")
    return jsonify(resp.json()), resp.status_code

@app.route('/api/convert', methods=['GET'])
def proxy_convert():
    """Прокси для конвертации валюты. Перенаправляет GET /api/convert на data-manager"""
    params = request.args.to_dict()
    resp = requests.get(f"{DATA_MANAGER_URL}/convert", params=params)
    return jsonify(resp.json()), resp.status_code

# ---------- Frontend (Jinja-шаблоны) ----------

@app.route('/')
def index():
    """Главная страница с меню всех операций"""
    return render_template('index.html')

@app.route('/list')
def list_currencies():
    """Страница со списком всех валют"""
    try:
        resp = requests.get(f"{DATA_MANAGER_URL}/currencies")
        currencies = resp.json()
    except:
        currencies = []
    return render_template('list.html', currencies=currencies)

@app.route('/add_currency')
def add_form():
    """Страница с формой для добавления валюты"""
    return render_template('add.html')

@app.route('/update_currency')
def update_form():
    """Страница с формой для обновления курса валюты"""
    return render_template('update.html')

@app.route('/delete_currency')
def delete_form():
    """Страница с формой для удаления валюты"""
    return render_template('delete.html')

@app.route('/convert_form')
def convert_form():
    """Страница с формой для конвертации валюты"""
    return render_template('convert.html')

# ---------- Запуск микросервиса ----------
if __name__ == '__main__':
    print("Gateway running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)