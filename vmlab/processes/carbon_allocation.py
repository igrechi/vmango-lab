import xsimlab as xs
import numpy as np
from scipy.sparse import csgraph

from ._base.parameter import ParameterizedProcess
from . import (
    topology,
    growth,
    phenology
)


@xs.process
class CarbonAllocation(ParameterizedProcess):

    GU = xs.foreign(topology.Topology, 'GU')
    adjacency = xs.foreign(topology.Topology, 'adjacency')
    nb_leaf = xs.foreign(growth.Growth, 'nb_leaf')
    nb_fruit = xs.foreign(phenology.Phenology, 'nb_fruit')
    gu_stage = xs.foreign(phenology.Phenology, 'gu_stage')

    distance_to_fruit = xs.any_object()
    is_in_distance_to_fruit = xs.any_object()
    allocation_share = xs.any_object()
    is_photo_active = xs.variable(dims='GU', intent='out')

    def initialize(self):

        super(CarbonAllocation, self).initialize()

        self.distance_to_fruit = np.array([], dtype=np.float32)
        self.is_in_distance_to_fruit = np.array([], dtype=np.bool)
        self.allocation_share = np.array([], dtype=np.float32)
        self.is_photo_active = np.zeros(self.GU.shape, dtype=np.float32)

    @xs.runtime(args=())
    def run_step(self):

        max_distance_to_fruit = self.parameters.max_distance_to_fruit

        is_fruting = (self.nb_fruit > 0.)
        is_leafy = (self.nb_leaf > 0.) & (self.gu_stage >= 4.)

        if np.any(is_fruting):

            self.distance_to_fruit = csgraph.shortest_path(
                self.adjacency,
                indices=np.flatnonzero(is_fruting),
                directed=False
            ).astype(np.float32)

            self.distance_to_fruit[self.distance_to_fruit > max_distance_to_fruit] = np.inf

            self.is_in_distance_to_fruit = np.isfinite(self.distance_to_fruit)
            sum_is_in_distance_to_fruit = np.sum(self.is_in_distance_to_fruit, axis=0)
            self.allocation_share = np.zeros(self.is_in_distance_to_fruit.shape, dtype=np.float32)
            self.allocation_share[:, sum_is_in_distance_to_fruit > 0] = self.is_in_distance_to_fruit[:, sum_is_in_distance_to_fruit > 0] / sum_is_in_distance_to_fruit[sum_is_in_distance_to_fruit > 0]

            # self.allocation_share = np.where(
            #     np.sum(self.is_in_distance_to_fruit, axis=0) > 0,
            #     self.is_in_distance_to_fruit / np.sum(self.is_in_distance_to_fruit, axis=0),
            #     0.
            # ).astype(np.float32)
            self.is_photo_active = ((np.sum(self.is_in_distance_to_fruit, axis=0) > 0) & is_leafy).astype(np.float32)
