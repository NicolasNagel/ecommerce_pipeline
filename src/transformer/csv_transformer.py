import pandas as pd

from pathlib import Path

from src.transformer.data_transformer import DataTransformer
from src.schemas.registry import SchemaRegistry


class ParquetTransformer(DataTransformer):
    """
    Classe responsável por transformar arquivos em Parquet.
    """
    def __init__(
            self,
            output_dir: str | Path = 'src/data/staging',
            schema_registry: SchemaRegistry | None = None
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.schema_registry = schema_registry

    def _validate_schema(self, df: pd.DataFrame, dataset_name: str) -> None:
        """
        Valida o schema com o contrato estabelecida.

        Args:
            df (DataFrame): DataFrame a ser validado
            dataset_name (str): Nome do dataset de contrato para validação
        """
        if not self.schema_registry:
            return
        
        schema = self.schema_registry.get(dataset_name)
        if not schema:
            return
        
        try:
            schema.validate(df, lazy=True)
        except Exception as e:
            raise

    def transform(self, csv_path: str | Path) -> Path:
        """
        Transforma arquivos CSV em Parquet e salva temporariamente localmente.

        Args:
            csv_path (str | Path): Diretório do arquivo CSV.

        Returns:
            Path: Diretório do arquivo Parquet.
        """
        csv_path = Path(csv_path)
        df = pd.read_csv(csv_path, encoding='utf-8')

        self._validate_schema(df, dataset_name=csv_path.stem)
        
        output_path = self.output_dir / csv_path.with_suffix('.parquet').name
        df.to_parquet(output_path, engine='pyarrow')

        return output_path