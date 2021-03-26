from typing import List

from victor.exchange.types import Candle
from victor.generators.generator.candle.candle_aggregator import CandleAggregator
from victor.generators.generator.technical_indicators import TechnicalIndicator


class Breakout(TechnicalIndicator):
    n: int
    m: int

    levels: List
    broken_levels = []

    def __init__(self, n, m, punct, candle_aggregator: CandleAggregator):
        TechnicalIndicator.__init__(self, punct=punct, name='breakout-up')
        self.add_dependency(candle_aggregator)

        self.m = m  # сила уровня
        self.punct = punct

        self.levels = []
        self.candle_aggregator = CandleAggregator(n)
        self.broken_levels = []

    def next(self, candle: Candle):
        for level in self.broken_levels:
            self.levels.remove(level)
        self.broken_levels.clear()

        for candle_aggregator in self.dependencies.values():
            candle_aggregated = candle_aggregator.next(candle)

            if candle_aggregated:
                c = candle_aggregated['close']
                o = candle_aggregated['open']
                h = candle_aggregated['high']
                l = candle_aggregated['low']
                v = candle_aggregated['volume']
                t = candle_aggregated['time']

                candles = list(self.candle_aggregator.resultDeque)

                co_max = max(c, o)

                def filter_func(level):
                    index = level['i']
                    n = self.m
                    qualifyable = n <= index < len(candles) - n

                    qualified_level = None

                    if qualifyable:
                        qualified_level = sorted(candles[index - n:index],
                                                 key=lambda x: x['high']) == candles[
                                                                             index - n:index] and sorted(
                            candles[index + 1:index + n + 1], key=lambda x: x['high'],
                            reverse=True) == candles[
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
                    'i': len(candles) - 1
                })

            # определяем, есть ли пробой
            for level in self.levels:
                d2 = level['d2']

                if candle['close'] > d2:
                    self.broken_levels.append(level)

        self.resultDeque.append(self.norm(w=10.0, bias=self.punct))

    def norm(self, w=1.0, bias=0.01):
        result = 0
        for item in self.broken_levels:
            return (item['d2'] - item['d1'])*w + bias

        return result
