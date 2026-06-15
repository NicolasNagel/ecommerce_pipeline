from abc import ABC, abstractmethod
from typing import Optional, Any

class DataCollector(ABC):
    """
    Classe de contrato responsável por definir o padrão dos coletores de dados.
    """

    @abstractmethod
    def collect(self) -> Optional[Any]:
        """
        Método de contrato para a função de coletar dado.

        Returns:
            Optional(Any): Pode retornar qualquer coisa, cabe ao próximo Engenheiro definir qual 
                será a regra a ser aplicada e o retorno da função dependendo o tipo de coletor.

        Raises:
            NotImplementedError: Por ser um método de contrato, é necessário fazer sua implementação
                nas classes que serão herdadas.
        """
        raise FileNotFoundError('Método ainda não implementado.')