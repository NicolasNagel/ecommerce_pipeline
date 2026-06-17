# E-commerce Data Pipeline

**An end-to-end, production-style data pipeline that turns scattered e-commerce data into trustworthy, decision-ready analytics — built with the same architectural patterns used by data teams at scale.**

[![Python](https://img.shields.io/badge/Python-3.13-blue)]()
[![dbt](https://img.shields.io/badge/dbt-Core-orange)]()
[![Airflow](https://img.shields.io/badge/Airflow-3.0-red)]()
[![Azure](https://img.shields.io/badge/Azure-Blob%20Storage-0078D4)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)]()

> 🇧🇷 Versão em português disponível [aqui](./README.pt-br.md).

---

## Why this project exists

E-commerce operations generate data across disconnected sources — sales spreadsheets, customer records, product catalogs, and competitor price feeds. Without a centralized structure, this data stays siloed, inconsistent, and impossible to analyze reliably.

In practice, that means the business can't confidently answer questions like:

- Which channel drives more revenue — physical store or e-commerce?
- Which products are priced above market and potentially losing sales?
- Which categories concentrate the most revenue?
- What's the average order value per customer and channel over time?

This project builds the infrastructure that makes those questions answerable — automated, reliable, and built to scale.

---

## What this demonstrates

This isn't a toy ETL script. It's a layered, production-oriented pipeline that reflects how real data teams design for reliability and growth:

- **Medallion architecture** (Bronze → Silver → Gold → BI) implemented with dbt, the same pattern used by modern data platforms
- **Schema contract enforcement** — pandera-based validation that blocks malformed data *before* it touches storage, preventing silent schema drift
- **Cloud-native storage** — partitioned data lake on Azure Blob Storage (`dataset/year/month/day`), enabling safe historical reprocessing
- **Orchestrated, scheduled workflows** — Apache Airflow 3 + Astronomer Cosmos coordinating ingestion and dbt transformations as a single dependency graph
- **Extensible-by-design architecture** — adding a new data source means writing one new class, not touching the rest of the pipeline
- **BI-ready output layer** — dimensional models exposed directly to Power BI, no extra transformation needed downstream

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                            DATA SOURCES                              │
│                                                                       │
│   📄 CSV / Spreadsheets          🔌 External APIs (HubSpot, etc.)    │
└──────────────────────────┬───────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         COLLECTOR LAYER                              │
│                                                                       │
│   CSVCollector                    APICollector (extensible)          │
│   └── collects local files        └── collects data from APIs        │
└──────────────────────────┬───────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        TRANSFORMER LAYER                             │
│                                                                       │
│   ParquetTransformer                                                 │
│   └── converts CSV → Parquet                                         │
│   SchemaRegistry                                                     │
│   └── validates schema against JSON contracts (pandera)              │
│   └── blocks files with schema drift before they're persisted        │
└──────────────────────────┬───────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          STORAGE LAYER                                │
│                                                                       │
│   Azure Blob Storage — Data Lake                                     │
│   └── bronze/                                                        │
│       └── {dataset}/year={Y}/month={M}/day={D}/{file}.parquet        │
└──────────────────────────┬───────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          LOADER LAYER                                 │
│                                                                       │
│   DataLakeReader                                                     │
│   └── downloads Parquet files from the Data Lake                     │
│   DatabaseWriter                                                      │
│   └── persists to PostgreSQL Bronze layer                            │
└──────────────────────────┬───────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MEDALLION ARCHITECTURE (dbt)                      │
│                                                                       │
│  BRONZE (tables)        SILVER (views)         GOLD (tables)         │
│  ────────────────       ──────────────         ────────────────────  │
│  customers          →   stg_customers     →    gold_revenue_channel  │
│  products            →   stg_products      →    gold_product_ranking │
│  sales                →   stg_sales         →    gold_revenue_category│
│  competitor_price     →   stg_competitor    →    gold_competitors    │
│                                                  ────────────────────  │
│                                                  BI LAYER (tables)    │
│                                                  bi_sales_full        │
│                                                  bi_products          │
│                                                  bi_customers         │
│                                                  bi_competitiveness   │
│                                                  bi_category_perf     │
│                                                  bi_calendar          │
└──────────────────────────┬───────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CONSUMER LAYER                                │
│                                                                       │
│                          📊 Power BI                                 │
│            Connected directly to the gold_bi schema                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Orchestration

```
Apache Airflow + Astronomer CLI
│
├── DAG: bronze_pipeline        (runs daily at 06:00)
│   ├── task: collect           → collects CSV files
│   ├── task: transform         → validates schema + converts to Parquet
│   ├── task: upload            → pushes to the Data Lake (Azure)
│   ├── task: download          → pulls from the Data Lake
│   ├── task: write_to_db       → persists to PostgreSQL (Bronze)
│   └── task: trigger_dbt  ─────────────────────────────────┐
│                                                            │
└── DAG: dbt_pipeline           (triggered after bronze)    ◄─┘
    └── Cosmos DbtTaskGroup
        ├── silver.*            → cleaning/standardization views
        └── gold.*              → analytical and BI-ready tables
```

---

## Schema drift protection

Every dataset has a schema contract defined in YAML:

```
src/schemas/contracts/
├── customers.yaml
├── products.yaml
├── sales.yaml
└── competitor_prices.yaml
```

If an incoming file has missing columns, renamed fields, or incorrect types, the pipeline **blocks the file and logs the error before any write happens** — preventing corrupted data from ever reaching the analytical layer.

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Dependency management | Poetry |
| Schema validation | Pandera |
| Cloud storage | Azure Blob Storage |
| Database | PostgreSQL |
| Transformation | dbt Core + dbt-postgres |
| Orchestration | Apache Airflow 3 + Astronomer CLI |
| dbt/Airflow integration | Astronomer Cosmos |
| Containerization | Docker |
| Visualization | Power BI |

---

## Project structure

```
PipelineEcommerce/
├── src/
│   ├── collector/
│   │   ├── data_collector.py       # base contract (ABC)
│   │   └── csv_collector.py        # CSV implementation
│   ├── transformer/
│   │   └── parquet_transformer.py  # CSV → Parquet + validation
│   ├── writer/
│   │   ├── datalake_writer.py      # upload to Azure
│   │   └── database_writer.py      # write to PostgreSQL
│   ├── reader/
│   │   └── datalake_reader.py      # download from Azure
│   ├── schemas/
│   │   ├── registry.py             # loads JSON contracts
│   │   └── contracts/              # per-dataset schemas
│   ├── pipeline/
│   │   └── pipeline_runner.py      # orchestrates all layers
│   └── core/
│       ├── azure_blob_client.py    # Azure connection
│       ├── settings.py             # environment variables
│       └── logging.py              # logging configuration
├── ecommerce/                      # dbt project
│   ├── models/
│   │   ├── silver/                 # standardization views
│   │   └── gold/                   # analytical tables
│   │       └── bi/                 # Power BI-facing layer
│   ├── macros/
│   └── dbt_project.yml
├── dags/
│   ├── bronze_pipeline.py          # main DAG
│   └── dbt_pipeline.py             # dbt DAG with Cosmos
├── include/
│   └── dbt/ecommerce/              # dbt project inside Airflow
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

---

## How this scales

The architecture was designed to grow without rewriting what already works.

**New data sources** — create a new `Collector` inheriting from `DataCollector` and add the corresponding JSON contract to `schemas/contracts/`. The rest of the pipeline doesn't change.

**New datasets** — drop in the CSV file, define the schema contract, and add the dbt model. `PipelineRunner` automatically processes every file in the directory.

**New analytics** — add a new model in the Gold or BI layer. dbt resolves dependencies automatically.

**New API sources** — implement an `APICollector` with pagination and auth logic. The `HubSpotCollector` class already serves as a reference for multi-endpoint configurations.

---

## Business problems this solves

**Revenue visibility by channel** — splits and compares physical store vs. e-commerce performance by period, category, and product.

**Competitive intelligence** — automatically tracks price positioning against Amazon, Shopee, Magalu, and Mercado Livre, flagging where the business is priced above or below market.

**Data traceability** — date-partitioned data lake storage guarantees full history and safe reprocessing of any period.

**Reliability** — schema validation at ingestion prevents unexpected upstream changes from corrupting analytical data.

**Analytics self-service** — BI-ready layer connects directly to Power BI with dimensions and facts ready to use, no extra transformation required.

---

## About me

I'm a Data Engineer based in Brazil, working with cloud data platforms, orchestration, and analytics engineering. I built this project to apply production-grade patterns — schema contracts, medallion architecture, orchestrated pipelines — to a realistic business scenario.

I'm currently open to **remote Data Engineering roles** with US-based teams. Feel free to connect or reach out.

📫 [LinkedIn](#) · 💻 [GitHub](https://github.com/NicolasNagel/ecommerce_pipeline)