from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# 🔐 Token da SuperFrete via variável de ambiente
SUPERFRETE_TOKEN = os.environ.get("SUPERFRETE_TOKEN")

# 🧭 URL base da SuperFrete (Authorization será passado via query string)
SUPERFRETE_URL = (
    "https://api.superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    "&accept=application%2Fjson"
    "&content-type=application%2Fjson"
)

@app.route("/api/calcular-frete", methods=["POST"])
def calcular_frete():
    data = request.get_json(silent=True)

    if not data or "cepDestino" not in data or "pacote" not in data:
        return jsonify({"erro": "JSON inválido ou campos ausentes"}), 400

    cep_destino = data["cepDestino"]
    pacote = data["pacote"]

    payload = {
        "from": {"postal_code": "25065007"},
        "to": {"postal_code": str(cep_destino)},
        "services": "1,2",
        "options": {
            "own_hand": False,
            "receipt": False,
            "insurance_value": 0,
            "use_insurance_value": False
        },
        "package": {
            "height": pacote.get("height", 2),
            "width": pacote.get("width", 11),
            "length": pacote.get("length", 16),
            "weight": pacote.get("weight", 0.3)
        }
    }

    try:
        response = requests.post(
            SUPERFRETE_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )
        try:
            return jsonify(response.json()), response.status_code
        except ValueError:
            return jsonify({"erro": "Resposta não é JSON", "texto": response.text}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": "Falha na comunicação com SuperFrete", "detalhes": str(e)}), 502
