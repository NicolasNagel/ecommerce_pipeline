from pathlib import Path
from datetime import datetime

from azure.storage.blob import BlobServiceClient


class DataLake:
    """
    Classe responsável por gerenciar arquivos no DataLake usando Azure Blob Storage.

    Responsabilidades:
        - Garantir que o container existe;
        - Montar caminhos padronizados;
        - Criar particionamento por data;
        - Listar arquivos blobs existentes;
        - Fazer upload de arquivos locais;
        - Fazer download de arquivos do DataLake;
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
        Garante que o container existe. Caso não exista, cria um novo.
        """
        if not self.container_client.exists():
            self.container_client.create_container()

    def infer_dataset_name(self, local_file_path: str | Path) -> str:
        """
        Infere o nome do dataset automaticamente apartir do Path.

        Returns:
            str: Nome do dataset.
        """
        local_file_path = Path(local_file_path)
        return local_file_path.stem
    
    def build_blob_path(
            self,
            root_folder: str,
            dataset_name: str,
            file_name: str | None = None,
            partition_date: datetime | None = None
    ) -> str:
        """
        Monta o caminho do diretório virtual para salvar arquivos no Container.

        Args:
            root_folder (str): Nome do diretório raíz.
            dataset_name (str): Nome do dataset que será salvo.
            file_name (str | None): Nome do arquivo que será buscado ou salvo.
            partition_date (datetime | None): Particionamento das datas para 
                organização dentro do Container.

        Returns:
            str: Diretório virtual completo do arquivo salvo
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
        )

        return f'{path}{file_name}' if file_name else path
    
    def list_blobs(self, root_folder: str, dataset_name: str) -> list[str]:
        """
        Procura por arquivos blob dentro do Container.

        Args:
            root_folder (str): Nome do diretório raíz.
            dataset_name (str): Nome do dataset salvo.

        Returns:
            list(str): Lista com os blobs salvos
        """
        prefix = self.build_blob_path(
            root_folder=root_folder,
            dataset_name=dataset_name
        )

        return [blob.name for blob in self.container_client.list_blobs(name_starts_with=prefix)]
    
    def upload_blob(
            self,
            local_file_path: str | Path,
            root_folder: str,
            dataset_name: str | None = None,
            overwrite: bool = True
    ) -> str:
        """
        Faz o upload de um arquivo local para o DataLake.

        Args:
            local_file_path (str | Path): Diretório do arquivo salvo localmente.
            root_folder (str): Nome do diretório raíz.
            dataset_name (str): Nome do dataset que será salvo.
            overwrite (bool): Define se irá sobreescrever o arquivo na hora de um novo salvamento.
        """
        self.ensure_container_exists()

        local_file_path = Path(local_file_path)
        if local_file_path is None:
            raise FileNotFoundError(f'Arquivo não encontrado: {local_file_path}')
    
        if dataset_name is None:
            dataset_name = self.infer_dataset_name(local_file_path=local_file_path)

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
    
    def download_blob(
            self,
            blob_path: str,
            output_dir: str | Path = 'src/data/staging' 
    ) -> Path:
        """
        Faz o download de um arquivo blob localmente, temporariamente.

        Args:
            blob_path (str): Diretório virtual do arquivo a ser baixado.
            output_dir (str | Path): Diretório local onde o arquivo será baixado.

        Returns:
            Path: Diretório do arquivo salvo localmente.
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