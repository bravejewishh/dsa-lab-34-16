import requests
import random

BASE = 'http://127.0.0.1:5000/number/'

# 1. GET
r1 = requests.get(BASE, params={'param': random.randint(1, 10)}).json()
n1 = r1.get('random_number', 0)
print(f"GET: число = {n1}")

# 2. POST
r2 = requests.post(BASE, json={'jsonParam': random.randint(1, 10)}).json()
n2 = r2.get('random_number', 0)
op2 = r2.get('operation', '+')
print(f"POST: число = {n2}, операция = {op2}")

# 3. DELETE
r3 = requests.delete(BASE).json()
n3 = r3.get('number', 0)
op3 = r3.get('operation', '+')
print(f"DELETE: число = {n3}, операция = {op3}")

# 4. Вычисляем: ((n1 op2 n2) op3 n3)
ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b, 
       '*': lambda a, b: a * b, '/': lambda a, b: a / b if b else a}

result = ops[op3](ops[op2](n1, n2), n3)
print(f"\nРезультат: {int(result)}")