from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator
from victor.generators.generator.technical_indicators.average import EMA
from victor.generators.generator.technical_indicators.price import D
from victor.generators.generator.technical_indicators.price.D import D_NAME
from victor.generators.generator.technical_indicators.price.U import U, U_NAME

RS_NAME = 'rs'


class RS(TechnicalIndicator):
    def __init__(self, punct: float, instrument: Instrument, limit: int, n: int):
        TechnicalIndicator.__init__(self, punct=punct, name=RS_NAME, instrument=instrument, limit=limit)
        self.n = n

        self.add_dependency(U(punct, instrument, limit))
        self.add_dependency(D(punct, instrument, limit))

        self.add_dependency(EMA(n, U_NAME, punct, instrument, limit))
        self.add_dependency(EMA(n, D_NAME, punct, instrument, limit))

    def next(self, candle: Candle):
        ema_u = self.general_pool.get_generator(EMA.make_name(U_NAME, self.n), self.instrument)
        ema_d = self.general_pool.get_generator(EMA.make_name(D_NAME, self.n), self.instrument)

        result = ema_u.value() / ema_d.value() if ema_d.value() != 0 else 1

        self.resultDeque.append(result)
