from __future__ import annotations

from collections import deque
from typing import Generic, TypeVar, Union, Dict

from victor.config import GENERATOR_MAX_DEQUE_LENGTH

GeneratorType = TypeVar('GeneratorType')  # имена иникаторов


class Generator(Generic[GeneratorType]):
    dependencies: Dict[str, Generator]
    resultDeque: deque
    name: str

    def __init__(self, **kwargs):
        name = kwargs.get('name', None)
        assert name is not None

        self.name = name
        self.resultDeque = deque([], GENERATOR_MAX_DEQUE_LENGTH)
        self.dependencies = {}

    def next(self, value: GeneratorType):
        raise NotImplementedError('Попытка вызова не реализованного метода')

    def value(self) -> Union[GeneratorType, None]:
        if len(self.resultDeque) > 0:
            return self.resultDeque[-1]
        else:
            return None

    def add_dependency(self, generator: Generator):
        assert generator is not None
        self.dependencies[generator.name] = generator

