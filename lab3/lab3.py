from flask import Flask, request, jsonify
from support import get_get_response, get_post_response, get_delete_response

lab3 = Flask(__name__)

@lab3.route('/number/', methods=['GET'])
def get_number():
    """
    GET запрос.
    Параметры передаются в URL (query parameters).
    """
    param = request.args.get('param')
    
    if param is None:
        return jsonify({'error': 'Parameter "param" is required'}), 400
    
    try:
        param_value = float(param)
        response_data = get_get_response(param_value)
        return jsonify(response_data), 200
    except ValueError:
        return jsonify({'error': 'Parameter "param" must be a number'}), 400

@lab3.route('/number/', methods=['POST'])
def post_number():
    """
    POST запрос.
    Данные передаются в теле сообщения (Message Body) в формате JSON.
    """
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    json_param = data.get('jsonParam')
    
    if json_param is None:
        return jsonify({'error': 'Field "jsonParam" is required'}), 400
    
    try:
        param_value = float(json_param)
        response_data = get_post_response(param_value)
        return jsonify(response_data), 200
    except ValueError:
        return jsonify({'error': 'Field "jsonParam" must be a number'}), 400

@lab3.route('/number/', methods=['DELETE'])
def delete_number():
    """
    DELETE запрос.
    Удаляет ресурс с сервера (имитация).
    """
    response_data = get_delete_response()
    return jsonify(response_data), 200

if __name__ == '__main__':
    lab3.run(debug=True)
