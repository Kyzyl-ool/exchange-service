"""
Все типы, относящиеся к биржевому клиенту
"""
import enum
from typing import TypedDict, Optional, Union


class Candle(TypedDict):
    open: float
    high: float
    low: float
    close: float
    volume: float
    time: str


class OrderState(TypedDict):
    price: float
    initial_volume: int
    realized_volume: int


class Instrument(TypedDict):
    id: str
    punct: float


class Order(Instrument):
    initialVolume: float
    executedVolume: float
    buy: bool
    price: float


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


class LimitOrderRequest(Instrument):
    buy: bool
    price: float
    volume: float


class MarketOrderRequest(Instrument):
    buy: bool
    volume: float


class StopOrder(Instrument):
    volume: float
    price: float
    buy: bool
    trailing: Optional[float]  # кол-во пунктов, после которых стоп начнет двигаться
