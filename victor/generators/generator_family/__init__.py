from typing import List, Dict

from victor.generators import GeneratorSet


class GeneratorFamily:
    generator_families: Dict[str, GeneratorSet] = {}

    def __init__(self, generator_sets: List[GeneratorSet]):
        for generator_set in generator_sets:
            self.generator_families[generator_set.name] = generator_set

