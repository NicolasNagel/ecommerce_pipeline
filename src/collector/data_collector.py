from abc import ABC, abstractmethod

class DataCollector(ABC):
    """Classe de contrato para a coleta de Dados."""

    @abstractmethod
    def collect(self) -> None:
        return NotImplementedError('Método ainda não implementado.')