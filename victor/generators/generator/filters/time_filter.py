from datetime import time
from enum import Enum

from victor.exchange.types import Candle, Instrument
from victor.generators.generator import Generator


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


class OnlyMarketOpening(TimeFilter):
    def __init__(self, instrument: Instrument, first_n_hours: int, market: Market):
        if market == Market.rus:
            TimeFilter.__init__(self, instrument=instrument, limit=TIME_FILTER_LENGTH, from_time=time(10, 0, 0),
                                to_time=time(10 + first_n_hours, 0, 0))
        elif market == Market.usa:
            TimeFilter.__init__(self, instrument=instrument, limit=TIME_FILTER_LENGTH, from_time=time(17, 30, 0),
                                to_time=time(17 + first_n_hours, 30, 0))
        else:
            raise AssertionError('Недопустимый тип рынка')

    @classmethod
    def make_name(cls, instrument: Instrument, *args, **kwargs):
        return TimeFilter.make_name(instrument, *args, **kwargs)
