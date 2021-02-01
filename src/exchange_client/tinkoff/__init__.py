from .. import ExchangeClient
from ..types import Candle, Timeframe, OrderState
from typing import Callable, List


class TinkoffExchangeClient(ExchangeClient):
    def ohlc_subscribe(self, instrument_id: str, timeframe: Timeframe, handler: Callable[[Candle], None]):
        """
        Подписаться на обновления японской свечи по инструменту
        :param timeframe:
        :param instrument_id:
        :param handler: обработчик получения новой свечи
        :return:
        """
        pass

    def limit_order(self, instrument_id: str, price: float, volume: float) -> str:
        pass

    def market_order(self, instrument_id: str, price: float) -> str:
        pass

    def cancel_order(self, order_id: str):
        pass
