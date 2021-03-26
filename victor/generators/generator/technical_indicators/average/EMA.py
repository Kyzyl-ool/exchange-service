from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator

EMA_BASE_NAME = 'ema'


class EMA(TechnicalIndicator):
    N: int
    target_generator_name: str

    @staticmethod
    def make_name(target_generator_name: str, n: int) -> str:
        return f'{EMA_BASE_NAME}({target_generator_name}, {n})'

    def __init__(self, n: int, target_generator_name: str, punct: float, instrument: Instrument, limit: int):
        """
        Гарантируется, что target_generator_name существует в общем пуле генераторов
        """
        generator_name = self.make_name(target_generator_name, n)

        TechnicalIndicator.__init__(self, punct=punct, name=generator_name, instrument=instrument, limit=limit)

        self.N = n
        self.target_generator_name = target_generator_name

    def next(self, candle: Candle):
        current_value = self.general_pool.get_generator(self.target_generator_name, self.instrument).value()
        previous_value = self.resultDeque[-1] if len(self.resultDeque) > 0 else 0

        k = 2 / (self.N + 1)

        result = current_value * k + previous_value * (1 - k)

        self.resultDeque.append(result)
