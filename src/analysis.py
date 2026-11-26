"""Compute characteristics of extinct species from the cleaned trait table."""

import numpy as np
from scipy import stats


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


def anomaly_by_group(df, group_col="Order.1.2", min_species=20):
    """Compare observed and size-expected extinctions per group.

    Each species gets the extinction rate of its mass bin as its
    expected probability of extinction. Summing these per group gives
    the number of extinctions expected from body size alone, and the
    difference to the observed number is the anomaly.

    The default value for group_col is by "Order.1.2", but it can
    be modified to any other column from the trait data file in order to
    run an analysis showing expected versus actual extinction rates
    for the specific traits in question.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned trait table from clean_traits().
    group_col : str, optional
        Column to group by. Default "Order.1.2".
    min_species : int, optional
        Groups with fewer species are left out. Default 20.

    Returns
    -------
    pandas.DataFrame
        One row per group with n_species, observed, expected and
        difference (observed - expected), sorted by difference.
    """
    expected_prob = df.groupby("mass_bin", observed=True)[
        "is_extinct"].transform("mean")

    result = df.assign(expected=expected_prob).groupby(group_col).agg(
        n_species=("is_extinct", "size"),
        observed=("is_extinct", "sum"),
        expected=("expected", "sum"),
    )
    result["difference"] = result["observed"] - result["expected"]
    result = result[result["n_species"] >= min_species]
    return result.sort_values("difference", ascending=False)


def mass_trend(df, step=0.5, min_species=10):
    """Fit a straight line to extinction rate against log10 body mass.

    Species are grouped into log-mass steps of width `step`; the
    extinction rate of each step is regressed on the step's log mass.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned trait table from clean_traits().
    step : float, optional
        Width of each log-mass step. Default 0.5 (about x3 in mass).
    min_species : int, optional
        Steps with fewer species are left out. Default 10.

    Returns
    -------
    tuple
        (table of steps with n_species and rate,
         scipy LinregressResult with slope, intercept, rvalue, pvalue)
    """
    steps = np.floor(df["log_mass"] / step) * step
    table = df.groupby(steps)["is_extinct"].agg(n_species="size",
                                                rate="mean")
    table = table[table["n_species"] >= min_species]
    result = stats.linregress(table.index, table["rate"])
    return table, result
