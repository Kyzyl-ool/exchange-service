import logging

from flask import Flask

from victor.algorithm.momentum.complex import MainAlgorithm
from victor.exchange.tinkoff import TinkoffExchangeClient
from victor.exchange.types import Instrument, Candle, Timeframe
from victor.generators.generator.filters.time_filter import Market
from victor.risk_management.momentum import MomentumRiskManagement
from victor.trader import Trader

logging.basicConfig(level=logging.DEBUG)

exchange = TinkoffExchangeClient()

instrument = Instrument(
        punct=0.01,
        id='BBG004730RP0'
    )

risk_management = MomentumRiskManagement(
    stop_loss=40,
    d=100,
    instrument=instrument,
    alpha=0.2,
    v0=1000,
)
trader = Trader(
    algorithms=[
        MainAlgorithm(
            instrument=instrument,
            risk_management=risk_management,
            market=Market.rus
        )
    ],
    exchange=exchange,
    max_orders=1
)


def handler(candle: Candle):
    trader.general_pool.update_generators(candle)
    trader.exchange.update(candle)
    trader.perform_signals(candle)


async def run():
    await exchange.ohlc_subscribe('BBG004730RP0', Timeframe.M5, handler)


run()

app = Flask(__name__)

app.run()