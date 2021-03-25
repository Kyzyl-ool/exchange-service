from tests.environments.algorithm import RSIAlgorithmEnvironment
from victor.trader import Trader


class TraderEnvironment(RSIAlgorithmEnvironment):
    trader: Trader

    def __init__(self):
        RSIAlgorithmEnvironment.__init__(self)

        self.trader = Trader(self.generator_family, [self.algorithm], self.exchange)



