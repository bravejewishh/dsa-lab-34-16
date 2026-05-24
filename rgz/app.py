from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import psycopg2
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from db_init import DB_CONFIG, init_database

app = Flask(__name__)
app.secret_key = "secret"  # Для работы сессий 

# Инициализация БД при старте 
init_database()

def get_db():
    """Возвращает подключение к БД с общими настройками"""
    return psycopg2.connect(**DB_CONFIG)

def get_current_user():
    """Возвращает ID пользователя из сессии — простая проверка авторизации"""
    return session.get("user_id")

# 2. РЕГИСТРАЦИЯ
@app.route("/reg", methods=["GET", "POST"])
def register():
    # Показываем форму регистрации 
    if request.method == "GET":
        return render_template("register.html")

    # Поддержка и JSON и form-data 
    if request.is_json:
        data = request.get_json()
        login = data.get("login")
        password = data.get("password")
    else:
        login = request.form.get("login")
        password = request.form.get("password")

    if not login or not password:
        return jsonify({"message": "Нет логина или пароля"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        # Проверяем, не занят ли логин
        cur.execute("SELECT id FROM users WHERE name = %s", (login,))
        if cur.fetchone():
            return jsonify({"message": "Пользователь существует"}), 409
        
        # Хэшируем пароль 
        hash_pwd = generate_password_hash(password)
        
        # Сохраняем пользователя, получаем его ID
        cur.execute(
            "INSERT INTO users (name, password_hash) VALUES (%s, %s) RETURNING id",
            (login, hash_pwd)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        
        # Если запрос от браузера — сохраняем сессию и редиректим
        if not request.is_json:
            session["user_id"] = user_id
            session["user_name"] = login
            return redirect(url_for("view_operations"))
            
        # Если JSON — возвращаем ответ в формате API
        return jsonify({"message": "OK", "user_id": user_id}), 200
    except Exception as e:
        conn.rollback()  # Откатываем изменения при ошибке
        return jsonify({"message": str(e)}), 500
    finally:
        cur.close()
        conn.close()  

# ВХОД 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    login_name = request.form.get("login")
    password = request.form.get("password")
    
    conn = get_db()
    cur = conn.cursor()
    try:
        # Ищем пользователя и проверяем хэш пароля
        cur.execute("SELECT id, password_hash FROM users WHERE name = %s", (login_name,))
        row = cur.fetchone()
        if row and check_password_hash(row[1], password):
            # Сохраняем данные в сессии 
            session["user_id"] = row[0]
            session["user_name"] = login_name
            return redirect(url_for("view_operations"))
        else:
            flash("Неверный логин или пароль")
            return redirect(url_for("login"))
    finally:
        cur.close()
        conn.close()

@app.route("/logout")
def logout():
    session.clear()  # Очищаем сессию 
    return redirect(url_for("login"))

# 3. ДОБАВЛЕНИЕ ОПЕРАЦИИ 
@app.route("/add_operation", methods=["GET", "POST"])
def add_operation():
    # Проверяем авторизацию 
    user_id = get_current_user()
    if not user_id:
        if request.is_json:
            return jsonify({"message": "Не авторизован"}), 401
        return redirect(url_for("login"))

    # Показываем форму добавления
    if request.method == "GET":
        return render_template("add_operation.html")

    # Извлекаем данные из JSON или формы
    if request.is_json:
        data = request.get_json()
        type_op = data.get("type_operation")
        amount = data.get("sum")
        date_op = data.get("date")
    else:
        type_op = request.form.get("type_operation")
        amount = request.form.get("sum")
        date_op = request.form.get("date")

    if not all([type_op, amount, date_op]):
        return jsonify({"message": "Заполните все поля"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        # Сохраняем операцию: chat_id = user_id 
        cur.execute(
            "INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
            (date_op, amount, user_id, type_op)
        )
        conn.commit()
        
        if request.is_json:
            return jsonify({"message": "OK"}), 200
        return redirect(url_for("view_operations"))  
    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# 2.1.4 ПРОСМОТР ОПЕРАЦИЙ 
@app.route("/operations", methods=["GET"])
def view_operations():
    user_id = get_current_user()
    if not user_id:
        if request.is_json:
            return jsonify({"message": "Не авторизован"}), 401
        return redirect(url_for("login"))

    # Получаем валюту из строки запроса, по умолчанию RUB
    currency = request.args.get("currency", "RUB").upper()
    
    conn = get_db()
    cur = conn.cursor()
    try:
        # Выбираем операции пользователя
        cur.execute(
            "SELECT id, date, sum, type_operation FROM operations WHERE chat_id = %s ORDER BY date DESC",
            (user_id,)
        )
        rows = cur.fetchall()
        
        # Формируем список операций
        ops_list = []
        for row in rows:
            ops_list.append({
                "id": row[0],
                "date": str(row[1]),
                "sum": float(row[2]),
                "type": row[3]
            })

        # Конвертация валюты
        rate = 1.0
        if currency != "RUB":
            try:
                resp = requests.get(
                    "http://localhost:5001/rate",
                    params={"currency": currency},
                    timeout=5
                )
                if resp.status_code == 200:
                    rate = resp.json().get("rate", 1.0)
                else:
                    flash("Ошибка получения курса")
            except:
                flash("Сервис курсов недоступен")

        # Добавляем конвертированную сумму к каждой операции
        result_ops = []
        for op in ops_list:
            result_ops.append({
                "date": op["date"],
                "sum_rub": op["sum"],
                "sum_conv": round(op["sum"] * rate, 2),
                "type": op["type"]
            })

        # Возврат: JSON для API или HTML-шаблон для браузера
        if request.is_json:
            return jsonify({"operations": result_ops}), 200
            
        return render_template(
            "operations.html",
            operations=result_ops,
            currency=currency
        )
    finally:
        cur.close()
        conn.close()

# ГЛАВНАЯ СТРАНИЦА 
@app.route("/")
def index():
    # Если авторизован — сразу на операции, иначе — на вход
    if get_current_user():
        return redirect(url_for("view_operations"))
    return redirect(url_for("login"))

# УДАЛЕНИЕ АККАУНТА
@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    user_id = get_current_user()
    if not user_id:
        if request.is_json:
            return jsonify({"message": "Не авторизован"}), 401
        return redirect(url_for("login"))
    
    # Показываем страницу подтверждения
    if request.method == "GET":
        return render_template("delete_account.html")
    
    # Обработка POST-запроса на удаление
    conn = get_db()
    cur = conn.cursor()
    try:
        # Сначала удаляем операции пользователя (если нет ON DELETE CASCADE)
        cur.execute("DELETE FROM operations WHERE chat_id = %s", (user_id,))
        # Затем удаляем самого пользователя
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        
        # Очищаем сессию и перенаправляем
        session.clear()
        flash("Ваш аккаунт был успешно удален", "success")
        
        if request.is_json:
            return jsonify({"message": "Аккаунт удален"}), 200
        return redirect(url_for("login"))
    
    except Exception as e:
        conn.rollback()
        if request.is_json:
            return jsonify({"message": str(e)}), 500
        flash(f"Ошибка при удалении: {e}", "error")
        return redirect(url_for("delete_account"))
    finally:
        cur.close()
        conn.close()

app.run(debug=True, port=5000)