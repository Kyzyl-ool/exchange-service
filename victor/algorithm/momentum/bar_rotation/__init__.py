from victor.algorithm import ProbabilityAlgorithm
from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.exchange.types import Instrument
from victor.generators.generator.patterns.bar_rotation import BarRotationGenerator
from victor.risk_management import RiskManagement


class BarRotationAlgorithm(ProbabilityAlgorithm):
    """
    Вероятностный алгоритм торговли ротации бара
    """

    def __init__(self, instrument: Instrument, risk_management: RiskManagement, short: bool):
        ProbabilityAlgorithm.__init__(self, BarRotationAlgorithm.make_name(instrument), risk_management, instrument)

        self._add_dependency(BarRotationGenerator(short, instrument, limit=GENERATOR_MAX_DEQUE_LENGTH))
        self.short = short

    def _probability(self) -> float:
        value = self.general_pool.get_generator(
            BarRotationGenerator.make_name(self.instrument, short=self.short)).value()

        if value > 0:
            return 1
        else:
            return 0
