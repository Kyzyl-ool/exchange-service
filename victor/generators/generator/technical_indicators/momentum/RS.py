from victor.exchange.types import Candle

from victor.generators.generator.technical_indicators import TechnicalIndicator
from victor.generators.generator.technical_indicators.average import EMA


class RS(TechnicalIndicator):
    ema_u: EMA
    ema_d: EMA

    def __init__(self, ema_u: EMA, ema_d: EMA, **kwargs):
        kwargs['name'] = kwargs.get('name', 'RS')
        super().__init__(**kwargs)

        assert ema_u is not None
        assert ema_d is not None

        self.ema_u = ema_u
        self.ema_d = ema_d

    def next(self, candle: Candle):
        result = self.ema_u.value() / self.ema_d.value() if self.ema_d.value() != 0 else 0

        self.resultDeque.append(result)
