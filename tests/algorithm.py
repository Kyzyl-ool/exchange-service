import unittest

from tests.environments.exchange import TestExchange
from victor.algorithm.momentum.RSI import RSIProbabilityAlgorithm
from victor.algorithm.momentum.bar_rotation import BarRotationAlgorithm
from victor.algorithm.momentum.breakout import BreakoutProbabilityAlgorithm
from victor.algorithm.momentum.complex.main import MainAlgorithm
from victor.config import TEST_INSTRUMENT, TEST_INSTRUMENT_ID
from victor.exchange.types import Timeframe, Candle
from victor.generators.generator.candle.heiken_ashi import HeikenAshi
from victor.generators.generator.patterns.bar_rotation import BarRotationGenerator
from victor.generators.generator.technical_indicators.momentum import RSI
from victor.risk_management.classic import Classic


class RSIProbabilityAlgorithmTest(unittest.TestCase, TestExchange):
    def setUp(self) -> None:
        TestExchange.__init__(self)

        self.risk_management = Classic(stop_loss=30, take_profit=60, v0=1, instrument=TEST_INSTRUMENT)
        self.algorithm = RSIProbabilityAlgorithm(lower_bound=10, upper_bound=90, risk_management=self.risk_management,
                                                 instrument=TEST_INSTRUMENT, rsi_n=14)

    def test_probability(self):
        def handler(candle: Candle):
            self.algorithm.general_pool.update_generators(candle)
            self.exchange.update(candle)

            p = self.algorithm.probability()
            rsi = self.algorithm.general_pool.get_generator(RSI.make_name(TEST_INSTRUMENT)).value()

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

    def test_logic(self):
        def handler(candle: Candle):
            self.exchange.update(candle)
            self.algorithm.general_pool.update_generators(candle)

        self.exchange.ohlc_subscribe(self.algorithm.instrument['id'], Timeframe.M1, handler)


class BarRotationAlgorithmTest(unittest.TestCase, TestExchange):
    def setUp(self) -> None:
        TestExchange.__init__(self)

        self.risk_management = Classic(stop_loss=30, take_profit=60, v0=1, instrument=TEST_INSTRUMENT)
        self.algorithm = BarRotationAlgorithm(risk_management=self.risk_management, instrument=TEST_INSTRUMENT,
                                              short=False)
        self.heiken_ashi = self.algorithm.general_pool.get_generator(HeikenAshi.make_name(TEST_INSTRUMENT))
        self.bar_rotation = self.algorithm.general_pool.get_generator(BarRotationGenerator.make_name(TEST_INSTRUMENT, short=False))

    def test_name(self):
        self.assertEqual(self.algorithm.name, BarRotationAlgorithm.make_name(TEST_INSTRUMENT))

    def test_logic(self):
        TestExchange.__init__(self)

        def handler(candle: Candle):
            self.algorithm.general_pool.update_generators(candle)
            self.exchange.update(candle)

            if len(self.heiken_ashi.resultDeque) > 2:
                previous_sign = self.heiken_ashi.resultDeque[-2]['close'] - self.heiken_ashi.resultDeque[-2]['open']
                current_sign = self.heiken_ashi.resultDeque[-1]['close'] - self.heiken_ashi.resultDeque[-1]['open']
                bar_rotation_value = self.bar_rotation.value()
                if bar_rotation_value > 0:
                    self.assertTrue(previous_sign*current_sign <= 0)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)


class MainAlgorithmTest(unittest.TestCase, TestExchange):
    def setUp(self) -> None:
        TestExchange.__init__(self)
        self.risk_management = Classic(stop_loss=30, take_profit=60, v0=1, instrument=TEST_INSTRUMENT)
        self.algorithm = MainAlgorithm(self.instrument, self.risk_management)

    def test_name(self):
        self.assertEqual(self.algorithm.name, MainAlgorithm.make_name(self.instrument))

    def test_logic(self):
        TestExchange.__init__(self)

        def handler(candle: Candle):
            self.algorithm.general_pool.update_generators(candle)
            self.exchange.update(candle)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

