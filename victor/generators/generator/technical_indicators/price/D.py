from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator


class D(TechnicalIndicator):
    def __init__(self, instrument: Instrument, limit: int):
        TechnicalIndicator.__init__(self, name=D.make_name(instrument), instrument=instrument, limit=limit, fr=0)

    def next(self, candle: Candle):
        price_change = candle['close'] - candle['open']
        d_value = -price_change if price_change < 0 else 0

        super()._apply_new_value(d_value)
