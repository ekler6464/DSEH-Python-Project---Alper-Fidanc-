"""Load and clean the PHYLACINE trait data."""

import os

import numpy as np
import pandas as pd

from src.download import FILE_PATH


def load_traits(path=FILE_PATH):
    """Read the PHYLACINE trait table into a DataFrame.

    Parameters
    ----------
    path : str, optional
        Location of the CSV file. Defaults to data/Trait_data.csv.

    Returns
    -------
    pandas.DataFrame
        The raw trait table, one row per mammal species.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Run 'python -m src.download' first."
        )
    return pd.read_csv(path)