from abc import ABC, abstractmethod
from typing import Optional, Any


class DataTransformer(ABC):
    """
    Classe de contrato responsável por definir o padrão das transformações de dados.
    """

    @abstractmethod
    def transform(self) -> Optional[Any]:
        """
        Método de contrato para a função de transformar dados.

        Returns:
            Optional(Any): Pode retornar qualquer coisa, cabe ao próximo Engenheiro definir qual 
                será a regra a ser aplicada e o retorno da função dependendo o tipo de transformador.

        Raises:
            NotImplementedError: Por ser um método de contrato, é necessário fazer sua implementação
                nas classes que serão herdadas.
        """
        raise FileNotFoundError('Método ainda não implementado.')