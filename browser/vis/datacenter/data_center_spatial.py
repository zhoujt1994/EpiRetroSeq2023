import numpy as np
import pandas as pd
from vis.config.path_config import SPATIAL_RATIO_DATA_UNFORMATTED_PATH, SPATIAL_META_CLUSTER
from vis.utils.common_utils import handle_file_exceptions, controlled_cached


@handle_file_exceptions
@controlled_cached()
def load_heat_map_data(region):
    path = str(SPATIAL_RATIO_DATA_UNFORMATTED_PATH).format(region)
    return pd.read_csv(path, index_col=0, header=0)


@handle_file_exceptions
@controlled_cached()
def load_meta_cluster():  # cache
    return pd.read_csv(SPATIAL_META_CLUSTER, index_col=0, header=0)


def get_spatial_scatter_data(sample, region, co_cluster_list):
    plot_data = load_meta_cluster()

    plot_data[['x', 'y']] = plot_data[['spatial_0', 'spatial_1']].astype(np.float16)
    plot_data['cocluster'] = plot_data['cocluster'].fillna(9999999).astype(int)

    plot_data['bottom'] = plot_data['sample'] == sample
    plot_data['middle'] = (plot_data['bottom']) & (plot_data['RegionGroup'] == region)

    if 'ALL' in co_cluster_list:
        plot_data['upper'] = plot_data['middle']
    elif 'None' in co_cluster_list:
        plot_data['upper'] = False
    else:
        co_cluster_list = list(map(int, co_cluster_list))
        plot_data['upper'] = plot_data['middle'] & plot_data['cocluster'].isin(co_cluster_list)

    return plot_data


def get_co_clusters(region):
    data = load_heat_map_data(region)
    sorted_list = sorted(data.index.tolist(), key=lambda x: int(x.split(':')[0]))
    return sorted_list
