import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os
import json

# Configuração do Firebase via GitHub Secrets
if os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY'):
    cred_json = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY'))
    cred = credentials.Certificate(cred_json)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

def buscar_e_atualizar():
    # Usando a API-Football que você abriu no navegador
    url = "https://v3.football.api-sports.io/fixtures?league=71&season=2026&next=10" # League 71 = Brasileirão
    headers = {
        'x-rapidapi-key': os.environ.get('FOOTBALL_API_KEY'),
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url, headers=headers)
    dados = response.json()

    for item in dados['response']:
        jogo_id = str(item['fixture']['id'])
        dados_jogo = {
            "campeonato": item['league']['name'],
            "timeA": item['teams']['home']['name'],
            "logoA": item['teams']['home']['logo'],
            "timeB": item['teams']['away']['name'],
            "logoB": item['teams']['away']['logo'],
            "data": item['fixture']['date'],
            "finalizado": False,
            "tipo": "oficial"
        }
        
        # Salva ou atualiza no Firestore
        db.collection("jogos").document(jogo_id).set(dados_jogo)
        print(f"Adicionado: {dados_jogo['timeA']} x {dados_jogo['timeB']}")

if __name__ == "__main__":
    buscar_e_atualizar()
