import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Aqui o robô pega a chave que você colou no GitHub Secrets
service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY'))
cred = credentials.Certificate(service_account_info)

# Inicializa o Firebase (usando Firestore, que é o que aparece no seu print)
firebase_admin.initialize_app(cred)
db = firestore.client()

def atualizar_jogos():
    # Aqui entraria a lógica de buscar na API de Futebol
    # Por enquanto, vamos simular a gravação de um jogo real
    novo_jogo = {
        "campeonato": "Champions League",
        "timeA": "Real Madrid",
        "timeB": "Manchester City",
        "data": "2026-03-20T20:00",
        "finalizado": False,
        "pontos_atribuidos": False
    }
    
    # Salva no banco igual o seu site espera ler
    db.collection("jogos").add(novo_jogo)
    print("Jogo atualizado com sucesso!")

if __name__ == "__main__":
    atualizar_jogos()
