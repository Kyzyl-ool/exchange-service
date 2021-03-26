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

    def __init__(self, lower_bound: float, upper_bound: float, name: str, risk_management: RiskManagement, instrument: Instrument):
        requirements = [
            RSI()
        ]
        ProbabilityAlgorithm.__init__(self, name=name, risk_management=risk_management, instrument=instrument, requirements=requirements)

        assert self.generator_set.__generators['RSI'] is not None

        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def _probability(self) -> float:
        k = 2 / (self.lower_bound - self.upper_bound)
        b = (self.lower_bound + self.upper_bound) / (self.upper_bound - self.lower_bound)
        x = self.generator_set.__generators['RSI'].value()

        if x <= self.lower_bound:
            return 1
        elif x >= self.upper_bound:
            return -1
        else:
            return k * x + b

