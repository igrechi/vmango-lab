import pathlib
import xsimlab as xs
import numpy as np
import openalea.lpy as lpy
import openalea.plantgl.all as pgl

from . import topology


@xs.process
class Geometry:

    lsystem = None

    lstring = xs.foreign(topology.Topology, 'lstring')
    nb_inflo = xs.foreign(topology.Topology, 'nb_inflo')
    phenology = xs.group_dict('phenology')
    growth = xs.group_dict('growth')

    scene = xs.any_object()

    def initialize(self):

        self.lsystem = lpy.Lsystem(str(pathlib.Path(__file__).parent.joinpath('geometry.lpy')), {
            'process': self
        })

    @xs.runtime(args=('step'))
    def run_step(self, step):

        self.scene = self.lsystem.sceneInterpretation(self.lstring)
