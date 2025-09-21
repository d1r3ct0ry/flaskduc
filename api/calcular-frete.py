from http import HTTPStatus
import requests
import json
from flask import jsonify, request
from flask_cors import cross_origin

# 🔐 Token da SuperFrete
SUPERFRETE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NTY3NTQ3NzcsInN1YiI6IlkydGZOTWhHQVFaNXFQUmF5VG1hWFEzT0ZoNTIifQ.Oo0CzxnRtwOPmBBAJgQBIz4U06qcVmrwLOic8CnyDe0"

SUPERFRETE_URL = (
    f"https://api.superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    f"&accept=application%2Fjson"
    f"&content-type=application%2Fjson"
)

# Função de entrada do Vercel
@cross_origin()  # libera CORS
def handler(request):
    if request.method != "POST":
        return jsonify({"erro": "Método não permitido"}), HTTPStatus.METHOD_NOT_ALLOWED

    data = request.get_json(silent=True)
    if not data or "cepDestino" not in data or "pacote" not in data:
        return jsonify({"erro": "JSON inválido ou campos ausentes"}), HTTPStatus.BAD_REQUEST

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
        response = requests.post(SUPERFRETE_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=10)
        try:
            result = response.json()
        except ValueError:
            result = {"erro": "Resposta não é JSON", "texto": response.text}
            return jsonify(result), HTTPStatus.BAD_GATEWAY
    except requests.exceptions.RequestException as e:
        result = {"erro": "Falha na comunicação com SuperFrete", "detalhes": str(e)}
        return jsonify(result), HTTPStatus.BAD_GATEWAY

    return jsonify(result), response.status_code
