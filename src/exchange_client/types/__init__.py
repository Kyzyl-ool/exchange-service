from typing import NamedTuple, Union


class Candle(NamedTuple):
    """
    Японская свеча.
    """
    open: float
    high: float
    low: float
    close: float
    volume: float
    time: str


class OrderState(NamedTuple):
    """
    Состояние заявки
    """
    price: float
    initial_volume: int
    realized_volume: int


Timeframe = Union['M1', 'M5', 'M10', 'M15', 'M30', 'H1', 'H2', 'H4', 'D1', 'W1']
