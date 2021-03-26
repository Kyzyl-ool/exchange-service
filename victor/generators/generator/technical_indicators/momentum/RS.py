from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator
from victor.generators.generator.technical_indicators.average import EMA
from victor.generators.generator.technical_indicators.price import D, U


class RS(TechnicalIndicator):
    def __init__(self, instrument: Instrument, limit: int, n: int):
        TechnicalIndicator.__init__(self, name=RS.make_name(instrument), instrument=instrument, limit=limit)
        self.n = n

        self._add_dependency(U(instrument, limit))
        self._add_dependency(D(instrument, limit))
        self.u_name = U.make_name(instrument)
        self.d_name = D.make_name(instrument)

        self._add_dependency(EMA(n, U.make_name(instrument), instrument, limit))
        self._add_dependency(EMA(n, D.make_name(instrument), instrument, limit))
        self.ema_u_name = EMA.make_name(instrument, target_generator_name=self.u_name, n=n)
        self.ema_d_name = EMA.make_name(instrument, target_generator_name=self.d_name, n=n)

    def next(self, candle: Candle):
        ema_u = self.general_pool.get_generator(self.ema_u_name, self.instrument)
        ema_d = self.general_pool.get_generator(self.ema_d_name, self.instrument)

        result = ema_u.value() / ema_d.value() if ema_d.value() != 0 else 1

        self.resultDeque.append(result)
