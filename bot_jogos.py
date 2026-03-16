import requests
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- CONFIGURAÇÃO INICIAL ---
if not firebase_admin._apps:
    cred = credentials.Certificate("sua-chave-firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
API_KEY = "SUA_CHAVE_AQUI"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

def buscar_e_gravar_jogos(league_id):
    # Pega a data de hoje automaticamente (ex: 2026-03-16)
    hoje = time.strftime("%Y-%m-%d") 
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={league_id}&timezone=America/Sao_Paulo"
    
    response = requests.get(url, headers=HEADERS)
    dados = response.json()

    if "response" in dados:
        for item in dados["response"]:
            fid = str(item["fixture"]["id"])
            dados_jogo = {
                "id_partida": fid,
                "campeonato": item["league"]["name"],
                "time_casa": item["teams"]["home"]["name"],
                "logo_casa": item["teams"]["home"]["logo"], # Garante o escudo correto
                "time_fora": item["teams"]["away"]["name"],
                "logo_fora": item["teams"]["away"]["logo"], # Garante o escudo correto
                "data_hora": item["fixture"]["date"],
                "status": "aberto"
            }
            # Grava usando o ID da partida para não duplicar
            db.collection("jogos_abertos").document(fid).set(dados_jogo)
            print(f"Adicionado: {dados_jogo['time_casa']} x {dados_jogo['time_fora']}")

# LOOP DE VIGILÂNCIA
print("Aguardando comando pelo Firebase...")
while True:
    comando_ref = db.collection("configuracoes").document("comando_busca")
    doc = comando_ref.get()
    
    if doc.exists:
        comando = doc.to_dict()
        if comando.get("status") == "executar":
            print(f"Comando recebido para League ID: {comando['league_id']}")
            buscar_e_gravar_jogos(comando['league_id'])
            
            # Volta o status para "concluido" para não ficar repetindo
            comando_ref.update({"status": "concluido"})
    
    time.sleep(10) # Verifica a cada 10 segundos
