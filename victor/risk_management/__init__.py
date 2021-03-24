from typing import TypeVar, Generic, Union

from victor.exchange.types import Candle, MarketOrderRequest, LimitOrderRequest

RuleType = TypeVar('RuleType')  # имена иникаторов


class Rule:
    p0: float
    v0: float

    def __init__(self, p0: float, v0: float):
        self.p0 = p0
        self.v0 = v0

    def order(self, candle: Candle) -> Union[LimitOrderRequest, MarketOrderRequest]:
        raise NotImplementedError('Необходимо унаследовать этот класс и реализовать этот метод')


class RiskManagement(Generic[RuleType]):
    def __init__(self):
        pass

    @staticmethod
    def createRule(p0: float, v0: float):
        return RuleType(p0=p0, v0=v0)
