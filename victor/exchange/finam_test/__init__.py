from victor.exchange.abstract import AbstractExchangeClient
from victor.exchange.types import Candle, Timeframe, OrderState, LimitOrderRequest, MarketOrderRequest
from typing import Callable
import pandas as pd
from victor.utils import D
from victor.utils.trade_toolkit import Portfolio
from tqdm import tqdm
import datetime

INITIAL_MONEY = 100000


class FinamExchangeTestClient(AbstractExchangeClient):
    df: pd.DataFrame
    portfolio: Portfolio
    current_index: int
    order_index: int

    def __init__(self):
        self.df = None
        self.portfolio = Portfolio(initial_money=INITIAL_MONEY, verbose=True)
        self.current_index = -1
        self.order_index = -1

    def ohlc_subscribe(self, instrument_id: str, timeframe: Timeframe, handler: Callable[[Candle], None]):
        """
        Имитирует подписку на получение свечных данных.
        Сразу после вызова прогоняет исторические данные через обработчик handler

        :param instrument_id: имя файла с историческими данными
        :param timeframe: таймфрейм, игнорируется
        :param handler: обработчик
        :return:
        """
        self.df = pd.read_csv(instrument_id)
        self.df = D.add_col(self.df, '<DATETIME>', D.make_datetime(self.df))
        self.df['<DATETIME>'] -= datetime.timedelta(minutes=1)

        for i, row in tqdm(self.df.iterrows()):
            self.current_index = i
            handler({
                'close': row['<CLOSE>'],
                'open': row['<OPEN>'],
                'high': row['<HIGH>'],
                'low': row['<LOW>'],
                'volume': row['<VOL>'],
                'time': row['<DATETIME>']
            })

    def __place_new_order(self, p, v):
        new_order = OrderState(
            price=p,
            initial_volume=v,
            realized_volume=v
        )

        self.order_index += 1
        self.orders[str(self.order_index)] = new_order

        return str(self.order_index)

    def limit_order(self, order: LimitOrderRequest) -> str:
        p = order['price']
        v = order['volume']
        time = self.df.iloc[self.current_index]['<DATETIME>']

        if order['buy']:
            self.portfolio.buy(p, v, time)
        else:
            self.portfolio.sell(p, v, time)

        return self.__place_new_order(p, v)

    def market_order(self, order: MarketOrderRequest) -> str:
        v = order['volume']
        time = self.df.iloc[self.current_index]['<DATETIME>']
        p = self.df.iloc[self.current_index]['<CLOSE>'] # без учета проскальзывания

        if order['buy']:
            self.portfolio.buy(p, v, time)
        else:
            self.portfolio.sell(p, v, time)

        return self.__place_new_order(p, v)

    def cancel_order(self, order_id: str):
        raise NotImplementedError()
