from victor.exchange.types import Candle

from victor.generators.generator.technical_indicators import TechnicalIndicator


class EMA(TechnicalIndicator):
    N: int
    target_generator_name: str

    def __init__(self, n: int, target_generator: TechnicalIndicator, **kwargs):
        super().__init__(**kwargs)

        assert n is not None
        assert target_generator is not None

        self.N = n

        self.add_dependency(target_generator)
        self.target_generator_name = target_generator.name

    def next(self, candle: Candle):
        current_value = self.dependencies[self.target_generator_name].value()
        previous_value = self.resultDeque[-1] if len(self.resultDeque) > 0 else 0

        k = 2 / (self.N + 1)

        result = current_value * k + previous_value * (1 - k)

        self.resultDeque.append(result)
