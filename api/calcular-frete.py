from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

# Cria a app Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔐 Token da SuperFrete
SUPERFRETE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NTY3NTQ3NzcsInN1YiI6IlkydGZOTWhHQVFaNXFQUmF5VG1hWFEzT0ZoNTIifQ.Oo0CzxnRtwOPmBBAJgQBIz4U06qcVmrwLOic8CnyDe0"

SUPERFRETE_URL = (
    f"https://api.superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    f"&accept=application%2Fjson"
    f"&content-type=application%2Fjson"
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
        result = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": "Falha na comunicação com SuperFrete", "detalhes": str(e)}), 502
    except ValueError:
        return jsonify({"erro": "Resposta não é JSON", "texto": response.text}), 502

    return jsonify(result), response.status_code
