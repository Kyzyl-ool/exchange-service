from victor.exchange.types import Candle

from victor.generators.generator.technical_indicators import TechnicalIndicator


class U(TechnicalIndicator):
    def __init__(self, **kwargs):
        kwargs['name'] = kwargs.get('name', 'U')
        super().__init__(**kwargs)

    def next(self, candle: Candle):
        price_change = candle['close'] - candle['open']
        u_value = price_change if price_change > 0 else 0

        self.resultDeque.append(u_value)
