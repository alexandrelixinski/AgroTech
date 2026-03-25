import json
import os

def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return []

def salvar_dados(dados, arquivo):
    with open(arquivo, "w", encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)