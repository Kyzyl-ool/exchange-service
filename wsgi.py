from threading import Thread
from victor.app import app, runner
from gevent.pywsgi import WSGIServer

if __name__ == '__main__':
    thread = Thread(target=runner.run_sync)
    thread.start()

    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
