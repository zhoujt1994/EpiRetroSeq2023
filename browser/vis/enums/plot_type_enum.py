from enum import Enum


class PlotType(Enum):
    CLUSTER = 'Cluster'
    DISSECTION_REGION = 'DissectionRegion'
    GENE_EXP = 'RNA'
    MC_EXP = 'mCH'
    TARGET = 'Target'
    CO_CLUSTER = 'CoCluster'


class ActivateType(Enum):
    CELL_TYPES = 'CellTypes'
    CO_CLUSTER = 'CoCluster'
