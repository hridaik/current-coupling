# Stage 2 Subgraph and Harmonization Planning Audit

Date: 2026-05-28

## Scope

Read-only planning audit for neuron-label harmonization and later subgraph
feasibility. The script inspected only documentation, filenames, lightweight
repository metadata, and code text under the Stage 2 allowed roots:

- `data/atanas/AtanasKim-Cell2023`
- `data/connectome/ConnectomeToolbox`
- `data/randi/wormneuroatlas`

No external packages were imported. No notebooks were executed. No biological
matrix, HDF5 atlas, XLSX table, CSV adjacency, or dataset package was loaded.
No covariance, precision matrix, DeltaQ-like object, enrichment, behavioral
threshold, state-conditioned neural statistic, or subgraph statistic was
computed.

## Files Inspected

- `task.md`
- `AGENTS.md`
- `data/atanas/AtanasKim-Cell2023/README.md`
- `data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb`
- `data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb`
- `data/atanas/AtanasKim-Cell2023/notebook/ANTSUN_NeuroPAL.ipynb`
- `data/connectome/ConnectomeToolbox/README.md`
- `data/connectome/ConnectomeToolbox/docs/Resources.md`
- `data/connectome/ConnectomeToolbox/docs/Validation.md`
- `data/connectome/ConnectomeToolbox/cect/Cells.py`
- `data/connectome/ConnectomeToolbox/cect/CellInfo.py`
- `data/connectome/ConnectomeToolbox/cect/readers/Cook2019HermReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/WitvlietDataReader8.py`
- `data/connectome/ConnectomeToolbox/cect/readers/RipollSanchezDataReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/WormNeuroAtlasReader.py`
- `data/randi/wormneuroatlas/README.md`
- `data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py`
- `data/randi/wormneuroatlas/wormneuroatlas/PeptideGPCR.py`
- `data/randi/wormneuroatlas/scripts/make_neuropeptidergic_connectome.py`
- `data/randi/wormneuroatlas/scripts/plot_signal_propagation.py`

## Candidate Label And Metadata Files

### Atanas

- `data/atanas/AtanasKim-Cell2023/notebook/ANTSUN_NeuroPAL.ipynb`
- `data/atanas/AtanasKim-Cell2023/notebook/CePNEM-plots.ipynb`
- `data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb`
- `data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL head curvature circuit.ipynb`
- `data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL table.ipynb`
- `data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/ANTSUN/ANTSUN_NeuroPAL.ipynb`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/ImageDataIO.jl/src/registration_io.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/NeuroPALData.jl/Project.toml`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/NeuroPALData.jl/src/NeuroPALData.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/NeuroPALData.jl/src/class.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/NeuroPALData.jl/src/import.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/NeuroPALData.jl/src/match.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/NeuroPALData.jl/src/reference/neuron_class_all.csv`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/NeuroPALData.jl/src/reference.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/Project.toml`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/README.md`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/docs/Project.toml`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/docs/make.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/docs/src/elastix.md`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/docs/src/graphs.md`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/docs/src/index.md`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/docs/src/openmind.md`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/docs/src/postprocessing.md`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/docs/src/visualization.md`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/params/parameters_euler_turbo_output.txt`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/params/parameters_freely_moving_affine.txt`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/params/parameters_freely_moving_bspline.txt`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/params/parameters_freely_moving_euler.txt`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/params/parameters_freely_moving_euler_output.txt`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/params/parameters_immobilized_affine.txt`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/params/parameters_immobilized_bspline.txt`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/params/parameters_immobilized_bspline_turbo.txt`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/scripts/euler_head_rotate.py`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/scripts/run_elastix_command.sh`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/src/RegistrationGraph.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/src/assess_registration_quality.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/src/make_elastix_difficulty.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/src/make_registration_graph.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/src/metrics.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/src/registration_visualization.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/RegistrationGraph.jl/src/run_elastix.jl`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/SegmentationStats.jl/src/label_component.jl`
- `data/atanas/AtanasKim-Cell2023/src/CePNEM/CePNEMAnalysis.jl/notebook/CePNEM-plots.ipynb`

### ConnectomeToolbox

- `data/connectome/ConnectomeToolbox/cect/cache/Cook2019HermReader.json`
- `data/connectome/ConnectomeToolbox/cect/cache/Cook2019MaleReader.json`
- `data/connectome/ConnectomeToolbox/cect/cache/Cook2020DataReader.json`
- `data/connectome/ConnectomeToolbox/cect/cache/RipollSanchezLongRangeReader.json`
- `data/connectome/ConnectomeToolbox/cect/cache/RipollSanchezMidRangeReader.json`
- `data/connectome/ConnectomeToolbox/cect/cache/RipollSanchezShortRangeReader.json`
- `data/connectome/ConnectomeToolbox/cect/cache/WormNeuroAtlasFuncReader.json`
- `data/connectome/ConnectomeToolbox/cect/cache/WormNeuroAtlasMAReader.json`
- `data/connectome/ConnectomeToolbox/cect/cache/WormNeuroAtlasPepReader.json`
- `data/connectome/ConnectomeToolbox/cect/cache/WormNeuroAtlasReader.json`
- `data/connectome/ConnectomeToolbox/cect/data/01022024_neuropeptide_connectome_long_range_model.csv`
- `data/connectome/ConnectomeToolbox/cect/data/01022024_neuropeptide_connectome_mid_range_model.csv`
- `data/connectome/ConnectomeToolbox/cect/data/01022024_neuropeptide_connectome_short_range_model.csv`
- `data/connectome/ConnectomeToolbox/cect/data/IndividualNeurons.csv`
- `data/connectome/ConnectomeToolbox/cect/data/SI 5 Connectome adjacency matrices.xlsx`
- `data/connectome/ConnectomeToolbox/cect/data/aconnectome_white_1986_A.csv`
- `data/connectome/ConnectomeToolbox/cect/data/aconnectome_white_1986_L4.csv`
- `data/connectome/ConnectomeToolbox/cect/data/aconnectome_white_1986_whole.csv`
- `data/connectome/ConnectomeToolbox/cect/data/all_cell_info.csv`
- `data/connectome/ConnectomeToolbox/cect/data/herm_full_edgelist.csv`
- `data/connectome/ConnectomeToolbox/cect/data/herm_full_edgelist_MODIFIED.csv`
- `data/connectome/ConnectomeToolbox/cect/data/white_1986_jsh.csv`
- `data/connectome/ConnectomeToolbox/cect/data/white_1986_n2u.csv`
- `data/connectome/ConnectomeToolbox/cect/data/witvliet_2020_8 adult.xlsx`
- `data/connectome/ConnectomeToolbox/cect/readers/Cook2019DataReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/Cook2019HermReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/Cook2019MaleReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/Cook2020DataReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/RipollSanchezDataReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/RipollSanchezLongRangeReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/RipollSanchezMidRangeReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/RipollSanchezShortRangeReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/WormNeuroAtlasExtSynReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/WormNeuroAtlasFuncReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/WormNeuroAtlasMAReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/WormNeuroAtlasPepReader.py`
- `data/connectome/ConnectomeToolbox/cect/readers/WormNeuroAtlasReader.py`
- `data/connectome/ConnectomeToolbox/cect/validation/Cook2020DataReader_expected_data.yaml`
- `data/connectome/ConnectomeToolbox/cect/validation/CookEtAl2019.md`
- `data/connectome/ConnectomeToolbox/cect/validation/CookEtAl2020.md`
- `data/connectome/ConnectomeToolbox/cect/validation/RipollSanchezEtAl2023.md`
- `data/connectome/ConnectomeToolbox/cect/validation/RipollSanchezLongRangeReader_expected_data.yaml`
- `data/connectome/ConnectomeToolbox/cect/validation/RipollSanchezMidRangeReader_expected_data.yaml`
- `data/connectome/ConnectomeToolbox/cect/validation/RipollSanchezShortRangeReader_expected_data.yaml`

### wormneuroatlas

- `data/randi/wormneuroatlas/wormneuroatlas/data/GenesExpressing-neuropeptide-receptors.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/GenesExpressing-neuropeptides.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/aconnectome.json`
- `data/randi/wormneuroatlas/wormneuroatlas/data/aconnectome_default.h5`
- `data/randi/wormneuroatlas/wormneuroatlas/data/aconnectome_ids_ganglia.json`
- `data/randi/wormneuroatlas/wormneuroatlas/data/aconnectome_white_1986_A.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/aconnectome_white_1986_L4.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/aconnectome_white_1986_whole.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/aconnectome_witvliet_2020_7.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/aconnectome_witvliet_2020_8.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/anatlas_neuron_positions.txt`
- `data/randi/wormneuroatlas/wormneuroatlas/data/cell_lineage.txt`
- `data/randi/wormneuroatlas/wormneuroatlas/data/deorphanization_media_6.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/esconnectome_neuropeptides_Bentley_2016.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/froonikcx_peptide_gpcr.txt`
- `data/randi/wormneuroatlas/wormneuroatlas/data/funatlas.h5`
- `data/randi/wormneuroatlas/wormneuroatlas/data/neuron_ids.txt`

## Evidence Excerpts

### Atanas Label And Cell-ID Sources

- data/atanas/AtanasKim-Cell2023/README.md:21: The processed data files and the trained neural network weights are available in [the repository](https://doi.org/10.5281/zenodo.8150514).
- data/atanas/AtanasKim-Cell2023/README.md:24: The datasets and modeling results (encoding detection) from this project can be browsed in [WormWideWeb](https://wormwideweb.org/). On the website, you can easily find the neural (GCaMP) traces of specific recorded/id...
- data/atanas/AtanasKim-Cell2023/README.md:52: - [NeuroPALData.jl](https://github.com/flavell-lab/NeuroPALData.jl) contains a collection of NeuroPAL labeling utilities
- data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb:192: "    data_dict = import_data(path_data, custom_keys=[\"neuropal_registration\"])\n",
- data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb:213: "list_neuropal_label = load(\"/scratch/prj_kfc/list_neuropal_label.jld2\")[\"list_neuropal_label\"];"
- data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb:264: "list_class_dv = get_list_class_dv(map(x->x[1],list_neuropal_label));"
- data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb:326: "list_match_dict = get_list_match_dict(list_neuropal_label, list_data_dict=list_data_dict, list_dict_fit=list_dict_fit,\n",
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:209: "    data_dict = import_data(path_data, custom_keys=[\"neuropal_registration\"])\n",
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:234: "# list_neuropal_label = []\n",
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:236: "#     path_label = joinpath(\"/data1/prj_neuropal/data/neuropal_label_prj_kfc/\", \"$(data_uid) Neuron ID.xlsx\")\n",
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:238: "#     push!(list_neuropal_label, import_neuropal_label(path_label))\n",
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:249: "list_neuropal_label = load(\"/scratch/prj_kfc/list_neuropal_label.jld2\")[\"list_neuropal_label\"];"

### Atanas Identity-Confidence Pointers

- data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb:328: "    list_class_classify_dv_enc=list_class_classify_dv_enc, θ_confidence_label=2.5);"
- data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb:1060: "                        (label, roi_gcamp, match_confidence) = neuron_match\n",
- data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb:1185: "                        for (label, roi_gcamp, match_confidence) = list_match\n",
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:364: "    list_class_classify_dv_enc=list_class_classify_dv_enc, θ_confidence_label=2.5);"
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:547: "#     r, theta, phi = x_spher\n",
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:551: "#     x = r * sin(theta) * cos(phi)\n",
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:552: "#     y = r * sin(theta) * sin(phi)\n",
- data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb:553: "#     z = r * cos(theta)\n",
- data/atanas/AtanasKim-Cell2023/notebook/ANTSUN_NeuroPAL.ipynb:360: "    param[\"seg_threshold_unet\"] = 0.5 # The UNet output confidence threshold for a pixel to be counted as a neuron.\n",
- data/atanas/AtanasKim-Cell2023/notebook/ANTSUN_NeuroPAL.ipynb:442: "    param[\"nose_confidence_threshold\"] = 0.99 # threshold for UNet's confidence of nose location for it to be used to crop medial axis\n",

### ConnectomeToolbox Label And Synapse Sources

- data/connectome/ConnectomeToolbox/cect/CellInfo.py:113: filename = "cect/data/IndividualNeurons.csv"
- data/connectome/ConnectomeToolbox/cect/CellInfo.py:451: cell_info_filename = "cect/data/all_cell_info.csv"
- data/connectome/ConnectomeToolbox/cect/readers/Cook2019HermReader.py:18: """Uses ``Cook2019DataReader`` to load data on hermaphrodite connectome
- data/connectome/ConnectomeToolbox/cect/readers/Cook2019HermReader.py:21: (Cook2019DataReader): The initialized hermaphrodite connectome reader
- data/connectome/ConnectomeToolbox/cect/readers/WitvlietDataReader8.py:9: SRC_FILENAME = "witvliet_2020_8 adult.xlsx"
- data/connectome/ConnectomeToolbox/cect/readers/RipollSanchezDataReader.py:32: filename = "%s01022024_neuropeptide_connectome_%s.csv" % (
- data/connectome/ConnectomeToolbox/docs/Validation.md:158: The 8 spreadsheet files (witvliet_2020_1 L1.xlsx, witvliet_2020_2 L1.xlsx, ..., witvliet_2020_8 adult.xlsx) hosted on [WormWiring](https://wormwiring.org/pages/witvliet.html), also contain electrical connectivity, and...
- data/connectome/ConnectomeToolbox/docs/Validation.md:380: - [01022024_neuropeptide_connectome_short_range_model.csv](https://github.com/LidiaRipollSanchez/Neuropeptide-Connectome/blob/main/Adjacency%20matrices%20for%20networks/01022024_neuropeptide_connectome_short_range_mod...
- data/connectome/ConnectomeToolbox/docs/Validation.md:381: - [01022024_neuropeptide_connectome_mid_range_model.csv](https://github.com/LidiaRipollSanchez/Neuropeptide-Connectome/blob/main/Adjacency%20matrices%20for%20networks/01022024_neuropeptide_connectome_mid_range_model.csv)
- data/connectome/ConnectomeToolbox/docs/Validation.md:382: - [01022024_neuropeptide_connectome_long_range_model.csv](https://github.com/LidiaRipollSanchez/Neuropeptide-Connectome/blob/main/Adjacency%20matrices%20for%20networks/01022024_neuropeptide_connectome_long_range_model...

### ConnectomeToolbox Left/Right Convention

- data/connectome/ConnectomeToolbox/cect/Cells.py:1767: return is_bilateral_left(cell) or is_bilateral_right(cell)
- data/connectome/ConnectomeToolbox/cect/Cells.py:1770: def get_contralateral_cell(cell: str):
- data/connectome/ConnectomeToolbox/cect/Cells.py:1799: if is_bilateral_left(cell):
- data/connectome/ConnectomeToolbox/cect/Cells.py:1801: if is_bilateral_right(cell):
- data/connectome/ConnectomeToolbox/cect/Cells.py:1807: def is_bilateral_left(cell: str):
- data/connectome/ConnectomeToolbox/cect/Cells.py:1818: def is_bilateral_right(cell: str):

### wormneuroatlas Label And Pair Sources

- data/randi/wormneuroatlas/README.md:2: Neural signal propagation atlas [1], genome [2], and single-cell transcriptome [3], neuropeptide/GPCR deorphanization [4], anatomical connectome [5,6], monoaminergic connectome [7], and chemical-synapse sign predictio...
- data/randi/wormneuroatlas/README.md:24: NeuroAtlas is the main class that aggregates all the datasets, and directly handles the Signal Propagation Atlas, the anatomical connectome, and the monoaminergic connectome [7].
- data/randi/wormneuroatlas/README.md:26: You can access the wild-type and unc-31 signal propagation atlas, for example, via
- data/randi/wormneuroatlas/README.md:39: NeuroAtlas also manages the conversions between different conventions for neural IDs. NeuroAtlas can be instantiated to maintain the "exact" neural identities, or to merge neurons into classes (i.e. to approximate neu...
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:27: fname_neuron_ids = "neuron_ids.txt"
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:31: fname_signal_propagation = "funatlas.h5"
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:104: self._neuron_ids = np.loadtxt(self.module_folder+self.fname_neuron_ids,
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:121: self.neuron_ids = self.approximate_ids(
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:122: self._neuron_ids,self.merge_bilateral,
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:125: self.neuron_ids = np.unique(self.neuron_ids)
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:126: self.n_neurons = self.neuron_n = len(self.neuron_ids)
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:163: '''if np.any(self.ids_to_ais(self.synapsesign.neuron_ids)==-1):
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:164: incompatible = self.ids_to_ais(self.synapsesign.neuron_ids)==-1
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:165: print(self.synapsesign.neuron_ids[incompatible])

### wormneuroatlas Left/Right Convention

- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:77: def __init__(self,merge_bilateral=False,merge_dorsoventral=False,
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:78: merge_numbered=False,merge_AWC=False,
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:85: merge_bilateral: bool, optional
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:87: merge_dorsoventral: bool, optional
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:89: merge_numbered: bool, optional
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:108: self.merge_bilateral = merge_bilateral
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:109: self.merge_dorsoventral = merge_dorsoventral
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:110: self.merge_numbered = merge_numbered
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:113: if merge_numbered and verbose:
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:122: self._neuron_ids,self.merge_bilateral,
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:123: self.merge_dorsoventral,self.merge_numbered,
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:133: self.head_ids,self.merge_bilateral,

### wormneuroatlas Neuropeptide Sources

- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:35: fname_neuropeptides = "GenesExpressing-neuropeptides.csv"
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:37: fname_neuropeptide_receptors = "GenesExpressing-neuropeptide-receptors.csv"
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:278: pepesc_out = self.get_peptidergic_connectome(neuron_ids_from=neuron_ids)
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:279: pepesc_in = self.get_peptidergic_connectome(neuron_ids_to=neuron_ids)
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:1758: f = open(self.module_folder+self.fname_neuropeptides,"r")
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:1793: f = open(self.module_folder+self.fname_neuropeptide_receptors,"r")
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:1929: # INTERFACE TO CENGEN AND NEUROPEPTIDE/GPCR DEORPHANIZATION
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:1989: print("*Supplementing peptide/GPCR combinations with older datasets.")
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:2011: def get_peptidergic_connectome(self,neuron_ids_from=None,neuron_ids_to=None,
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:2014: GPCR expression data and the peptide/GPCR binding screen.
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:2025: Whether to return also the list of peptide/GPCR combinations for
- data/randi/wormneuroatlas/wormneuroatlas/NeuroAtlas.py:2032: of peptide/GPCR combinations for the connection i<-j. Note that i
- data/randi/wormneuroatlas/scripts/make_neuropeptidergic_connectome.py:7: # This script will generate the neuropeptidergic extrasynaptic connectome
- data/randi/wormneuroatlas/scripts/make_neuropeptidergic_connectome.py:12: # Supplement the peptide/GPCR dataset with previous literature. Not done

## Planning Conclusions

### Atanas

- The local Atanas repository is primarily source code and notebooks. The README
  points processed data to Zenodo/WormWideWeb, while notebooks point to processed
  HDF5/JLD2 artifacts such as `neuropal_registration`, `list_neuropal_label`,
  `Neuron ID.xlsx`, `new_label_map`, and `roi_match_confidence`.
- Left/right naming appears to be present in NeuroPAL class/order handling, but
  the exact per-animal canonical label table cannot be finalized from filenames
  alone.
- Identity-confidence information appears to exist in the processing outputs or
  matching code (`roi_match_confidence`, `theta_confidence_label`), but the
  project threshold remains a human decision. `IDENTITY_CONFIDENCE_THRESHOLD`
  should remain unset until the relevant label/confidence table is loaded and
  reviewed under an explicit Stage 2 data-loading authorization.

### ConnectomeToolbox

- Candidate neuron-label metadata is present in `IndividualNeurons.csv`,
  `all_cell_info.csv`, and the `cect/Cells.py` preferred-name lists.
- Candidate synapse/connectome sources include Cook/Witvliet reader inputs:
  `SI 5 Connectome adjacency matrices.xlsx`, `witvliet_2020_8 adult.xlsx`,
  `herm_full_edgelist.csv`, and White/Witvliet CSVs.
- Ripoll-Sanchez neuropeptide adjacency matrices are present in
  `cect/data/01022024_neuropeptide_connectome_*_model.csv`.
- Left/right neurons are represented as separate names in the preferred-name
  machinery, with helper functions for bilateral left/right and contralateral
  names.

### wormneuroatlas / Randi

- Candidate label metadata is explicitly stored in
  `wormneuroatlas/data/neuron_ids.txt` and
  `wormneuroatlas/data/aconnectome_ids_ganglia.json`.
- Candidate Randi pair/response data is stored in
  `wormneuroatlas/data/funatlas.h5`; code text shows `wt` and `unc31` groups
  containing response and q-value arrays.
- Candidate neuropeptide metadata includes
  `GenesExpressing-neuropeptides.csv`,
  `GenesExpressing-neuropeptide-receptors.csv`,
  `deorphanization_media_6.csv`, `froonikcx_peptide_gpcr.txt`, and the
  `get_peptidergic_connectome` implementation.
- Left/right identity is separate by default in `NeuroAtlas` because
  `merge_bilateral=False`; the package can intentionally collapse labels when
  requested, which should not be used for the primary `LR_POLICY = "separate"`
  workflow without human approval.

## Later Loading Requirements

- A later actual Stage 2 feasibility step will need to load small label tables
  or metadata files for harmonization. Atanas may require processed HDF5/JLD2 or
  a WormWideWeb/Zenodo label export, not just repository source code.
- Computing `N_COMMON_NEURONS`, building adjacency matrices, or printing coverage
  fractions will require loading biological label/connectome/neuropeptide tables
  and is outside this planning audit.
- A human checkpoint is recommended before moving from this audit to table
  loading because `IDENTITY_CONFIDENCE_THRESHOLD` is still unset and because any
  harmonization-table construction or ambiguity resolution is checkpointed by
  the project contract.

## Config Status

- `phase0_config.py` was not modified by this audit.
- `IDENTITY_CONFIDENCE_THRESHOLD`, `N_COMMON_NEURONS`,
  `SUBGRAPH_ADEQUATE`, and `N_RANDI_SUBGRAPH_PAIRS` remain unset.
- `PHASE0_COMPLETE` remains `False`.

## Deviations

No deviations recorded.
