from collections import deque
from typing import Generic, TypeVar

from victor.config import GENERATOR_MAX_DEQUE_LENGTH

GeneratorType = TypeVar('GeneratorType')  # имена иникаторов


class Generator(Generic[GeneratorType]):
    resultDeque: deque
    name: str

    def __init__(self, **kwargs):
        name = kwargs.get('name', None)
        assert name is not None

        self.name = name
        self.resultDeque = deque([], GENERATOR_MAX_DEQUE_LENGTH)

    def next(self, value: GeneratorType):
        raise NotImplementedError('Попытка вызова не реализованного метода')

    def value(self):
        assert len(self.resultDeque) > 0
        return self.resultDeque[-1]
