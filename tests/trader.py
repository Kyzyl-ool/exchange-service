import unittest

from tests.environments.RSI import RSIEnvironment
from victor.algorithm.momentum import RSIProbabilityAlgorithm
from victor.config import TEST_INSTRUMENT_ID
from victor.exchange.finam_test import FinamExchangeTestClient
from victor.exchange.types import Candle, Timeframe
from victor.generators import GeneratorSet, GeneratorFamily
from victor.trader import Trader

LOWER_BOUND = 10
UPPER_BOUND = 90
EXCHANGE_SERVICE_HOST = 'http://localhost:3000'


class TraderTest(unittest.TestCase, RSIEnvironment):
    algorithm: RSIProbabilityAlgorithm
    generator_set: GeneratorSet
    generator_family: GeneratorFamily
    exchange: FinamExchangeTestClient
    trader: Trader

    def setUp(self) -> None:
        RSIEnvironment.setUp(self)

        self.generator_set = GeneratorSet([self.rsi], "Only RSI")
        self.algorithm = RSIProbabilityAlgorithm(self.generator_set, LOWER_BOUND, UPPER_BOUND)
        self.exchange = FinamExchangeTestClient()
        self.generator_family = GeneratorFamily([self.generator_set])
        self.trader = Trader(self.generator_family, EXCHANGE_SERVICE_HOST, [self.algorithm])

    def test_trader(self):
        def handler(candle: Candle):
            self.trader.update(candle)
            self.trader.perform_signals(candle)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)