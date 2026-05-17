# 🌦️ Pipeline Meteorológico End-to-End

Pipeline de dados completo usando arquitetura **Medallion (Bronze / Silver / Gold)**, consumindo dados meteorológicos em tempo real da [Open-Meteo API](https://open-meteo.com/) para Brasília, DF.

---

## 🏗️ Arquitetura

```
[Open-Meteo API]
      │
      ▼
  [Bronze] ← dado bruto em JSON, fidelidade total à fonte
      │
      ▼
  [Silver] ← dado limpo, tipado, sem nulos, particionado por hora
      │
      ▼
   [Gold]  ← agregado diário: temp média, máx, mín, precipitação total
```

| Camada | Formato | Transformações |
|---|---|---|
| Bronze | `.json` | Nenhuma — dado bruto + metadados da API |
| Silver | `.parquet` | Tipagem, remoção de nulos, conversão de datetime |
| Gold | `.parquet` | Agregação diária por temperatura e precipitação |

---

## 🗂️ Estrutura do Projeto

```
Pipeline_End_to_End/
├── data/
│   ├── bronze/          → raw.json
│   ├── silver/          → silver.parquet
│   └── gold/            → gold.parquet
├── src/
│   ├── extract.py       → coleta da API
│   ├── transform.py     → Bronze→Silver e Silver→Gold
│   ├── load.py          → persiste cada camada
│   └── pipeline.py      → orquestrador
├── tests/
│   ├── unit/
│   │   └── test_transform.py
│   └── integration/
│       └── test_pipeline.py
├── config/
│   └── .env             → variáveis de ambiente (não versionado)
├── docs/
│   └── day_one.md       → decisões e contexto do projeto
├── conftest.py
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

> ⚠️ A pasta `data/` não é versionada. Os arquivos são gerados ao rodar o pipeline.

---

## ⚙️ Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Ingestão | `requests` |
| Transformação | `pandas` |
| Formato de dados | Parquet + JSON |
| Gerenciador de pacotes | `uv` |
| Testes | `pytest` |
| Containerização | Docker (requer virtualização habilitada) |

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) instalado

### 1. Clonar e instalar dependências

```bash
git clone <repo-url>
cd Pipeline_End_to_End
uv sync
```

### 2. Configurar variáveis de ambiente

Cria o arquivo `config/.env`:

```env
API_URL=[documentação da Open-Meteo](https://open-meteo.com/en/docs)
```

### 3. Rodar o pipeline

```bash
python src/pipeline.py
```

### Output esperado

```
2026-05-12 10:34:54 - INFO - Camada bronze funcionando
2026-05-12 10:34:54 - INFO - Nulos por coluna: ...
2026-05-12 10:34:54 - INFO - Transform funcionando com sucesso !
2026-05-12 10:34:54 - INFO - Camada silver funcionando
2026-05-12 10:34:54 - INFO - Agrupamento funcionando
2026-05-12 10:34:54 - INFO - Camada gold funcionando
2026-05-12 10:34:54 - INFO - Pipeline concluído com sucesso !
```

### 4. Rodar com Docker

> ⚠️ Requer virtualização habilitada no Windows (Hyper-V ou WSL2).

```bash
docker-compose up --build
```

---

## 🧪 Testes

```bash
pytest tests/ -v
```

```
tests/integration/test_pipeline.py::test_pipeline_completo_cria_arquivos   PASSED
tests/integration/test_pipeline.py::test_pipeline_bronze_conteudo_correto  PASSED
tests/unit/test_transform.py::test_bronze_to_silver_retorna_dataframe       PASSED
tests/unit/test_transform.py::test_bronze_to_silver_colunas_corretas        PASSED
tests/unit/test_transform.py::test_bronze_to_silver_time_é_datetime         PASSED
tests/unit/test_transform.py::test_bronze_to_silver_sem_nulos               PASSED
tests/unit/test_transform.py::test_bronze_to_silver_remove_nulos            PASSED
tests/unit/test_transform.py::test_bronze_to_silver_numero_de_linhas        PASSED
tests/unit/test_transform.py::test_silver_to_gold_retorna_dataframe         PASSED
tests/unit/test_transform.py::test_silver_to_gold_colunas_corretas          PASSED
tests/unit/test_transform.py::test_silver_to_gold_agrega_por_dia            PASSED
tests/unit/test_transform.py::test_silver_to_gold_temp_max_correta          PASSED
tests/unit/test_transform.py::test_silver_to_gold_precipitacao_total_correta PASSED
13 passed
```

---

## 📊 Dados Coletados

| Campo | Descrição | Unidade |
|---|---|---|
| `temperature_2m` | Temperatura a 2m do solo | °C |
| `precipitation` | Precipitação | mm |
| `wind_speed_10m` | Velocidade do vento a 10m | km/h |

**Localização:** Brasília, DF (-15.78, -47.93)
**Frequência:** Horária (168 registros por semana)
