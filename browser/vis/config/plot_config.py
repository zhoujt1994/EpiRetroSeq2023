from vis.enums.plot_type_enum import PlotType


class PlotConfig:
    def __init__(self):
        self.plot_type_dict = {
            'AIBS_10x': [PlotType.CLUSTER, PlotType.DISSECTION_REGION, PlotType.GENE_EXP, PlotType.CO_CLUSTER],
            'CEMBA_snmC': [PlotType.CLUSTER, PlotType.DISSECTION_REGION, PlotType.MC_EXP, PlotType.CO_CLUSTER],
            'CEMBA_EpiRetro': [PlotType.CLUSTER, PlotType.DISSECTION_REGION, PlotType.TARGET, PlotType.CO_CLUSTER],
        }
        self.td_key_list = ["plot", 'modality', 'region', 'subregion', 'cell_type', 'co_cluster', 'gene_name',
                            'target', 'down_sample', 'coords', 'zscore']

        self.down_sample_dict = {'10000 (Fast)': 10000,
                                 '50000 (Slow)': 50000,
                                 'ALL (Very Slow)': 9999999}

        self.heat_map_size = {'width': 1400, 'height': 1000}

        self.zscore_cnorm = [-3, 3]


plot_config = PlotConfig()
