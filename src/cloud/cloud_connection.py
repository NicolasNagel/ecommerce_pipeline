from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

from src.core.settings import settings


class AzureBlobClient:
    """
    Classe responsável apenas por criar a conexão com o Azure Blob Storage.
    """
    def __init__(self) -> None:
        self.credentials = ClientSecretCredential(
            tenant_id=settings.TENANT_ID,
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET
        )

        self.blob_service_client = BlobServiceClient(
            account_url=settings.AZURE_BLOB_STORAGE,
            credential=self.credentials
        )

    def get_client(self) -> BlobServiceClient:
        """
        Retorna o cliente da Azure Blob Storage.
        """
        return self.blob_service_client