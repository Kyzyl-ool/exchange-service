from victor.algorithm import ProbabilityAlgorithm
from victor.exchange.types import Instrument
from victor.generators.generator.patterns.breakout import Breakout
from victor.risk_management import RiskManagement


class BreakoutProbabilityAlgorithm(ProbabilityAlgorithm):
    """
    Вероятностный алгоритм по пробитию уровня
    Пока что обрабатывает только пробития вверх
    """

    def __init__(self, risk_management: RiskManagement, instrument: Instrument, n: int, m: int):
        ProbabilityAlgorithm.__init__(self, BreakoutProbabilityAlgorithm.make_name(instrument, n, m), risk_management,
                                      instrument)

        self._add_dependency(Breakout(n=n, m=m, instrument=instrument))
        self.breakout = self.general_pool.get_generator(Breakout.make_name(n, m), instrument)

    def _probability(self) -> float:
        if self.breakout.value() > 0:
            return 1
        else:
            return 0