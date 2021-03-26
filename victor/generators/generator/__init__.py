from __future__ import annotations

from collections import deque
from typing import Generic, TypeVar, Union

from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.exchange.types import Instrument
from victor.generators import GeneralPool

GeneratorInput = TypeVar('GeneratorInput')
GeneratorOutput = TypeVar('GeneratorOutput')


class GeneratorDependencyManager:
    general_pool: GeneralPool = GeneralPool.getInstance()

    def _add_dependency(self, generator: Generator):
        """
        Добавляет генератор в общий пул. Если уже есть – ничего не делает
        """
        if not self.general_pool.is_generator_exist(generator.name):
            self.general_pool.add_generator(generator)

    @classmethod
    def make_name(cls, instrument: Instrument, *args, **kwargs):
        instrument_id = instrument['id']

        str1 = ', '.join(map(str, args))
        str2 = ", ".join(f"{key}={value}" for key, value in sorted(kwargs.items()))

        params = ', '.join(
            [x for x in [instrument_id, str1 if len(str1) > 0 else None, str2 if len(str2) > 0 else None] if
             x is not None]
        )
        return f'{cls.__name__}({params})'


class Generator(GeneratorDependencyManager, Generic[GeneratorInput, GeneratorOutput]):
    def __init__(self, name: str, instrument: Instrument, limit=GENERATOR_MAX_DEQUE_LENGTH):
        self.name = name
        self.resultDeque = deque([], limit)
        self.instrument = instrument

    def next(self, value: GeneratorInput):
        """
        Обновить значение генератора
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
