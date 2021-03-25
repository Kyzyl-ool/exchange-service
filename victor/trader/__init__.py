from typing import Dict, List, Union

from victor.algorithm import Algorithm
from victor.exchange.abstract import AbstractExchangeClient
from victor.exchange.types import Candle, MarketOrderRequest, LimitOrderRequest, Order
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

    def __init__(self, generator_family: GeneratorFamily, algorithms: List[Algorithm],
                 exchange: AbstractExchangeClient):
        assert len(generator_family.generator_families) > 0
        self.__generators = {}
        self.algorithms = {}
        self.active_rules = []

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

        for algorithm in self.algorithms.values():
            decision = algorithm.determine()
            if decision is not None:
                p0 = candle['close']
                rule = algorithm.risk_management.createRule(p0=p0, buy=True if decision == 'BUY' else False)

                self.active_rules.append(rule)
                limit_order = rule.enter_order()
                assert limit_order is not None

                if limit_order['id'] not in limit_orders:
                    limit_orders[limit_order['id']] = []

                limit_orders[limit_order['id']].append(limit_order)

        for rule in self.active_rules:
            order = rule.exit_order(candle)

            if order is LimitOrderRequest:
                limit_orders[order['id']].append(order)
            elif order is MarketOrderRequest:
                market_orders[order['id']].append(order)

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
