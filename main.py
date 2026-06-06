from src.cloud.cloud_connection import AzureBlobClient
from src.cloud.datalake_writer import DataLakeWriter

if __name__ == '__main__':
    azure_client = AzureBlobClient()

    data_lake_writer = DataLakeWriter(
        blob_service_client=azure_client.get_client(),
        container_name='datalake'
    )

    blob_path = data_lake_writer.upload_file(
        local_file_path='src/data/vendas.csv',
        root_folder='staging',
    )

    print(f'Arquivo salvo com sucesso em: {blob_path}')