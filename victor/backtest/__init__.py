from datetime import timedelta
from typing import List

from victor.algorithm import Algorithm
from matplotlib import pyplot as plt
from tqdm.notebook import tqdm
import pandas as pd

from victor.backtest.configs import AAPLConfig
from victor.utils.D import add_col, make_datetime
from victor.utils.I import ema_g
from victor.utils.S import XiEta
from victor.utils.bar_rotation import BarRotationHA
from victor.utils.breakout import Breakout


def dd_max(summary_history, initial_money=100000):
    maximal = summary_history[0]
    dd_max = 0
    for x in summary_history:
        maximal = max(x, maximal)
        dd_max = max(maximal - x, dd_max)

    return dd_max / (maximal + initial_money)


def make_array_from_recognizer(recognizer, metric, df):
    brs = []

    for i, row in tqdm(df.iterrows()):
        item = recognizer.get_next(
            close=row['<CLOSE>'],
            open=row['<OPEN>'],
            high=row['<HIGH>'],
            low=row['<LOW>'],
            volume=row['<VOL>'],
            time=row['<DATETIME>'],
        )

        brs.append(metric(item))

    return brs


def profit_factor(summary):
    changes = []

    for i in range(1, len(summary)):
        changes.append(summary[i] - summary[i - 1])

    return -sum([x for x in changes if x > 0]) / sum([x for x in changes if x < 0])


class Shallow(AAPLConfig):
    algorithm: Algorithm
    xieta: XiEta
    xis: List[float]
    df: pd.DataFrame

    def __init__(self, algorithm: Algorithm):
        self.algorithm = algorithm

    def __backtest(self, func, xis, t, gamma=0.0005, alpha=0.3, initial_money=100000):
        Rs = {}

        summary = 0
        summary_history = [0]
        n_failure = 0

        for i, s in tqdm(enumerate(xis)):
            long = func(i)
            if long:
                if s not in Rs:
                    Rs[s] = self.xieta.R(S=s, t=t, p0=100, alpha=alpha, gamma=gamma)

                summary += Rs[s]
                summary_history.append(summary)

        plt.plot(summary_history)
        plt.show()

        print('dd_max:', dd_max(summary_history, initial_money))

        return summary_history

    def prepare(self, d: float, sl: float, V: float, punct: float):
        df = pd.read_csv(self.filename, dtype=str)
        df = add_col(df, '<DATETIME>', make_datetime(df))
        df['<CLOSE>'] = pd.to_numeric(df['<CLOSE>'])
        df['<HIGH>'] = pd.to_numeric(df['<HIGH>'])
        df['<LOW>'] = pd.to_numeric(df['<LOW>'])
        df['<VOL>'] = pd.to_numeric(df['<VOL>'])
        df['<OPEN>'] = pd.to_numeric(df['<OPEN>'])
        df['<DATETIME>'] -= timedelta(minutes=1)
        self.df = df

        self.brs_up = make_array_from_recognizer(BarRotationHA(False),
                                                 lambda item: abs(item[0] - 5) + abs(item[1] - 2) if item else -1)
        self.breakouts_up = make_array_from_recognizer(Breakout(2, 15),
                                                       lambda item: item[0]['d2'] - item[0]['d1'] + len(
                                                           item) * self.punct if item else -1)
        self.delta_ts = [x.time().minute + (x.time().hour - (17.5 if x.month >= 4 else 16.5)) * 60 + (
            0 if 6 <= x.month <= 8 else 10000) for x in self.df['<DATETIME>']]

        ema_gen = ema_g(df['<CLOSE>'], 233)
        self.emas = [next(ema_gen) for _ in tqdm(range(len(df)))]

        self.xieta = XiEta(verbose=True, d=d, sl=sl, V=V, b0=punct, data=self.df)
        self.xis = self.xieta.get_Xi()

    def run(self):
        summary = self.__backtest(alpha=0.2, xis=self.xis, t='xi',
                                  func=lambda i: 15 <= self.delta_ts[i] <= 60 and 0 < self.breakouts_up[i] and 0 <
                                                 self.brs_up[i] and self.emas[
                                                     i] < self.df['<CLOSE>'][i], gamma=0.0005)

        print('profit_factor', profit_factor(summary))
        print('recovery factor', summary[-1] / (100000 * 0.03))
        print('revenue', summary[-1] / 100000)
        print('=================================')

