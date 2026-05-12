# 🌦️ Pipeline Meteorológico End-to-End (Medallion Architecture)

> Projeto de aprendizado de Engenharia de Dados — construído de forma incremental, seguindo boas práticas de mercado.

---

## 📌 Status do Projeto

**Fase atual:** `Fase 1 — Fundamentos` (em construção)

| Etapa | Status |
|---|---|
| Definição de arquitetura | ✅ Concluído |
| Estrutura de pastas | ✅ Concluído |
| Definição de stack | ✅ Concluído |
| `extract.py` | 🔄 Em andamento |
| `transform.py` | ⏳ Pendente |
| `load.py` | ⏳ Pendente |
| `pipeline.py` | ⏳ Pendente |
| Docker | ⏳ Pendente |
| Testes | ⏳ Pendente |

---

## 🎯 Objetivo

Construir um pipeline de dados End-to-End usando a arquitetura **Medallion (Bronze / Silver / Gold)**, consumindo dados meteorológicos em tempo real da API Open-Meteo para a cidade de **Brasília, DF**.

O projeto é dividido em fases evolutivas — começando simples e adicionando complexidade de forma consciente.

---

## 🏗️ Arquitetura Medallion

```
[Open-Meteo API]
      │
      ▼
  [Bronze] ← dado bruto, sem transformações, com metadados de ingestão
      │
      ▼
  [Silver] ← dado limpo, tipado, padronizado, particionado por data
      │
      ▼
   [Gold]  ← dado agregado com regras de negócio (ex: temp média diária)
      │
      ▼
[Consumo: BI / ML / Relatórios]
```

### Responsabilidade de cada camada

| Camada | Responsabilidade | Transformações |
|---|---|---|
| **Bronze** | Fidelidade à fonte | Nenhuma — dado bruto + metadados de ingestão |
| **Silver** | Qualidade | Limpeza, tipagem, remoção de duplicatas, padronização |
| **Gold** | Valor de negócio | Agregações, métricas, regras de negócio aplicadas |

---

## 🗂️ Estrutura de Pastas

```
pipeline-meteo/
├── data/
│   ├── bronze/          ← Parquet bruto (como veio da API)
│   ├── silver/          ← Parquet limpo e tipado
│   └── gold/            ← Parquet agregado para consumo
├── src/
│   ├── extract.py       ← Chama a API e retorna dado bruto
│   ├── transform.py     ← Limpeza Bronze→Silver e agregação Silver→Gold
│   ├── load.py          ← Persiste os dados em cada camada
│   └── pipeline.py      ← Orquestrador — chama extract, transform e load em ordem
├── config/
│   └── .env             ← Variáveis de ambiente (URL da API, parâmetros, caminhos)
├── .gitignore
├── pyproject.toml       ← Gerenciado pelo uv
├── Dockerfile
└── docker-compose.yml
```

---

## ⚙️ Stack Tecnológica

### Fase 1 — Fundamentos (atual)

| Componente | Tecnologia | Justificativa |
|---|---|---|
| Linguagem | Python 3.11+ | Padrão de mercado em DE |
| Ingestão | `requests` | Chamadas HTTP para a API |
| Transformação | `pandas` | Volume pequeno (~8.7k linhas/ano), overhead do Spark não se justifica |
| Formato de dados | `Parquet` | Colunar, comprimido, compatível com todo o ecossistema |
| Gerenciador de pacotes | `uv` | Substituto moderno do pip — significativamente mais rápido |
| Containerização | `Docker` | Reproducibilidade de ambiente |

### Fases futuras (planejadas)

| Fase | Adição | Por quê esperar |
|---|---|---|
| Fase 2 | Airflow ou Prefect | Orquestração só faz sentido após o pipeline funcionar |
| Fase 3 | dbt | Transformações declarativas — mais fácil entender o que substitui |
| Fase 4 | AWS S3 / GCS + BigQuery | Nuvem muda infra, não lógica — aprender lógica primeiro |

> **Princípio:** tecnologia é consequência do problema, não ponto de partida.

---

## 🌐 Fonte de Dados

**API:** [Open-Meteo](https://open-meteo.com/) — gratuita, sem autenticação necessária.

**Endpoint utilizado:**
```
https://api.open-meteo.com/v1/forecast
  ?latitude=-15.78
  &longitude=-47.93
  &hourly=temperature_2m,precipitation,windspeed_10m
```

**Dados coletados (horários):**

| Campo | Descrição | Unidade |
|---|---|---|
| `temperature_2m` | Temperatura a 2m do solo | °C |
| `precipitation` | Precipitação | mm |
| `windspeed_10m` | Velocidade do vento a 10m | km/h |

---

## 🚀 Como Executar

> ⚠️ Seção será atualizada conforme o projeto avança.

```bash
# Clonar o repositório
git clone <repo-url>
cd pipeline-meteo

# Instalar dependências com uv
uv pip install -r requirements.txt

# Rodar o pipeline completo
python src/pipeline.py
```

### Com Docker

```bash
docker-compose up --build
```

---

## 📐 Decisões de Design Registradas

| Decisão | Escolha | Alternativa descartada | Motivo |
|---|---|---|---|
| Formato Bronze | Parquet (sem transformações) | JSON bruto | Pragmático — sem perda de dado original se não houver limpeza |
| Ferramenta de transformação | Pandas | Apache Spark | Volume ~8.7k linhas — Spark tem overhead desnecessário |
| Gerenciador de pacotes | uv | pip / poetry | Mais rápido, é para onde o mercado está migrando |
| Orquestração inicial | pipeline.py (Python puro) | Airflow | Fundamentos antes de ferramentas — evita debugar dois problemas ao mesmo tempo |

---

## 📚 Conceitos Aprendidos

- [x] Arquitetura Medallion (Bronze / Silver / Gold) e responsabilidade de cada camada
- [x] Por que separar em camadas ao invés de transformar tudo de uma vez (reprocessamento, rastreabilidade, debug)
- [x] Tecnologia como consequência do problema, não ponto de partida
- [x] Princípio de responsabilidade única aplicado a módulos Python
- [x] Como dimensionar ferramenta de processamento pelo volume de dados
- [ ] Ingestão via API com tratamento de erros
- [ ] Escrita e leitura de Parquet com pyarrow
- [ ] Transformações com Pandas seguindo boas práticas
- [ ] Particionamento de dados por data

---

*Última atualização: Fase 1 — Estrutura e stack definidas.*