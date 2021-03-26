from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator


class EMA(TechnicalIndicator):
    N: int
    target_generator_name: str

    def __init__(self, n: int, target_generator_name: str, instrument: Instrument, limit: int):
        """
        Гарантируется, что target_generator_name существует в общем пуле генераторов
        """
        generator_name = EMA.make_name(instrument, target_generator_name=target_generator_name, n=n)

        TechnicalIndicator.__init__(self, name=generator_name, instrument=instrument, limit=limit)

        self.N = n
        self.target_generator_name = target_generator_name

    def next(self, candle: Candle):
        current_value = self.general_pool.get_generator(self.target_generator_name).value()
        previous_value = self.resultDeque[-1] if len(self.resultDeque) > 0 else 0

        k = 2 / (self.N + 1)

        result = current_value * k + previous_value * (1 - k)

        self.resultDeque.append(result)
