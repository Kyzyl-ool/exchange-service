from victor.config import TEST_INSTRUMENT_ID, TEST_PUNCT
from victor.exchange.finam_test import FinamExchangeTestClient
from victor.exchange.types import Instrument


class TestExchange:
    exchange: FinamExchangeTestClient
    instrument: Instrument

    def __init__(self):
        self.exchange = FinamExchangeTestClient()
        self.instrument = Instrument(id=TEST_INSTRUMENT_ID, punct=TEST_PUNCT)

