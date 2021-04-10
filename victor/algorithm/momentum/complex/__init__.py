from victor.algorithm import ProbabilityAlgorithm
from victor.config import GENERATOR_MAX_DEQUE_LENGTH
from victor.exchange.types import Instrument
from victor.generators.generator.filters.time_filter import OnlyMarketOpening, Market
from victor.generators.generator.patterns.bar_rotation import BarRotationGenerator
from victor.generators.generator.patterns.breakout import Breakout, BreakoutDown
from victor.generators.generator.technical_indicators.average import EMA
from victor.generators.generator.technical_indicators.average.EMA import EMADeviation
from victor.risk_management import RiskManagement

N = 2
M = 15

EMA_N = 233


class MainAlgorithm(ProbabilityAlgorithm):
    def __init__(self, instrument: Instrument, risk_management: RiskManagement, market: Market,
                 enable_shorts: bool = False, enable_longs=True):
        ProbabilityAlgorithm.__init__(self, MainAlgorithm.make_name(instrument), risk_management, instrument)

        self.enable_shorts = enable_shorts
        self.enable_longs = enable_longs

        self._add_dependency(BarRotationGenerator(False, instrument, limit=GENERATOR_MAX_DEQUE_LENGTH))
        self._add_dependency(Breakout(n=N, m=M, instrument=instrument))
        self._add_dependency(OnlyMarketOpening(instrument, market))
        ema_generator = EMA(EMA_N, None, instrument, GENERATOR_MAX_DEQUE_LENGTH, 'close')
        self._add_dependency(ema_generator)
        ema_generator_name = ema_generator.name
        ema_dev_gen = EMADeviation(ema_generator_name, instrument, GENERATOR_MAX_DEQUE_LENGTH,
                                   lambda candle: candle['close'])
        self._add_dependency(ema_dev_gen)

        self.bar_rotation = self.general_pool.select_generator(BarRotationGenerator, self.instrument, short=False)
        self.breakout = self.general_pool.select_generator(Breakout, self.instrument, n=N, m=M)
        self.time_filter = self.general_pool.select_generator(OnlyMarketOpening, self.instrument)
        self.ema = self.general_pool.select_generator(EMA, self.instrument, target_generator_name=None, n=EMA_N,
                                                      use_candle='close')
        self.ema_dev = ema_dev_gen

        if enable_shorts:
            self.bar_rotation_short = BarRotationGenerator(True, instrument, limit=GENERATOR_MAX_DEQUE_LENGTH)
            self._add_dependency(self.bar_rotation_short)
            self.breakout_short = BreakoutDown(n=N, m=M, instrument=instrument)
            self._add_dependency(self.breakout_short)

    def _probability(self) -> float:
        bar_rotation = self.bar_rotation.value()
        breakout = self.breakout.value()
        delta_min = self.time_filter.value()
        ema_dev_value = self.ema_dev.value()

        if not 15 <= delta_min <= 60:
            return 0

        if self.enable_longs and bar_rotation > 15 and breakout > 1 and ema_dev_value > 0:
            return 1
        elif not self.enable_shorts:
            return 0

        breakout_short = self.breakout_short.value()
        bar_rotation_short = self.bar_rotation_short.value()

        if bar_rotation_short > 0 and breakout_short > 0 and ema_dev_value < 0:
            return -1
        else:
            return 0
