import unittest

from tests.environments.trader import TraderEnvironment
from victor.config import TEST_INSTRUMENT_ID
from victor.exchange.types import Candle, Timeframe

LOWER_BOUND = 10
UPPER_BOUND = 90


class TraderTest(unittest.TestCase, TraderEnvironment):
    def setUp(self) -> None:
        TraderEnvironment.__init__(self)

    def test_trader(self):
        def handler(candle: Candle):
            self.trader.update(candle)
            self.trader.perform_signals(candle)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)
