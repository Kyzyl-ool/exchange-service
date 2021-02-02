import unittest
from src.exchange.finam_test import FinamExchangeTestClient
from src.exchange.types import Timeframe, Candle


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.exchange = FinamExchangeTestClient()
        self.amount_of_calls = 0
        self.maximum = 0

    def test_handler_calls(self):
        self.maximum = 0

        def handler(candle: Candle):
            self.amount_of_calls += 1
            self.maximum = max(candle['close'], self.maximum)

        self.exchange.ohlc_subscribe('../data/TATN_210101_210131.csv', Timeframe.M1, handler)

        self.assertEqual(self.amount_of_calls, len(self.exchange.df))
        self.assertAlmostEqual(self.maximum, self.exchange.df['<CLOSE>'].max(), delta=0.1)


if __name__ == '__main__':
    unittest.main()
