import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURAÇÃO DO FIREBASE ---
# Baixe seu arquivo JSON no Console do Firebase (Configurações do Projeto > Contas de Serviço)
if not firebase_admin._apps:
    cred = credentials.Certificate("sua-chave-firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. CONFIGURAÇÃO DA API DE FUTEBOL ---
API_KEY = "SUA_CHAVE_AQUI"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# IDs que você quer buscar (71 = Brasileirão Série A, 2 = Champions League)
CAMPEONATOS_ALVO = [71, 2]

def sincronizar_rodada(data_selecionada):
    """
    Busca jogos reais e salva no Firestore com IDs únicos.
    Formato da data: 'YYYY-MM-DD'
    """
    print(f"Iniciando busca para o dia {data_selecionada}...")
    
    url = f"https://v3.football.api-sports.io/fixtures?date={data_selecionada}&timezone=America/Sao_Paulo"
    response = requests.get(url, headers=HEADERS)
    dados = response.json()

    if "response" not in dados or not dados["response"]:
        print("Nenhum jogo encontrado para esta data.")
        return

    # Referência da coleção onde ficam os palpites
    jogos_ref = db.collection("jogos_abertos")

    for item in dados["response"]:
        league_id = item["league"]["id"]

        # FILTRO: Só processa se for um dos campeonatos que você quer
        if league_id in CAMPEONATOS_ALVO:
            fixture_id = str(item["fixture"]["id"]) # ID único da partida
            
            # Monta o objeto exatamente como seu banco precisa
            objeto_jogo = {
                "id_partida": fixture_id,
                "campeonato": item["league"]["name"],
                "time_casa": item["teams"]["home"]["name"],
                "logo_casa": item["teams"]["home"]["logo"], # URL oficial da imagem
                "time_fora": item["teams"]["away"]["name"],
                "logo_fora": item["teams"]["away"]["logo"], # URL oficial da imagem
                "data_iso": item["fixture"]["date"],
                "status": "pendente"
            }

            # SALVA NO FIREBASE: Usar .document(fixture_id) impede nomes aleatórios e duplicados
            jogos_ref.document(fixture_id).set(objeto_jogo)
            print(f"Sucesso: {objeto_jogo['time_casa']} x {objeto_jogo['time_fora']}")

# Exemplo de uso:
sincronizar_rodada("2026-03-20")
