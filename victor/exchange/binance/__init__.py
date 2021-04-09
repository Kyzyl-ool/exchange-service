from binance.client import Client
import os

from binance.websockets import BinanceSocketManager

from victor.exchange.abstract import AbstractExchangeClient


class BinanceExchange(AbstractExchangeClient):
    client = Client(os.environ['BINANCE_API_KEY'], os.environ['BINANCE_SECRET_KEY'])
    depth = client.get_order_book(symbol='BNBBTC')
    bm = BinanceSocketManager(client)
    prices = {}
    socket_keys = []

    def run_depth(self, process_message):
        diff_key = self.bm.start_depth_socket('BNBBTC', process_message)
        partial_key = self.bm.start_depth_socket('BNBBTC', process_message,
                                                 depth=BinanceSocketManager.WEBSOCKET_DEPTH_5)
        self.bm.start()

    def run_arbitrage(self, *args):
        def process(msg, instrument):
            bid = msg['bids'][0][0]
            ask = msg['asks'][0][0]
            self.prices[instrument] = (float(bid), float(ask))
            # print(self.prices)
            a1 = (self.prices['BTCUSDT'][0]*1.00015) * (self.prices['BNBBTC'][0]*1.0015) / self.prices['BNBUSDT'][1]*(2-1.0005) - 2*0.001 - 0.0004
            a2 =  (self.prices['BNBUSDT'][0]*1.0005) / (self.prices['BTCUSDT'][1]*(2-1.00015)) / (self.prices['BNBBTC'][1]*(2-1.0015)) - 2*0.001 - 0.0004
            print( max(a1, a2) )

        def process_message(instrument):
            return lambda x: process(x, instrument)

        for arg in args:
            partial_key = self.bm.start_depth_socket(arg, process_message(arg),
                                                     depth=BinanceSocketManager.WEBSOCKET_DEPTH_5)
            self.socket_keys.append(partial_key)
        self.bm.start()

    def close_connections(self):
        self.bm.close()

        for key in self.socket_keys:
            self.bm.stop_socket(key)
