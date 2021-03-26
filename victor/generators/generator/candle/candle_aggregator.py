import functools
from typing import List

from victor.exchange.types import Candle, Instrument
from victor.generators.generator import Generator


class CandleAggregator(Generator[Candle, Candle]):
    n: int
    k: int
    buffer: List

    def __init__(self, n: int, instrument: Instrument):
        assert (n > 0)

        Generator.__init__(self, name=self.make_name(instrument, n), limit=None, instrument=instrument)
        self.n = n
        self.k = 0
        self.buffer = []

    @staticmethod
    def make_name(instrument: Instrument, n: int):
        instrument_id = instrument['id']
        return f'candle-aggregator({instrument_id}, {n})'

    def __get_next(self, close, open, high, low, volume, time):
        if self.k == self.n:
            self.buffer.clear()
            self.k = 0

        self.buffer.append({
            'close': close,
            'high': high,
            'open': open,
            'low': low,
            'volume': volume,
            'time': time
        })
        self.k += 1

        if self.k < self.n:
            return None
        else:
            return {
                'close': self.buffer[-1]['close'],
                'open': self.buffer[0]['open'],
                'high': max(self.buffer, key=lambda x: x['high'])['high'],
                'low': min(self.buffer, key=lambda x: x['low'])['low'],
                'volume': functools.reduce(lambda acc, curr: acc + curr['volume'], self.buffer, 0),
                'time': self.buffer[0]['time']
            }

    def next(self, candle: Candle):
        result = self.__get_next(
            close=candle['close'],
            volume=candle['volume'],
            low=candle['low'],
            time=candle['time'],
            open=candle['open'],
            high=candle['high'],
        )

        if result is not None:
            self.resultDeque.append(result)

        return result
