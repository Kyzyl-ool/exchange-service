from victor.exchange.types import Candle, Instrument
from victor.generators.generator import Generator


class HeikenAshi(Generator[Candle, Candle]):
    name = 'heiken-ashi'

    def __init__(self, instrument: Instrument):
        Generator.__init__(self, name=HeikenAshi.name, limit=None, instrument=instrument)
        self.open_prev = None
        self.close_prev = None

    def __HA(self, open1, close1, high1, low1, open, close):
        open2 = (open + close)/2
        close2 = (open1 + close1 + high1 + low1)/4
        high2 = max(high1, open2, close2)
        low2 = min(low1, open2, close2)
        return open2, close2, high2, low2

    def next(self, candle: Candle):
        close = candle['close']
        high = candle['high']
        low = candle['low']
        open = candle['open']
        time = candle['time']
        volume = candle['volume']

        if self.open_prev and self.close_prev:
            open1, close1, high1, low1 = self.__HA(open, close, high, low, self.open_prev, self.close_prev)
        else:
            open1, close1, high1, low1 = open, close, high, low

        self.open_prev = open
        self.close_prev = close

        self.resultDeque.append(Candle(
            volume=volume,
            low=low1,
            open=open1,
            close=close1,
            high=high1,
            time=time,
        ))
