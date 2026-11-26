"""Load and clean the PHYLACINE trait data."""

import os

import numpy as np
import pandas as pd

from src.download import FILE_PATH

EXTINCT_CODES = ["EP", "EX", "EW"]

STATUS_GROUPS = {"LC": "Not Threatened",
                 "NT": "Not Threatened",
                 "VU": "Threatened",
                 "EN": "Threatened",
                 "CR": "Threatened",
                 "EP": "Prehistoric Extinct",
                 "EX": "Historically Extinct",
                 "EW": "Historically Extinct",
                 "DD": "Data Deficient"
                 }

MASS_EDGES = [0, 1_000, 10_000, 45_000, 1_000_000, np.inf]

MASS_LABELS = ["<1 kg", "1-10 kg", "10-45 kg", "45 kg-1 t", ">=1 t"]

DIET_THRESHOLD = 50


def load_traits(path=FILE_PATH):
    """Read the PHYLACINE trait table into a DataFrame.

    Parameters
    ----------
    path: str, optional
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


def classify_diet(row):
    """Return the diet type of a species by examining the percentages of its diet.

    A species is classified by its main food source if that food source makes up more than
    DIET_THRESHOLD of its diet. It is set as 50% in reference to Pineda-Munoz & Alroy 2014.
    If the main food source is less than or equal to DIET_THRESHOLD, the species is a generalist.

    Parameters
    ----------
    row : pandas.Series
        One species' row, with the columns Diet.Plant, Diet.Vertebrate
        and Diet.Invertebrate.

    Returns
    -------
    str
        "Herbivore", "Carnivore", "Invertivore", or "Generalist".
    """
    if row["Diet.Plant"] > DIET_THRESHOLD:
        return "Herbivore"
    if row["Diet.Vertebrate"] > DIET_THRESHOLD:
        return "Carnivore"
    if row["Diet.Invertebrate"] > DIET_THRESHOLD:
        return "Invertivore"
    return "Generalist"


def clean_traits(df):
    """Add columns needed for the analysis.

    Columns added are:
    is_extinct -> show mammals with extinct status
    status_group -> add names to the status variable
    log_mass -> convert mass from grams to log scale
    mass_bin -> divide species into 5 bins according to weight
    diet_type -> classify species according to their diet

    Parameters
    ----------
    df: pandas.DataFrame
        the raw trait table returned by load_traits()

    Returns
    -------
    pandas.DataFrame
        a copy of df with the added columns
    """

    df = df.copy()

    # 1. True if the species is extinct (EP, EX, or EW)
    df["is_extinct"] = df["IUCN.Status.1.2"].isin(EXTINCT_CODES)

    # 2. new column to name the status_group variables
    df["status_group"] = df["IUCN.Status.1.2"].map(STATUS_GROUPS)

    # 3. new column made from converting the mass column from grams to log scale
    # log transformation is needed to lessen data skew since body mass is strongly right skewed
    df["log_mass"] = np.log10(df["Mass.g"])

    # 4. new column which divides species into 5 bins according to their mass
    # the bin cutoffs were made according to the definition of megafauna in ecology
    # right=False so that exactly 45 kg counts as megafauna
    df["mass_bin"] = pd.cut(df["Mass.g"], bins=MASS_EDGES,
                            labels=MASS_LABELS, right=False)

    # 5. new column to classify species according to their diet type
    # the classification process is done through the classify_diet function
    df["diet_type"] = df.apply(classify_diet, axis=1)

    return df
