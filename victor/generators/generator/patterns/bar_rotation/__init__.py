from collections import deque

from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.exchange.types import Candle, Instrument
from victor.generators.generator.candle.heiken_ashi import HeikenAshi
from victor.generators.generator.technical_indicators import TechnicalIndicator


class BarRotationGenerator(TechnicalIndicator):
    def __init__(self, short: bool, instrument: Instrument, fr: float, limit=GENERATOR_MAX_DEQUE_LENGTH):
        TechnicalIndicator.__init__(self, name=BarRotationGenerator.make_name(instrument, short=short),
                                    instrument=instrument,
                                    limit=limit, fr=fr)

        self._add_dependency(HeikenAshi(instrument))
        self.first_white_bars_amount = 0
        self.black_bars_amount = 0
        self.queue = deque()

        self.short = short

        self.is_white_bar = None

        self.state = 0

    def __HA(self, open1, close1, high1, low1, open, close):
        open2 = (open + close) / 2
        close2 = (open1 + close1 + high1 + low1) / 4
        high2 = max(high1, open2, close2)
        low2 = min(low1, open2, close2)
        return open2, close2, high2, low2

    def __place(self, candle: Candle):
        self.queue.append({
            'close': candle['close'],
            'open': candle['open'],
            'high': candle['high'],
            'low': candle['low'],
            'volume': candle['volume'],
            'time': candle['time']
        })

    def __next(self, candle: Candle):
        ha_candle = self.general_pool.get_generator(HeikenAshi.make_name(self.instrument)).value()
        close1 = ha_candle['close']
        open1 = ha_candle['open']
        self.is_white_bar = (close1 - open1 > 0) == (not self.short)

        if self.state == 0:
            if self.is_white_bar:
                self.state = 1
                self.__place(candle)
                self.first_white_bars_amount += 1
        elif self.state == 1:
            if self.is_white_bar:
                self.__place(candle)
                self.first_white_bars_amount += 1
            else:
                self.state = 2
                self.__place(candle)
                self.black_bars_amount += 1
        elif self.state == 2:
            if not self.is_white_bar:
                self.__place(candle)
                self.black_bars_amount += 1
            else:
                self.__place(candle)
                result = list(self.queue)
                self.queue.clear()
                a, b = self.first_white_bars_amount, self.black_bars_amount
                self.first_white_bars_amount, self.black_bars_amount = 0, 0
                self.state = 0
                return [a, b, result]

        return None

    def next(self, candle: Candle):
        result = self.__next(candle)

        self._apply_new_value(self.norm(result, bias=self.instrument['punct'], w1=10.0, w2=10.0))
        return result

    def norm(self, item, w1=1.0, w2=1.0, bias=0.01) -> float:
        return abs(item[0] - 5) * w1 + abs(item[1] - 2) * w2 + bias if item else 0
