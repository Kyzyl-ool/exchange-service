import unittest

from victor.exchange.types import Candle, Timeframe
from victor.exchange.finam_test import FinamExchangeTestClient

from victor.generators.generator.technical_indicators.average import EMA
from victor.generators.generator.technical_indicators.momentum import RSI, RS
from victor.generators.generator.technical_indicators.price import U, D

from config import GENERATOR_MAX_DEQUE_LENGTH

N = 14
INSTRUMENT_ID = '../data/TATN_210101_210131.csv'
PUNCT = 0.1


def get_close(candle: Candle):
    return candle['close']


class TechnicalIndicatorTest(unittest.TestCase):
    rsi: RSI
    rs: RS
    ema_u: EMA
    ema_d: EMA
    u: U
    d: D

    def setUp(self) -> None:
        self.u = U()
        self.d = D()

        self.ema_u = EMA(N, lambda x: self.u.value(), name='EMA_U')
        self.ema_d = EMA(N, lambda x: self.d.value(), name='EMA_D')

        self.rs = RS(self.ema_u, self.ema_d)
        self.rsi = RSI(self.rs)

        self.exchange = FinamExchangeTestClient()

    def test_rsi(self):
        def next_candle(candle: Candle):
            self.d.next(candle)
            self.u.next(candle)
            self.ema_u.next(candle)
            self.ema_d.next(candle)
            self.rs.next(candle)
            self.rsi.next(candle)

        def handler(candle: Candle):
            next_candle(candle)

        self.exchange.ohlc_subscribe(INSTRUMENT_ID, Timeframe.M1, handler)

        self.assertEqual(len(self.rsi.resultDeque), GENERATOR_MAX_DEQUE_LENGTH)
        self.assertTrue(all(map(lambda x: 0 <= x <= 100, self.rsi.resultDeque)))
