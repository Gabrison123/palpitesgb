import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURAÇÕES ---
# 1. Substitua pelo caminho do seu arquivo JSON do Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("caminho/do/seu/firebase-key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Sua chave da API-Football
API_KEY = "SUA_API_KEY_AQUI"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# 3. IDs dos campeonatos (Brasileirão: 71, Champions: 2, Premier League: 39)
CAMPEONATOS_PERMITIDOS = [71, 2]

def atualizar_jogos_no_firebase(data_busca):
    url = f"https://v3.football.api-sports.io/fixtures?date={data_busca}&timezone=America/Sao_Paulo"
    
    try:
        response = requests.get(url, headers=HEADERS)
        dados = response.json()
        
        # Referência da sua coleção de jogos no Firestore
        jogos_ref = db.collection("jogos_abertos") # Ajuste para o nome da sua coleção

        if "response" in dados:
            for item in dados["response"]:
                league_id = item["league"]["id"]
                
                # FILTRO DE CAMPEONATO
                if league_id in CAMPEONATOS_PERMITIDOS:
                    fixture_id = str(item["fixture"]["id"])
                    
                    dados_jogo = {
                        "campeonato": item["league"]["name"],
                        "campeonato_id": league_id,
                        "time_casa": item["teams"]["home"]["name"],
                        "logo_casa": item["teams"]["home"]["logo"], # URL oficial da imagem
                        "time_fora": item["teams"]["away"]["name"],
                        "logo_fora": item["teams"]["away"]["logo"], # URL oficial da imagem
                        "data_hora": item["fixture"]["date"],
                        "status": "aberto"
                    }
                    
                    # Salva ou atualiza no Firebase usando o ID da partida como nome do documento
                    jogos_ref.document(fixture_id).set(dados_jogo)
                    print(f"Jogo adicionado: {dados_jogo['time_casa']} x {dados_jogo['time_fora']}")
                    
    except Exception as e:
        print(f"Erro ao processar: {e}")

# Execução (Ex: buscar jogos para o dia 20/03/2026)
atualizar_jogos_no_firebase("2026-03-20")
