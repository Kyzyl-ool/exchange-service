import logging
import unittest

from victor.exchange.tinkoff import TinkoffExchangeClient
from victor.exchange.types import Timeframe, Candle, LimitOrderRequest, MarketOrderRequest

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
