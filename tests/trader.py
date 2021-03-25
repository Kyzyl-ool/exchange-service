import logging
import unittest

from tests.environments.trader import TraderEnvironment
from victor.config import TEST_INSTRUMENT_ID
from victor.exchange.types import Candle, Timeframe

logging.basicConfig(level=logging.INFO)


class TraderTest(unittest.TestCase, TraderEnvironment):
    def setUp(self) -> None:
        TraderEnvironment.__init__(self)

    def test_trader(self):

        def handler(candle: Candle):
            self.trader.update(candle)
            self.trader.perform_signals(candle)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

        rsi_max = max(50,
                        max(self.trader.algorithms['rsi-algorithm'].generator_set.generators['RSI'].resultDeque))
        rsi_min = min(50,
                        min(self.trader.algorithms['rsi-algorithm'].generator_set.generators['RSI'].resultDeque))

        self.assertGreater(rsi_max, 50)
        self.assertLess(rsi_min, 50)

        for rule in self.trader.active_rules:
            order = rule.exit_force()
            self.exchange.market_order(order)

        logging.info(f'Финансовый результат: {self.trader.exchange.portfolio.result()}')



