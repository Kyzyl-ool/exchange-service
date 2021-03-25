from tests.environments.RSI import RSIEnvironment
from victor.algorithm.momentum import RSIProbabilityAlgorithm
from victor.generators import GeneratorSet
from victor.risk_management import RiskManagement
from victor.risk_management.classic import Classic

LOWER_BOUND = 10
UPPER_BOUND = 90

STOP_LOSS = 100
TAKE_PROFIT = 200


class RSIAlgorithmEnvironment(RSIEnvironment):
    risk_management: RiskManagement

    def __init__(self):
        RSIEnvironment.__init__(self)

        self.risk_management = Classic(
            stop_loss=STOP_LOSS,
            take_profit=TAKE_PROFIT,
            instrument=self.instrument
        )

        self.generator_set = GeneratorSet([self.rsi], "Only RSI")
        self.algorithm = RSIProbabilityAlgorithm(
            lower_bound=LOWER_BOUND,
            upper_bound=UPPER_BOUND,
            generator_set=self.generator_set,
            name='RSI algorithm',
            instrument=self.instrument,
            risk_management=self.risk_management
        )