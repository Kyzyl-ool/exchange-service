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
    order_id: str
    take_profit: float
    stop_loss: float

    def __init__(self, v0: float, instrument: Instrument, buy: bool):
        self.v0 = v0
        self.instrument = instrument
        self.opened = False
        self.closed = False
        self.buy = buy

    def exit_order(self, candle: Candle) -> Union[LimitOrderRequest, MarketOrderRequest]:
        raise NotImplementedError('Необходимо унаследовать этот класс и реализовать этот метод')

    def enter_order(self, candle: Candle) -> LimitOrderRequest:
        assert not self.opened
        self.opened = True

        return LimitOrderRequest(
            volume=self.v0,
            punct=self.instrument['punct'],
            buy=self.buy,
            id=self.instrument['id'],
            price=candle['close']
        )

    def exit_force(self) -> MarketOrderRequest:
        raise NotImplementedError('Необходимо унаследовать этот класс и реализовать этот метод')

    def is_order_would_fulfilled(self, candle: Candle, is_take_profit: bool, use_close_value: bool = False):
        high = candle['high']
        low = candle['low']
        close = candle['close']

        if not self.opened:
            return False

        if is_take_profit:
            return self.buy and (close if use_close_value else high) > self.take_profit or not self.buy and (close if use_close_value else low) < self.take_profit

        return self.buy and (close if use_close_value else low) < self.stop_loss or not self.buy and (close if use_close_value else high) > self.stop_loss


class RiskManagement(Generic[RuleType]):
    v0: float  # рабочий объем
    instrument: Instrument  # торгуемный инструмент

    def __init__(self, v0: float, instrument: Instrument):
        self.v0 = v0
        self.instrument = instrument

    def createRule(self, buy: bool) -> RuleType:
        return RuleType(v0=self.v0, buy=buy)
