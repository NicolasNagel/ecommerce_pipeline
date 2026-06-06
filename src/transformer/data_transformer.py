from abc import ABC, abstractmethod


class DataTransformer(ABC):
    """
    Classe de contrato para a criação das classes de Transformações.
    """

    @abstractmethod
    def transform(self) -> None:
        raise NotImplementedError('Método ainda não implementado.')