import unittest

from victor.exchange.tinkoff import TinkoffExchangeClient
from victor.exchange.types import Timeframe, Candle


class TinkoffTest(unittest.IsolatedAsyncioTestCase):
    exchange: TinkoffExchangeClient = TinkoffExchangeClient()

    def setUp(self) -> None:
        pass

    async def test_subscribe(self):
        def handler(candle: Candle):
            print(candle)

        await self.exchange.ohlc_subscribe('BBG0013HGFT4', Timeframe.M1, handler)

    def tearDown(self) -> None:
        self.exchange.close_connections()
