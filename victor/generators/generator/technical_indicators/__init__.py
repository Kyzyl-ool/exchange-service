from victor.generators import Generator
from victor.exchange.types import Candle


class TechnicalIndicator(Generator[Candle, float]):
    punct: float

    def __init__(self, punct: float, **kwargs):
        super().__init__(**kwargs)
        self.punct = punct

    def next(self, candle: Candle):
        pass