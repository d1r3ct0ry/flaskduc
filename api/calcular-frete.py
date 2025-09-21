# api/calcular-frete.py
import os
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS completo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # qualquer origem
    allow_methods=["*"],  # POST, OPTIONS, etc
    allow_headers=["*"],  # Content-Type, Authorization, etc
)

SUPERFRETE_TOKEN = os.environ.get("SUPERFRETE_TOKEN")
if not SUPERFRETE_TOKEN:
    raise RuntimeError("SUPERFRETE_TOKEN não definido")

SUPERFRETE_URL = (
    f"https://api.superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    f"&accept=application%2Fjson"
    f"&content-type=application%2Fjson"
)

@app.post("/api/calcular-frete")
async def calcular_frete(request: Request):
    data = await request.json()
    if not data or "cepDestino" not in data or "pacote" not in data:
        return JSONResponse({"erro": "JSON inválido ou campos ausentes"}, status_code=400)

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

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(SUPERFRETE_URL, json=payload)
            resp_json = resp.json()
        except Exception as e:
            return JSONResponse({"erro": "Falha na comunicação com SuperFrete", "detalhes": str(e)}, status_code=502)

    return JSONResponse(resp_json, status_code=resp.status_code)
