from pathlib import Path

from include.src.collector.data_collector import DataCollector


class CSVCollector(DataCollector):
    """
    Responsável pela coleta de arquivos do tipo CSV.
    """
    def __init__(self, local_file_path: str | Path) -> None:
        self.local_file_path = Path(local_file_path)

    def collect(self) -> list[Path]:
        """
        Faz a coleta de arquivos CSV dentro de um diretório específico.

        Returns:
            list(Path): Lista com todos os diretórios para serem 
                passados a próxima etapa da pipeline
        """
        return list(self.local_file_path.glob('*.csv'))