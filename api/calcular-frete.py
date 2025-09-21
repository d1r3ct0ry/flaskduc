from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import os
import time
import uuid
import logging

# ==================== Configurações ====================
app = Flask(__name__)
CORS(app)

# Logging estruturado
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("superfrete-api")

# Token da SuperFrete via variável de ambiente
SUPERFRETE_TOKEN = os.environ.get("SUPERFRETE_TOKEN")
if not SUPERFRETE_TOKEN:
    logger.error("SUPERFRETE_TOKEN não configurado")
    raise RuntimeError("SUPERFRETE_TOKEN não configurado")

# URL base da SuperFrete
SUPERFRETE_URL = (
    "https://api.superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    "&accept=application%2Fjson"
    "&content-type=application%2Fjson"
)

# Session com retry/backoff
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 502, 503, 504],
    allowed_methods=["POST"]
)
session.mount("https://", HTTPAdapter(max_retries=retries))

# ==================== Endpoint ====================
@app.route("/api/calcular-frete", methods=["POST"])
def calcular_frete():
    request_id = str(uuid.uuid4())
    start_time = time.time()

    data = request.get_json(silent=True)

    # Validação de payload
    if not data or "cepDestino" not in data or "pacote" not in data:
        msg = "JSON inválido ou campos ausentes"
        logger.warning(msg, extra={"request_id": request_id, "payload": data})
        return jsonify({
            "request_id": request_id,
            "status": "erro",
            "mensagem": msg
        }), 400

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

    logger.info("Chamando SuperFrete", extra={"request_id": request_id, "payload": payload})

    try:
        response = session.post(
            SUPERFRETE_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )
        elapsed_time = round(time.time() - start_time, 3)

        try:
            resultado_json = response.json()
            logger.info("Resposta recebida", extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "elapsed_time": elapsed_time
            })
            return jsonify({
                "request_id": request_id,
                "status": "ok",
                "elapsed_time": elapsed_time,
                "resultado": resultado_json
            }), response.status_code
        except ValueError:
            msg = "Resposta da SuperFrete não é JSON"
            logger.error(msg, extra={
                "request_id": request_id,
                "texto": response.text,
                "elapsed_time": elapsed_time
            })
            return jsonify({
                "request_id": request_id,
                "status": "erro",
                "mensagem": msg,
                "texto": response.text
            }), 502

    except requests.exceptions.RequestException as e:
        elapsed_time = round(time.time() - start_time, 3)
        msg = "Falha na comunicação com SuperFrete"
        logger.error(msg, extra={"request_id": request_id, "detalhes": str(e), "elapsed_time": elapsed_time})
        return jsonify({
            "request_id": request_id,
            "status": "erro",
            "mensagem": msg,
            "detalhes": str(e),
            "elapsed_time": elapsed_time
        }), 502

# ==================== Run ====================
if __name__ == "__main__":
    app.run(debug=True)
