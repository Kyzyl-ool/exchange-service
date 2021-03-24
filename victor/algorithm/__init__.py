from victor.generators import GeneratorSet


class ProbabilityAlgorithm:
    generator_set: GeneratorSet

    def __init__(self, generator_set: GeneratorSet):
        self.generator_set = generator_set

    def probability(self, reverse = False) -> float:
        if reverse:
            return -self._probability()
        else:
            return self._probability()

    def _probability(self) -> float:
        """
        Вероятность покупки.

        -1 – покупка в шорт
        1 – покупка в лонг
        """
        raise NotImplementedError('Необходимо отнаследоваться и реализовать этот метод')
