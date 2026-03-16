import requests
import firebase_admin
from firebase_admin import credentials, firestore
import time

# 1. Configuração do Firebase (use o seu arquivo JSON)
if not firebase_admin._apps:
    cred = credentials.Certificate("sua-chave-firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Configuração da API-Football
API_KEY = "SUA_API_KEY_AQUI"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

def atualizar_jogos(league_id):
    # Pega a data de hoje para buscar jogos reais
    hoje = time.strftime("%Y-%m-%d") 
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={league_id}&timezone=America/Sao_Paulo"
    
    response = requests.get(url, headers=HEADERS)
    dados = response.json()

    if "response" in dados and dados["response"]:
        # Referência da coleção onde os jogos aparecem no site
        # Mude "jogos" para o nome exato da sua coleção de partidas
        jogos_ref = db.collection("jogos") 

        for item in dados["response"]:
            fixture_id = str(item["fixture"]["id"])
            
            dados_partida = {
                "id": fixture_id,
                "campeonato": item["league"]["name"],
                "time_casa": item["teams"]["home"]["name"],
                "logo_casa": item["teams"]["home"]["logo"], # URL direta para o escudo certo
                "time_fora": item["teams"]["away"]["name"],
                "logo_fora": item["teams"]["away"]["logo"], # URL direta para o escudo certo
                "data_hora": item["fixture"]["date"],
                "status": "aberto"
            }
            # Grava usando o ID da partida (ex: 112233) em vez de IDs aleatórios
            jogos_ref.document(fixture_id).set(dados_partida)
            print(f"Adicionado: {dados_partida['time_casa']} x {dados_partida['time_fora']}")
    else:
        print("Nenhum jogo encontrado para hoje neste campeonato.")

# Loop que fica vigiando o comando
print("Monitorando comandos do Firebase...")
while True:
    try:
        doc_ref = db.collection("configuracoes").document("comando_busca")
        doc = doc_ref.get()
        
        if doc.exists:
            comando = doc.to_dict()
            if comando.get("status") == "executar":
                print(f"Executando busca para League ID: {comando.get('league_id')}")
                atualizar_jogos(comando.get("league_id"))
                
                # Reseta o status para não entrar em loop infinito
                doc_ref.update({"status": "concluido"})
    except Exception as e:
        print(f"Erro: {e}")
    
    time.sleep(10) # Espera 10 segundos para checar de novo
