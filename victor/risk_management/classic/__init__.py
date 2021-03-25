from typing import Union

from victor.exchange.types import Candle, LimitOrderRequest, MarketOrderRequest, Instrument
from victor.risk_management import RiskManagement, Rule


class ClassicRule(Rule):
    stop_loss: float
    take_profit: float

    def __init__(self, stop_loss: float, take_profit: float, **kwargs):
        """
        stop_loss, take_profit – уровень цены
        """
        super().__init__(**kwargs)
        self.stop_loss = stop_loss
        self.take_profit = take_profit

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

    def createRule(self, p0: float, buy: bool):
        stop_loss = p0 - self.stop_loss if buy else p0 + self.stop_loss
        take_profit = p0 + self.take_profit if buy else p0 - self.take_profit

        return ClassicRule(
            p0=p0,
            v0=self.v0,
            stop_loss=stop_loss,
            take_profit=take_profit,
            buy=buy,
            instrument=self.instrument
        )
