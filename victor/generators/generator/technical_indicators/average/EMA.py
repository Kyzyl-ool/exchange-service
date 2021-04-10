from typing import Optional, Union, Callable

from victor.exchange.types import Candle, Instrument

from victor.generators.generator.technical_indicators import TechnicalIndicator


class EMA(TechnicalIndicator):
    N: int
    target_generator_name: str

    correct: bool
    __n_calls: int

    def __init__(self, n: int, target_generator_name: Optional[str], instrument: Instrument, limit: int,
                 use_candle=None):
        """
        Гарантируется, что target_generator_name существует в общем пуле генераторов
        """
        generator_name = EMA.make_name(instrument, target_generator_name=target_generator_name, n=n,
                                       use_candle=use_candle)

        TechnicalIndicator.__init__(self, name=generator_name, instrument=instrument, limit=limit, fr=0)

        self.N = n
        self.correct = False
        self.__n_calls = 0
        self.target_generator_name = target_generator_name
        self.use_candle = use_candle

    def next(self, candle: Candle):
        if self.use_candle:
            current_value = candle[self.use_candle]
        else:
            current_value = self.general_pool.get_generator(self.target_generator_name).value()
        previous_value = self.resultDeque[-1] if len(self.resultDeque) > 0 else 0

        k = 2 / (self.N + 1)

        result = current_value * k + previous_value * (1 - k)
        self.__n_calls += 1
        self.correct = self.__n_calls > self.N*10

        super()._apply_new_value(result)


EMADeviationType = Union['close']


class EMADeviation(TechnicalIndicator):
    def __init__(self, ema_generator_name: str, instrument: Instrument, limit: int, target_value_func: Callable[[Candle], float]):
        TechnicalIndicator.__init__(self, EMADeviation.make_name(instrument), instrument, limit=limit, fr=0)

        self.ema_generator_name = ema_generator_name
        self.target_value_func = target_value_func

    def next(self, candle: Candle):
        value = self.general_pool.get_generator(self.ema_generator_name).value()

        self._apply_new_value(self.target_value_func(candle) - value)
