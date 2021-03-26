from __future__ import annotations

from collections import deque
from typing import Generic, TypeVar, Union, Dict, Optional

from victor.config import GENERATOR_MAX_DEQUE_LENGTH

GeneratorInput = TypeVar('GeneratorInput')
GeneratorOutput = TypeVar('GeneratorOutput')


class Generator(Generic[GeneratorInput, GeneratorOutput]):
    dependencies: Dict[str, Generator]
    resultDeque: deque
    name: str

    def __init__(self, name: str, limit=GENERATOR_MAX_DEQUE_LENGTH):
        self.name = name
        self.resultDeque = deque([], limit)
        self.dependencies = {}

    def next(self, value: GeneratorInput):
        raise NotImplementedError('Попытка вызова не реализованного метода')

    def value(self) -> Union[GeneratorOutput, None]:
        if len(self.resultDeque) > 0:
            return self.resultDeque[-1]
        else:
            return None

    def add_dependency(self, generator: Generator):
        assert generator is not None
        self.dependencies[generator.name] = generator

