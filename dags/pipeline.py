from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import dag, task
from airflow.sdk import Variable
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    'owner': 'nicolas_nagel',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

@dag(
    dag_id='pipeline',
    description='Coleta CSVs, transforma em Parquet e salva no Banco de Dados.',
    schedule="0 6 * * *",
    start_date=datetime(2026, 6, 15),
    catchup=False,
    default_args=default_args,
    tags=['bronze, pipeline']
)
def bronze_pipeline():

    @task
    def collect() -> list[str]:
        from include.src.collector.csv_collector import CSVCollector

        collector = CSVCollector(local_file_path=Path('include/src/data'))
        files = collector.collect()
        return [str(f) for f in files]

    @task
    def transform(csv_files: list[str]) -> list[str]:
        from include.src.transformer.csv_transformer import ParquetTransformer
        from include.src.schemas.registry import SchemaRegistry

        registry = SchemaRegistry(schema_dir=Path('include/src/schemas/contracts'))
        transformer = ParquetTransformer(schema_registry=registry)

        return [str(transformer.transform(f)) for f in csv_files]
    
    @task
    def upload(parquet_files: list[str]) -> list[str]:
        from include.src.cloud.cloud_connection import AzureServiceClient
        from include.src.cloud.storage import DataLake

        blob_client = AzureServiceClient().get_client()
        writer = DataLake(blob_client, Variable.get('CONTAINER_NAME'))

        return [
            writer.upload_blob(local_file_path=f, root_folder='staging')
            for f in parquet_files
        ]
    
    @task
    def download(blob_paths: list[str]) -> list[str]:
        from include.src.cloud.cloud_connection import AzureServiceClient
        from include.src.cloud.storage import DataLake

        blob_client = AzureServiceClient().get_client()
        reader = DataLake(blob_client, Variable.get('CONTAINER_NAME'))

        return [str(reader.download_blob(blob_path=p)) for p in blob_paths]
    
    @task
    def write_to_db(local_files: list[str]) -> None:
        from include.src.database.db_writer import DataBaseWriter
        from include.src.schemas.registry import SchemaRegistry

        registry = SchemaRegistry()
        writer = DataBaseWriter(Variable.get('DB_CONNECTION_STRING'), schema_registry=registry)

        for path in local_files:
            writer.write(
                local_file_path=path,
                schema='bronze'
            )

    trigger_dbt = TriggerDagRunOperator(
        task_id="trigger_dbt_pipeline",
        trigger_dag_id="dbt_pipeline",      # ← nome da DAG do Cosmos
        wait_for_completion=True,           # ← aguarda o dbt terminar
        poke_interval=30                    # ← verifica a cada 30 segundos
    )

    csv_files = collect()
    parquet_files = transform(csv_files)
    blob_paths = upload(parquet_files)
    local_files = download(blob_paths)
    write_to_db(local_files)
    trigger_dbt

bronze_pipeline() 