import logging
import unittest

import numpy as np

from tests.environments.exchange import TestExchange
from victor.algorithm.momentum.RSI import RSIProbabilityAlgorithm
from victor.algorithm.momentum.complex.main import MainAlgorithm
from victor.config import TEST_INSTRUMENT_ID, TEST_INSTRUMENT
from victor.exchange.types import Candle, Timeframe, MarketOrderRequest
from victor.generators.generator.technical_indicators.momentum import RSI
from victor.risk_management.classic import Classic
from victor.trader import Trader

logging.basicConfig(level=logging.INFO)

np.random.seed(42)


class TraderTest(unittest.TestCase, TestExchange):
    def setUp(self) -> None:
        TestExchange.__init__(self)
        self.risk_management = Classic(stop_loss=30, take_profit=60, instrument=TEST_INSTRUMENT, v0=1)
        self.short = False

    def test_trader(self):
        self.trader = Trader(
            algorithms=[
                RSIProbabilityAlgorithm(
                    instrument=TEST_INSTRUMENT,
                    risk_management=self.risk_management,
                    rsi_n=14,
                    lower_bound=10,
                    upper_bound=90
                )
                # BarRotationAlgorithm(instrument=TEST_INSTRUMENT, risk_management=self.risk_management,
                #                      short=self.short),
                # BreakoutProbabilityAlgorithm(instrument=TEST_INSTRUMENT, risk_management=self.risk_management, n=5,
                #                              m=2),
                # OnlyMarketOpeningAlgorithm(instrument=TEST_INSTRUMENT, risk_management=self.risk_management,
                #                            market=Market.rus, first_n_hours=1)
            ],
            exchange=self.exchange,
            max_orders=1
        )

        def handler(candle: Candle):
            self.trader.general_pool.update_generators(candle)
            self.trader.exchange.update(candle)
            self.trader.perform_signals(candle)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

        trader = self.trader.get_algorithm(RSIProbabilityAlgorithm, self.instrument)
        rsi_generator = trader.general_pool.select_generator(RSI, self.instrument)

        rsi_max = max(50, max(rsi_generator.resultDeque))
        rsi_min = min(50, min(rsi_generator.resultDeque))

        self.assertGreater(rsi_max, 50)
        self.assertLess(rsi_min, 50)

        self.exchange.market_order(MarketOrderRequest(
            punct=TEST_INSTRUMENT['punct'],
            volume=abs(self.exchange.portfolio.V),
            buy=self.exchange.portfolio.V < 0,
            id=TEST_INSTRUMENT['id'],
        ))

        self.trader.exchange.update(self.exchange.last_candle)

        logging.info(
            f'Финансовый результат по portfolio: {self.trader.exchange.portfolio.result()}, комиссия: ({self.trader.exchange.portfolio.getComission()})')
        logging.info(
            f'Финансовый результат по exchange: {self.trader.exchange.financial_result(self.exchange.last_candle)}')

        self.assertEqual(len(self.exchange.orders)-len(self.exchange.active_orders), len(self.exchange.portfolio.log))

    def test_trader_with_main_algorithm(self):
        self.trader = Trader(
            algorithms=[
                MainAlgorithm(
                    instrument=TEST_INSTRUMENT,
                    risk_management=self.risk_management,
                )
                # BarRotationAlgorithm(instrument=TEST_INSTRUMENT, risk_management=self.risk_management,
                #                      short=self.short),
                # BreakoutProbabilityAlgorithm(instrument=TEST_INSTRUMENT, risk_management=self.risk_management, n=5,
                #                              m=2),
                # OnlyMarketOpeningAlgorithm(instrument=TEST_INSTRUMENT, risk_management=self.risk_management,
                #                            market=Market.rus, first_n_hours=1)
            ],
            exchange=self.exchange,
            max_orders=1
        )

        def handler(candle: Candle):
            self.trader.general_pool.update_generators(candle)
            self.trader.exchange.update(candle)
            self.trader.perform_signals(candle)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

        self.exchange.market_order(MarketOrderRequest(
            punct=TEST_INSTRUMENT['punct'],
            volume=abs(self.exchange.portfolio.V),
            buy=self.exchange.portfolio.V < 0,
            id=TEST_INSTRUMENT['id'],
        ))

        self.trader.exchange.update(self.exchange.last_candle)

        logging.info(
            f'Финансовый результат по portfolio: {self.trader.exchange.portfolio.result()}, комиссия: ({self.trader.exchange.portfolio.getComission()})')
        logging.info(
            f'Финансовый результат по exchange: {self.trader.exchange.financial_result(self.exchange.last_candle)}')

        self.assertEqual(len(self.exchange.orders) - len(self.exchange.active_orders), len(self.exchange.portfolio.log))


