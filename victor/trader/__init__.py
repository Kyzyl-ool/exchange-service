from typing import Dict, List, Union

from victor.algorithm import Algorithm
from victor.exchange.abstract import AbstractExchangeClient
from victor.exchange.types import Candle, MarketOrderRequest, LimitOrderRequest, is_limit_order_request, \
    is_market_order_request
from victor.generators import GeneratorFamily, Generator
from victor.risk_management import Rule


def add_dependencies_recursively(generator: Generator, generators_dict: Dict[str, Generator]):
    if len(generator.dependencies) > 0:
        for dependency_generator in generator.dependencies.values():
            add_dependencies_recursively(dependency_generator, generators_dict)
            generators_dict[dependency_generator.name] = dependency_generator
    generators_dict[generator.name] = generator


class Trader:
    generator_family: GeneratorFamily
    __generators: Dict[str, Generator]
    algorithms: Dict[str, Algorithm]
    exchange: AbstractExchangeClient
    active_rules: List[Rule]
    max_orders: float

    def __init__(self, generator_family: GeneratorFamily, algorithms: List[Algorithm],
                 exchange: AbstractExchangeClient, max_orders=1):
        assert len(generator_family.generator_families) > 0
        self.__generators = {}
        self.algorithms = {}
        self.active_rules = []
        self.max_orders = max_orders

        self.generator_family = generator_family
        self.exchange = exchange

        for generator_set in generator_family.generator_families.values():
            for generator in generator_set.generators.values():
                add_dependencies_recursively(generator, self.__generators)

        for algorithm in algorithms:
            self.algorithms[algorithm.name] = algorithm

    def update(self, candle: Candle) -> None:
        for generator in self.__generators.values():
            generator.next(candle)

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
                limit_order = rule.enter_order(candle)
                assert limit_order is not None

                __add_order(limit_order, limit_orders)

        #  Обрабатываем все открытые сделки
        for rule in self.active_rules:
            order = rule.exit_order(candle)

            if order is not None:
                if is_limit_order_request(order):
                    __add_order(order, limit_orders)
                elif is_market_order_request(order):
                    __add_order(order, market_orders)

        self.active_rules = list(filter(lambda order_item: not order_item.closed, self.active_rules))

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

            assert len(market_orders[market_orders_id]) == 1

            self.exchange.market_order(market_orders[market_orders_id][0])

        for limit_orders_list in limit_orders.values():
            for limit_order in limit_orders_list:
                self.exchange.limit_order(limit_order)
