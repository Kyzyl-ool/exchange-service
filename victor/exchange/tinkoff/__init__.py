from decimal import Decimal

from victor.config import TINKOFF_SANDBOX_TOKEN
from victor.exchange.abstract import AbstractExchangeClient
from victor.exchange.types import Timeframe, Candle, LimitOrderRequest, MarketOrderRequest
from typing import Callable, Dict, List
import tinvest as ti
import asyncio
import os

timeframe_mapping = dict()
timeframe_mapping[Timeframe.M1] = ti.CandleResolution.min1
timeframe_mapping[Timeframe.M5] = ti.CandleResolution.min5
timeframe_mapping[Timeframe.M15] = ti.CandleResolution.min15
timeframe_mapping[Timeframe.M30] = ti.CandleResolution.min30
timeframe_mapping[Timeframe.H1] = ti.CandleResolution.hour
timeframe_mapping[Timeframe.D1] = ti.CandleResolution.day
timeframe_mapping[Timeframe.W1] = ti.CandleResolution.week
timeframe_mapping[Timeframe.MONTH] = ti.CandleResolution.month


def candle_mapping(ti_candle: ti.Candle) -> Candle:
    return Candle(
        volume=ti_candle.v,
        close=float(ti_candle.c),
        high=float(ti_candle.h),
        low=float(ti_candle.l),
        open=float(ti_candle.o),
        time=ti_candle.time
    )


class TinkoffExchangeClient(AbstractExchangeClient):
    streaming: ti.Streaming
    subscried_candles: Dict[str, Timeframe]
    async_client: ti.AsyncClient = ti.AsyncClient(os.environ[TINKOFF_SANDBOX_TOKEN], use_sandbox=True)
    accounts: List

    def __init__(self):
        self.subscried_candles = {}
        # result = await self.async_client.get_accounts()
        # self.accounts = result.payload.accounts

    async def ohlc_subscribe(self, instrument_id: str, timeframe: Timeframe, handler: Callable[[Candle], None]):
        """
        Подписаться на обновления японской свечи по инструменту
        :param timeframe:
        :param instrument_id:
        :param handler: обработчик получения новой свечи
        :return:
        """
        async with ti.Streaming(os.environ[TINKOFF_SANDBOX_TOKEN]) as streaming:
            self.streaming = streaming
            assert instrument_id not in self.subscried_candles
            await streaming.candle.subscribe(instrument_id, self.map_timeframe(timeframe))
            async for event in streaming:
                handler(candle_mapping(event.payload))
        pass

    @staticmethod
    def map_timeframe(timeframe: Timeframe) -> ti.CandleResolution:
        assert timeframe in timeframe_mapping
        return timeframe_mapping[timeframe]

    async def limit_order(self, order: LimitOrderRequest) -> str:
        body = ti.LimitOrderRequest(
            lots=int(order['volume']),
            operation='Buy' if order['buy'] else 'Sell',
            price=Decimal(order['price'])
        )

        result = await self.async_client.post_orders_limit_order(order['id'], body)

        return result.payload.order_id

    async def market_order(self, order: MarketOrderRequest) -> str:
        body = ti.MarketOrderRequest(
            lots=int(order['volume']),
            operation='Buy' if order['buy'] else 'Sell',
        )

        result = await self.async_client.post_orders_market_order(order['id'], body)

        return result.payload.order_id

    async def cancel_order(self, order_id: str):
        await self.async_client.post_orders_cancel(order_id)

    def update(self, candle: Candle) -> None:
        pass

    def close_connections(self):
        for figi in self.subscried_candles:
            timeframe = self.subscried_candles[figi]
            self.streaming.candle.unsubscribe(figi, self.map_timeframe(timeframe))
