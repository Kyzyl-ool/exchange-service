from tests.environments.algorithm import RSIAlgorithmEnvironment
from victor.config import TEST_EXCHANGE_SERVICE_HOST
from victor.generators import GeneratorFamily
from victor.trader import Trader


class TraderEnvironment(RSIAlgorithmEnvironment):
    generator_family: GeneratorFamily
    trader: Trader

    def __init__(self):
        RSIAlgorithmEnvironment.__init__(self)

        self.generator_family = GeneratorFamily([self.generator_set])
        self.trader = Trader(self.generator_family, TEST_EXCHANGE_SERVICE_HOST, [self.algorithm])



