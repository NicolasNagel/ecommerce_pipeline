FROM astrocrpublic.azurecr.io/runtime:3.2-5

USER root

RUN apt-get update && apt-get install -y libpq-dev gcc python3-venv

USER astro

RUN python -m venv /usr/local/airflow/dbt_venv && \
    /usr/local/airflow/dbt_venv/bin/pip install --upgrade pip && \
    /usr/local/airflow/dbt_venv/bin/pip install psycopg2-binary && \
    /usr/local/airflow/dbt_venv/bin/pip install dbt-core dbt-postgres