import unittest

from victor.exchange.types import LimitOrderRequest, MarketOrderRequest, Timeframe
from victor.exchange.abstract import AbstractExchangeClient


class AbstractExchange(unittest.TestCase):
    limit_order: LimitOrderRequest

    def setUp(self) -> None:
        self.exchange = AbstractExchangeClient()

        self.order_id = '1'
        self.instrument_id = '123'
        self.timeframe = Timeframe.M1
        self.handler = lambda x: None
        self.limit_order = LimitOrderRequest(buy=True, id=self.order_id, price=100, punct=0.01, volume=1000)
        self.market_order = MarketOrderRequest(buy=True, id=self.order_id, punct=0.01, volume=1000)

    def test_check_methods(self):
        self.assertRaises(NotImplementedError, self.exchange.limit_order, self.limit_order)
        self.assertRaises(NotImplementedError, self.exchange.market_order, self.market_order)
        self.assertRaises(NotImplementedError, self.exchange.cancel_order, self.order_id)
        self.assertRaises(NotImplementedError, self.exchange.ohlc_subscribe, self.order_id, self.instrument_id, self.handler)
