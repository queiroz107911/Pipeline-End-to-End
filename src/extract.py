import requests
import logging
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / 'config' / '.env')
URL = os.getenv("API_URL") 

def extract_data():
    try:
        response = requests.get(URL , timeout=10)
        response.raise_for_status() # verifica erro, mas não retorna nada
        response_data = response.json()
        return response_data
    except requests.exceptions.RequestException as e:
        logging.warning(f"Erro ao extrair dados da API: {e}")
        raise

if __name__ == "__main__":
    print(extract_data())

