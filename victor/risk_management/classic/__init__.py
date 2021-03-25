from typing import Union

from victor.exchange.types import Candle, LimitOrderRequest, MarketOrderRequest, Instrument
from victor.risk_management import RiskManagement, Rule


class ClassicRule(Rule):
    stop_loss_punct: float
    take_profit_punct: float

    stop_loss: float
    take_profit: float

    def __init__(self, stop_loss: float, take_profit: float, **kwargs):
        """
        stop_loss, take_profit – в пунктах
        """
        super().__init__(**kwargs)
        self.stop_loss_punct = stop_loss
        self.take_profit_punct = take_profit

    def exit_order(self, candle: Candle) -> Union[LimitOrderRequest, MarketOrderRequest, None]:
        high = candle['high']
        low = candle['low']

        if self.opened:
            if self.buy:
                if high > self.take_profit or low < self.stop_loss:
                    self.closed = True
                    return MarketOrderRequest(
                        volume=self.v0,
                        punct=self.instrument['punct'],
                        buy=False,
                        id=self.instrument['id']
                    )
            else:
                if low < self.take_profit or high > self.stop_loss:
                    self.closed = True
                    return MarketOrderRequest(
                        volume=self.v0,
                        punct=self.instrument['punct'],
                        id=self.instrument['id'],
                        buy=True
                    )

        return None

    def exit_force(self):
        self.closed = True
        return MarketOrderRequest(
            volume=self.v0,
            punct=self.instrument['punct'],
            buy=not self.buy,
            id=self.instrument['id']
        )

    def enter_order(self, candle: Candle) -> LimitOrderRequest:
        p0 = candle['close']
        buy = self.buy

        self.stop_loss = p0 - self.stop_loss_punct if buy else p0 + self.stop_loss_punct
        self.take_profit = p0 + self.take_profit_punct if buy else p0 - self.take_profit_punct

        return Rule.enter_order(self, candle)


class Classic(RiskManagement[ClassicRule]):
    stop_loss: float
    take_profit: float
    instrument: Instrument

    def __init__(self, stop_loss: float, take_profit: float, **kwargs):
        """
        stop_loss - в пунктах
        take_profit - в пунктах
        """
        super().__init__(**kwargs)
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def createRule(self, buy: bool):
        return ClassicRule(
            v0=self.v0,
            stop_loss=self.stop_loss,
            take_profit=self.take_profit,
            buy=buy,
            instrument=self.instrument
        )
