import pytest
import json
from pathlib import Path
from unittest.mock import patch
from pipeline import pipeline_completo


# ─────────────────────────────────────────────
# DADO FALSO — simula retorno da API
# ─────────────────────────────────────────────

API_RESPONSE_FAKE = {
    'hourly': {
        'time': [
            '2026-05-12T00:00', '2026-05-12T01:00', '2026-05-12T02:00',
            '2026-05-13T00:00', '2026-05-13T01:00', '2026-05-13T02:00',
        ],
        'temperature_2m': [22.0, 21.0, 20.0, 25.0, 24.0, 23.0],
        'precipitation':  [0.0,  0.1,  0.0,  0.5,  0.2,  0.0],
        'wind_speed_10m': [8.1,  9.0,  7.5,  10.0, 11.0, 9.5],
    }
}


# ─────────────────────────────────────────────
# TESTE DE INTEGRAÇÃO
# ─────────────────────────────────────────────

def test_pipeline_completo_cria_arquivos(tmp_path):
    """
    Testa o pipeline de ponta a ponta — do extract ao load.

    'tmp_path' é uma fixture nativa do pytest que cria uma pasta
    temporária para cada teste. Assim não sujamos a pasta data/ real.

    'patch' substitui temporariamente o extract_data() real pelo fake —
    sem isso o teste faria chamada real para a API (lento e frágil).
    """
    # Substitui os caminhos de destino pela pasta temporária do teste
    bronze_path = tmp_path / 'bronze'
    silver_path = tmp_path / 'silver'
    gold_path   = tmp_path / 'gold'

    bronze_path.mkdir()
    silver_path.mkdir()
    gold_path.mkdir()

    with patch('pipeline.extract_data', return_value=API_RESPONSE_FAKE), \
         patch('load.BRONZE_PATH', bronze_path), \
         patch('load.SILVER_PATH', silver_path), \
         patch('load.GOLD_PATH',   gold_path):

        pipeline_completo()

    # Verifica se os três arquivos foram criados
    assert (bronze_path / 'raw.json').exists(),       "raw.json não foi criado"
    assert (silver_path / 'silver.parquet').exists(), "silver.parquet não foi criado"
    assert (gold_path   / 'gold.parquet').exists(),   "gold.parquet não foi criado"


def test_pipeline_bronze_conteudo_correto(tmp_path):
    """
    Verifica se o conteúdo do raw.json é exatamente o que veio da API.
    Bronze não deve transformar nada — fidelidade total à fonte.
    """
    bronze_path = tmp_path / 'bronze'
    silver_path = tmp_path / 'silver'
    gold_path   = tmp_path / 'gold'

    bronze_path.mkdir()
    silver_path.mkdir()
    gold_path.mkdir()

    with patch('pipeline.extract_data', return_value=API_RESPONSE_FAKE), \
         patch('load.BRONZE_PATH', bronze_path), \
         patch('load.SILVER_PATH', silver_path), \
         patch('load.GOLD_PATH',   gold_path):

        pipeline_completo()

    with open(bronze_path / 'raw.json') as f:
        conteudo = json.load(f)

    assert conteudo == API_RESPONSE_FAKE