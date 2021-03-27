from __future__ import annotations

import logging
from typing import Dict, Any, Type

from ..exchange.types import Candle, Instrument


class GeneralPool(object):
    __instance = None
    __generators: Dict[str, Any] = {}

    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = GeneralPool()
        return cls.__instance

    def is_generator_exist(self, generator_id: str):
        return generator_id in self.__generators

    def add_generator(self, generator_instance: Any):
        if generator_instance.name in self.__generators:
            logging.error(f'Генератор {generator_instance.name} уже создан')
            return

        self.__generators[generator_instance.name] = generator_instance

    def get_generator(self, generator_id: str):
        return self.__generators[generator_id]

    def select_generator(self, generator: Type[Any], instrument: Instrument, *args, **kwargs):
        return self.__generators[generator.make_name(instrument, *args, **kwargs)]

    def update_generators(self, candle: Candle):
        for generator in self.__generators.values():
            generator.next(candle)



