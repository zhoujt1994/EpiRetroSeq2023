import xarray
import pandas as pd
import numpy as np
from vis.utils.common_utils import handle_file_exceptions
from vis.config.path_config import META_DATA_PATH_UNFORMATTED_PATH, RNA_DATA_PATH, MC_DATA_PATH
from vis.config.dataset_config import dataset_config
from vis.utils.common_utils import controlled_cached, calculate_zscore


@handle_file_exceptions
@controlled_cached()
def load_data(path):
    dataset = xarray.open_dataset(path, engine='zarr')
    return dataset


@handle_file_exceptions
@controlled_cached()
def read_csv_file(path):
    plot_data = pd.read_csv(path, index_col=0, low_memory=False)
    return plot_data


def get_data_by_gene_name(gene_name, modality, normalization_factor=1e5):
    data = load_data(RNA_DATA_PATH if modality == 'AIBS_10x' else MC_DATA_PATH)
    gene_id = dataset_config.gene2ens[gene_name]
    if gene_id is None:
        raise ValueError(f"Gene name '{gene_name}' not found in gene2ens dictionary.")
    if modality not in ['AIBS_10x', 'CEMBA_snmC']:
        return None

    # float-16 will overflow when calculates Z-score
    if modality == 'AIBS_10x':
        select_data = data.sel({'gene': gene_id})
        expression = select_data['gene_da_fc'].to_pandas()
        umi_count = select_data['umi_count']
        gene_data = (expression.div(umi_count, axis=0) * normalization_factor).astype(np.float32)
    elif modality == 'CEMBA_snmC':
        gene_data = (data.sel({'geneslop2k-vm23': gene_id, 'mc_type': 'CHN'})['geneslop2k-vm23_da_frac_fc']
                     .to_pandas()).astype(np.float32)
    return gene_data


def get_active_and_background_data(
        region: str,
        subregions: list,
        modality: str,
        cell_types: list = None,
        gene_name: str = None,
        targets: list = None,
        co_clusters: list = None,
        gene_zscore: bool = False,
):
    meta_data_path = str(META_DATA_PATH_UNFORMATTED_PATH).format(region)
    plot_data = read_csv_file(meta_data_path)
    plot_data = reprocess(plot_data)
    plot_data[['x', 'y']] = plot_data[['tsne_0', 'tsne_1']].astype(np.float16)

    mapping_dict = 'rs1_subregion_dict' if modality == 'CEMBA_snmC' else 'rs2_subregion_dict'

    if modality == 'AIBS_10x' or 'ALL' in subregions:
        plot_data['active'] = (plot_data['Modality'] == modality)
    else:
        selected_subregions = []
        selected_subregions += [sr for region in subregions for sr in
                                dataset_config.region_mapping[mapping_dict].get(region, [])]

        selected_subregions = set(selected_subregions)
        plot_data['active'] = (plot_data['DissectionRegion'].isin(selected_subregions)) & (
            plot_data['Modality'] == modality)

    subtype_column, annot_column = ('RNA_cluster', 'L2_annot') if modality == 'AIBS_10x' else ('mC_cluster', 'L2_annot')
    plot_data[['SubType', 'Annot']] = plot_data[[subtype_column, annot_column]]

    if cell_types and "ALL" not in cell_types:
        plot_data['active'] &= plot_data['Annot'].isin(cell_types)

    gene_meta_data_dict = {}
    if gene_name and modality != 'CEMBA_EpiRetro':
        gene_data = get_data_by_gene_name(gene_name, modality)
        gene_meta_data_dict = {
            'modality': modality,
            'gene_name': gene_name,
            'min': int(np.min(gene_data)),
            'max': int(np.max(gene_data)),
        }
        if gene_zscore:
            gene_data = (gene_data - np.mean(gene_data)) / np.std(gene_data)

        plot_data[gene_name] = gene_data.reindex(plot_data.index).values

    if targets and "" not in targets and modality == 'CEMBA_EpiRetro' and 'ALL' not in targets:
        plot_data['active'] &= plot_data['Target'].isin(targets)

    if co_clusters and "ALL" not in co_clusters:
        co_clusters = list(map(int, co_clusters))
        plot_data['active'] &= plot_data['cocluster'].isin(co_clusters)

    active_data = plot_data[plot_data['active']].copy()
    background_data = plot_data[~plot_data['active']].copy()

    result = {
        'active_data': active_data,
        'background_data': background_data,
        'gene_data_meta_dict': gene_meta_data_dict
    }
    return result


@controlled_cached()
def get_hidden_options(region: str,
                       subregions: tuple,  # required by cache
                       modality: str):
    result = \
        get_active_and_background_data(region=region, subregions=list(subregions), modality=modality)
    activate_data = result['active_data']
    cell_type = []
    subtype_column, annot_column = ('RNA_cluster', 'L2_annot') if modality == 'AIBS_10x' else ('mC_cluster', 'L2_annot')
    if modality != 'CEMBA_EpiRetro':
        cell_type = activate_data[annot_column].unique()
    target = []
    if modality == 'CEMBA_EpiRetro':
        target = activate_data['Target'].unique()
    co_cluster = activate_data['cocluster'].unique()

    return sorted(cell_type), sorted(target), sorted(co_cluster)


def get_by_co_cluster(region: str,
                      co_cluster_list: list):
    meta_data_path = str(META_DATA_PATH_UNFORMATTED_PATH).format(region)
    plot_data = read_csv_file(meta_data_path)
    plot_data = reprocess(plot_data)
    plot_data[['x', 'y']] = plot_data[['tsne_0', 'tsne_1']].astype(np.float16)
    plot_data['active'] = (plot_data['cocluster'].isin(co_cluster_list))

    active_data = plot_data[plot_data['active']].copy()
    background_data = plot_data[~plot_data['active']].copy()

    return active_data, background_data


@controlled_cached()
def get_gene_name(modality):
    """
    Extracts gene names from mc data or rna data
    """
    MODALITY_PATHS = {
        'AIBS_10x': RNA_DATA_PATH,
        'CEMBA_snmC': MC_DATA_PATH
    }
    gene = 'gene' if modality == 'AIBS_10x' else 'geneslop2k-vm23'
    if modality in MODALITY_PATHS:
        data = load_data(MODALITY_PATHS[modality])
        gene_ids = data.get_index(gene)
        ens2gene_mapping = dataset_config.ens2gene
        gene_names = [ens2gene_mapping[gene_id] for gene_id in gene_ids]
        return gene_names
    else:
        return []


def reprocess(plot_data):
    plot_data.rename(columns={'Study': 'Modality'}, inplace=True)
    return plot_data
