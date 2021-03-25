import unittest

from tests.environments.algorithm import RSIAlgorithmEnvironment
from victor.exchange.finam_test import FinamExchangeTestClient
from victor.exchange.types import Timeframe, Candle
from victor.generators import GeneratorSet
from victor.algorithm.momentum import RSIProbabilityAlgorithm


class RSIProbabilityAlgorithmTest(unittest.TestCase, RSIAlgorithmEnvironment):
    algorithm: RSIProbabilityAlgorithm
    generator_set: GeneratorSet
    exchange: FinamExchangeTestClient

    def setUp(self) -> None:
        RSIAlgorithmEnvironment.__init__(self)

        self.exchange = FinamExchangeTestClient()

    def test_probability(self):
        def handler(candle: Candle):
            self.next_candle(candle)
            p = self.algorithm.probability()
            rsi = self.rsi.value()

            if rsi < self.algorithm.lower_bound:
                self.assertEqual(p, 1)
            elif rsi > self.algorithm.upper_bound:
                self.assertEqual(p, -1)
            else:
                self.assertGreaterEqual(p, -1)
                self.assertLessEqual(p, 1)

        self.exchange.ohlc_subscribe(self.algorithm.instrument['id'], Timeframe.M1, handler)
