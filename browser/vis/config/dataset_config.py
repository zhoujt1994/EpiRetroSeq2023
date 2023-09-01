import pandas as pd
from vis.config.path_config import GENE_NAME_IDS


class DatasetConfig:
    """
    Class for storing configuration and metadata related to the dataset.
    """
    def __init__(self):
        self.coord_names = ['T-SNE']

        self.modalities = ['AIBS_10x', 'CEMBA_snmC', 'CEMBA_EpiRetro']

        self.gene_meta = pd.read_csv(str(GENE_NAME_IDS),
                                     header=0, sep='\t', index_col=None).set_index('gene_id')

        self.gene2ens = self.gene_meta.reset_index().set_index('gene_name')['gene_id'].to_dict()
        self.ens2gene = self.gene_meta.reset_index().set_index('gene_id')['gene_name'].to_dict()
        self.co_clusters = 127

        self.region_mapping = {
            "region_name_to_acc": {
                "MOp": "Primary Motor Cortex",
                "SSp": "Primary Somatosensory Cortex",
                "ACA": "Anterior Cingulate Cortex",
                "AI": "Agranular Insular Cortex",
                "AUD": "Auditory Cortex",
                "RSP": "Retrosplenial Cortex",
                "PTLp": "Posterior Parietal Cortex",
                "VIS": "Visual Cortex",
                "CTX": "Isocortex",
                "CAa": "Ammon horn, anterior",
                "CAp": "Ammon horn, posterior",
                "DGa": "Dentate Gyrus, anterior",
                "DGp": "Dentate Gyrus, posterior",
                "HIP": "Hippocampal Region",
                "ENT": "Entorhinal Cortex",
                "RHP": "Retrohippocampal Region",
                "MOB": "Main Olfactory Bulb",
                "OLF": "Olfactory Bulb & Nucleus",
                "PIRa": "Piriform Cortex, anterior",
                "PIRp": "Piriform Cortex, posterior",
                "PIR": "Piriform Cortex",
                "AMY": "Amygdala",
                "STR": "Striatum",
                "PAL": "Pallidum",
                "THm": "Thalamus, medial",
                "THl": "Thalamus, lateral",
                "THp": "Thalamus, posterior",
                "TH": "Thalamus",
                "HY": "Hypothalamus",
                "SC": "Superior Colliculus",
                "MRN": "Midbrain Reticular Nucleus",
                "VTA": "Ventral Tegmental Area & Substantia Nigra, reticular",
                "PAG": "Periaqueductal Gray",
                "IC": "Inferior Colliculus",
                "MB": "Midbrain",
                "P": "Pons",
                "MY": "Medulla",
                "HB": "Hindbrain",
                "CBN": "Cerebellar Nuclei",
                "CBX": "Cerebellar Cortex"
            },
            # The dataset contains existing regions
            "region_to_subregion": {
                "CTX": ["MOp", "SSp", "ACA", "AI", "RSP", "AUD", "PTLp", "VIS"],  # not exists in previous metadata
                "HIP": ["CAa", "CAp", "DGa", "DGp"],
                "RHP": ["ENT"],
                "OLF": ["MOB"],
                "PIR": ["PIRa", "PIRp"],
                "STR": ["STR"],
                "PAL": ["PAL"],
                "AMY": ["AMY"],
                "TH": ["THm", "THl", "THp"],
                "HY": ["HY"],
                "MB": ["SC", "MRN", "VTA", "PAG", "IC"],
                "HB": ["P", "MY"]
            },
            "rna_region_dict": {
                "CTX": ["RSP", "ACA", "PL-ILA-ORB", "AI-CLA", "AId-AIv", "AId-AIv-AIp", "TEa-PERI-ECT",
                        "AUD-TEa-PERI-ECT", "AUD", "PTLp", "VIS", "VIS-PTLp", "VISl", "VISm", "VISp", "MOp", "MOs-FRP",
                        "MO-FRP", "SSp", "SSs-GU-VISC-AIp", "SS-GU-VISC"],
                "HIP": ["HIP", "HIP - CA"],
                "OLF": ["OLF - MOB-AOB", "OLF - AON-TT-DP"],
                "RHP": ["PAR-POST-PRE-SUB-ProS", "ENT"],
                "PIR": ["OLF - COA-PAA-NLOT-TR", "OLF - PIR", "OLF - AON-TT-DP-PIR-COA-NLOT-PAA-TR",
                        "CTXsp - CLA-EP-LA-BLA-BMA-PA"],
                "AMY": ["STR - sAMY"],
                "STR": ["STR - STRd", "STR - STRv"],
                "PAL": ["CNU - PAL"],
                "TH": ["TH - Middle-lateral", "TH - LGd-IGL-LGv", "TH - Posterior", "TH - Anterior", "TH - PVT-PT",
                       "TH - MG-SPFp-PP-POL-SGN-PoT-PIL", "TH - PO-Eth", "TH - PF-SPA-SPFm-VPMpc-VPLpc-RT", "TH",
                       "TH - MH-LH-LP", "TH - Middle-medial", "TH - AD-AV-AM-IAD-LD", "TH - RE-RH-CM-IAM-SMT-PR-Xi",
                       "TH - MD-IMD-PCN-CL", "TH - VAL-VPM-VPL-VM"],
                "HY": ["HY - HYa1", "HY - HYa2", "HY - HYm2", "HY - HYml", "HY - HYmm", "HY - HYpl", "HY - HYpm",
                       "HY - MEZ-PVZ-PVR", "HY LZ"],
                "MB": ["MB - VTA-SN", "MB - IC", "MB - MRN-CUN-RN-RR-PPN-PRT-SC-IC", "MB - SC-IC", "MB - SC",
                       "MB - MRN-CUN-RN-RR-PN", "MB - MRN-CUN-RN-RR-PPN-NB-SAG-PBG", "MB - MRN-CUN-RN-RR-PPN-PRT",
                       "MB - PAG-RAmb", "MB - PRT"],
                "HB": ["MY - AP-DCO-VCO-DCN-ECU-NTS", "MY - CN-DCN-ECU-NTS-SPVC-SPVI-SPVO", "MY - MYsat-MYmot",
                       "MY - MYsat-MYmot ant", "MY - MYsat-MYmot post", "MY - MYsat-MYmot-vent post",
                       "MY - MYsat-Mymot-vent ant", "MY - SPVC-SPVI-SPVO", "MY - VNC-PHY-DMX-XII", "HB - MY",
                       "PONS - Pmot-Psat ant", "PONS - Pmot-Psat post", "PONS - Psen"]
            },
            "rs1_region_dict": {
                "CTX": ["RSP-1", "RSP-2", "RSP-3", "RSP-4", "RSP-5", "RSP-6", "PFC-1", "PFC-2", "ACA-1", "ACA-2",
                        "ACA-3", "ORB", "AI", "TEa,ECT,PERI-1", "AUD-1", "AUD-2", "AUD-3", "PTLp", "VIS-1", "VIS-2",
                        "VIS-3", "VIS-4", "MOp-1", "MOp-2", "MOp-3", "MOp-4", "MOs-1", "MOs-2", "MOs-3", "SSp-1",
                        "SSp-2", "SSp-3", "SSp-4", "SSp-5", "SSp-6", "SSs-1", "SSs-2", "SSs-3", "SSs-4", "VISC"],
                "HIP": ["DG-1", "DG-2", "DG-3", "DG-4", "CA-i", "CA-ii", "CA-iii", "CA-iv"],
                "OLF": ["AON", "MOB"],
                "RHP": ["RHP-1", "RHP-2", "RHP-3", "RHP-4", "RHP-5"],
                "PIR": ["PIR-1", "PIR-2", "PIR-3", "PIR-4", "PIR-5", "PIR-6", "PIR-7", "PIR-8"],
                "AMY": ["AMY-1", "AMY-2", "AMY-3"],
                "STR": ["CP-1", "CP-2", "CP-3", "ACB-1", "ACB-2", "ACB-3"],
                "PAL": ["GP", "PAL-1", "PAL-2", "PAL-3"],
                "TH": ["TH-5", "TH-7", "TH-2", "TH-4", "TH-6", "TH-1", "TH-3"],
                "HY": ["HY-1", "HY-2", "HY-3", "HY-4"],
                "MB": ["VTA-1", "VTA-2", "IC-1", "SC-1", "SC-2", "SC-3", "MRN", "PAG-1", "PAG-2", "PAG-3", "PAG-4"],
                "HB": ["MY-1", "MY-2", "MY-3", "MY-4", "PCG", "PRN-1", "PRN-2", "PRN-3", "PRN-4"]
            },
            "rs1_subregion_dict": {
                "MOp": ["MOp-2", "MOp-3"],
                "SSp": ["SSp-3", "SSp-4"],
                "ACA": ["PFC-2", "ACA-1", "ACA-2"],
                "AI": ["AI"],
                "RSP": ["RSP-3", "RSP-4"],
                "AUD": ["AUD-1", "AUD-2"],
                "PTLp": ["PTLp"],
                "VIS": ["VIS-2", "VIS-3"],
                "ENT": ["RHP-1", "RHP-2", "RHP-3", "RHP-5"],
                "CAa": ["CA-i", "CA-ii"],
                "CAp": ["CA-iii", "CA-iv"],
                "DGa": ["DG-1", "DG-2"],
                "DGp": ["DG-3", "DG-4"],
                "PIRa": ["PIR-1", "PIR-2", "PIR-3", "PIR-4"],
                "PIRp": ["PIR-5", "PIR-6", "PIR-7", "PIR-8"],
                "MOB": ["MOB", "AON"],
                "PAL": ["PAL-1", "PAL-2", "PAL-3", "GP"],
                "STR": ["CP-1", "CP-2", "CP-3"],
                "AMY": ["AMY-1", "AMY-2", "AMY-3"],
                "THl": ["TH-1", "TH-3"],
                "THm": ["TH-2", "TH-4"],
                "THp": ["TH-5", "TH-6", "TH-7"],
                "HY": ["HY-1", "HY-2", "HY-3", "HY-4"],
                "SC": ["SC-1", "SC-2", "SC-3"],
                "MRN": ["PAG-3", "PAG-4", "MRN"],
                "VTA": ["VTA-1", "VTA-2"],
                "PAG": ["PAG-1", "PAG-2"],
                "IC": ["IC-1"],
                "P": ["PRN-1", "PRN-2", "PRN-3", "PRN-4", "PCG"],
                "MY": ["MY-1", "MY-2", "MY-3", "MY-4"]
            },
            "rs2_subregion_dict": {
                "MOp": ["3C", "4B"],
                "SSp": ["6B", "7B"],
                "ACA": ["3A", "4A", "5A"],
                "AI": ["3D"],
                "RSP": ["9A", "10A"],
                "AUD": ["9D", "10C"],
                "PTLp": ["9B"],
                "VIS": ["11B", "12B"],
                "ENT": ["10D11D12D13B"],
                "CAa": ["8E9H"],
                "CAp": ["10E11E"],
                "DGa": ["8J9J"],
                "DGp": ["10F11F"],
                "PIRa": ["2D3E4F5G"],
                "PIRp": ["6D7D8D9E"],
                "MOB": ["1C", "2E"],
                "PAL": ["4H5H6F7F", "6F7F"],
                "STR": ["4D5E6E"],
                "AMY": ["7H8H9G"],
                "THl": ["7E8F"],
                "THm": ["7G8G"],
                "THp": ["9K10G"],
                "HY": ["6H7J8K9L"],
                "SC": ["11G12F13C"],
                "MRN": ["10H11H12H"],
                "VTA": ["10J11J"],
                "PAG": ["12G13D"],
                "IC": ["14A"],
                "P": ["12J13E13F14C14D"],
                "MY": ["15C16C17B18B"]
            }
        }

        self.samples = ['Sagittal-R1', 'Sagittal-R2', 'C1-R1', 'C1-R2', 'C3-R1', 'C3-R2', 'C5-R1', 'C5-R2', 'C7-R1',
                        'C7-R2', 'C9-R1', 'C9-R2', 'C11R1', 'C11-R2', 'C13-R1', 'C13-R2']


dataset_config = DatasetConfig()
