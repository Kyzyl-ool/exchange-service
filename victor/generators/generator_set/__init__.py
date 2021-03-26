from typing import List, Dict

from victor.exchange.types import Instrument
from victor.generators import GeneralPool
from victor.generators.generator import Generator


class GeneratorSet:
    general_pool: GeneralPool = GeneralPool.getInstance()
    generators: Dict[str, Generator]

    def __init__(self, generators: List[Generator], name: str, instrument: Instrument):
        assert len(generators) > 0
        self.generators = {}
        self.instrument = instrument

        for generator in generators:
            self.generators[generator.name] = generator

        self.name = name

    def make_name(self, **kwargs):
        raise NotImplementedError

