from datetime import datetime

from victor.exchange.types import Candle, Timeframe, OrderState, LimitOrderRequest, MarketOrderRequest, Instrument
from typing import Callable, Dict, Coroutine


class AbstractExchangeClient:
    orders: Dict[str, OrderState] = {}
    active_orders: Dict[str, OrderState] = {}
    last_candle: Candle
    fixed_comission: float # в долях от сделки

    def ohlc_subscribe(self, instrument_id: str, timeframe: Timeframe, handler: Callable[[Candle], None]):
        """
        Подписаться на обновления японской свечи по инструменту
        :param timeframe:
        :param instrument_id:
        :param handler: обработчик получения новой свечи
        :return:
        """
        raise NotImplementedError()

    def limit_order(self, order: LimitOrderRequest) -> str:
        raise NotImplementedError()

    def market_order(self, order: MarketOrderRequest) -> str:
        raise NotImplementedError()

    def cancel_order(self, order_id: str):
        raise NotImplementedError()

    def update(self, candle: Candle) -> Coroutine:
        raise NotImplementedError()

    def financial_result(self, candle: Candle) -> (float, float):
        result = 0
        result_volume = 0
        comission = 0

        for order in self.orders.values():
            amount = order['price']*order['realized_volume']
            result -= amount
            result_volume += order['realized_volume']
            comission += abs(amount)*self.fixed_comission

        for order in self.active_orders.values():
            amount = candle['close']*order['realized_volume']
            result -= amount
            result_volume += order['realized_volume']
            comission += abs(amount)*self.fixed_comission

        assert result_volume == 0

        return result - comission, comission

    def close_connections(self):
        raise NotImplementedError

    def preload_candles(self, instrument: Instrument, from_: datetime, to: datetime, timeframe: Timeframe):
        raise NotImplementedError
