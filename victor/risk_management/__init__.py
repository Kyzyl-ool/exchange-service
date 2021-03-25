from typing import TypeVar, Generic, Union

from victor.exchange.types import Candle, MarketOrderRequest, LimitOrderRequest, Instrument

RuleType = TypeVar('RuleType')  # имена иникаторов


class Rule:
    p0: float
    v0: float
    opened: bool
    closed: bool
    instrument: Instrument
    buy: bool

    def __init__(self, p0: float, v0: float, instrument: Instrument, buy: bool):
        self.p0 = p0
        self.v0 = v0
        self.instrument = instrument
        self.opened = False
        self.closed = False
        self.buy = buy

    def exit_order(self, candle: Candle) -> Union[LimitOrderRequest, MarketOrderRequest]:
        raise NotImplementedError('Необходимо унаследовать этот класс и реализовать этот метод')

    def enter_order(self):
        if self.opened:
            return None

        self.opened = True

        return LimitOrderRequest(
            volume=self.v0,
            punct=self.instrument['punct'],
            buy=self.buy,
            id=self.instrument['id'],
            price=self.p0
        )


class RiskManagement(Generic[RuleType]):
    v0: float  # рабочий объем
    instrument: Instrument  # торгуемный инструмент

    def __init__(self, v0: float, instrument: Instrument):
        self.v0 = v0
        self.instrument = instrument

    def createRule(self, p0: float, buy: bool) -> RuleType:
        return RuleType(p0=p0, v0=self.v0)
