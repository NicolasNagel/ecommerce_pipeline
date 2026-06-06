from pathlib import Path
from datetime import datetime

from azure.storage.blob import BlobServiceClient


class DataLakeWriter:
    """
    Classe responsável por escrever arquivos no DataLake usando Azure Blob Storage.

    Responsabilidades:
        - Garantir que o container existe;
        - Montar caminhos padronizados;
        - Criar particionamento por data;
        - Fazer upload de arquivos locais;
        - Inferir o nome do dataset a partir do arquivo, se necessário.
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

    def ensure_container_exists(self) -> None:
        """
        Garante que o container exista.
        Caso não exista, cria um novo container.
        """
        if not self.container_client.exists():
            self.container_client.create_container()

    def infer_dataset_name(self, local_file_path: str | Path) -> str:
        """
        Infere o nome do dataset apartir do nome do arquivo local.
        """
        local_file_path = Path(local_file_path)
        return local_file_path.stem
    
    def build_blob_path(
            self,
            root_folder: str,
            dataset_name: str,
            file_name: str,
            partition_date: datetime | None = None
    ) -> str:
        """
        Monta o caminho final da pastas virtuais dentro do DataLake.
        """
        if not partition_date:
            partition_date = datetime.now()

        year = partition_date.strftime('%Y')
        month = partition_date.strftime('%m')
        day = partition_date.strftime('%d')

        return (
            f'{root_folder}/'
            f'{dataset_name}/'
            f'ano={year}/'
            f'mes={month}/'
            f'dia={day}/'
            f'{file_name}'
        )
    
    def upload_file(
            self,
            local_file_path: str | Path,
            root_folder: str,
            dataset_name: str | None = None,
            overwrite: bool = True
    ) -> str:
        """
        Faz o upload de um arquivo para o DataLake.
        """
        self.ensure_container_exists()

        local_file_path = Path(local_file_path)
        if not local_file_path.exists():
            raise FileNotFoundError(f'Arquivo não encontrado: {local_file_path}')
        
        if dataset_name is None:
            dataset_name = self.infer_dataset_name(local_file_path)

        blob_path = self.build_blob_path(
            root_folder=root_folder,
            dataset_name=dataset_name,
            file_name=local_file_path.name
        )

        blob_client = self.container_client.get_blob_client(blob=blob_path)

        with open(local_file_path, 'rb') as file:
            blob_client.upload_blob(
                data=file,
                overwrite=overwrite
            )

        return blob_path