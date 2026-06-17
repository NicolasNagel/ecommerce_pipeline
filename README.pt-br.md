# Pipeline Ecommerce

Pipeline de dados end-to-end para operações de e-commerce com múltiplos canais de venda, monitoramento de competitividade e modelagem analítica em camadas.

[![Python](https://img.shields.io/badge/Python-3.13-blue)]()
[![dbt](https://img.shields.io/badge/dbt-Core-orange)]()
[![Airflow](https://img.shields.io/badge/Airflow-3.0-red)]()
[![Azure](https://img.shields.io/badge/Azure-Blob%20Storage-0078D4)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)]()

---

## O problema que esse projeto resolve

Operações de e-commerce geram dados em fontes distintas — planilhas de vendas, cadastros de clientes, catálogos de produtos e coletas de preço de concorrentes. Sem uma estrutura centralizada, esses dados ficam isolados, inconsistentes e inacessíveis para análise.

O resultado prático disso são perguntas que o negócio não consegue responder com confiança:

- **Qual canal gera mais receita — loja física ou e-commerce?**
- **Quais produtos estão com preço acima do mercado e podem estar perdendo venda?**
- **Quais categorias concentram a maior parte da receita?**
- **Qual o ticket médio por cliente e canal ao longo do tempo?**

Esse projeto constrói a infraestrutura que torna essas perguntas respondíveis — de forma automatizada, confiável e escalável.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FONTES DE DADOS                             │
│                                                                     │
│   📄 CSV / Planilhas          🔌 APIs Externas (HubSpot, etc.)      │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      COLLECTOR LAYER                                │
│                                                                     │
│   CSVCollector                    APICollector (extensível)         │
│   └── coleta arquivos locais      └── coleta dados de APIs          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     TRANSFORMER LAYER                               │
│                                                                     │
│   ParquetTransformer                                                │
│   └── converte CSV → Parquet                                        │
│   SchemaRegistry                                                    │
│   └── valida schema com contratos JSON (pandera)                    │
│   └── bloqueia arquivos com Schema Drift antes de salvar            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                                 │
│                                                                     │
│   Azure Blob Storage — Data Lake                                    │
│   └── bronze/                                                       │
│       └── {dataset}/ano={Y}/mes={M}/dia={D}/{arquivo}.parquet       │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        LOADER LAYER                                 │
│                                                                     │
│   DataLakeReader                                                    │
│   └── baixa arquivos Parquet do Data Lake                           │
│   DatabaseWriter                                                    │
│   └── salva no PostgreSQL na camada Bronze                          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MEDALLION ARCHITECTURE (dbt)                     │
│                                                                     │
│  BRONZE (tabelas)      SILVER (views)        GOLD (tabelas)         │
│  ────────────────      ──────────────        ────────────────────   │
│  clientes         →    stg_clientes    →     gold_receita_canal     │
│  produtos         →    stg_produtos    →     gold_ranking_produtos  │
│  vendas           →    stg_vendas      →     gold_receita_categoria │
│  preco_competidor →    stg_competit.   →     gold_competidores      │
│                                              ────────────────────   │
│                                              BI LAYER (tabelas)     │
│                                              bi_vendas_completo     │
│                                              bi_produtos            │
│                                              bi_clientes            │
│                                              bi_competitividade     │
│                                              bi_performance_categ.  │
│                                              bi_calendario          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CONSUMER LAYER                                 │
│                                                                     │
│                       📊 Power BI                                   │
│         Conectado diretamente ao schema gold_bi                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Orquestração

```
Apache Airflow + Astronomer CLI
│
├── DAG: bronze_pipeline        (roda todo dia às 06:00)
│   ├── task: collect           → coleta arquivos CSV
│   ├── task: transform         → valida schema + converte para Parquet
│   ├── task: upload            → envia para o Data Lake (Azure)
│   ├── task: download          → baixa do Data Lake
│   ├── task: write_to_db       → salva no PostgreSQL (Bronze)
│   └── task: trigger_dbt  ─────────────────────────────────┐
│                                                            │
└── DAG: dbt_pipeline           (disparada ao fim da bronze) ◄─┘
    └── Cosmos DbtTaskGroup
        ├── silver.*            → views de limpeza e padronização
        └── gold.*              → tabelas analíticas e camada BI
```

---

## Proteção contra Schema Drift

Cada dataset tem um contrato de schema definido em JSON:

```
src/schemas/contracts/
├── clientes.json
├── produtos.json
├── vendas.json
└── preco_competidores.json
```

Se um arquivo chegar com colunas faltando, renomeadas ou com tipos errados, o pipeline **bloqueia o arquivo e loga o erro** antes de qualquer escrita — evitando que dados corrompidos cheguem ao banco.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.13 |
| Gerenciamento de dependências | Poetry |
| Validação de schema | Pandera |
| Armazenamento em nuvem | Azure Blob Storage |
| Banco de dados | PostgreSQL |
| Transformação | dbt Core + dbt-postgres |
| Orquestração | Apache Airflow 3 + Astronomer CLI |
| Integração dbt/Airflow | Astronomer Cosmos |
| Containerização | Docker |
| Visualização | Power BI |

---

## Estrutura do projeto

```
PipelineEcommerce/
├── src/
│   ├── collector/
│   │   ├── data_collector.py       # contrato base (ABC)
│   │   └── csv_collector.py        # implementação para CSV
│   ├── transformer/
│   │   └── parquet_transformer.py  # CSV → Parquet + validação
│   ├── writer/
│   │   ├── datalake_writer.py      # upload para Azure
│   │   └── database_writer.py      # escrita no PostgreSQL
│   ├── reader/
│   │   └── datalake_reader.py      # download do Azure
│   ├── schemas/
│   │   ├── registry.py             # carrega contratos JSON
│   │   └── contracts/              # schemas por dataset
│   ├── pipeline/
│   │   └── pipeline_runner.py      # orquestra todas as camadas
│   └── core/
│       ├── azure_blob_client.py    # conexão com Azure
│       ├── settings.py             # variáveis de ambiente
│       └── logging.py              # configuração de logs
├── ecommerce/                      # projeto dbt
│   ├── models/
│   │   ├── silver/                 # views de padronização
│   │   └── gold/                   # tabelas analíticas
│   │       └── bi/                 # camada para Power BI
│   ├── macros/
│   └── dbt_project.yml
├── dags/
│   ├── bronze_pipeline.py          # DAG principal
│   └── dbt_pipeline.py             # DAG dbt com Cosmos
├── include/
│   └── dbt/ecommerce/              # projeto dbt dentro do Airflow
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

---

## Como escalar esse projeto

A arquitetura foi desenhada para crescer sem reescrever o que já funciona.

**Novas fontes de dados** — crie um novo `Collector` herdando de `DataCollector` e adicione o contrato JSON correspondente em `schemas/contracts/`. O restante da pipeline não muda.

**Novos datasets** — adicione o arquivo CSV, crie o contrato de schema e o model dbt. O `PipelineRunner` processa automaticamente todos os arquivos do diretório.

**Novas análises** — crie um novo model na camada Gold ou BI. O dbt resolve as dependências automaticamente.

**Novas fontes de API** — implemente um `APICollector` com a lógica de paginação e autenticação. A classe `HubSpotCollector` já serve como referência para múltiplos endpoints configuráveis.

---

## Dores de negócio atendidas

**Visibilidade de receita por canal** — separa e compara o desempenho de loja física e e-commerce por período, categoria e produto.

**Inteligência competitiva** — monitora automaticamente o posicionamento de preço contra Amazon, Shopee, Magalu e Mercado Livre — identificando onde o negócio está acima ou abaixo do mercado.

**Rastreabilidade de dados** — particionamento por data no Data Lake garante histórico completo e reprocessamento seguro de qualquer período.

**Confiabilidade** — validação de schema na entrada impede que mudanças inesperadas nas fontes corrompam os dados analíticos.

**Autonomia analítica** — camada BI diretamente conectável ao Power BI, com dimensões e fatos prontos para uso sem transformação adicional.