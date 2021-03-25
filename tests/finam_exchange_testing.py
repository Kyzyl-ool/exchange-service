import unittest

from victor.config import TEST_INSTRUMENT_ID, TEST_PUNCT
from victor.exchange.finam_test import FinamExchangeTestClient
from victor.exchange.types import Timeframe, Candle, LimitOrderRequest, MarketOrderRequest


class SimpleCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.exchange = FinamExchangeTestClient()
        self.amount_of_calls = 0
        self.maximum = 0

    def test_handler_calls(self):
        self.maximum = 0

        def handler(candle: Candle):
            self.amount_of_calls += 1
            self.maximum = max(candle['close'], self.maximum)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

        self.assertEqual(self.amount_of_calls, len(self.exchange.df))
        self.assertAlmostEqual(self.maximum, self.exchange.df['<CLOSE>'].max(), delta=0.1)


class CheckOrders(unittest.TestCase):
    exchange: FinamExchangeTestClient

    def setUp(self) -> None:
        self.exchange = FinamExchangeTestClient()
        self.counter = 0

    def test_market_order(self):
        def handler(candle: Candle):
            self.counter += 1
            if self.counter == 10000:
                self.exchange.market_order({
                    'id': TEST_INSTRUMENT_ID,
                    'punct': TEST_PUNCT,
                    'buy': True,
                    'volume': 1
                })

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)
        self.exchange.market_order({
            'id': TEST_INSTRUMENT_ID,
            'punct': TEST_PUNCT,
            'buy': False,
            'volume': 1
        })
        self.assertEqual(len(self.exchange.portfolio.log), 2)
        self.assertEqual(self.exchange.portfolio.log[1]['p'], self.exchange.df['<CLOSE>'].values[-1])

    def test_limit_order(self):
        def handler(candle: Candle):
            self.counter += 1

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)
        self.exchange.limit_order({
            'id': TEST_INSTRUMENT_ID,
            'punct': TEST_PUNCT,
            'price': self.exchange.df['<CLOSE>'].values[-1],
            'buy': False,
            'volume': 1
        })
        self.assertEqual(len(self.exchange.portfolio.log), 1)
        self.assertEqual(self.exchange.portfolio.log[-1]['p'], self.exchange.df['<CLOSE>'].values[-1])

    def test_cancel_order(self):
        def handler(candle: Candle):
            pass

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

        order_id = self.exchange.limit_order(LimitOrderRequest(
            volume=1,
            price=100,
            buy=True,
            id=TEST_INSTRUMENT_ID,
            punct=TEST_PUNCT
        ))

        self.assertEqual(len(self.exchange.orders), 1)
        self.assertEqual(len(self.exchange.active_orders), 1)

        self.exchange.cancel_order(order_id)

        self.assertEqual(len(self.exchange.orders), 1)
        self.assertEqual(len(self.exchange.active_orders), 0)

    def test_financial_result(self):
        bought = []

        def handler(candle: Candle):
            self.counter += 1
            if not self.counter % 1000:
                price = candle['close']
                self.exchange.limit_order(LimitOrderRequest(
                    volume=1,
                    price=price,
                    buy=True,
                    id=TEST_INSTRUMENT_ID,
                    punct=TEST_PUNCT
                ))

                bought.append(price)
            self.exchange.update(candle)

        self.exchange.ohlc_subscribe(TEST_INSTRUMENT_ID, Timeframe.M1, handler)

        self.exchange.market_order(MarketOrderRequest(
            volume=len(bought),
            punct=TEST_PUNCT,
            id=TEST_INSTRUMENT_ID,
            buy=False,
        ))
        self.exchange.update(self.exchange.last_candle)

        fin_res, comission = self.exchange.financial_result(self.exchange.last_candle)

        last_price = self.exchange.last_candle['close']

        fin_res_2 = last_price * len(bought) - sum(bought)

        # self.assertAlmostEqual(last_price, self.exchange.)
        self.assertAlmostEqual(fin_res + comission, fin_res_2, delta=0.1)
