from typing import Dict, List, Union, Type

from victor.algorithm import Algorithm
from victor.exchange.abstract import AbstractExchangeClient
from victor.exchange.types import Candle, MarketOrderRequest, LimitOrderRequest, is_limit_order_request, \
    is_market_order_request, Instrument
from victor.generators import GeneralPool
from victor.risk_management import Rule


class Trader:
    general_pool: GeneralPool = GeneralPool.getInstance()
    algorithms: Dict[str, Algorithm]
    exchange: AbstractExchangeClient
    active_rules: List[Rule]
    max_orders: float

    def __init__(self, algorithms: List[Algorithm],
                 exchange: AbstractExchangeClient, max_orders=1):
        self.algorithms = {}
        self.active_rules = []
        self.max_orders = max_orders
        self.exchange = exchange

        for algorithm in algorithms:
            self.algorithms[algorithm.name] = algorithm

    def get_algorithm(self, algorithm: Type[Algorithm], instrument: Instrument):
        return self.algorithms[algorithm.make_name(instrument)]

    def perform_rule(self, rule: Rule, candle: Candle) -> None:
        limit_order = rule.enter_order(candle)
        limit_order_id = self.exchange.limit_order(limit_order)
        rule.order_id = limit_order_id

    def perform_signals(self, candle: Candle) -> None:
        limit_orders: Dict[str, List[LimitOrderRequest]] = {}
        market_orders: Dict[str, List[MarketOrderRequest]] = {}

        def __check_orders(key: str,
                           orders: Union[Dict[str, List[LimitOrderRequest]], Dict[str, List[MarketOrderRequest]]]):
            if key not in orders:
                orders[key] = []

        def __add_order(order: Union[LimitOrderRequest, MarketOrderRequest],
                        orders: Union[Dict[str, List[LimitOrderRequest]], Dict[str, List[MarketOrderRequest]]]):
            __check_orders(order['id'], orders)
            orders[order['id']].append(order)

        #  Собираем сделки по всем алгоритмам
        for algorithm in self.algorithms.values():
            decision = algorithm.determine()
            if len(self.active_rules) < self.max_orders and decision is not None:
                rule = algorithm.risk_management.createRule(buy=True if decision == 'BUY' else False)

                self.active_rules.append(rule)
                self.perform_rule(rule, candle)

        #  Обрабатываем все открытые сделки
        for rule in self.active_rules:
            order = rule.exit_order(candle)

            if order is not None:
                if is_limit_order_request(order):
                    __add_order(order, limit_orders)
                elif is_market_order_request(order):
                    __add_order(order, market_orders)

        self.active_rules = list(filter(lambda order_item: not order_item.closed, self.active_rules))

        #  Мержим все рыночные заявки
        for market_orders_id in market_orders:
            if len(market_orders[market_orders_id]) > 1:
                buy_reduced, volume_reduced = market_orders[market_orders_id][0]
                if not buy_reduced:
                    volume_reduced = -volume_reduced
                for market_order in market_orders[market_orders_id]:
                    buy, volume = market_order.values()
                    if buy:
                        volume_reduced += volume
                    else:
                        volume_reduced -= volume
                if volume_reduced < 0:
                    buy_reduced = False

                punct = market_orders[market_orders_id][0]['punct']
                market_orders[market_orders_id] = [
                    MarketOrderRequest(id=market_orders_id, punct=punct, buy=buy_reduced, volume=volume_reduced)]

            #  Для кажого инструмента теперь только одна рынояная заявка
            assert len(market_orders[market_orders_id]) == 1
            self.exchange.market_order(market_orders[market_orders_id][0])

        # Исполняем все лимитные заявки по очереди
        for limit_orders_list in limit_orders.values():
            for limit_order in limit_orders_list:
                self.exchange.limit_order(limit_order)
