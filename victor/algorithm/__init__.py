from typing import Union
import numpy as np

from victor.exchange.types import Instrument
from victor.generators import GeneralPool
from victor.generators.generator import Generator, GeneratorDependencyManager
from victor.risk_management import RiskManagement

OperationType = Union['BUY', 'SELL']


class Algorithm(GeneratorDependencyManager):
    general_pool: GeneralPool = GeneralPool.getInstance()

    def __init__(self, name: str, risk_management: RiskManagement, instrument: Instrument):
        self.name = name
        self.risk_management = risk_management
        self.instrument = instrument

    def determine(self) -> Union[OperationType, None]:
        raise NotImplementedError('Необходимо отнаследоваться и реализовать этот метод')


class ProbabilityAlgorithm(Algorithm):
    def probability(self, reverse=False) -> float:
        if reverse:
            return -self._probability()
        else:
            return self._probability()

    def _probability(self) -> float:
        """
        Вероятность покупки.

        -1 – покупка в шорт
        1 – покупка в лонг
        """
        raise NotImplementedError('Необходимо отнаследоваться и реализовать этот метод')

    def determine(self) -> Union[OperationType, None]:
        p = self.probability()
        p_abs = abs(p)
        rand = np.random.random()

        if rand < p_abs:
            if p < 0:
                return 'SELL'
            else:
                return 'BUY'
        else:
            return None
