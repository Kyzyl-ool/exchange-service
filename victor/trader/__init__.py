from typing import Dict, List, Union

from victor.algorithm import Algorithm
from victor.exchange.abstract import AbstractExchangeClient
from victor.exchange.finam_test import FinamExchangeTestClient
from victor.exchange.types import Candle, MarketOrderRequest, LimitOrderRequest
from victor.generators import GeneratorFamily, Generator
from victor.risk_management import Rule


class Trader:
    generator_family: GeneratorFamily
    __generators: Dict[str, Generator]
    algorithms: Dict[str, Algorithm]
    __exchange: AbstractExchangeClient
    active_rules: List[Rule]

    def __init__(self, generator_family: GeneratorFamily, exchange_service_host: str, algorithms: List[Algorithm]):
        assert len(generator_family.generator_families) > 0
        self.__generators = {}
        self.algorithms = {}
        self.active_rules = []

        self.generator_family = generator_family
        # todo: нормально подключиться к биржевому сервису при помощи exchange_service_host
        self.__exchange = FinamExchangeTestClient()

        for generator_set in generator_family.generator_families.values():
            for generator in generator_set.generators.values():
                self.__generators[generator.name] = generator

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
                # todo: получить каким-то образом цену текущего инструмента и расссчитать объем исходя из риск-менеджмента
                sign = 1 if decision == 'BUY' else -1
                p0 = 1
                v0_unsigned = 1
                id='1'
                punct=0.01

                v0 = v0_unsigned*sign
                rule = algorithm.risk_management.createRule(p0=p0, v0=v0)
                self.active_rules.append(rule)
                # orders.append(Order(id=id, punct=punct, initialVolume=v0_unsigned, executedVolume=0, buy=sign > 0, price=p0))

        for rule in self.active_rules:
            order, id = rule.order(candle)
            if order is LimitOrderRequest:
                limit_orders[id].append(order)
            elif order is MarketOrderRequest:
                market_orders[id].append(order)

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
                market_orders[market_orders_id] = [MarketOrderRequest(id=market_orders_id, punct=punct, buy=buy_reduced, volume=volume_reduced)]

            assert len(market_orders[market_orders_id]) == 1

            self.__exchange.market_order(market_orders[market_orders_id][0])

        for limit_orders_list in limit_orders.values():
            for limit_order in limit_orders_list:
                self.__exchange.limit_order(limit_order)