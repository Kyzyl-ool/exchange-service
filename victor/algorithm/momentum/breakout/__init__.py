from victor.algorithm import ProbabilityAlgorithm

BREAKOUT_GENERATOR_NAME = 'breakout-up'


class BreakoutProbabilityAlgorithm(ProbabilityAlgorithm):
    """
    Вероятностный алгоритм по пробитию уровня
    Пока что обрабатывает только пробития вверх
    """
    def __init__(self, **kwargs):
        ProbabilityAlgorithm.__init__(self, **kwargs)

        assert self.generator_set.__generators[BREAKOUT_GENERATOR_NAME] is not None

        self.breakout = self.generator_set.__generators[BREAKOUT_GENERATOR_NAME]

    def _probability(self) -> float:
        if self.breakout.value() > 0:
            return 1
        else:
            return 0


