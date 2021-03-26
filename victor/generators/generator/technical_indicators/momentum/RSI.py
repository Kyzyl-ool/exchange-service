from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator
from victor.generators.generator.technical_indicators.momentum import RS


class RSI(TechnicalIndicator):
    def __init__(self, instrument: Instrument, limit: int, n: int):
        TechnicalIndicator.__init__(self, RSI.make_name(instrument), instrument, limit)

        self._add_dependency(RS(instrument, limit, n))

    def next(self, candle: Candle):
        rs_value = self.general_pool.get_generator(RS.make_name(self.instrument), self.instrument).value()

        if rs_value is not None:
            result = 100 - 100 / (1 + rs_value)
        else:
            result = 50

        self.resultDeque.append(result)
