import pandas as pd
import pytest
from transform import bronze_to_silver, silver_to_gold


# ─────────────────────────────────────────────
# FIXTURE — dado falso reutilizável em todos os testes
# ─────────────────────────────────────────────

@pytest.fixture
def data_fake():
    """
    Simula o dicionário retornado pela Open-Meteo API.
    Usar fixture evita repetir o mesmo dicionário em cada teste.
    """
    return {
        'hourly': {
            'time': [
                '2026-05-12T00:00', '2026-05-12T01:00',
                '2026-05-12T02:00', '2026-05-13T00:00',
                '2026-05-13T01:00', '2026-05-13T02:00',
            ],
            'temperature_2m': [22.0, 21.0, 20.0, 25.0, 24.0, 23.0],
            'precipitation':  [0.0,  0.1,  0.0,  0.5,  0.2,  0.0],
            'wind_speed_10m': [8.1,  9.0,  7.5,  10.0, 11.0, 9.5],
        }
    }


@pytest.fixture
def data_fake_com_nulos():
    """
    Simula dados com valores nulos — para testar se o pipeline os remove.
    """
    return {
        'hourly': {
            'time': ['2026-05-12T00:00', '2026-05-12T01:00', '2026-05-12T02:00'],
            'temperature_2m': [22.0, None, 20.0],   # None = nulo
            'precipitation':  [0.0,  0.1,  None],
            'wind_speed_10m': [8.1,  9.0,  7.5],
        }
    }


# ─────────────────────────────────────────────
# TESTES — bronze_to_silver
# ─────────────────────────────────────────────

def test_bronze_to_silver_retorna_dataframe(data_fake):
    """
    Verifica se a função retorna um DataFrame — não um dicionário, lista, etc.
    É o teste mais básico: o tipo do retorno está certo?
    """
    df = bronze_to_silver(data_fake)
    assert isinstance(df, pd.DataFrame)


def test_bronze_to_silver_colunas_corretas(data_fake):
    """
    Verifica se o DataFrame tem exatamente as 4 colunas esperadas.
    Se alguém mudar o nome de uma coluna no transform, esse teste quebra e avisa.
    """
    df = bronze_to_silver(data_fake)
    colunas_esperadas = ['time', 'temperature_2m', 'precipitation', 'wind_speed_10m']
    assert list(df.columns) == colunas_esperadas


def test_bronze_to_silver_time_é_datetime(data_fake):
    """
    Verifica se a coluna 'time' foi convertida para datetime.
    String '2026-05-12T00:00' não permite operações de data — datetime sim.
    """
    df = bronze_to_silver(data_fake)
    assert pd.api.types.is_datetime64_any_dtype(df['time'])


def test_bronze_to_silver_sem_nulos(data_fake):
    """
    Verifica se o DataFrame retornado não tem nulos.
    O _drop_nulls deve ter removido qualquer linha com valor faltante.
    """
    df = bronze_to_silver(data_fake)
    assert df.isnull().sum().sum() == 0


def test_bronze_to_silver_remove_nulos(data_fake_com_nulos):
    """
    Passa dados COM nulos e verifica se eles foram removidos.
    Diferente do teste acima — aqui forçamos nulos para entrar e vemos se saem.
    Dados originais têm 3 linhas, 2 têm nulos → deve sobrar 1 linha limpa.
    """
    df = bronze_to_silver(data_fake_com_nulos)
    assert df.isnull().sum().sum() == 0
    assert len(df) == 1  # só a primeira linha não tinha nulos


def test_bronze_to_silver_numero_de_linhas(data_fake):
    """
    Verifica se o número de linhas está correto.
    data_fake tem 6 registros horários sem nulos — devem todos passar.
    """
    df = bronze_to_silver(data_fake)
    assert len(df) == 6


# ─────────────────────────────────────────────
# TESTES — silver_to_gold
# ─────────────────────────────────────────────

def test_silver_to_gold_retorna_dataframe(data_fake):
    """
    Verifica se silver_to_gold retorna um DataFrame.
    """
    silver = bronze_to_silver(data_fake)
    gold = silver_to_gold(silver)
    assert isinstance(gold, pd.DataFrame)


def test_silver_to_gold_colunas_corretas(data_fake):
    """
    Verifica se o DataFrame Gold tem as colunas de agregação esperadas.
    """
    silver = bronze_to_silver(data_fake)
    gold = silver_to_gold(silver)
    colunas_esperadas = ['temp_media', 'temp_max', 'temp_min', 'precipitacao_total']
    assert list(gold.columns) == colunas_esperadas


def test_silver_to_gold_agrega_por_dia(data_fake):
    """
    data_fake tem 6 registros: 3 do dia 2026-05-12 e 3 do dia 2026-05-13.
    Após agregar por dia, o Gold deve ter exatamente 2 linhas.
    """
    silver = bronze_to_silver(data_fake)
    gold = silver_to_gold(silver)
    assert len(gold) == 2


def test_silver_to_gold_temp_max_correta(data_fake):
    """
    Verifica se o cálculo de temperatura máxima está correto.
    Dia 2026-05-12 tem temperaturas [22.0, 21.0, 20.0] → máxima deve ser 22.0
    """
    silver = bronze_to_silver(data_fake)
    gold = silver_to_gold(silver)
    assert gold['temp_max'].iloc[0] == 22.0


def test_silver_to_gold_precipitacao_total_correta(data_fake):
    """
    Verifica se a soma de precipitação está correta.
    Dia 2026-05-12 tem precipitações [0.0, 0.1, 0.0] → total deve ser 0.1
    """
    silver = bronze_to_silver(data_fake)
    gold = silver_to_gold(silver)
    assert round(gold['precipitacao_total'].iloc[0], 1) == 0.1