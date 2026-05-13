#!/bin/bash

# Запуск скрипта создания БД
python3 lab6r.py

# Запуск микросервиса currency-manager на порту 5001
python3 lab6r2.py &

# Запуск микросервиса data-manager на порту 5002
python3 lab6r3.py &

# Запуск микросервиса gateway на порту 5000
python3 gateway.py &

echo "Все микросервисы запущены"
echo "Gateway доступен по адресу http://127.0.0.1:5000"