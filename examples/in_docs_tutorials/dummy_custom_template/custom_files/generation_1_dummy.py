# ==================================================================================================
# --- Imports
# ==================================================================================================

# Import standard library modules
import logging
import os

# Import third-party modules
# Import user-defined modules
from study_da.utils import (
    load_dic_from_path,
    set_item_in_dic,
    write_dic_to_path,
)

# Set up the logger here if needed


# ==================================================================================================
# --- Script functions
# ==================================================================================================
def add(configuration):
    x = float(configuration["a_random_nest"]["x"])
    z = float(configuration["another_random_nest"]["and_another"]["z"])
    configuration["result"] = {"x_plus_z": x + z}
    return configuration


# ==================================================================================================
# --- Parameters placeholders definition
# ==================================================================================================
dict_mutated_parameters = {}  ###---parameters---###
path_configuration = "{} ###---main_configuration---###"
# In case the placeholders have not been replaced, use default path
if path_configuration.startswith("{}"):
    path_configuration = "config.yaml"
# ==================================================================================================
# --- Script for execution
# ==================================================================================================

if __name__ == "__main__":
    logging.info("Starting custom script")

    # Load full configuration
    full_configuration, ryaml = load_dic_from_path(path_configuration)

    # Mutate parameters in configuration
    for key, value in dict_mutated_parameters.items():
        set_item_in_dic(full_configuration, key, value)

    # Add x and z and write to configuration
    full_configuration = add(full_configuration)

    # Dump configuration
    name_configuration = os.path.basename(path_configuration)
    write_dic_to_path(full_configuration, name_configuration, ryaml)

    logging.info("Script finished")