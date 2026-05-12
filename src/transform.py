import pandas as pd
import logging

def _convert_to_time(df):
    df['time'] = pd.to_datetime(df['time']) 
    return df

def _check_nulls(df: pd.DataFrame):
    logging.info(f"Nulos por coluna:\n{df.isnull().sum()}")
    return df

def _drop_nulls(df: pd.DataFrame): # garantir para que caso mude a base de dados não haja nenhum nulo
    return df.dropna()

def _groupby_by_day(df: pd.DataFrame):
    grouped = df.groupby(df['time' ].dt.date)
    result = grouped.agg(
        temp_media=('temperature_2m', 'mean'),
        temp_max=('temperature_2m', 'max'),
        temp_min=('temperature_2m', 'min'),
        precipitacao_total=('precipitation', 'sum')
    )
    return result

def bronze_to_silver(data: dict):
    hourly = data['hourly'] # extrai só o conteúdo interno
    df = pd.DataFrame(hourly) # transforma as chaves do dicionário em colunas
    df = _convert_to_time(df)
    df = _check_nulls(df)
    df = _drop_nulls(df)

    logging.info("Transform funcionando com sucesso !")

    return df

def silver_to_gold(df: pd.DataFrame):
    df = _groupby_by_day(df)

    logging.info("Agrupamento funcionando")

    return df
    

if __name__ == "__main__":
    from extract import extract_data
    data = extract_data()
    silver = bronze_to_silver(data)
    gold = silver_to_gold(silver)
    print(gold)
    print(gold.dtypes)