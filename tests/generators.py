import unittest

from tests.environments.RSI import RSIEnvironment
from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.generators import Generator
from victor.exchange.types import Candle, Timeframe
from victor.exchange.finam_test import FinamExchangeTestClient


TEST_INSTRUMENT_ID = '../data/TATN_210101_210131.csv'


class TechnicalIndicatorTest(unittest.TestCase, RSIEnvironment):
    exchange: FinamExchangeTestClient

    def setUp(self) -> None:
        RSIEnvironment.__init__(self)

        self.exchange = FinamExchangeTestClient()

    def test_rsi(self):
        def handler(candle: Candle):
            self.d.next(candle)
            self.u.next(candle)
            self.ema_u.next(candle)
            self.ema_d.next(candle)
            self.rs.next(candle)
            self.rsi.next(candle)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

        self.assertEqual(len(self.rsi.resultDeque), GENERATOR_MAX_DEQUE_LENGTH)
        self.assertTrue(all(map(lambda x: 0 <= x <= 100, self.rsi.resultDeque)))

    def test_not_implemented_methods(self):
        abstract_generator = Generator[float](name='some generator')

        self.assertRaises(NotImplementedError, abstract_generator.next, 1)
