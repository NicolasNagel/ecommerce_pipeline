import shutil

from pathlib import Path

from src.cloud.cloud_connection import AzureBlobClient
from src.cloud.datalake_writer import DataLakeWriter
from src.cloud.datalake_reader import DataLakeReader
from src.collector.csv_collector import CSVCollector
from src.database.db_writer import DataBaseWriter
from src.transformer.parquet_transformer import ParquetTransformer


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
        blob_client = AzureBlobClient().get_client()

        self.collector = CSVCollector(path=Path(source_dir))
        self.transformer = ParquetTransformer()
        self.datalake_writer = DataLakeWriter(blob_client, container_name)
        self.datalake_reader = DataLakeReader(blob_client, container_name)
        self.db_writer = DataBaseWriter(db_connection_string)

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
        csv_files = self.collector.collect()

        for csv_file in csv_files:

            parquet_path = self.transformer.transform(csv_file)

            blob_path = self.datalake_writer.upload_file(
                local_file_path=parquet_path,
                root_folder=self.root_folder
            )

            local_path = self.datalake_reader.download_file(
                blob_path=blob_path
            )

            self.db_writer.write(
                local_path=local_path,
                table_name=csv_file.stem,
                schema=self.db_schema
            )

        self._cleanup(self.transformer.output_dir)