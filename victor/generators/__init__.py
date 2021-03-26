from __future__ import annotations

import logging
from typing import Dict, Any

from ..exchange.types import Instrument


class GeneralPool(object):
    __instance = None
    __generators: Dict[str, Any] = {}

    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = GeneralPool()
        return cls.__instance

    @staticmethod
    def __make_name(generator_id: str, instrument: Instrument):
        instrument_id = instrument['id']
        return f'[{instrument_id}]-{generator_id}'

    def is_generator_exist(self, generator_id: str, instrument: Instrument):
        return self.__make_name(generator_id, instrument) in self.__generators

    def add_generator(self, generator_instance: Any, instrument: Instrument):
        if self.__make_name(generator_instance.name, instrument) in self.__generators:
            logging.error(f'Генератор {generator_instance.name} уже создан')
            return

        self.__generators[self.__make_name(generator_instance.name, instrument)] = generator_instance

    def get_generator(self, generator_id: str, instrument: Instrument):
        return self.__generators[self.__make_name(generator_id, instrument)]


