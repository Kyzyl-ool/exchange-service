from victor.algorithm import ProbabilityAlgorithm
from victor.exchange.types import Instrument
from victor.generators.generator.filters.time_filter import OnlyMarketOpening, Market
from victor.risk_management import RiskManagement


class OnlyMarketOpeningAlgorithm(ProbabilityAlgorithm):
    def __init__(self, instrument: Instrument, risk_management: RiskManagement, first_n_hours: int, market: Market):
        ProbabilityAlgorithm.__init__(self, instrument=instrument,
                                      name=OnlyMarketOpeningAlgorithm.make_name(instrument),
                                      risk_management=risk_management)
        self._add_dependency(
            OnlyMarketOpening(instrument=instrument, market=market, first_n_hours=first_n_hours)
        )

    def _probability(self) -> float:
        value = self.general_pool.get_generator(OnlyMarketOpening.make_name(self.instrument)).value()

        return 1 if value else 0
