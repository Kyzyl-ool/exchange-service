import unittest
from service.exchange.finam_test import FinamExchangeTestClient
from service.exchange.types import Timeframe, Candle

INSTRUMENT_ID = '../data/TATN_210101_210131.csv'
PUNCT = 0.1


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

        self.exchange.ohlc_subscribe(INSTRUMENT_ID, Timeframe.M1, handler)

        self.assertEqual(self.amount_of_calls, len(self.exchange.df))
        self.assertAlmostEqual(self.maximum, self.exchange.df['<CLOSE>'].max(), delta=0.1)


class CheckOrders(unittest.TestCase):
    def setUp(self) -> None:
        self.exchange = FinamExchangeTestClient()
        self.counter = 0

    def test(self):
        def handler(candle: Candle):
            self.counter += 1
            if self.counter == 10000:
                self.exchange.market_order({
                    'id': INSTRUMENT_ID,
                    'punct': PUNCT,
                    'buy': True,
                    'volume': 1
                })
        self.exchange.ohlc_subscribe(INSTRUMENT_ID, Timeframe.M1, handler)
        self.exchange.market_order({
            'id': INSTRUMENT_ID,
            'punct': PUNCT,
            'buy': False,
            'volume': 1
        })
        self.assertEqual(len(self.exchange.portfolio.log), 2)
        self.assertEqual(self.exchange.portfolio.log[1]['p'], self.exchange.df['<CLOSE>'].values[-1])


if __name__ == '__main__':
    unittest.main()
