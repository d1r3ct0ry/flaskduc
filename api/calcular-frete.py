import os
import requests
import json

SUPERFRETE_TOKEN = os.environ.get("SUPERFRETE_TOKEN")
if not SUPERFRETE_TOKEN:
    raise RuntimeError("SUPERFRETE_TOKEN não definido")

SUPERFRETE_URL = (
    f"https://api.superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    f"&accept=application%2Fjson"
    f"&content-type=application%2Fjson"
)

def handler(request):
    # ✅ Preflight
    if request.method == "OPTIONS":
        return {}, 204, {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }

    # Apenas POST
    if request.method != "POST":
        return {"erro": "Método não permitido"}, 405, {"Access-Control-Allow-Origin": "*"}

    try:
        data = request.json
    except Exception:
        data = None

    if not data or "cepDestino" not in data or "pacote" not in data:
        return {"erro": "JSON inválido ou campos ausentes"}, 400, {"Access-Control-Allow-Origin": "*"}

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
            return {"erro": "Resposta não é JSON", "texto": response.text}, 502, {"Access-Control-Allow-Origin": "*"}
    except requests.exceptions.RequestException as e:
        return {"erro": "Falha na comunicação com SuperFrete", "detalhes": str(e)}, 502, {"Access-Control-Allow-Origin": "*"}

    return result, response.status_code, {"Access-Control-Allow-Origin": "*"}
