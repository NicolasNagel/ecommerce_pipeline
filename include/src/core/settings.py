from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Credentials for DataBase Connection
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # Credentials for Microsoft Azure
    CLIENT_ID: str
    TENANT_ID: str
    CLIENT_SECRET: str
    AZURE_BLOB_STORAGE: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

    @property
    def database_url(self) -> str:
        return (
            f'postgresql://'
            f'{self.DB_USER}:'
            f'{self.DB_PASS}@'
            f'{self.DB_HOST}:'
            f'{self.DB_PORT}/'
            f'{self.DB_NAME}'
        )
    
settings = Settings()