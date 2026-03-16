import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURAÇÃO DO FIREBASE ---
# Ajustado para ler a Secret exata do seu GitHub: FIREBASE_KEY
chave_github = os.getenv('FIREBASE_KEY')

if chave_github:
    print("✅ Conectado ao GitHub Actions: Usando Secret FIREBASE_KEY.")
    try:
        cred_dict = json.loads(chave_github)
        cred = credentials.Certificate(cred_dict)
    except Exception as e:
        print(f"❌ Erro ao converter a Secret para JSON: {e}")
        exit(1)
else:
    print("⚠️ FIREBASE_KEY não encontrada no ambiente. Tentando modo local...")
    # No seu PC, o arquivo deve ter esse nome:
    cred = credentials.Certificate("firebase-key.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- FUNÇÃO DE SCRAPING (GE) ---
def buscar_jogos_ge():
    url = "https://ge.globo.com/futebol/brasileirao-serie-a/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscando os itens da lista de jogos
        jogos = soup.find_all('li', class_='lista-jogos__item')

        if not jogos:
            print("❌ Não encontrei jogos. Verifique se as classes do GE mudaram.")
            return

        for jogo in jogos:
            try:
                time_casa = jogo.find('div', class_='jogo-equipes__equipe--casa').find('span', class_='equipe-nome').text
                time_fora = jogo.find('div', class_='jogo-equipes__equipe--fora').find('span', class_='equipe-nome').text
                info_data = jogo.find('div', class_='jogo-informacoes').text.strip()
                
                # Cria um ID baseado nos times para não duplicar
                id_jogo = f"ge_2026_{time_casa.replace(' ', '')}_{time_fora.replace(' ', '')}"
                
                db.collection('jogos').document(id_jogo).set({
                    'campeonato': 'Brasileirão',
                    'timeA': time_casa,
                    'timeB': time_fora,
                    'data_bruta': info_data,
                    'data': datetime.now().isoformat(),
                    'finalizado': False
                }, merge=True) # merge=True evita apagar dados extras se o jogo já existir
                
                print(f"✔️ {time_casa} x {time_fora} sincronizado.")
                
            except AttributeError:
                continue # Pula itens que não são jogos reais (anúncios, etc)

    except Exception as e:
        print(f"❌ Erro geral no scraping: {e}")

if __name__ == "__main__":
    buscar_jogos_ge()
