from __future__ import annotations

import logging
from typing import Dict

from .generator import Generator
from .generator_set import GeneratorSet
from .generator_family import GeneratorFamily
from ..exchange.types import Instrument


class GeneralPool:
    __generators: Dict[str, Generator]
    __generator_sets: Dict[str, GeneratorSet]
    __generator_families: Dict[str, GeneratorFamily]
    __instance: GeneralPool

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GeneralPool, cls).__new__(cls)
        return cls.instance

    @staticmethod
    def __make_name(generator_id: str, instrument: Instrument):
        instrument_id = instrument['id']
        return f'[{instrument_id}]-{generator_id}'

    def is_generator_exist(self, generator_id: str, instrument: Instrument):
        return self.__make_name(generator_id, instrument) in self.__generators

    def is_generator_set_exist(self, generator_set_id: str, instrument: Instrument):
        return self.__make_name(generator_set_id, instrument) in self.__generator_sets

    def is_generator_family_exist(self, generator_family_id: str, instrument: Instrument):
        return self.__make_name(generator_family_id, instrument) in self.__generator_families

    def add_generator(self, generator_instance: Generator, instrument: Instrument):
        if self.__make_name(generator_instance.name, instrument) in self.__generators:
            logging.error(f'Генератор {generator_instance.name} уже создан')
            return

        self.__generators[generator_instance.name] = generator_instance

    def add_generator_set(self, generator_set_instance: GeneratorSet, instrument: Instrument):
        if self.__make_name(generator_set_instance.name, instrument) in self.__generator_sets:
            logging.error(f'Множество генераторов {generator_set_instance.name} уже есть')
            return

        self.__generator_sets[generator_set_instance.name] = generator_set_instance

    def add_generator_family(self, generator_family_instance: GeneratorFamily, instrument: Instrument):
        if self.__make_name(generator_family_instance.name, instrument) in self.__generator_families:
            logging.error(f'Семейство генераторов {generator_family_instance.name} уже есть')
            return

        self.__generator_families[generator_family_instance.name] = generator_family_instance

    def get_generator(self, generator_id: str, instrument: Instrument):
        return self.__generators[self.__make_name(generator_id, instrument)]

    def get_generator_set(self, generator_set_id: str, instrument: Instrument):
        return self.__generator_sets[self.__make_name(generator_set_id, instrument)]

    def get_generator_family(self, generator_family_id: str, instrument: Instrument):
        return self.__generator_families[self.__make_name(generator_family_id, instrument)]


