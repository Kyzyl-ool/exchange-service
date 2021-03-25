from victor.exchange.types import Candle

from victor.generators.generator.technical_indicators import TechnicalIndicator
from victor.generators.generator.technical_indicators.momentum import RS


class RSI(TechnicalIndicator):
    rs: TechnicalIndicator

    def __init__(self, rs: RS, **kwargs):
        kwargs['name'] = kwargs.get('name', 'RSI')
        super().__init__(**kwargs)

        assert rs is not None

        self.rs = rs

    def next(self, candle: Candle):
        rs = self.rs.value()

        result = None

        if rs is not None:
            result = 100 - 100 / (1 + rs)
        else:
            result = 50

        assert result is not None

        self.resultDeque.append(result)
