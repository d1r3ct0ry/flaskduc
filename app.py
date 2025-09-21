# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Permite todas as origens para a rota '/api/*'

# Coordenadas da origem
ORIGEM = (-22.7500087, -43.2872977)

@app.route('/api/obter_coordenadas', methods=['POST'])
def obter_coordenadas():
    data = request.get_json()
    endereco = data.get('endereco')
    if endereco:
        geolocator = Nominatim(user_agent="calculadora-de-entrega")
        location = geolocator.geocode(endereco)
        if location:
            latitude = location.latitude
            longitude = location.longitude
            distancia = calcular_distancia((latitude, longitude), ORIGEM)  # Calcula a distância em relação à origem
            return jsonify({'latitude': latitude, 'longitude': longitude, 'distancia': distancia})
    
    return jsonify({'error': 'Nao foi possivel obter as coordenadas.'}), 400

def calcular_distancia(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

if __name__ == '__main__':
    app.run(debug=True)
