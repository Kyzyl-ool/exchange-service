from victor.algorithm.momentum import RSIProbabilityAlgorithm
from victor.risk_management import RiskManagement
from victor.risk_management.classic import Classic

LOWER_BOUND = 10
UPPER_BOUND = 90

STOP_LOSS = 30
TAKE_PROFIT = 60


class RSIAlgorithmEnvironment:
    risk_management: RiskManagement

    def __init__(self):
        self.risk_management = Classic(
            stop_loss=STOP_LOSS,
            take_profit=TAKE_PROFIT,
            instrument=self.instrument,
            v0=100
        )

        self.algorithm = RSIProbabilityAlgorithm(
            lower_bound=LOWER_BOUND,
            upper_bound=UPPER_BOUND,
            generator_set=self.generator_family.generator_families['only-rsi'],
            name='rsi-algorithm',
            instrument=self.instrument,
            risk_management=self.risk_management
        )