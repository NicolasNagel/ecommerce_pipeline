from pathlib import Path

from src.collector.data_collector import DataCollector

class CSVCollector(DataCollector):
    def __init__(self, path: Path) -> None:
        self.path = path

    def collect(self) -> list[Path]:
        return list(self.path.glob('*.csv'))