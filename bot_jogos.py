import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Tenta pegar a chave da variável de ambiente (GitHub)
# Se não encontrar, tenta carregar o arquivo local (Seu PC)
firebase_key_raw = os.getenv('FIREBASE_KEY_JSON')

if firebase_key_raw:
    # Configuração para o GITHUB ACTIONS
    # Converte a string da Secret de volta para um dicionário JSON
    cred_dict = json.loads(firebase_key_raw)
    cred = credentials.Certificate(cred_dict)
else:
    # Configuração para o seu COMPUTADOR (Local)
    # Certifique-se de que o nome do arquivo aqui é o mesmo que você tem na pasta
    cred = credentials.Certificate("firebase-key.json")

# 2. Inicializa o App apenas se não tiver sido inicializado ainda
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
