import logging
import unittest
import numpy as np

from tests.environments.trader import TraderEnvironment
from victor.config import TEST_INSTRUMENT_ID
from victor.exchange.types import Candle, Timeframe

logging.basicConfig(level=logging.INFO)

np.random.seed(42)


class TraderTest(unittest.TestCase, TraderEnvironment):
    def setUp(self) -> None:
        TraderEnvironment.__init__(self)

    def test_trader(self):
        def handler(candle: Candle):
            self.trader.update(candle)
            self.trader.perform_signals(candle)
            self.trader.exchange.update(candle)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

        rsi_max = max(50,
                      max(self.trader.algorithms['rsi-algorithm'].generator_set.__generators['RSI'].resultDeque))
        rsi_min = min(50,
                      min(self.trader.algorithms['rsi-algorithm'].generator_set.__generators['RSI'].resultDeque))

        self.assertGreater(rsi_max, 50)
        self.assertLess(rsi_min, 50)

        for rule in self.trader.active_rules:
            order = rule.exit_force()
            self.exchange.market_order(order)

        logging.info(
            f'Финансовый результат по portfolio: {self.trader.exchange.portfolio.result()}, комиссия: ({self.trader.exchange.portfolio.getComission()})')
        logging.info(
            f'Финансовый результат по exchange: {self.trader.exchange.financial_result(self.exchange.last_candle)}')

        self.assertEqual(len(self.exchange.orders), len(self.exchange.portfolio.log))
