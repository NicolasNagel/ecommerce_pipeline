from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

from include.src.core.settings import settings


class AzureServiceClient:
    """
    Responsável por fazer a conexão com a Azure Blob Storage.
    """
    def __init__(self) -> None:
        self.credential = ClientSecretCredential(
            client_id=settings.CLIENT_ID,
            tenant_id=settings.TENANT_ID,
            client_secret=settings.CLIENT_SECRET
        )

        self.azure_service_client = BlobServiceClient(
            account_url=settings.AZURE_BLOB_STORAGE,
            credential=self.credential
        )

    def get_client(self) -> BlobServiceClient:
        """
        Retorna o client da Azure Storage Blob

        Returns:
            BlobServiceClient: Client da Azure Storage Blob
        """
        return self.azure_service_client