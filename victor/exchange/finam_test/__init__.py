import logging

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
    handler: Callable[[Candle], None]

    def __init__(self, fixed_comission=0.0005):
        self.df = None
        self.portfolio = Portfolio(initial_money=INITIAL_MONEY, verbose=True)
        self.current_index = -1
        self.order_index = -1
        self.fixed_comission = fixed_comission

    def ohlc_subscribe(self, instrument_id: str, timeframe: Timeframe, handler: Callable[[Candle], None],
                       run_immediately=True):
        """
        Имитирует подписку на получение свечных данных.
        Сразу после вызова прогоняет исторические данные через обработчик handler

        :param instrument_id: имя файла с историческими данными
        :param timeframe: таймфрейм, игнорируется
        :param handler: обработчик
        :param run_immediately
        :return:
        """
        self.df = pd.read_csv(instrument_id)
        self.df = D.add_col(self.df, '<DATETIME>', D.make_datetime(self.df))
        self.df['<DATETIME>'] -= datetime.timedelta(minutes=1)
        self.handler = handler

        if run_immediately:
            self.run()

    def run(self):
        for i, row in tqdm(self.df.iterrows()):
            self.current_index = i
            self.handler({
                'close': row['<CLOSE>'],
                'open': row['<OPEN>'],
                'high': row['<HIGH>'],
                'low': row['<LOW>'],
                'volume': row['<VOL>'],
                'time': row['<DATETIME>']
            })

    def __place_new_order(self, p, v) -> str:
        new_order = OrderState(
            price=p,
            initial_volume=v,
            realized_volume=0
        )

        self.order_index += 1
        self.orders[str(self.order_index)] = new_order
        self.active_orders[str(self.order_index)] = new_order

        return str(self.order_index)

    def limit_order(self, order: LimitOrderRequest) -> str:
        p = order['price']
        v = order['volume']
        time = self.df.iloc[self.current_index]['<DATETIME>']

        if order['buy']:
            self.portfolio.buy(p, v, time)
        else:
            self.portfolio.sell(p, v, time)

        sign = 1 if order['buy'] else -1

        return self.__place_new_order(p, v * sign)

    def market_order(self, order: MarketOrderRequest) -> str:
        v = order['volume']
        time = self.df.iloc[self.current_index]['<DATETIME>']
        p = self.df.iloc[self.current_index]['<CLOSE>']  # без учета проскальзывания

        if order['buy']:
            self.portfolio.buy(p, v, time)
        else:
            self.portfolio.sell(p, v, time)

        sign = 1 if order['buy'] else -1

        return self.__place_new_order(p, v * sign)

    def cancel_order(self, order_id: str):
        if order_id not in self.active_orders:
            logging.error(f'Order id ({order_id}) is not in active orders list!')
            return

        del self.active_orders[order_id]

    def update(self, candle: Candle):
        to_delete = []
        for order_id in self.active_orders:
            order = self.active_orders[order_id]
            sign = 1 if order['initial_volume'] > 0 else -1

            if sign > 0 and candle['low'] < order['price'] or sign < 0 and candle['high'] > order['price']:
                self.orders[order_id]['realized_volume'] = self.orders[order_id]['initial_volume']
                to_delete.append(order_id)

        for order_id in to_delete:
            del self.active_orders[order_id]

        self.last_candle = candle
