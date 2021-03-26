from __future__ import annotations

from collections import deque
from typing import Generic, TypeVar, Union

from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.exchange.types import Instrument
from victor.generators import GeneralPool

GeneratorInput = TypeVar('GeneratorInput')
GeneratorOutput = TypeVar('GeneratorOutput')


class Generator(Generic[GeneratorInput, GeneratorOutput]):
    general_pool: GeneralPool = GeneralPool()

    def __init__(self, name: str, instrument: Instrument, limit=GENERATOR_MAX_DEQUE_LENGTH):
        self.name = name
        self.resultDeque = deque([], limit)
        self.instrument = instrument

    def next(self, value: GeneratorInput):
        """
        Оьновить значение генератора
        """
        raise NotImplementedError('Попытка вызова не реализованного метода')

    def value(self) -> Union[GeneratorOutput, None]:
        """
        Значение генератора в данный момент
        """
        if len(self.resultDeque) > 0:
            return self.resultDeque[-1]
        else:
            return None

    def add_dependency(self, generator: Generator):
        """
        Добавляет генератор в общий пул. Если уже есть – ничего не делает
        """
        if not self.general_pool.is_generator_exist(generator.name, self.instrument):
            self.general_pool.add_generator(generator, self.instrument)

