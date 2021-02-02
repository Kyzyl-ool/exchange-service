import unittest
from src.exchange_client.finam_test import FinamExchangeTestClient
from src.exchange_client.types import Timeframe, Candle


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.exchange = FinamExchangeTestClient()
        self.amount_of_calls = 0

    def testSBER2018(self):
        def handler(candle: Candle):
            self.amount_of_calls += 1

        self.exchange.ohlc_subscribe('../data/SBER_180101_181231.csv', Timeframe.M1, handler)

        self.assertEqual(self.amount_of_calls, len(self.exchange.df))


if __name__ == '__main__':
    unittest.main()
