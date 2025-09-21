import os
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 🔐 Pega o token da variável de ambiente (definida na Vercel)
SUPERFRETE_TOKEN = os.environ.get("SUPERFRETE_TOKEN")
if not SUPERFRETE_TOKEN:
    raise ValueError("A variável de ambiente SUPERFRETE_TOKEN não está definida!")

# 🧭 URL base da SuperFrete com token na query string
SUPERFRETE_URL = (
    f"https://api.superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    f"&accept=application%2Fjson"
    f"&content-type=application%2Fjson"
)

app = FastAPI()

# ✅ Configuração CORS
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
    print("🚚 Nova requisição recebida para /calcular-frete")
    print("📨 JSON recebido:", data.dict())

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

    payload_json = json.dumps(payload)
    print("📦 Payload JSON enviado para SuperFrete:")
    print(payload_json)

    headers = {"Content-Type": "application/json"}

    try:
        print(f"🌍 Fazendo requisição para SuperFrete: {SUPERFRETE_URL}")
        response = requests.post(SUPERFRETE_URL, headers=headers, data=payload_json, timeout=10)
        print(f"📬 Status code da SuperFrete: {response.status_code}")

        try:
            result = response.json()
            print("📥 Resposta JSON da SuperFrete:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except ValueError:
            print("⚠️ Resposta da SuperFrete não é JSON:")
            print(response.text)
            raise HTTPException(status_code=502, detail={"erro": "Resposta não é JSON", "texto": response.text})

    except requests.exceptions.RequestException as e:
        print("❌ Erro ao chamar SuperFrete:", str(e))
        raise HTTPException(status_code=502, detail={"erro": "Falha na comunicação com SuperFrete", "detalhes": str(e)})

    return result
