from victor.config import TEST_INSTRUMENT_ID, TEST_PUNCT
from victor.exchange.types import Instrument


class HistoricData:
    instrument: Instrument

    def __init__(self):
        self.instrument = Instrument(id=TEST_INSTRUMENT_ID, punct=TEST_PUNCT)
