import requests
import firebase_admin
from firebase_admin import credentials, firestore

# Inicialização (ajuste o caminho do seu JSON)
if not firebase_admin._apps:
    cred = credentials.Certificate("sua-chave-firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def adicionar_jogos_reais(league_id):
    API_KEY = "SUA_API_KEY_AQUI"
    headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
    
    # Busca jogos de hoje
    url = f"https://v3.football.api-sports.io/fixtures?date=2026-03-20&league={league_id}&timezone=America/Sao_Paulo"
    
    res = requests.get(url, headers=headers)
    dados = res.json()

    if "response" in dados:
        for jogo in dados["response"]:
            # O fixture_id garante que não existam jogos duplicados
            fid = str(jogo["fixture"]["id"])
            
            doc_jogo = {
                "campeonato": jogo["league"]["name"],
                "time_casa": jogo["teams"]["home"]["name"],
                "logo_casa": jogo["teams"]["home"]["logo"], # <--- LINK DA IMAGEM REAL
                "time_fora": jogo["teams"]["away"]["name"],
                "logo_fora": jogo["teams"]["away"]["logo"], # <--- LINK DA IMAGEM REAL
                "data": jogo["fixture"]["date"]
            }
            
            # Salva no Firebase usando o ID da partida
            db.collection("jogos_abertos").document(fid).set(doc_jogo)
            print(f"Adicionado: {doc_jogo['time_casa']} vs {doc_jogo['time_fora']}")

# Para o Brasileirão use 71, para Champions use 2
adicionar_jogos_reais(71)
