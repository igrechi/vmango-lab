import xsimlab as xs
import numpy as np
import datetime

from . import parameters
from . import environment
from . import topology


@xs.process
class Phenology():

    params = xs.foreign(parameters.Parameters, 'phenology')

    GU = xs.foreign(topology.Topology, 'GU')

    TM = xs.foreign(environment.Environment, 'TM')

    bloom_date = xs.variable(
        dims=('GU'),
        intent='inout',
        description='bloom date',
        attrs={
            'unit': 'date'
        }
    )

    gu_growth_tts = xs.variable(
        dims=('GU'),
        intent='out'
    )

    leaf_growth_tts = xs.variable(
        dims=('GU'),
        intent='out'
    )

    gu_pheno_tts = xs.variable(
        dims=('GU'),
        intent='out'
    )

    DAB = xs.variable(
        dims=('GU'),
        intent='out',
        description='days after bloom',
        attrs={
            'unit': 'd'
        }
    )

    dd_cum_gu = xs.variable(
        dims=('GU'),
        intent='out',
        description='cumulated degree-days of the current day after bloom date',
        attrs={
            'unit': 'dd'
        }
    )

    dd_delta_gu = xs.variable(
        dims=('GU'),
        intent='out',
        description='daily variation in degree days',
        attrs={
            'unit': 'dd day-1'
        }
    )

    def initialize(self):

        self.gu_growth_tts = np.zeros(self.GU.shape)
        self.leaf_growth_tts = np.zeros(self.GU.shape)
        self.gu_pheno_tts = np.zeros(self.GU.shape)

        self.bloom_date = np.array([np.datetime64(datetime.date.fromisoformat(bloom_date)).astype('datetime64[D]')
                                    for bloom_date in self.bloom_date])

        self.dd_delta_gu = np.zeros(self.GU.shape)
        self.dd_cum_gu = np.zeros(self.GU.shape)

    @xs.runtime(args=('step', 'step_start'))
    def run_step(self, step, step_start):

        _, params = self.params
        Tbase_gu = params.Tbase_gu
        Tbase_leaf = params.Tbase_leaf
        Tbase_fruit = params.Tbase_fruit

        self.gu_growth_tts = self.gu_growth_tts + max(0, self.TM - Tbase_gu)
        self.leaf_growth_tts = self.leaf_growth_tts + max(0, self.TM - Tbase_leaf)

        self.DAB = np.where(
            step_start >= self.bloom_date,
            (step_start - self.bloom_date).astype('timedelta64[D]') / np.timedelta64(1, 'D'),
            -1
        )

        self.dd_delta_gu = np.where(
            step_start >= self.bloom_date,
            max(0, self.TM - Tbase_fruit),
            0.
        )

        self.dd_cum_gu = np.where(
            step_start >= self.bloom_date,
            self.dd_cum_gu + self.dd_delta_gu,
            0.
        )

    def finalize_step(self):
        pass

    def finalize(self):
        pass
