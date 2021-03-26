import unittest
from datetime import datetime, timedelta, time
from typing import List

from tests.environments.exchange import TestExchange
from victor.config import GENERATOR_MAX_DEQUE_LENGTH, TEST_INSTRUMENT
from victor.exchange.types import Candle, Timeframe
from victor.exchange.finam_test import FinamExchangeTestClient
from victor.generators.generator import Generator
from victor.generators.generator.candle.candle_aggregator import CandleAggregator

import numpy as np

from victor.generators.generator.candle.heiken_ashi import HeikenAshi
from victor.generators.generator.filters.time_filter import TimeFilter
from victor.generators.generator.patterns.bar_rotation import BarRotationGenerator
from victor.generators.generator.patterns.breakout import Breakout

TEST_INSTRUMENT_ID = '../data/TATN_210101_210131.csv'


class TechnicalIndicatorTest(unittest.TestCase):
    exchange: FinamExchangeTestClient

    def setUp(self) -> None:
        self.exchange = FinamExchangeTestClient()

    def test_not_implemented_methods(self):
        abstract_generator = Generator[float, float](name='some generator', instrument=TEST_INSTRUMENT)

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
    def setUp(self) -> None:
        TestExchange.__init__(self)
        self.candle_aggregator = CandleAggregator(instrument=TEST_INSTRUMENT, n=5)
        self.breakout = Breakout(instrument=TEST_INSTRUMENT, n=5, m=2)

    def test_breakout_name(self):
        self.assertEqual(self.breakout.name, Breakout.make_name(self.instrument, n=5, m=2))

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


class TimeFilterTest(unittest.TestCase, TestExchange):
    def setUp(self) -> None:
        self.from_time = time(10, 0, 0)
        self.to_time = time(13, 0, 0)
        self.time_filter = TimeFilter(self.from_time, self.to_time)

    def test_name(self):
        self.assertEqual(self.time_filter.name, 'time-filter')

    def test_logic(self):
        TestExchange.__init__(self)

        def handler(candle: Candle):
            self.time_filter.next(candle)

            condition = self.from_time <= candle['time'].time() <= self.to_time
            self.assertTrue(self.time_filter.value() == condition)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)
