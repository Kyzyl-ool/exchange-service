from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator
from victor.generators.generator.technical_indicators.momentum import RS
from victor.generators.generator.technical_indicators.momentum.RS import RS_NAME

RSI_NAME = 'rsi'


class RSI(TechnicalIndicator):
    def __init__(self, punct: float, instrument: Instrument, limit: int, n: int):
        TechnicalIndicator.__init__(self, punct, RSI_NAME, instrument, limit)

        self.add_dependency(RS(punct, instrument, limit, n))

    def next(self, candle: Candle):
        rs_value = self.general_pool.get_generator(RS_NAME, self.instrument).value()

        if rs_value is not None:
            result = 100 - 100 / (1 + rs_value)
        else:
            result = 50

        self.resultDeque.append(result)
