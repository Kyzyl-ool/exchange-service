import logging
from datetime import datetime, timedelta
from decimal import Decimal

from victor.config import TINKOFF_SANDBOX_TOKEN
from victor.exchange.abstract import AbstractExchangeClient
from victor.exchange.types import Timeframe, Candle, LimitOrderRequest, MarketOrderRequest, Order, OrderState, \
    Instrument
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
    async_client: ti.AsyncClient
    accounts: List
    streaming: ti.Streaming

    def __init__(self):
        self.subscried_candles = {}

    async def init(self):
        self.async_client = ti.AsyncClient(os.environ[TINKOFF_SANDBOX_TOKEN], use_sandbox=True)
        self.streaming = ti.Streaming(os.environ[TINKOFF_SANDBOX_TOKEN])
        await self.streaming.start()

        result = await self.async_client.get_accounts()
        self.accounts = result.payload.accounts
        body = ti.SandboxSetCurrencyBalanceRequest(
            balance=100000,
            currency='RUB',
        )
        await self.async_client.set_sandbox_currencies_balance(body)

    async def ohlc_subscribe(self, instrument_id: str, timeframe: Timeframe, handler: Callable[[Candle], None]):
        """
        Подписаться на обновления японской свечи по инструменту
        :param timeframe:
        :param instrument_id:
        :param handler: обработчик получения новой свечи
        :return:
        """
        streaming = self.streaming
        assert instrument_id not in self.subscried_candles
        await streaming.candle.subscribe(instrument_id, self.map_timeframe(timeframe))
        self.subscried_candles[instrument_id] = timeframe
        logging.debug(f'Subscribed to {instrument_id} candle updates')
        async for event in streaming:
            handler(candle_mapping(event.payload))

    @staticmethod
    def map_timeframe(timeframe: Timeframe) -> ti.CandleResolution:
        assert timeframe in timeframe_mapping
        return timeframe_mapping[timeframe]

    async def limit_order(self, order: LimitOrderRequest) -> str:
        logging.debug('LIMIT ORDER:', order)
        body = ti.LimitOrderRequest(
            lots=int(order['volume']),
            operation='Buy' if order['buy'] else 'Sell',
            price=Decimal(order['price'])
        )

        result = await self.async_client.post_orders_limit_order(order['id'], body)
        order_id = result.payload.order_id
        self.orders[order_id] = OrderState(
            price=order['price'] if order['buy'] else -order['price'],
            initial_volume=order['volume'],
            realized_volume=float(result.payload.executed_lots)
        )

        return order_id

    async def market_order(self, order: MarketOrderRequest) -> str:
        logging.debug('MARKET ORDER:', order)
        body = ti.MarketOrderRequest(
            lots=int(order['volume']),
            operation='Buy' if order['buy'] else 'Sell',
        )

        result = await self.async_client.post_orders_market_order(order['id'], body)

        order_id = result.payload.order_id

        executed_order = []
        while len(executed_order) == 0:
            await asyncio.sleep(5)
            logging.debug('Getting operations...')
            orders = await self.async_client.get_operations(datetime.now() - timedelta(minutes=30), datetime.now(),
                                                            order['id'])
            logging.debug('Got operations:', orders)
            executed_order = [x for x in orders.payload.operations if x.id == order_id]

        self.orders[order_id] = OrderState(
            price=float(executed_order[0].price),
            initial_volume=order['volume'],
            realized_volume=float(result.payload.executed_lots)
        )

        return order_id

    async def cancel_order(self, order_id: str):
        await self.async_client.post_orders_cancel(order_id)

    async def update(self, candle: Candle) -> None:
        pass

    async def close_connections(self):
        for figi in self.subscried_candles:
            timeframe = self.subscried_candles[figi]
            self.streaming.candle.unsubscribe(figi, self.map_timeframe(timeframe))

        await self.async_client.close()
        await self.streaming.stop()

    async def preload_candles(self, instrument: Instrument, from_: datetime, to: datetime, timeframe: Timeframe) -> List[Candle]:
        result = []
        delta = timedelta(hours=23, minutes=59)
        t0 = from_
        t1 = from_ + delta
        while abs(t1 - t0) >= delta:
            batch = await self.async_client.get_market_candles(instrument['id'], t0, t1, timeframe_mapping[timeframe])
            result += batch.payload.candles
            t0 = t1 + timedelta(minutes=1)
            t1 = min(to, t0 + delta)
        result += (await self.async_client.get_market_candles(instrument['id'], t0, t1, timeframe_mapping[timeframe])).payload.candles

        logging.debug('CANDLES PRELOADED')
        return list(map(candle_mapping, result))
