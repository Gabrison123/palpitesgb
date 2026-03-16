import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURAÇÃO DO FIREBASE (GITHUB OU LOCAL) ---
firebase_key_raw = os.getenv('FIREBASE_KEY_JSON')

if firebase_key_raw:
    cred_dict = json.loads(firebase_key_raw)
    cred = credentials.Certificate(cred_dict)
else:
    # Se estiver no seu PC, use o arquivo físico
    cred = credentials.Certificate("firebase-key.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- FUNÇÃO DO ROBÔ HACKER (SCRAPING) ---
def buscar_jogos_ge():
    # URL do Brasileirão no GE
    url = "https://ge.globo.com/futebol/brasileirao-serie-a/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # No GE, os jogos costumam ficar dentro de tags <article> ou <li> com classes específicas
    # As classes abaixo são exemplos comuns, mas o GE pode variar conforme a rodada
    jogos = soup.find_all('li', class_='lista-jogos__item')

    if not jogos:
        print("Atenção: Não encontrei jogos. As classes do site podem ter mudado.")
        return

    for jogo in jogos:
        try:
            # Pegando o nome dos times
            time_casa = jogo.find('div', class_='jogo-equipes__equipe--casa').find('span', class_='equipe-nome').text
            time_fora = jogo.find('div', class_='jogo-equipes__equipe--fora').find('span', class_='equipe-nome').text
            
            # Pegando a data e hora (Ex: "Sáb 16/03 16:00")
            info_data = jogo.find('div', class_='jogo-informacoes').text.strip()
            
            # Criando um ID único para não duplicar o jogo no seu banco
            id_jogo = f"ge_2026_{time_casa.replace(' ', '')}_{time_fora.replace(' ', '')}"
            
            # Enviando para o Firestore do palpitesGB
            db.collection('jogos').document(id_jogo).set({
                'campeonato': 'Brasileirão',
                'timeA': time_casa,
                'timeB': time_fora,
                'data_bruta': info_data, # Texto como aparece no site
                'data': datetime.now().isoformat(), # Hora que foi importado
                'finalizado': False
            })
            print(f"✅ Adicionado: {time_casa} x {time_fora}")
            
        except Exception as e:
            print(f"Erro ao processar um jogo: {e}")

# Executa o robô
buscar_jogos_ge()
