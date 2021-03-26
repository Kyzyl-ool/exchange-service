from victor.generators import Generator
from victor.exchange.types import Candle, Instrument


class TechnicalIndicator(Generator[Candle, float]):
    punct: float

    def __init__(self, punct: float, name: str, instrument: Instrument, limit: int):
        Generator.__init__(self, name=name, instrument=instrument, limit=limit)
        self.punct = punct

    def next(self, candle: Candle):
        pass
