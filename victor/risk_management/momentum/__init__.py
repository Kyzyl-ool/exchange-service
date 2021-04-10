import logging
from typing import Union

from victor.exchange.types import Instrument, Candle, LimitOrderRequest, MarketOrderRequest
from victor.risk_management import RiskManagement, Rule


class MomentumRule(Rule):
    def __init__(self, v0: float, instrument: Instrument, buy: bool, alpha: float, stop_loss: float, d: float):
        Rule.__init__(self, v0, instrument, buy)
        self.alpha = alpha
        self.stop_loss_punct = stop_loss
        self.d = d
        self.v = 0

    def enter_order(self, candle: Candle) -> LimitOrderRequest:
        p0 = candle['close']
        self.p0 = p0
        self.v = self.v0

        if self.buy:
            self.stop_loss = p0 - self.stop_loss_punct * self.instrument['punct']
            self.take_profit = p0 + self.d * self.instrument['punct']
        else:
            self.stop_loss = p0 + self.stop_loss_punct * self.instrument['punct']
            self.take_profit = p0 - self.d*self.instrument['punct']

        return super().enter_order(candle)

    def exit_force(self) -> MarketOrderRequest:
        self.closed = True

        logging.debug(f'[{self.order_id}] {self.p0} -> ? (force exit)')

        return MarketOrderRequest(
            volume=self.v,
            punct=self.instrument['punct'],
            buy=not self.buy,
            id=self.instrument['id']
        )

    def exit_order(self, candle: Candle) -> Union[LimitOrderRequest, MarketOrderRequest]:
        close = candle['close']

        if self.is_order_would_fulfilled(candle, is_take_profit=True, use_close_value=False):
            self.closed = self.v <= self.v0*self.alpha
            if self.closed:
                logging.debug(f'[{self.order_id}]: {self.p0} -> {close} (long)')
            if self.buy:
                self.stop_loss = self.take_profit - self.d * self.instrument['punct']
                self.take_profit += self.d * self.instrument['punct']
            else:
                self.stop_loss = self.take_profit + self.d * self.instrument['punct']
                self.take_profit -= self.d * self.instrument['punct']

            amount_to_release = min(self.v, self.v0*self.alpha)
            self.v -= amount_to_release

            return MarketOrderRequest(
                volume=amount_to_release,
                punct=self.instrument['punct'],
                buy=not self.buy,
                id=self.instrument['id']
            )

        if self.is_order_would_fulfilled(candle, is_take_profit=False, use_close_value=True):
            amount_to_release = self.v
            self.closed = True

            return MarketOrderRequest(
                volume=amount_to_release,
                punct=self.instrument['punct'],
                buy=not self.buy,
                id=self.instrument['id']
            )


class MomentumRiskManagement(RiskManagement[MomentumRule]):
    def __init__(self, stop_loss: float, v0: float, instrument: Instrument, alpha: float, d: float):
        RiskManagement.__init__(self, v0=v0, instrument=instrument)

        self.stop_loss = stop_loss
        self.alpha = alpha
        self.d = d

    def createRule(self, buy: bool) -> MomentumRule:
        return MomentumRule(
            buy=buy,
            instrument=self.instrument,
            stop_loss=self.stop_loss,
            alpha=self.alpha,
            d=self.d,
            v0=self.v0
        )
