"""Compute characteristics of extinct species from the cleaned trait table."""

import pandas as pd


def extinction_rate(df, group_col):
    """Count species, extinct species and extinction rate per group.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned trait table from clean_traits().
    group_col : str
        Name of the column to group by, e.g. "mass_bin" or "diet_type".

    Returns
    -------
    pandas.DataFrame
        One row per group, with the columns n_species (number of
        species), n_extinct (number of extinct species) and rate
        (share of species that are extinct, from 0 to 1).
    """
    return df.groupby(group_col, observed=True)["is_extinct"].agg(
        n_species="size",
        n_extinct="sum",
        rate="mean",
    )


def rate_table(df, row_col, col_col, min_species=10):
    """Extinction rate for every combination of two columns.

    Cells with fewer than min_species species are set to NaN,
    because rates based on very few species are not meaningful.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned trait table from clean_traits().
    row_col : str
        Column whose values become the rows, e.g. "mass_bin".
    col_col : str
        Column whose values become the columns, e.g. "diet_type".
    min_species : int, optional
        Minimum number of species for a cell to be shown. Default 10.

    Returns
    -------
    pandas.DataFrame
        Grid of extinction rates (0 to 1), with NaN for small cells.
    """
    rates = df.pivot_table(index=row_col, columns=col_col,
                           values="is_extinct", aggfunc="mean",
                           observed=True)
    counts = df.pivot_table(index=row_col, columns=col_col,
                            values="is_extinct", aggfunc="size",
                            observed=True)
    return rates.where(counts >= min_species)
