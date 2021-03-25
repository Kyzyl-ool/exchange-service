from tests.environments.exchange import TestExchange
from victor.exchange.types import Candle
from victor.generators.generator.technical_indicators.average import EMA
from victor.generators.generator.technical_indicators.momentum import RSI, RS
from victor.generators.generator.technical_indicators.price import U, D

N = 14


class RSIEnvironment(TestExchange):
    rsi: RSI
    rs: RS
    ema_u: EMA
    ema_d: EMA
    u: U
    d: D

    def __init__(self):
        TestExchange.__init__(self)

        self.u = U()
        self.d = D()

        self.ema_u = EMA(N, lambda x: self.u.value(), name='EMA_U')
        self.ema_d = EMA(N, lambda x: self.d.value(), name='EMA_D')

        self.rs = RS(self.ema_u, self.ema_d)
        self.rsi = RSI(self.rs)

    def next_candle(self, candle: Candle):
        self.d.next(candle)
        self.u.next(candle)
        self.ema_u.next(candle)
        self.ema_d.next(candle)
        self.rs.next(candle)
        self.rsi.next(candle)
