import pandas as pd

from pathlib import Path

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
        with self.engine.connect() as conn:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {schema}'))
            conn.commit()

    def read_parquet(self, local_path: str | Path) -> pd.DataFrame:
        return pd.read_parquet(local_path, engine='pyarrow')
    
    def write(
            self,
            local_path: str | Path,
            table_name: str,
            schema: str = 'bronze',
            if_exists: str = 'append'
    ) -> None:
        self.ensure_schema_exists(schema)

        df = self.read_parquet(local_path)

        df.to_sql(
            name=table_name,
            con=self.engine,
            schema=schema,
            if_exists=if_exists,
            index=False
        )