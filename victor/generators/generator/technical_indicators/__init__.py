from typing import Optional

from victor.exchange.types import Candle, Instrument
from victor.generators.generator import Generator


class TechnicalIndicator(Generator[Candle, float]):
    def __init__(self, name: str, instrument: Instrument, limit: Optional[int]):
        Generator.__init__(self, name=name, instrument=instrument, limit=limit)

    def next(self, candle: Candle):
        pass


class ProbabilityIndicator(TechnicalIndicator):
    pass

