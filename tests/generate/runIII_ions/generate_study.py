# ==================================================================================================
# --- Imports
# ==================================================================================================

# Import standard library modules

# Import third-party modules
# Import user-defined modules
from study_da import (
    GenerateScan,
    load_configuration_from_path,
    write_configuration_to_path,
)

# ==================================================================================================
# --- Script to generate a study
# ==================================================================================================

# Load the configuration
config, ryaml = load_configuration_from_path(
    "../../../study_da/generate/template_configurations/config_runIII_ions.yaml"
)

# Adapt the number of turns
config["config_simulation"]["n_turns"] = 100

# Drop the configuration locally
write_configuration_to_path(config, "config_runIII_ions.yaml", ryaml)

# Now generate the study in the local directory
study_da = GenerateScan(path_config="config_scan.yaml")
study_da.create_study(tree_file=True, force_overwrite=True)