from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator

D_NAME = 'd'


class D(TechnicalIndicator):
    def __init__(self, punct: float, instrument: Instrument, limit: int):
        TechnicalIndicator.__init__(self, punct=punct, name=D_NAME, instrument=instrument, limit=limit)

    def next(self, candle: Candle):
        price_change = candle['close'] - candle['open']
        d_value = -price_change if price_change < 0 else 0

        self.resultDeque.append(d_value)
