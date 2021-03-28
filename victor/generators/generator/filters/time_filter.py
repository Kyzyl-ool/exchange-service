from datetime import time
from enum import Enum

from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.exchange.types import Candle, Instrument
from victor.generators.generator import Generator
from victor.generators.generator.technical_indicators import TechnicalIndicator

TIME_FILTER_LENGTH = 5


class Market(str, Enum):
    rus = 'rus',
    usa = 'usa'


def time_in_range(start, end, x) -> bool:
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


class TimeFilter(Generator[Candle, bool]):
    def __init__(self, from_time: time, to_time: time, instrument: Instrument, limit: int):
        Generator.__init__(self, name=TimeFilter.make_name(instrument), instrument=instrument, limit=limit)
        self.from_time = from_time
        self.to_time = to_time

    def next(self, candle: Candle):
        result = time_in_range(self.from_time, self.to_time, candle['time'].time())
        self.resultDeque.append(result)


class OnlyMarketOpening(TechnicalIndicator):
    def __init__(self, instrument: Instrument, market: Market):
        TechnicalIndicator.__init__(self, OnlyMarketOpening.make_name(instrument), instrument, GENERATOR_MAX_DEQUE_LENGTH)
        self.market = market

    def next(self, candle: Candle):
        x = candle['time']
        if self.market == Market.usa:
            delta_min = x.time().minute + (x.time().hour - (17.5 if x.month >= 4 else 16.5)) * 60
        else:
            delta_min = x.time().minute + (x.time().hour - 10) * 60

        self.resultDeque.append(delta_min)
