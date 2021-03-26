from victor.exchange.types import Instrument
from victor.generators.generator.patterns.breakout import Breakout
from victor.generators.generator_set import GeneratorSet


class BreakoutGeneratorSet(GeneratorSet):
    def __init__(self, instrument: Instrument):
        breakout = self.general_pool.get_generator(Breakout.make_name(instrument), instrument)

        GeneratorSet.__init__(self, name=BreakoutGeneratorSet.make_name(instrument), generators=[breakout],
                              instrument=instrument)

    @staticmethod
    def make_name(instrument: Instrument):
        instrument_id = instrument['id']
        return f'breakout-generator-set({instrument_id})'
