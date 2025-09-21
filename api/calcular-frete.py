from flask import Flask, request, jsonify, make_response
import requests, os, json, uuid, time, logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("superfrete-api")

SUPERFRETE_TOKEN = os.environ.get("SUPERFRETE_TOKEN")
if not SUPERFRETE_TOKEN:
    raise RuntimeError("SUPERFRETE_TOKEN não configurado")

SUPERFRETE_URL = f"https://api.superfrete.com/api/v0/calculator?Authorization=Bearer%20{SUPERFRETE_TOKEN}&accept=application/json&content-type=application/json"

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429,502,503,504], allowed_methods=["POST"])
session.mount("https://", HTTPAdapter(max_retries=retries))

def cors_response(payload, status=200):
    response = make_response(jsonify(payload), status)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/api/calcular-frete", methods=["POST","OPTIONS"])
def calcular_frete():
    if request.method == "OPTIONS":
        return cors_response({"status":"ok"},200)

    request_id = str(uuid.uuid4())
    start_time = time.time()
    data = request.get_json(silent=True)

    if not data or "cepDestino" not in data or "pacote" not in data:
        return cors_response({
            "request_id": request_id,
            "status":"erro",
            "mensagem":"JSON inválido ou campos ausentes"
        },400)

    cep_destino = data["cepDestino"]
    pacote = data["pacote"]

    payload = {
        "from":{"postal_code":"25065007"},
        "to":{"postal_code":str(cep_destino)},
        "services":"1,2",
        "options":{"own_hand":False,"receipt":False,"insurance_value":0,"use_insurance_value":False},
        "package":{
            "height": pacote.get("height",2),
            "width": pacote.get("width",11),
            "length": pacote.get("length",16),
            "weight": pacote.get("weight",0.3)
        }
    }

    try:
        resp = session.post(SUPERFRETE_URL, headers={"Content-Type":"application/json"}, data=json.dumps(payload), timeout=10)
        resultado_json = resp.json()
        elapsed_time = round(time.time()-start_time,3)
        return cors_response({
            "request_id": request_id,
            "status":"ok",
            "elapsed_time": elapsed_time,
            "resultado": resultado_json
        }, resp.status_code)
    except Exception as e:
        elapsed_time = round(time.time()-start_time,3)
        return cors_response({
            "request_id": request_id,
            "status":"erro",
            "mensagem":"Falha na comunicação com SuperFrete",
            "detalhes": str(e),
            "elapsed_time": elapsed_time
        },502)
