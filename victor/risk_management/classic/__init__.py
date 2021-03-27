import logging
from typing import Union

from victor.exchange.types import Candle, LimitOrderRequest, MarketOrderRequest, Instrument
from victor.risk_management import RiskManagement, Rule


class ClassicRule(Rule):
    stop_loss_punct: float
    take_profit_punct: float

    def __init__(self, stop_loss: float, take_profit: float, **kwargs):
        """
        stop_loss, take_profit – в пунктах
        """
        super().__init__(**kwargs)
        self.stop_loss_punct = stop_loss * self.instrument['punct']
        self.take_profit_punct = take_profit * self.instrument['punct']

    def exit_order(self, candle: Candle) -> Union[LimitOrderRequest, MarketOrderRequest, None]:
        close = candle['close']

        if self.is_order_would_fulfilled(candle):
            self.closed = True
            logging.debug(f'[{self.order_id}]: {self.p0} -> {close} (long)')

            return MarketOrderRequest(
                volume=self.v0,
                punct=self.instrument['punct'],
                buy=not self.buy,
                id=self.instrument['id']
            )

        return None

    def exit_force(self) -> MarketOrderRequest:
        self.closed = True

        logging.debug(f'[{self.order_id}] {self.p0} -> ? (force exit)')

        return MarketOrderRequest(
            volume=self.v0,
            punct=self.instrument['punct'],
            buy=not self.buy,
            id=self.instrument['id']
        )

    def enter_order(self, candle: Candle) -> LimitOrderRequest:
        p0 = candle['close']
        buy = self.buy
        self.p0 = p0

        self.stop_loss = p0 - self.stop_loss_punct if buy else p0 + self.stop_loss_punct
        self.take_profit = p0 + self.take_profit_punct if buy else p0 - self.take_profit_punct

        return Rule.enter_order(self, candle)


class Classic(RiskManagement[ClassicRule]):
    stop_loss: float
    take_profit: float
    instrument: Instrument

    def __init__(self, stop_loss: float, take_profit: float, v0: float, instrument: Instrument):
        """
        stop_loss - в пунктах
        take_profit - в пунктах
        """
        RiskManagement.__init__(self, v0=v0, instrument=instrument)
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
