import random

# Список доступных операций
OPERATIONS = ['+', '-', '*', '/']

def generate_random_number(min_val=1, max_val=100):
    """
    Генерирует случайное целое число в заданном диапазоне.
    """
    return random.randint(min_val, max_val)

def get_random_operation():
    """
    Возвращает случайную математическую операцию.
    """
    return random.choice(OPERATIONS)

def calculate_result(random_val, param_value):
    """
    Вычисляет результат умножения случайного числа на параметр.
    """
    return random_val * param_value

def get_get_response(param_value):
    """
    Формирует ответ для GET запроса.
    """
    random_val = generate_random_number()
    result = calculate_result(random_val, param_value)
    
    return {
        'method': 'GET',
        'random_number': random_val,
        'param': param_value,
        'result': result
    }

def get_post_response(param_value):
    """
    Формирует ответ для POST запроса (с добавлением операции).
    """
    random_val = generate_random_number()
    result = calculate_result(random_val, param_value)
    operation = get_random_operation()
    
    return {
        'method': 'POST',
        'random_number': random_val,
        'param': param_value,
        'result': result,
        'operation': operation
    }

def get_delete_response():
    """
    Формирует ответ для DELETE запроса.
    """
    random_val = generate_random_number()
    operation = get_random_operation()
    
    return {
        'method': 'DELETE',
        'number': random_val,
        'operation': operation,
        'message': 'Resource processed for deletion'
    }