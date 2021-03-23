from typing import Callable

from victor.exchange.types import Candle

from victor.generators.generator.technical_indicators import TechnicalIndicator


class EMA(TechnicalIndicator):
    N: int
    calculate_function: Callable[[Candle], float]

    def __init__(self, n: int, calculate_function: Callable[[Candle], float], **kwargs):
        super().__init__(**kwargs)

        assert n is not None
        assert calculate_function is not None

        self.N = n
        self.calculate_function = calculate_function

    def next(self, candle: Candle):
        current_value = self.calculate_function(candle)
        previous_value = self.resultDeque[-1] if len(self.resultDeque) > 0 else 0

        k = 2 / (self.N + 1)

        result = current_value * k + previous_value * (1 - k)

        self.resultDeque.append(result)