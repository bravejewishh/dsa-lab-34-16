# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote_plus

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

user_db = "postgres"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "lab4"
password = "postgres"

encoded_password = quote_plus(password)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{user_db}:{encoded_password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('lab4.html', page='index', user=current_user)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('lab4.html', page='login')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password_input = request.form.get('password')
    
    if not email or not password_input:
        flash('все поля обязательны для заполнения', 'error')
        return redirect(url_for('login'))  
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('пользователь с таким email не найден', 'error')
        return redirect(url_for('login'))  
    
    if not check_password_hash(user.password, password_input):
        flash('неверный пароль', 'error')
        return redirect(url_for('login')) 
    
    login_user(user)
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('lab4.html', page='signup')


@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form.get('name')
    email = request.form.get('email')
    password_input = request.form.get('password')
    
    if not name or not email or not password_input:
        flash('все поля обязательны для заполнения', 'error')
        return redirect(url_for('signup'))  
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('пользователь с таким email уже существует', 'error')
        return redirect(url_for('signup')) 
    
    hashed_password = generate_password_hash(password_input, method='pbkdf2:sha256')
    new_user = User(email=email, password=hashed_password, name=name)
    
    db.session.add(new_user)
    db.session.commit()
    
    flash('регистрация успешна, пожалуйста, войдите', 'success')
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)