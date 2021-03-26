import unittest

from tests.environments.algorithm import RSIAlgorithmEnvironment
from tests.environments.exchange import TestExchange
from victor.algorithm.momentum.breakout import BreakoutProbabilityAlgorithm
from victor.config import TEST_INSTRUMENT
from victor.exchange.types import Timeframe, Candle
from victor.algorithm.momentum import RSIProbabilityAlgorithm
from victor.generators.generator_set import GeneratorSet
from victor.risk_management.classic import Classic


class RSIProbabilityAlgorithmTest(unittest.TestCase, RSIAlgorithmEnvironment, TestExchange):
    algorithm: RSIProbabilityAlgorithm
    generator_set: GeneratorSet

    def setUp(self) -> None:
        RSIAlgorithmEnvironment.__init__(self)
        TestExchange.__init__(self)

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


class BreakoutProbabilityAlgorithmTest(unittest.TestCase, TestExchange):
    def setUp(self) -> None:
        TestExchange.__init__(self)

        self.risk_management = Classic(stop_loss=30, take_profit=60, v0=1, instrument=TEST_INSTRUMENT)
        self.algorithm = BreakoutProbabilityAlgorithm(risk_management=self.risk_management, instrument=TEST_INSTRUMENT,
                                                      n=5, m=2)

    def test_name(self):
        self.assertEqual(self.algorithm.name, BreakoutProbabilityAlgorithm.make_name(TEST_INSTRUMENT, 5, 2))
