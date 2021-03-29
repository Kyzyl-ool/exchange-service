import logging
import unittest

from victor.algorithm.momentum.complex import MainAlgorithm
from victor.exchange.tinkoff import TinkoffExchangeClient
from victor.exchange.types import Timeframe, Candle, LimitOrderRequest, MarketOrderRequest, Instrument
from victor.generators.generator.filters.time_filter import Market
from victor.risk_management.momentum import MomentumRiskManagement
from victor.trader import Trader

logging.basicConfig(level=logging.DEBUG)


class TinkoffTest(unittest.IsolatedAsyncioTestCase):
    exchange: TinkoffExchangeClient = TinkoffExchangeClient()

    async def asyncSetUp(self) -> None:
        await self.exchange.init()

    async def asyncTearDown(self) -> None:
        await self.exchange.close_connections()

    async def test_subscribe(self):
        def handler(candle: Candle):
            print(candle)

        await self.exchange.ohlc_subscribe('BBG0013HGFT4', Timeframe.M1, handler)

    async def test_limit_order(self):
        order_id = await self.exchange.limit_order(LimitOrderRequest(
            volume=1,
            punct=0.01,
            price=75,
            id='BBG0013HGFT4',
            buy=True
        ))

        self.assertIsNotNone(order_id)
        self.assertIn(order_id, self.exchange.orders)

    @unittest.skip('market orders in sandbox does not work')
    async def test_market_order(self):
        order_id = await self.exchange.market_order(MarketOrderRequest(
            volume=1,
            punct=0.01,
            id='BBG0013HGFT4',
            buy=True
        ))

        self.assertIsNotNone(order_id)
        self.assertIn(order_id, self.exchange.orders)

    async def test_running(self):
        instrument = Instrument(
            punct=0.01,
            id='BBG004730RP0'
        )

        risk_management = MomentumRiskManagement(
            stop_loss=40,
            d=100,
            instrument=instrument,
            alpha=0.2,
            v0=10,
        )
        trader = Trader(
            algorithms=[
                MainAlgorithm(
                    instrument=instrument,
                    risk_management=risk_management,
                    market=Market.rus
                )
            ],
            exchange=self.exchange,
            max_orders=1
        )

        def handler(candle: Candle):
            trader.general_pool.update_generators(candle)
            trader.perform_signals(candle)
            logging.debug(candle)

        await self.exchange.ohlc_subscribe('BBG004730RP0', Timeframe.M5, handler)


