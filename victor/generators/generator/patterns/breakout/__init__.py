from typing import List

from victor.exchange.types import Candle
from victor.generators import Generator
from victor.generators.generator.technical_indicators import TechnicalIndicator

class Breakout(Generator[Candle, Candle]):
    n: int
    m: int
    punct: float

    levels: List
    candles: List
    candle_aggregator = CandleAggregator(n)
    broken_levels = []
    m = m  # сила уровня
    punct = punct

    def __init__(self, n, m, punct, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.m = m
        self.punct = punct

        self.levels = []
        self.candles = []
        self.candle_aggregator = CandleAggregator(n)
        self.broken_levels = []
        self.m = m  # сила уровня
        self.punct = punct


    def __get_next(self, close, open, high, low, volume, time):
        for level in self.broken_levels:
            self.levels.remove(level)
        self.broken_levels.clear()

        candle = self.candle_aggregator.get_next(close, open, high, low, volume, time)
        if candle:
            c = candle['close']
            o = candle['open']
            h = candle['high']
            l = candle['low']
            v = candle['volume']
            t = candle['time']

            self.candles.append({
                'close': c,
                'open': o,
                'low': l,
                'high': h,
                'volume': v,
                'time': t
            })

            co_max = max(c, o)

            def filter_func(level):
                index = level['i']
                n = self.m
                qualifyable = n <= index < len(self.candles) - n

                qualified_level = None

                if qualifyable:
                    qualified_level = sorted(self.candles[index - n:index], key=lambda x: x['high']) == self.candles[
                                                                                                        index - n:index] and sorted(
                        self.candles[index + 1:index + n + 1], key=lambda x: x['high'], reverse=True) == self.candles[
                                                                                                         index + 1:index + n + 1]
                else:
                    qualified_level = True

                return qualified_level

            self.levels = list(filter(filter_func, self.levels))

            # обнолвние уровней
            for level in self.levels:
                d1 = level['d1']
                d2 = level['d2']

                if c <= d2:
                    if h > d2:
                        level['d2'] = max(d2, h)
                    if co_max > d1:
                        level['d1'] = max(d1, co_max)

            self.levels.append({
                'd1': co_max,
                'd2': h,
                'time': t,
                'i': len(self.candles) - 1
            })

        # определяем, есть ли пробой
        for level in self.levels:
            d2 = level['d2']

            if close > d2:
                self.broken_levels.append(level)

        return self.broken_levels

    def next(self, candle: Candle):


