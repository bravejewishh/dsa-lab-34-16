from flask import Flask, request, jsonify

app = Flask(__name__)

# Статические курсы (можно менять по необходимости)
RATES = {
    "EUR": 82.54,
    "USD": 71.20
}

@app.route("/rate", methods=["GET"])
def get_rate():
    try:
        currency = request.args.get("currency", "").upper()
        
        if currency not in RATES:
            return jsonify({"message": "UNKNOWN CURRENCY"}), 400
        
        return jsonify({"rate": RATES[currency]}), 200
    
    except Exception:
        return jsonify({"message": "UNEXPECTED ERROR"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)