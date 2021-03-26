from datetime import time

from victor.exchange.types import Candle, Instrument
from victor.generators.generator import Generator


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
