# Contexto do Projeto — Pipeline End-to-End Medallion
> Documento pessoal para referência futura e contexto em novas conversas com IA.

---

## Como usar esse documento

Cole esse arquivo no início de uma nova conversa com Claude e diga:
> "Leia esse documento. Ele descreve meu nível técnico, como prefiro aprender e um projeto que já construí. Quero continuar sendo ensinado da mesma forma."

---

## Perfil do Desenvolvedor

- **Nível atual:** Estagiário em transição para Júnior
- **Área:** Engenharia de Dados
- **Stack principal:** Python
- **Conhecimentos prévios:** Lógica de programação básica, algum contato com Docker/WSL, SQL básico
- **Forma de aprender melhor:** Socrática — perguntas e respostas, tentativa e erro, explicação após o erro. Não aprende bem recebendo respostas prontas sem contexto.

---

## Como o assistente deve se comportar

O assistente deve agir como um **engenheiro de dados sênior com 10+ anos de experiência** ensinando um estagiário. As regras são:

1. **Nunca dar respostas prontas de mão beijada** — sempre fazer perguntas antes, deixar o aluno tentar primeiro
2. **Usar perguntas de múltipla escolha** quando quiser testar conceitos — o aluno responde e o assistente corrige e explica
3. **Sempre começar pelo raciocínio** antes de codar — arquitetura, stack, estrutura de pastas
4. **Revisar o código do aluno** apontando problemas e explicando o porquê, não reescrevendo tudo
5. **Ensinar boas práticas de mercado** — responsabilidade única, nomenclatura, tratamento de erro, logging
6. **Ler documentação** antes de falar sobre qualquer biblioteca — não confiar só no treinamento
7. **Mostrar como pensar perguntas** — não só responder, mas ensinar que tipo de pergunta fazer
8. **Progredir em fases** — fundamentos antes de ferramentas complexas
9. **Ser honesto sobre erros** — quando o aluno errar, corrigir diretamente sem ser condescendente
10. **Nunca adicionar complexidade desnecessária** — tecnologia é consequência do problema, não ponto de partida

---

## Projeto Construído — Pipeline Meteorológico End-to-End

### Objetivo
Pipeline de dados completo usando arquitetura Medallion (Bronze/Silver/Gold) consumindo dados meteorológicos da Open-Meteo API para Brasília, DF.

### Stack utilizada
| Componente | Tecnologia | Decisão |
|---|---|---|
| Linguagem | Python 3.12 | Padrão de mercado em DE |
| Ingestão | `requests` | Chamadas HTTP simples |
| Transformação | `pandas` | Volume pequeno (~168 linhas/semana) |
| Formato | Parquet (Silver/Gold) + JSON (Bronze) | Colunar para análise, JSON para fidelidade |
| Gerenciador de pacotes | `uv` | Mais rápido que pip, mercado migrando para ele |
| Containerização | Docker (pendente) | Virtualização Windows não habilitada |
| Testes | `pytest` | 13/13 passando |
| Variáveis de ambiente | `python-dotenv` | Credenciais fora do código |

### Arquitetura das pastas
```
Pipeline_End_to_End/
├── data/
│   ├── bronze/          → raw.json (dado bruto da API)
│   ├── silver/          → silver.parquet (limpo e tipado)
│   └── gold/            → gold.parquet (agregado diário)
├── src/
│   ├── extract.py       → chama API, retorna dicionário
│   ├── transform.py     → bronze_to_silver() e silver_to_gold()
│   ├── load.py          → persiste cada camada no disco
│   └── pipeline.py      → orquestra tudo em ordem
├── tests/
│   ├── unit/
│   │   └── test_transform.py   → 11 testes unitários
│   └── integration/
│       └── test_pipeline.py    → 2 testes de integração
├── config/
│   └── .env             → API_URL
├── docs/
│   └── day_one.md       → esse arquivo
├── conftest.py          → configura path do pytest
├── Dockerfile           → pendente virtualização
├── docker-compose.yml   → pendente virtualização
├── pyproject.toml       → dependências via uv
└── .gitignore
```

### Responsabilidade de cada arquivo

**`extract.py`**
- Função pública: `extract_data()` → retorna `dict`
- Lê `API_URL` do `.env` via `python-dotenv`
- Usa `timeout=10` no requests
- Trata erro com `raise_for_status()` + `except requests.exceptions.RequestException` + `raise`

**`transform.py`**
- Funções privadas (prefixo `_`): `_convert_to_time`, `_check_nulls`, `_drop_nulls`, `_groupby_by_day`
- Função pública: `bronze_to_silver(data: dict)` → retorna DataFrame horário limpo
- Função pública: `silver_to_gold(df: pd.DataFrame)` → retorna DataFrame agregado por dia
- Gold tem colunas: `temp_media`, `temp_max`, `temp_min`, `precipitacao_total`

**`load.py`**
- Usa `pathlib` para caminhos dinâmicos — `BASE_DIR = Path(__file__).parent.parent`
- `load_bronze(data: dict)` → salva `raw.json` com `json.dump`
- `load_silver(df)` → salva `silver.parquet` com `df.to_parquet`
- `load_gold(df)` → salva `gold.parquet` com `df.to_parquet`
- `os.makedirs(PATH, exist_ok=True)` em cada função

**`pipeline.py`**
- Configura logging: `basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')`
- Função `pipeline_completo()` — orquestra em ordem:
  1. `extract_data()`
  2. `load_bronze(data)`
  3. `bronze_to_silver(data)` → silver
  4. `load_silver(silver)`
  5. `silver_to_gold(silver)` → gold
  6. `load_gold(gold)`

---

## Decisões de Design Importantes

### Bronze em JSON, não Parquet
Discussão real durante o projeto. Duas escolas:
- **Puristas:** Bronze = JSON/JSONL bruto, Silver em diante usa Parquet
- **Pragmáticos:** Bronze já em Parquet sem transformações

Decisão final: **JSON para Bronze** — preserva estrutura original da API incluindo metadados (`latitude`, `elevation`, `hourly_units`) que se perderiam numa conversão para DataFrame tabular.

### `raise` no except do extract
Quando a API falha, o `except` loga o erro e relança com `raise` (sozinho). Não retorna `None` nem `{}` — deixa o pipeline falhar explicitamente com mensagem clara. Retornar `None` causaria `TypeError: 'NoneType' object is not subscriptable` em outro lugar, difícil de debugar.

### `pathlib` ao invés de strings de caminho
Caminhos como `'data/bronze/raw.json'` são relativos ao diretório de execução. Se rodar de dentro de `src/`, cria a pasta errada. `Path(__file__).parent.parent` sempre resolve relativo ao arquivo, independente de onde você roda.

### `patch('pipeline.extract_data')` nos testes
`patch('extract.extract_data')` não funciona porque `pipeline.py` já importou a referência com `from extract import extract_data`. O patch precisa interceptar onde a função **é usada**, não onde **é definida**.

### Funções privadas com `_`
Convenção Python para sinalizar que a função não deve ser chamada fora do módulo. `_convert_to_time`, `_check_nulls`, `_drop_nulls`, `_groupby_by_day` são detalhes de implementação — só `bronze_to_silver` e `silver_to_gold` são contratos públicos.

---

## Conceitos Aprendidos

### Arquitetura
- Medallion Bronze/Silver/Gold — responsabilidade e quando usar cada camada
- Responsabilidade única por módulo — extract não salva, transform não busca, load não transforma
- Tecnologia como consequência do problema — Spark seria absurdo para 168 linhas

### Python
- `if __name__ == "__main__"` — roda só quando executado diretamente, nunca ao importar
- `raise_for_status()` — lança HTTPError automaticamente em 4xx/5xx
- `raise` sozinho — relança a exceção capturada sem perder o traceback original
- `Path(__file__).parent` — caminho relativo ao arquivo, não ao diretório de execução
- Funções privadas com `_` — convenção de interface pública vs implementação
- Type hints — `data: dict`, `df: pd.DataFrame` — documentação inline do contrato

### Pandas
- `pd.DataFrame(dict)` — chaves viram colunas, listas viram linhas
- `pd.to_datetime()` — converte string para datetime64
- `df.isnull().sum()` — conta nulos por coluna
- `df.dropna()` — remove linhas com qualquer nulo
- `df.groupby().agg()` — agrupa e calcula múltiplas métricas
- `.dt.date` — extrai só a data de uma coluna datetime

### Testes
- `@pytest.fixture` — dado reutilizável injetado automaticamente nas funções de teste
- `tmp_path` — fixture nativa do pytest para pasta temporária por teste
- `unittest.mock.patch` — substitui função real por fake durante o teste
- Testes unitários vs integração — unitário testa função isolada, integração testa o fluxo completo
- Por que mockar a API — testes não devem depender de internet ou serviços externos

### DevOps / Boas Práticas
- `.gitignore` com `!` para exceções — `data/**/*.parquet` mas `!data/**/.gitkeep`
- `.gitkeep` — mantém pastas vazias versionadas no Git
- `uv` — gerenciador de pacotes moderno, `uv add`, `uv sync`, `pyproject.toml`
- `python-dotenv` + `.env` — credenciais fora do código, nunca no Git
- Logging vs print — timestamp, nível, formato estruturado, observabilidade real

---

## O que Falta (Próximas Fases)

### Fase 2 — Orquestração
- Airflow ou Prefect para agendar execução do pipeline
- Só faz sentido depois de entender o pipeline em si

### Fase 3 — Transformações Declarativas
- dbt por cima da Silver/Gold
- Mais fácil entender o que substitui depois de ter feito na mão

### Fase 4 — Nuvem
- AWS S3 ou GCS no lugar de `data/` local
- BigQuery ou Redshift no lugar de Parquet
- O código muda pouco — só a infraestrutura muda

### Pendente nesse projeto
- Docker funcionando — requer habilitar virtualização no Windows (Hyper-V ou WSL2)
- Mais testes de edge cases — API retornando campos extras, datas fora de ordem

---

## Como Rodar o Projeto

```bash
# Instalar dependências
uv sync

# Rodar o pipeline
python src/pipeline.py

# Rodar os testes
pytest tests/ -v
```

### Output esperado do pipeline
```
2026-05-12 10:34:54 - INFO - Camada bronze funcionando
2026-05-12 10:34:54 - INFO - Nulos por coluna: time 0 / temperature_2m 0 ...
2026-05-12 10:34:54 - INFO - Transform funcionando com sucesso !
2026-05-12 10:34:54 - INFO - Camada silver funcionando
2026-05-12 10:34:54 - INFO - Agrupamento funcionando
2026-05-12 10:34:54 - INFO - Camada gold funcionando
2026-05-12 10:34:54 - INFO - Pipeline concluído com sucesso !
```