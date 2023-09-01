from pathlib import Path

# Get the path of the current file
CURRENT_FILE_PATH = Path(__file__)

# Get the parent directory of the current file, which is the project root directory
PROJECT_ROOT = CURRENT_FILE_PATH.parent.parent

# Concatenate to form the complete DATA_DIR path
DATA_DIR = PROJECT_ROOT / "data"

# Concatenate to form specific file paths
MC_DATA_PATH = DATA_DIR / "mC_downsample.zarr"
RNA_DATA_PATH = DATA_DIR / "RNA_downsample.zarr"

GENE_NAME_IDS = DATA_DIR / "modified_gencode.vM23.primary_assembly.annotation.gene.flat.tsv.gz"

META_DATA_PATH_UNFORMATTED_PATH = DATA_DIR / "metadata"/"meta"/"{}_meta.csv"
SPATIAL_RATIO_DATA_UNFORMATTED_PATH = DATA_DIR / "metadata"/"ratio"/"{}_ratio.csv"
SPATIAL_META_CLUSTER = DATA_DIR / "metadata"/"merfish_metacluster.csv"





