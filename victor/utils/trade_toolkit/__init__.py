import logging
from datetime import datetime

eps = 0.000001  # мера близости двух чисел
COMMISSION = 0.0005
MAX_CALLS = 100


class Portfolio:
    def __init__(self, gamma=COMMISSION, verbose=False, initial_money=0):
        self.gamma = gamma
        self.equity = initial_money
        self.comission = 0
        self.V = 0
        self.verbose = verbose
        self.log = []
        self.__amount_of_calls = 0

    def __log(self, p, V, time):
        self.log.append({
            'p': p,
            'V': V,
            'time': time
        })

    def __watch_result(self, time: datetime):
        self.__amount_of_calls = min(self.__amount_of_calls + 1, MAX_CALLS)

        if self.__amount_of_calls >= MAX_CALLS and self.V == 0:
            logging.info(f'{self.result()}, {time}')

    def buy(self, p, V, time):
        if self.verbose:
            self.__log(p, V, time)
        self.comission += p * V * self.gamma
        self.equity -= p * V
        self.V += V

        self.__watch_result(time)

    def sell(self, p, V, time):
        if self.verbose:
            self.__log(p, -V, time)
        self.comission += p * V * self.gamma
        self.equity += p * V
        self.V -= V

        self.__watch_result(time)

    def clear(self):
        self.comission = 0
        self.equity = 0
        self.V = 0

    def getV(self):
        return self.V

    def getEquity(self):
        assert (abs(self.V) < eps)
        return self.equity

    def getComission(self):
        return self.comission

    def result(self):
        assert (self.V == 0)
        return self.equity - self.comission

    def getLog(self):
        return self.log
