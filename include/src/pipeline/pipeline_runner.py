import shutil

from pathlib import Path

from include.src.cloud.cloud_connection import AzureServiceClient
from include.src.cloud.storage import DataLake
from include.src.collector.csv_collector import CSVCollector
from include.src.database.db_writer import DataBaseWriter
from include.src.schemas.registry import SchemaRegistry
from include.src.transformer.csv_transformer import ParquetTransformer


class PipelineRunner:
    """
    Responsável por orquestrar as etapas da pipeline.

    Responsabilidades:
        - Coletar arquivos CSV;
        - Transformar em Parquet;
        - Escrever no DataLake;
        - Ler do DataLake;
        - Escrever no Banco de Dados;
    """
    def __init__(
            self,
            source_dir: str | Path,
            container_name: str,
            root_folder: str,
            db_connection_string: str,
            db_schema: str = 'bronze'
    ) -> None:
        blob_client = AzureServiceClient().get_client()
        schema_registry = SchemaRegistry()

        self.collector = CSVCollector(local_file_path=Path(source_dir))
        self.transformer = ParquetTransformer(schema_registry=schema_registry)
        self.datalake = DataLake(blob_client, container_name)
        self.db_writer = DataBaseWriter(db_connection_string, schema_registry=schema_registry)

        self.root_folder = root_folder
        self.db_schema = db_schema

    def _cleanup(self, *paths: Path) -> None:
        """
        Remove arquivos e diretórios temporários gerados durante a pipeline.
        """
        for path in paths:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

    def run(self) -> None:
        """
        Inicia a Pipeline de Dados.
        """
        csv_files = self.collector.collect()

        for csv_file in csv_files:
            parquet_path = self.transformer.transform(csv_file)

            blob_path = self.datalake.upload_blob(
                local_file_path=parquet_path,
                root_folder=self.root_folder
            )

            local_path = self.datalake.download_blob(
                blob_path=blob_path
            )

            self.db_writer.write(
                local_file_path=local_path,
                schema=self.db_schema
            )

        self._cleanup()