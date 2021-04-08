import logging
from datetime import datetime, timedelta
from threading import Thread

from dotenv import load_dotenv

from flask import Flask

from victor.algorithm.momentum.complex import MainAlgorithm
from victor.exchange.tinkoff import TinkoffExchangeClient
from victor.exchange.types import Instrument, Candle, Timeframe
from victor.generators.generator.filters.time_filter import Market
from victor.risk_management.momentum import MomentumRiskManagement
from victor.trader import Trader

import asyncio

load_dotenv()

logging.basicConfig(level=logging.DEBUG)


class Runner:
    exchange = TinkoffExchangeClient()
    loop = asyncio.get_event_loop()

    def __init__(self):
        self.instrument = Instrument(
            punct=0.01,
            id='BBG004730RP0'
        )

        self.risk_management = MomentumRiskManagement(
            stop_loss=40,
            d=100,
            instrument=self.instrument,
            alpha=0.2,
            v0=10,
        )
        self.trader = Trader(
            algorithms=[
                MainAlgorithm(
                    instrument=self.instrument,
                    risk_management=self.risk_management,
                    market=Market.rus
                )
            ],
            exchange=self.exchange,
            max_orders=1
        )

    def handler(self, candle: Candle):
        self.trader.general_pool.update_generators(candle)
        self.trader.perform_signals(candle)
        logging.debug(candle)

    async def init(self):
        await self.exchange.init()

    async def run(self):
        self.trader.general_pool.preload_candles(
            await self.exchange.preload_candles(self.instrument, datetime.now() - timedelta(days=60, minutes=30),
                                                datetime.now(),
                                                Timeframe.M5))
        await self.exchange.ohlc_subscribe('BBG004730RP0', Timeframe.M5, self.handler)

    def run_sync(self):
        self.loop.run_until_complete(self.init())
        self.loop.run_until_complete(self.run())


runner = Runner()

app = Flask(__name__)


@app.route('/')
def get_data():
    return runner.trader.general_pool.get_generators_log()


if __name__ == '__main__':
    thread = Thread(target=runner.run_sync)
    thread.start()
    app.run()