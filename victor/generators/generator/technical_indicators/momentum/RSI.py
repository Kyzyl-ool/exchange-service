from victor.exchange.types import Candle

from victor.generators.generator.technical_indicators import TechnicalIndicator
from victor.generators.generator.technical_indicators.momentum import RS


class RSI(TechnicalIndicator):
    def __init__(self, rs: RS, **kwargs):
        kwargs['name'] = kwargs.get('name', 'RSI')
        super().__init__(**kwargs)

        assert rs is not None
        assert rs.name == 'RS'

        self.add_dependency(rs)

    def next(self, candle: Candle):
        rs_value = self.dependencies['RS'].value()

        result = None

        if rs_value is not None:
            result = 100 - 100 / (1 + rs_value)
        else:
            result = 50

        assert result is not None

        self.resultDeque.append(result)
