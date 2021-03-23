from victor.exchange.types import Candle, Timeframe, OrderState, LimitOrderRequest, MarketOrderRequest
from typing import Callable, List, Dict


class AbstractExchangeClient:
    orders: Dict[str, OrderState] = {}

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
