"""
DO NOT RUN THIS SCRIPT DIRECTLY.
It is meant to be run as part of the Docker build process for the worker image.
"""

from jyutping2characters.data_builder import build_mapping_data
import os
from pathlib import Path

if __name__ == "__main__":
    jyutping_data_path = os.getenv("JYUTPING_CHARACTERS_DATA_PATH")
    if jyutping_data_path is None:
        raise ValueError("Environment variable JYUTPING_CHARACTERS_DATA_PATH must be set")
    Path(jyutping_data_path).parent.mkdir(parents=True, exist_ok=True)
    build_mapping_data(str(jyutping_data_path))
