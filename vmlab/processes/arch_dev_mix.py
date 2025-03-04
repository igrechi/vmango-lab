import xsimlab as xs
import numpy as np

from . import topology, arch_dev_veg_within
from ._base.probability_table import ProbabilityTableProcess


@xs.process
class ArchDevMix(ProbabilityTableProcess):

    GU = xs.foreign(topology.Topology, 'GU')
    seed = xs.foreign(topology.Topology, 'seed')
    appeared = xs.foreign(topology.Topology, 'appeared')
    current_cycle = xs.foreign(topology.Topology, 'current_cycle')
    appearance_month = xs.foreign(topology.Topology, 'appearance_month')
    is_initially_terminal = xs.foreign(topology.Topology, 'is_initially_terminal')
    sim_start_date = xs.foreign(topology.Topology, 'sim_start_date')

    has_veg_children_within = xs.foreign(arch_dev_veg_within.ArchDevVegWithin, 'has_veg_children_within')

    tbls_has_mixed_inflo_children_between = None
    has_mixed_inflo_children_between = xs.variable(dims='GU', intent='out')

    def initialize(self):

        super(ArchDevMix, self).initialize()

        self.has_mixed_inflo_children_between = np.zeros(self.GU.shape, dtype=np.float32)

        probability_tables = self.get_probability_tables()

        self.tbls_has_mixed_inflo_children_between = probability_tables['has_mixed_inflo_children_between']

        self.run_step(-1)

    @xs.runtime(args=('step'))
    def run_step(self, step):

        appeared = (self.appeared == 1.) if step >= 0 else (self.is_initially_terminal == 1.)

        if np.any(appeared & (self.has_veg_children_within == 0.)):

            gu_indices = np.flatnonzero(appeared & (self.has_veg_children_within == 0.))

            if self.current_cycle in self.tbls_has_mixed_inflo_children_between:
                tbl = self.tbls_has_mixed_inflo_children_between[self.current_cycle]
                self.has_mixed_inflo_children_between[gu_indices] = self.get_binomial(tbl, gu_indices)
