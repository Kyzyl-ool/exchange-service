from threading import Thread
import sys
import os

from victor.app import app, runner

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

if __name__ == '__main__':
    thread = Thread(target=runner.run_sync)
    thread.start()

    thread2 = Thread(target=app.run)
    thread2.start()
