import unittest
from src.exchange_client.finam_test import FinamExchangeTestClient
from src.exchange_client.types import Timeframe


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.exchange = FinamExchangeTestClient()
        self.amount_of_calls = 0

    def test_handler_calls(self):
        def handler():
            self.amount_of_calls += 1

        self.exchange.ohlc_subscribe('../data/TATN_210101_210131.csv', Timeframe.M1, handler)

        self.assertEqual(self.amount_of_calls, len(self.exchange.df))


if __name__ == '__main__':
    unittest.main()
