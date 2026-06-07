import pandas as pd
import pyarrow as py

from pathlib import Path

from src.transformer.data_transformer import DataTransformer


class ParquetTransformer(DataTransformer):
    """
    Responsável por converter arquivos CSV em Parquet.

    Responsabilidades:
        - Ler CSV com inferência de tipos.
        - Salvar Parquet localmente.
        - Retornar o caminho do arquivo gerado.
    """
    def __init__(self, output_dir: str | Path = 'src/data/staging') -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def transform(self, csv_path: str | Path) -> Path:
        csv_path = Path(csv_path)
        df = pd.read_csv(csv_path, encoding='utf-8')
        output_path = self.output_dir / csv_path.with_suffix('.parquet').name
        df.to_parquet(output_path, index=False, engine='pyarrow')

        return output_path