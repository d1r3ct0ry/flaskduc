import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# â Libera CORS para todas rotas, todos mÃ©todos e headers
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

SUPERFRETE_TOKEN = os.environ.get("SUPERFRETE_TOKEN")
if not SUPERFRETE_TOKEN:
    raise RuntimeError("SUPERFRETE_TOKEN nÃ£o definido")

SUPERFRETE_URL = (
    f"https://api.superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    f"&accept=application%2Fjson"
    f"&content-type=application%2Fjson"
)

@app.route("/calcular-frete", methods=["POST", "OPTIONS"])
def calcular_frete():
    # Flask-CORS jÃ¡ trata OPTIONS, mas podemos reforÃ§ar
    if request.method == "OPTIONS":
        return jsonify({}), 204

    data = request.get_json(silent=True)
    if not data or "cepDestino" not in data or "pacote" not in data:
        return jsonify({"erro": "JSON invÃ¡lido ou campos ausentes"}), 400

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
            result = response.json()
        except ValueError:
            return jsonify({"erro": "Resposta nÃ£o Ã© JSON", "texto": response.text}), 502

    except requests.exceptions.RequestException as e:
        return jsonify({"erro": "Falha na comunicaÃ§Ã£o com SuperFrete", "detalhes": str(e)}), 502

    return jsonify(result), response.status_code
