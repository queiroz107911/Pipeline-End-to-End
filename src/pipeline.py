from extract import extract_data
from transform import bronze_to_silver, silver_to_gold
from load import load_bronze, load_silver, load_gold
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def pipeline_completo():
    data = extract_data()
    load_bronze(data)
    silver = bronze_to_silver(data)
    load_silver(silver)
    gold = silver_to_gold(silver)
    load_gold(gold)

    logging.info("Pipeline concluído com sucesso !")

if __name__ == "__main__":
    pipeline_completo()

