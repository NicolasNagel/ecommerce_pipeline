from pathlib import Path

from abc import ABC, abstractmethod

class DataCollector(ABC):
    """Classe de contrato para a coleta de Dados."""

    @abstractmethod
    def collect(self) -> list[Path]:
        return NotImplementedError('Método ainda não implementado.')