import pickle

from tqdm import tqdm

from victor.utils.trade_toolkit import Portfolio

ticker_column = '<TICKER>'


class XiEta(object):
    """
    Необходимые параметры:
    d - мера расстояния в пунктах
    sl - длина стоп-лосса
    k - множитель объема в алгоритме Мартингейла
    V - рабочий объем
    b0 - стоимость одного пункта в валюте
    data - данные из ФИНАМ по инструменту
    """

    def __init__(self, verbose=False, gamma=0.0005, d=None, sl=None, k=None, V=None, b0=None, data=None):
        self.d = d
        self.sl = sl
        self.k = k
        self.V = V
        self.b0 = b0
        self.data = data
        self.days = list(map(lambda x: x.day, data['<DATETIME>']))
        self.verbose = verbose
        self.gamma = gamma
        self.ticker = self.data[ticker_column][0]
        self.S_values_xi = None
        self.S_values_eta = None

        self.close_values = data['<CLOSE>'].values
        self.high_values = data['<HIGH>'].values
        self.low_values = data['<LOW>'].values

    def __get_file_name(self, t=None):
        assert (t == 'xi' or t == 'eta')
        return f'{self.ticker}_(d={self.d};sl={self.sl};{t})'

    def get_Eta(self, noload=False):
        """
        Возвращает набор eta-значений для инструмента
        """
        if self.S_values_eta == None:
            try:
                fi = open(self.__get_file_name('eta'), 'rb')
                self.S_values_eta = pickle.load(fi)
                fi.close()
                print('get_Eta returning cached value')
                return self.S_values_eta
            except IOError:
                if noload:
                    return []
                # В первый раз считаем
                self.S_values_eta = [self.__calculate_S_value_eta(i) for i in tqdm(range(len(self.data)))]
                fo = open(self.__get_file_name('eta'), 'wb')
                pickle.dump(self.S_values_eta, fo)
                fo.close()
                return self.S_values_eta
        else:
            print('get_Eta returning class-stored value')
            return self.S_values_eta

    def get_Xi(self, noload=False):
        """
        Возвращает набор xi-значений для инструмента
        """
        if self.S_values_xi == None:
            try:
                fi = open(self.__get_file_name('xi'), 'rb')
                self.S_values_xi = pickle.load(fi)
                fi.close()
                print('get_Xi returning cached value')
                return self.S_values_xi
            except IOError:
                if noload:
                    return []
                self.S_values_xi = [self.__calculate_S_value_xi(i) for i in tqdm(range(len(self.data)))]
                fo = open(self.__get_file_name('xi'), 'wb')
                pickle.dump(self.S_values_xi, fo)
                fo.close()
                return self.S_values_xi
        else:
            print('get_Xi returning class-stored value')
            return self.S_values_xi

    def __calculate_S_value_eta(self, initial_index=0):
        k = initial_index + 1
        s = 0
        p0 = self.close_values[initial_index]
        d = self.d * self.b0
        sl = self.sl * self.b0
        while k < len(self.data):
            p = self.close_values[k]
            if p > p0 + sl:
                break
            elif p < p0 - d * (s + 1):
                s += 1
                continue
            elif s > 0 and p > p0 + d * (1 - s):
                break
            k += 1
        return s

    def __calculate_S_value_xi(self, initial_index=0):
        k = initial_index + 1
        s = 0
        p0 = self.close_values[initial_index]
        day = self.days[initial_index]
        d = self.d * self.b0
        sl = self.sl * self.b0
        while k < len(self.data):
            current_day = self.days[k]
            p = self.close_values[k]
            if current_day != day:
                break
            if self.low_values[k] < p0 - sl:
                break
            elif self.high_values[k] > p0 + d * (s + 1):
                s += 1
                continue
            elif s > 0 and self.low_values[k] < p0 + d * (s - 1):
                break
            k += 1
        return s

    def S_values_map(self, s):
        """
        Маппинг, полезный для отображения xi-, eta-значений на графике
        """
        if s == 0:
            return 'or'
        elif s == 1:
            return 'oy'
        elif s == 2:
            return 'ob'
        elif s >= 3:
            return 'og'

    def R_Martin(self, S=None, gamma=0.0005, t=None, p0=None, alpha=None, K=None):
        """
        Прибыль по Мартингейлу
        """
        assert (S >= 0)
        assert (t == 'xi' or t == 'eta')
        assert (p0 > 0)
        assert (alpha > 0)
        assert (K > 0)

        sl = self.sl * self.b0
        d = self.d * self.b0
        V = self.V
        portfolio = Portfolio(verbose=self.verbose, gamma=gamma)
        if t == 'xi':
            if S == 0:
                portfolio.sell(p0, V)
                portfolio.buy(p0 - sl, V)
                return portfolio.result()
            elif S > 0:
                k = 0
                portfolio.sell(p0, V)
                while k < S:
                    rest = portfolio.getV()
                    portfolio.sell(p0 + d * (k + 1), -rest * K)
                    k += 1
                rest = portfolio.getV()
                assert (rest < 0)
                portfolio.buy(p0 + d * (S - 1), -rest)
                return portfolio.result()

    def R(self, S=None, gamma=0.0005, t=None, p0=None, alpha=None):
        """
        Прибыль для стратегии t на S
        """
        assert (S >= 0)
        assert (t == 'xi' or t == 'eta')
        assert (p0 > 0)
        assert (alpha > 0)
        sl = self.sl * self.b0
        d = self.d * self.b0
        V = self.V
        portfolio = Portfolio(verbose=self.verbose, gamma=gamma)
        if t == 'xi':
            if S == 0:
                portfolio.buy(p0, V)
                portfolio.sell(p0 - sl, V)
                return portfolio.result()
            elif S > 0:
                k = 0
                portfolio.buy(p0, V)
                while k < S:
                    if portfolio.getV() - alpha * V <= 0:
                        rest = portfolio.getV()
                        assert (rest > 0)
                        portfolio.sell(p0 + d * (k + 1), rest)
                        return portfolio.result()
                    portfolio.sell(p0 + d * (k + 1), alpha * V)
                    k += 1
                rest = portfolio.getV()
                assert (rest > 0)
                portfolio.sell(p0 + d * (S - 1), rest)
                return portfolio.result()
        elif t == 'eta':
            if S == 0:
                portfolio.sell(p0, V)
                portfolio.buy(p0 + sl, V)
                return portfolio.result()
            elif S > 0:
                k = 0
                portfolio.sell(p0, V)
                while k < S:
                    rest = portfolio.getV()
                    if rest + alpha * V >= 0:
                        portfolio.buy(p0 - d * (k + 1), -rest)
                        return portfolio.result()
                    else:
                        portfolio.buy(p0 - d * (k + 1), alpha * V, )
                    k += 1
                rest = portfolio.getV()
                assert (rest < 0)
                portfolio.buy(p0 - d * (S - 1), -rest)
                return portfolio.result()
