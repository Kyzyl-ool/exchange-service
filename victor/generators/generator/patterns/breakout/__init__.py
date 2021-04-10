from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.exchange.types import Candle, Instrument
from victor.generators.generator.candle.candle_aggregator import CandleAggregator
from victor.generators.generator.technical_indicators import TechnicalIndicator


class Breakout(TechnicalIndicator):
    def __init__(self, n: int, m: int, instrument: Instrument):
        TechnicalIndicator.__init__(self, name=self.make_name(instrument, n=n, m=m), instrument=instrument,
                                    limit=GENERATOR_MAX_DEQUE_LENGTH)

        self._add_dependency(CandleAggregator(n=n, instrument=instrument))
        self.candle_aggregator = self.general_pool.select_generator(CandleAggregator, instrument, n=n)

        self.m = m  # сила уровня
        self.n = n

        self.levels = {}
        self.broken_levels = []

    def __filter_func(self, level):
        candles = list(self.candle_aggregator.resultDeque)

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

    def __update_levels(self, candle_aggregated: Candle):
        c = candle_aggregated['close']
        o = candle_aggregated['open']
        h = candle_aggregated['high']
        l = candle_aggregated['low']
        v = candle_aggregated['volume']
        t = candle_aggregated['time']

        co_max = max(c, o)

        for level in self.levels.values():
            d1 = level['d1']
            d2 = level['d2']

            if c <= d2:
                if h > d2:
                    level['d2'] = max(d2, h)
                if co_max > d1:
                    level['d1'] = max(d1, co_max)

        self.levels[len(self.levels)] = {
            'd1': co_max,
            'd2': h,
            'time': t,
            'i': len(self.candle_aggregator.resultDeque) - 1,
            'id': len(self.levels)
        }

    def __check_broken_levels(self, candle: Candle):
        for level in self.levels.values():
            d2 = level['d2']

            if candle['close'] > d2:
                self.broken_levels.append(level)

    def next(self, candle: Candle):
        for level in self.broken_levels:
            del self.levels[level['id']]
        self.broken_levels.clear()

        candle_aggregator = self.candle_aggregator

        candle_aggregated = candle_aggregator.value()

        if candle_aggregated:
            new_levels = {}
            for x in filter(self.__filter_func, self.levels.values()):
                new_levels[x['id']] = x
            self.levels = new_levels

            # обнолвние уровней
            self.__update_levels(candle_aggregated)

        # определяем, есть ли пробой
        self.__check_broken_levels(candle)

        self.resultDeque.append(self.norm(w=10.0, bias=self.instrument['punct']))

    def norm(self, w=1.0, bias=0.01):
        result = 0
        for item in self.broken_levels:
            result += abs(item['d2'] - item['d1']) * w + bias

        return result


class BreakoutDown(Breakout):
    def __update_levels(self, candle_aggregated: Candle):
        c = candle_aggregated['close']
        o = candle_aggregated['open']
        l = candle_aggregated['low']
        t = candle_aggregated['time']

        co_min = min(c, o)

        for level in self.levels.values():
            d1 = level['d1']
            d2 = level['d2']

            if c >= d2:
                if l < d2:
                    level['d2'] = min(d2, l)
                if co_min < d1:
                    level['d1'] = min(d1, co_min)

        self.levels[len(self.levels)] = {
            'd1': co_min,
            'd2': l,
            'time': t,
            'i': len(self.candle_aggregator.resultDeque) - 1,
            'id': len(self.levels)
        }

    def __check_broken_levels(self, candle: Candle):
        for level in self.levels.values():
            d2 = level['d2']

            if candle['close'] < d2:
                self.broken_levels.append(level)
