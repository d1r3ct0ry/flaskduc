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
@@ -40,7 +72,6 @@ def calcular_frete():
            "insurance_value": 0,
            "use_insurance_value": False
        },

        "package": {
            "height": pacote.get("height", 2),
            "width": pacote.get("width", 11),
@@ -49,41 +80,57 @@ def calcular_frete():
        }
    }

    logger.info("Chamando SuperFrete", extra={"request_id": request_id, "payload": payload})
