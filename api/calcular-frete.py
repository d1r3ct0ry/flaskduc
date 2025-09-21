import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json

# 🔐 Pega o token da variável de ambiente (definida na Vercel)
SUPERFRETE_TOKEN = os.environ.get("SUPERFRETE_TOKEN")
if not SUPERFRETE_TOKEN:
    raise ValueError("A variável de ambiente SUPERFRETE_TOKEN não está definida!")

# 🧭 URL base da SuperFrete com token
SUPERFRETE_URL = (
    f"https://api.superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    f"&accept=application%2Fjson"
    f"&content-type=application%2Fjson"
)

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📝 Modelos de dados
class Pacote(BaseModel):
    height: float = 2
    width: float = 11
    length: float = 16
    weight: float = 0.3

class FreteRequest(BaseModel):
    cepDestino: str
    pacote: Pacote

@app.post("/calcular-frete")
def calcular_frete(data: FreteRequest):
    payload = {
        "from": {"postal_code": "25065007"},
        "to": {"postal_code": str(data.cepDestino)},
        "services": "1,2",
        "options": {
            "own_hand": False,
            "receipt": False,
            "insurance_value": 0,
            "use_insurance_value": False
        },
        "package": {
            "height": data.pacote.height,
            "width": data.pacote.width,
            "length": data.pacote.length,
            "weight": data.pacote.weight
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(SUPERFRETE_URL, headers=headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Falha na comunicação com SuperFrete: {e}")
    except ValueError:
        raise HTTPException(status_code=502, detail=f"Resposta da SuperFrete não é JSON: {response.text}")

    return result
