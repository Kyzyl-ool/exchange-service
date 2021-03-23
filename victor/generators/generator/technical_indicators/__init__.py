from victor.generators import Generator
from victor.exchange.types import Candle


class TechnicalIndicator(Generator[Candle]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def next(self, candle: Candle):
        pass