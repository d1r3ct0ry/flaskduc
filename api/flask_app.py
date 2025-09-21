from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ?? Token de autenticação da SuperFrete
SUPERFRETE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NTY3NTQ3NzcsInN1YiI6IlkydGZOTWhHQVFaNXFQUmF5VG1hWFEzT0ZoNTIifQ.Oo0CzxnRtwOPmBBAJgQBIz4U06qcVmrwLOic8CnyDe0"

# ?? URL com token e headers como query strings (reproduzindo curl funcional)
SUPERFRETE_URL = (
    f"https://superfrete.com/api/v0/calculator"
    f"?Authorization=Bearer%20{SUPERFRETE_TOKEN}"
    f"&accept=application%2Fjson"
    f"&content-type=application%2Fjson"
)

@app.route("/calcular-frete", methods=["POST"])
def calcular_frete():
    print("?? Nova requisição recebida para /calcular-frete")

    data = request.get_json(silent=True)
    print("?? JSON recebido:", data)

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
        # usa os valores enviados do frontend
        "package": {
            "height": pacote.get("height", 2),
            "width": pacote.get("width", 11),
            "length": pacote.get("length", 16),
            "weight": pacote.get("weight", 0.3)
        }
    }


    payload_json = json.dumps(payload)
    print("?? Payload JSON enviado para SuperFrete:")
    print(payload_json)

    headers = {
        "Content-Type": "application/json"
        # ? NÃO usa mais Authorization aqui, está na URL
    }

    # 3?? Chamada para a API da SuperFrete
    try:
        print(f"?? Fazendo requisição para SuperFrete: {SUPERFRETE_URL}")
        print(f"?? Headers enviados: {headers}")

        response = requests.post(SUPERFRETE_URL, headers=headers, data=payload_json, timeout=10)
        print(f"?? Status code da SuperFrete: {response.status_code}")

        try:
            result = response.json()
            print("?? Resposta JSON da SuperFrete:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except ValueError:
            result = {"erro": "Resposta não é JSON", "texto": response.text}
            print("?? Resposta da SuperFrete não é JSON:")
            print(response.text)
            return jsonify(result), 502

    except requests.exceptions.RequestException as e:
        print("? Erro ao chamar SuperFrete:", str(e))
        result = {"erro": "Falha na comunicação com SuperFrete", "detalhes": str(e)}
        return jsonify(result), 502

    # 4?? Retornar SOMENTE o que a SuperFrete retornou
    return jsonify(result), response.status_code

if __name__ == "__main__":
    app.run(debug=True)
