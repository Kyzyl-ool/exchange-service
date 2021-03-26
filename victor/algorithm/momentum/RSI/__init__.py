from victor.algorithm import ProbabilityAlgorithm
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
    name: str = 'rsi-algorithm'

    def __init__(self, lower_bound: float, upper_bound: float, risk_management: RiskManagement,
                 instrument: Instrument):
        ProbabilityAlgorithm.__init__(self, name=RSIProbabilityAlgorithm.name, risk_management=risk_management,
                                      instrument=instrument)
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

        self.general_pool.is_generator_exist()

    def _probability(self) -> float:
        k = 2 / (self.lower_bound - self.upper_bound)
        b = (self.lower_bound + self.upper_bound) / (self.upper_bound - self.lower_bound)
        x = self.general_pool.get_generator(RSI.name, self.instrument).value()

        if x <= self.lower_bound:
            return 1
        elif x >= self.upper_bound:
            return -1
        else:
            return k * x + b
