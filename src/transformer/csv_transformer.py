import pandas as pd

from pathlib import Path

from src.transformer.data_transformer import DataTransformer


class ParquetTransformer(DataTransformer):
    """
    Classe responsável por transformar arquivos em Parquet.
    """
    def __init__(self, output_dir: str | Path = 'src/data/staging') -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
        output_path = self.output_dir / csv_path.with_suffix('.parquet').name
        df.to_parquet(output_path, engine='pyarrow')

        return output_path