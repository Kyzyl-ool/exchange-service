from typing import NamedTuple, Generic, Optional, TypeVar, Union

PayloadType = TypeVar('PayloadType')





class IndicatorType(Generic[PayloadType]):
    """
    Абстрактный инжикатор.
    В качестве конкретной реализации это может быть RSI, EMA,
    или даже формации, например "Двойное дно", "Ротация бара", "Пробой уровня на M5"
    """
    value: float  # значение индикатора
    payload: Optional[PayloadType]  # любая полезная информация про индикатор




