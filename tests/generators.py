import unittest
from datetime import datetime, timedelta
from typing import List

from tests.environments.RSI import RSIEnvironment
from tests.environments.exchange import TestExchange
from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.generators import Generator
from victor.exchange.types import Candle, Timeframe
from victor.exchange.finam_test import FinamExchangeTestClient
from victor.generators.generator.candle.candle_aggregator import CandleAggregator

import numpy as np

from victor.generators.generator.patterns.breakout import Breakout

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


class BreakoutTest(unittest.TestCase, TestExchange):
    breakout: Breakout
    candle_aggregator: CandleAggregator

    def setUp(self) -> None:
        self.candle_aggregator = CandleAggregator(5)
        self.breakout = Breakout(n=5, m=2, punct=0.01, candle_aggregator=self.candle_aggregator)

    def test_breakout_name(self):
        self.assertEqual(self.breakout.name, 'breakout-up')

    def test_breakout_next(self):
        TestExchange.__init__(self)

        def handler(candle: Candle):
            self.breakout.next(candle)

            for broken_level in self.breakout.broken_levels:
                self.assertGreaterEqual(candle['close'], broken_level['d2'])
                self.assertGreater(self.breakout.value(), 0)
                # self.assertEqual(broken_level['i'], self.exchange.current_index)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

        for level in self.breakout.levels:
            i = level['i']
            self.assertTrue(abs(level['time'] - self.exchange.df.iloc[i]['<DATETIME>']), timedelta(seconds=1))
        pass