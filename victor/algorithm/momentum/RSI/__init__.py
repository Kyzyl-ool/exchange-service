from victor.algorithm import ProbabilityAlgorithm
from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.exchange.types import Instrument
from victor.generators.generator.technical_indicators.momentum import RSI
from victor.risk_management import RiskManagement


class RSIProbabilityAlgorithm(ProbabilityAlgorithm):
    """
    Вероятностный алгоритм по индикатору RSI

    GeneratorSet должен иметь RSI
    """
    upper_bound: float
    lower_bound: float

    def __init__(self, lower_bound: float, upper_bound: float, risk_management: RiskManagement,
                 instrument: Instrument, rsi_n: int):
        ProbabilityAlgorithm.__init__(self, name=RSIProbabilityAlgorithm.make_name(instrument),
                                      risk_management=risk_management,
                                      instrument=instrument)
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

        self._add_dependency(RSI(instrument, GENERATOR_MAX_DEQUE_LENGTH, rsi_n))

    @staticmethod
    def make_name(instrument: Instrument):
        instrument_id = instrument['id']
        return f'rsi-algorithm({instrument_id})'

    def _probability(self) -> float:
        k = 2 / (self.lower_bound - self.upper_bound)
        b = (self.lower_bound + self.upper_bound) / (self.upper_bound - self.lower_bound)
        x = self.general_pool.get_generator(RSI.make_name(self.instrument), self.instrument).value()

        if x <= self.lower_bound:
            return 1
        elif x >= self.upper_bound:
            return -1
        else:
            return k * x + b
