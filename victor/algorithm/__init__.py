from typing import Union, List
import numpy as np

from victor.exchange.types import Instrument
from victor.generators import GeneratorSet, GeneralPool, Generator
from victor.risk_management import RiskManagement

OperationType = Union['BUY', 'SELL']


class Algorithm:
    general_pool: GeneralPool = GeneralPool()

    def __init__(self, name: str, risk_management: RiskManagement, instrument: Instrument,
                 requirements: List[Generator]):
        self.name = name
        self.risk_management = risk_management
        self.instrument = instrument
        self.requirements = requirements

        for generator in requirements:
            if not self.general_pool.is_generator_exist(generator_id=generator.name, instrument=instrument):
                self.general_pool.add_generator(generator_instance=generator, instrument=instrument)

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
