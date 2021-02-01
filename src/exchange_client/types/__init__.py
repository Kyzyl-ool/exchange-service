from typing import Union, TypedDict, Optional


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


Timeframe = Union['M1', 'M5', 'M10', 'M15', 'M30', 'H1', 'H2', 'H4', 'D1', 'W1']


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
