from typing import Optional, Union

from victor.exchange.types import Candle, Instrument
from victor.generators.generator import Generator


class TechnicalIndicator(Generator[Candle, float]):
    def __init__(self, name: str, instrument: Instrument, limit: Optional[int], fr: float):
        Generator.__init__(self, name=name, instrument=instrument, limit=limit)

        self.fr = fr
        self.__value = 0

    def _apply_new_value(self, value: float):
        self.__value *= self.fr
        self.__value += value

        self.resultDeque.append(self.__value)

    def next(self, value: Candle):
        pass

    def value(self) -> Union[float, None]:
        return self.__value


class ProbabilityIndicator(TechnicalIndicator):
    pass
