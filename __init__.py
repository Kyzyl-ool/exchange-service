from flask import Flask
from flask_socketio import SocketIO, send, emit
import configuration
from flask import request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@socketio.on('subscribe')
def handle_subscribe(data):
    namespace = data['exchange'] + ':' + data['instrument']
    configuration.exchanges[data['exchange']].ohlc_subscribe(
        data['instrument'],
        data['timeframe'],
        lambda candle: send(candle, namespace=namespace)
    )


@app.route('/limit/<exchange_id>/<instrument>', methods=['POST'])
def handle_limit_order(exchange_id, instrument):
    punct = request.json['punct']
    buy = request.json['buy']
    price = request.json['price']
    volume = request.json['volume']

    return configuration.exchanges[exchange_id].limit_order({
        'id': instrument,
        'punct': punct,
        'buy': buy,
        'price': price,
        'volume': volume
    })


@app.route('/market/<exchange_id>/<instrument>', methods=['POST'])
def handle_market_order(exchange_id, instrument):
    punct = request.json['punct']
    buy = request.json['buy']
    volume = request.json['volume']

    return configuration.exchanges[exchange_id].market_order({
        'id': instrument,
        'punct': punct,
        'buy': buy,
        'volume': volume
    })


@app.route('/orders/<exchange_id>/<instrument>', methods=['GET'])
def handle_get_orders(exchange_id, instrument):
    return configuration.exchanges[exchange_id].orders[instrument]


if __name__ == '__main__':
    socketio.run(app, host=configuration.host, port=configuration.port)
