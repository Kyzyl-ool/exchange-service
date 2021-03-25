from victor.exchange.types import Candle

from victor.generators.generator.technical_indicators import TechnicalIndicator
from victor.generators.generator.technical_indicators.average import EMA


class RS(TechnicalIndicator):
    def __init__(self, ema_u: EMA, ema_d: EMA, **kwargs):
        kwargs['name'] = kwargs.get('name', 'RS')
        super().__init__(**kwargs)

        assert ema_u is not None
        assert ema_d is not None
        assert ema_u.name == 'EMA_U'
        assert ema_d.name == 'EMA_D'

        self.add_dependency(ema_u)
        self.add_dependency(ema_d)

    def next(self, candle: Candle):
        ema_u = self.dependencies['EMA_U']
        ema_d = self.dependencies['EMA_D']

        result = ema_u.value() / ema_d.value() if ema_d.value() != 0 else 1

        self.resultDeque.append(result)
