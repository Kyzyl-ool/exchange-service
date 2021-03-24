import unittest

from tests.environments.RSI import RSIEnvironment
from victor.exchange.finam_test import FinamExchangeTestClient
from victor.exchange.types import Timeframe, Candle
from victor.generators import GeneratorSet
from victor.algorithm.momentum import RSIProbabilityAlgorithm

N = 14
INSTRUMENT_ID = '../data/TATN_210101_210131.csv'
PUNCT = 0.1

LOWER_BOUND = 10
UPPER_BOUND = 90


class RSIProbabilityAlgorithmTest(unittest.TestCase, RSIEnvironment):
    algorithm: RSIProbabilityAlgorithm
    generator_set: GeneratorSet
    exchange: FinamExchangeTestClient

    def setUp(self) -> None:
        RSIEnvironment.setUp(self)

        self.generator_set = GeneratorSet([self.rsi], "Only RSI")
        self.algorithm = RSIProbabilityAlgorithm(self.generator_set, LOWER_BOUND, UPPER_BOUND)
        self.exchange = FinamExchangeTestClient()

    def test_probability(self):
        def handler(candle: Candle):
            self.next_candle(candle)
            p = self.algorithm.probability()
            rsi = self.rsi.value()

            if rsi < LOWER_BOUND:
                self.assertEqual(p, 1)
            elif rsi > UPPER_BOUND:
                self.assertEqual(p, -1)
            else:
                self.assertGreaterEqual(p, -1)
                self.assertLessEqual(p, 1)

        self.exchange.ohlc_subscribe(INSTRUMENT_ID, Timeframe.M1, handler)
