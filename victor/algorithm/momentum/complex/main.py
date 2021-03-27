from victor.algorithm import ProbabilityAlgorithm
from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.exchange.types import Instrument
from victor.generators.generator.filters.time_filter import OnlyMarketOpening, Market
from victor.generators.generator.patterns.bar_rotation import BarRotationGenerator
from victor.generators.generator.patterns.breakout import Breakout
from victor.risk_management import RiskManagement

N = 5
M = 2


class MainAlgorithm(ProbabilityAlgorithm):
    def __init__(self, instrument: Instrument, risk_management: RiskManagement):
        ProbabilityAlgorithm.__init__(self, MainAlgorithm.make_name(instrument), risk_management, instrument)

        self.short = False

        self._add_dependency(BarRotationGenerator(self.short, instrument, limit=GENERATOR_MAX_DEQUE_LENGTH))
        self._add_dependency(Breakout(n=N, m=M, instrument=instrument))
        self._add_dependency(OnlyMarketOpening(instrument, 3, Market.rus))

        self.bar_rotation = self.general_pool.select_generator(BarRotationGenerator, self.instrument, short=self.short)
        self.breakout = self.general_pool.select_generator(Breakout, self.instrument, n=N, m=M)
        self.time_filter = self.general_pool.select_generator(OnlyMarketOpening, self.instrument)

    def _probability(self) -> float:
        bar_rotation = self.bar_rotation.value()
        breakout = self.breakout.value()
        time_filter = self.time_filter.value()

        if bar_rotation > 0 and breakout > 0 and time_filter:
            return 1
        else:
            return 0
