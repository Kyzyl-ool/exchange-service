import asyncio
from threading import Thread

from dotenv import load_dotenv

from app import app

load_dotenv()

from victor.exchange.binance import BinanceExchange

binance = BinanceExchange()

if __name__ == '__main__':
    try:
        binance.run_arbitrage('BNBBTC', 'BTCUSDT', 'BNBUSDT')
    except KeyboardInterrupt:
        binance.close_connections()
