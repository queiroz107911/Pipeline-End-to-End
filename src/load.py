import json
import pandas as pd
import logging

from pathlib import Path
BASE_DIR = Path(__file__).parent.parent # variável especial do Python que contém o caminho do arquivo atual.
BRONZE_PATH = BASE_DIR / 'data' / 'bronze'
SILVER_PATH = BASE_DIR / 'data' / 'silver'
GOLD_PATH = BASE_DIR / 'data' / 'gold'

def load_bronze(data: dict):
    with open(BRONZE_PATH / 'raw.json', 'w') as f:
        json.dump(data, f)
    logging.info("Camada bronze funcionando")

def load_silver(df: pd.DataFrame):
    df.to_parquet(SILVER_PATH / 'silver.parquet')
    logging.info("Camada silver funcionando")

def load_gold(df: pd.DataFrame):
    df.to_parquet(GOLD_PATH /'gold.parquet')
    logging.info("Camada gold funcionando")