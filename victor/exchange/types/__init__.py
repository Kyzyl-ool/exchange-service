"""
Все типы, относящиеся к биржевому клиенту
"""
import enum
from datetime import datetime
from typing import TypedDict, Optional, Dict


class Candle(TypedDict):
    open: float
    high: float
    low: float
    close: float
    volume: float
    time: datetime


class OrderState(TypedDict):
    price: float
    initial_volume: float
    realized_volume: float


class Instrument(TypedDict):
    id: str
    punct: float


class Timeframe(enum.Enum):
    """
    Таймфреймы
    """
    M1 = 0
    M5 = 1
    M10 = 2
    M15 = 3
    M30 = 4
    H1 = 5
    H2 = 6
    H4 = 7
    D1 = 8
    W1 = 9
    MONTH = 10


class Order(Instrument):
    initialVolume: float
    executedVolume: float
    buy: bool
    price: float


class OrderRequest(Instrument):
    buy: bool
    volume: float


class LimitOrderRequest(OrderRequest):
    price: float


def is_limit_order_request(value: Dict):
    return 'price' in value and 'id' in value and 'buy' in value


def is_market_order_request(value):
    return 'price' not in value and 'id' in value and 'buy' in value


class MarketOrderRequest(OrderRequest):
    pass


class StopOrder(Instrument):
    volume: float
    price: float
    buy: bool
    trailing: Optional[float]  # кол-во пунктов, после которых стоп начнет двигаться
