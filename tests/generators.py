import unittest
from datetime import datetime, timedelta
from typing import List

from tests.environments.RSI import RSIEnvironment
from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.generators import Generator
from victor.exchange.types import Candle, Timeframe
from victor.exchange.finam_test import FinamExchangeTestClient
from victor.generators.generator.candle.candle_aggregator import CandleAggregator

import numpy as np

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


class CandleAggregatorTest(unittest.TestCase):
    candle_aggregator: CandleAggregator

    def setUp(self) -> None:
        pass

    def test_5_minutes(self):
        self.candle_aggregator = CandleAggregator(5)
        candles: List[Candle] = []

        for i, close in enumerate(np.linspace(10, 100, 101)):
            candles.append(Candle(
                close=close,
                volume=1,
                low=close - 0.1,
                high=close + 0.1,
                open=close,
                time=datetime.now() - timedelta(minutes=200 - i)
            ))

        for candle in candles:
            self.candle_aggregator.next(candle)

        for i in range(1, len(self.candle_aggregator.resultDeque)):
            self.assertTrue(
                abs(self.candle_aggregator.resultDeque[i]['time'] - self.candle_aggregator.resultDeque[i - 1]['time']),
                timedelta(seconds=1))
            self.assertAlmostEqual(self.candle_aggregator.resultDeque[i - 1]['open'], candles[(i - 1) * 5]['open'])
            self.assertAlmostEqual(self.candle_aggregator.resultDeque[i - 1]['low'], candles[(i - 1) * 5]['low'])
            self.assertAlmostEqual(self.candle_aggregator.resultDeque[i - 1]['close'], candles[i * 5 - 1]['close'])
            self.assertAlmostEqual(self.candle_aggregator.resultDeque[i - 1]['high'], candles[i * 5 - 1]['high'])
