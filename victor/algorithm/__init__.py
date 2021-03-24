from typing import Union
import numpy as np

from victor.generators import GeneratorSet
from victor.risk_management import RiskManagement

OperationType = Union['BUY', 'SELL']


class Algorithm:
    name: str
    generator_set: GeneratorSet
    risk_management: RiskManagement

    def __init__(self, generator_set: GeneratorSet, name: str, risk_management: RiskManagement):
        self.generator_set = generator_set
        self.name = name
        self.risk_management = risk_management

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
