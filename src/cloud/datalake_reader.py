from pathlib import Path
from datetime import datetime

from azure.storage.blob import BlobServiceClient



class DataLakeReader:
    """
    Classe responsável por ler arquivos do DataLake usando Azure Blob Storage.

    Responsabilidades:
        - Montar caminhos padronizados (espelho do DataLakeWriter);
        - Fazer Download de arquivos para um diretório local;
        - Listar arquivos disponíveis dentro de um dataset;
    """
    def __init__(
            self,
            blob_service_client: BlobServiceClient,
            container_name: str
    ) -> None:
        self.blob_service_client = blob_service_client
        self.container_name = container_name
        self.container_client = self.blob_service_client.get_container_client(
            container=self.container_name
        )

    def build_blob_path(
            self,
            root_folder: str,
            dataset_name: str,
            file_name: str | None = None,
            partition_date: datetime | None = None
    ) -> str:
        """
        Monta o caminho do arquivo dentro do DataLake.
        """
        if partition_date is None:
            partition_date = datetime.now()

        year = partition_date.strftime('%Y')
        month = partition_date.strftime('%m')
        day = partition_date.strftime('%d')

        path = (
            f'{root_folder}/'
            f'{dataset_name}/'
            f'ano={year}/'
            f'mes={month}/'
            f'dia={day}/'
            f'{file_name}'
        )
        
        return f'{path}{file_name}' if file_name else path
    
    def list_blobs(
            self,
            root_folder: str,
            dataset_name: str
    ) -> list[str]:
        """
        Lista os arquivos dentro de um diretório virtual específico.
        """
        prefix = self.build_blob_path(
            root_folder=root_folder,
            dataset_name=dataset_name
        )

        return [
            blob.name
            for blob in self.container_client.list_blobs(name_starts_with=prefix)
        ]
    
    def download_file(
            self,
            blob_path: str,
            output_dir: str | Path = 'src/data/staging'
    ) -> Path:
        """
        Faz o download de um blob para o computador, temporariamente.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        file_name = Path(blob_path).name
        local_path = output_dir / file_name

        blob_client = self.container_client.get_blob_client(blob=blob_path)

        with open(local_path, 'wb') as file:
            data = blob_client.download_blob()
            data.readinto(file)

        return local_path