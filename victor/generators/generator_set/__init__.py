from typing import List, Dict

from victor.generators import Generator


class GeneratorSet:
    generators: Dict[str, Generator] = {}
    name: str

    def __init__(self, generators: List[Generator], name: str):
        assert len(generators) > 0

        for generator in generators:
            self.generators[generator.name] = generator

        self.name = name
