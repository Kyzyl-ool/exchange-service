from victor.exchange.finam_test import FinamExchangeTestClient
from victor.exchange.types import Instrument

host = '0.0.0.0'
port = 9999

TEST_EXCHANGE_SERVICE_HOST = 'http://localhost:3000'
TEST_INSTRUMENT_ID = '../data/TATN_210101_210131.csv'
TEST_PUNCT = 0.01
TINKOFF_SANDBOX_TOKEN = 'TINKOFF_SANDBOX_TOKEN'
TINKOFF_TOKEN = 'TINKOFF_TOKEN'
TEST_INSTRUMENT = Instrument(id=TEST_INSTRUMENT_ID, punct=TEST_PUNCT)

GENERATOR_MAX_DEQUE_LENGTH = 30

backtesting = {
    'finam': {
        'exchange': FinamExchangeTestClient,
        'instruments': {
            'id': TEST_INSTRUMENT_ID
        }
    }
}



