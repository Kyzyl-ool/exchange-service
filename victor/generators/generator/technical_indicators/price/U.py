from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator

U_NAME = 'u'


class U(TechnicalIndicator):
    def __init__(self, punct: float, instrument: Instrument, limit: int):
        TechnicalIndicator.__init__(self, punct=punct, name=U_NAME, instrument=instrument, limit=limit)

    def next(self, candle: Candle):
        price_change = candle['close'] - candle['open']
        u_value = price_change if price_change > 0 else 0

        self.resultDeque.append(u_value)
