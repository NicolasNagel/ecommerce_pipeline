import pandas as pd

from pathlib import Path
from datetime import datetime

from sqlalchemy import create_engine, text


class DataBaseWriter:
    """
    Classe responsável por escrever dados no Banco de Dados.

    Responsabilidades:
        - Criar e gerenciar a conexão com o Banco de Dados;
        - Ler arquivos Parquet locais;
        - Escrever dados em tabelas do Banco;
        - Garantir que o schema existe antes de escrever;
    """
    def __init__(self, connection_string: str) -> None:
        self.engine = create_engine(connection_string)

    def ensure_schema_exists(self, schema: str) -> None:
        """
        Garante que o schema existe no Banco de Dados. Caso não, cria um novo.

        Args:
            schema (str): Nome do schema.
        """
        with self.engine.connect() as conn:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {schema}'))
            conn.commit()

    def infer_table_name(self, local_file_path: str | Path) -> str:
        """
        Infere o nome da tabela automaticamente com base no diretório do arquivo.

        Args:
            local_file_path (str | Path): Diretório temporário local.

        Returns:
            str: Nome da tabela.
        """
        local_file_path = Path(local_file_path)
        return f'bronze_{local_file_path.stem}'
    
    def read_parquet(self, local_file_path: str | Path) -> pd.DataFrame:
        """
        Lê um arquivo Parquet e salva o DataFrame em memória.

        Args:
            local_file_path (str | Path): Diretório temporário local.

        Returns:
            DataFrame: DataFrame do Pandas em memória.
        """
        return pd.read_parquet(local_file_path, engine='pyarrow')
    
    def insert_control_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Insere duas colunas de controle antes de salvar no Banco de Dados.

        Args:
            df (DataFrame): DataFrame do Pandas.

        Returns:
            DataFrame: DataFrame com as colunas de controle adicionadas.
        """
        df['sistem_source'] = 'excel'
        df['inserted_at'] = datetime.now()

        return df
    
    def write(
            self,
            local_file_path: str | Path,
            schema: str,
            if_exists: str = 'replace'
    ) -> None:
        """
        Salva os Dados no Banco de Dados.

        Args:
            local_file_path (str | Path): Diretório temporário local.
            schema (str): Schema a ser salvo no Banco de Dados.
            if_exists (str): Informa o que acontece se os Dados existem. 
        """
        self.ensure_schema_exists(schema=schema)

        local_file_path = Path(local_file_path)
        if local_file_path is None:
            raise FileNotFoundError(f'Arquivo não encontrado: {local_file_path}')
        
        table_name = self.infer_table_name(local_file_path=local_file_path)

        df = self.read_parquet(local_file_path)
        transformed_df = self.insert_control_columns(df)

        transformed_df.to_sql(
            name=table_name,
            con=self.engine,
            schema=schema,
            if_exists=if_exists,
            index=False
        )