from tests.environments.exchange import TestExchange
from victor.generators.generator.technical_indicators.average import EMA
from victor.generators.generator.technical_indicators.momentum import RSI, RS
from victor.generators.generator.technical_indicators.price import U, D
from victor.generators.generator_family import GeneratorFamily
from victor.generators.generator_set import GeneratorSet

N = 14


class RSIEnvironment(TestExchange):
    generator_family: GeneratorFamily

    def __init__(self):
        TestExchange.__init__(self)

        u = U()
        d = D()

        ema_u = EMA(N, u, name='EMA_U')
        ema_d = EMA(N, d, name='EMA_D')

        rs = RS(ema_u, ema_d)
        rsi = RSI(rs)

        generator_set = GeneratorSet([rsi], "only-rsi")
        self.generator_family = GeneratorFamily([generator_set])

