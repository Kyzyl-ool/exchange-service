from datetime import time
from enum import Enum

from victor.algorithm import ProbabilityAlgorithm
from victor.exchange.types import Instrument
from victor.generators.generator.filters.time_filter import TimeFilter
from victor.risk_management import RiskManagement

TIME_FILTER_LENGTH = 5


class Market(str, Enum):
    rus = 'rus',
    usa = 'usa'


class OnlyMarketOpeningAlgorithm(ProbabilityAlgorithm):
    def __init__(self, instrument: Instrument, risk_management: RiskManagement, first_n_hours: int, market: Market):
        ProbabilityAlgorithm.__init__(self, instrument=instrument,
                                      name=OnlyMarketOpeningAlgorithm.make_name(instrument),
                                      risk_management=risk_management)
        if market == Market.rus:
            self._add_dependency(
                TimeFilter(instrument=instrument, limit=TIME_FILTER_LENGTH, from_time=time(10, 0, 0),
                           to_time=time(10 + first_n_hours, 0, 0))
            )
        elif market == Market.usa:
            self._add_dependency(
                TimeFilter(instrument=instrument, limit=TIME_FILTER_LENGTH, from_time=time(17, 30, 0),
                           to_time=time(17 + first_n_hours, 30, 0))
            )
        else:
            raise AssertionError('Недопустимый тип рынка')

    def _probability(self) -> float:
        value = self.general_pool.get_generator(TimeFilter.make_name(self.instrument)).value()

        return 1 if value else 0
