from victor.generators import GeneratorSet
from victor.algorithm import ProbabilityAlgorithm


class RSIProbabilityAlgorithm(ProbabilityAlgorithm):
    """
    Вероятностный алгоритм по индикатору RSI

    GeneratorSet должен иметь RSI
    """
    upper_bound: float
    lower_bound: float

    def __init__(self, generator_set: GeneratorSet, lower_bound: float, upper_bound: float):
        super().__init__(generator_set)

        assert generator_set.generators['RSI'] is not None

        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def _probability(self) -> float:
        k = 2 / (self.lower_bound - self.upper_bound)
        b = (self.lower_bound + self.upper_bound) / (self.upper_bound - self.lower_bound)
        x = self.generator_set.generators['RSI'].value()

        if x <= self.lower_bound:
            return 1
        elif x >= self.upper_bound:
            return -1
        else:
            return k * x + b

