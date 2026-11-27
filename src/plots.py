"""Draw the charts of the extinction analysis."""

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

BAR_COLOR = "#257de0"


def plot_rate_bars(rates, title, xlabel):
    """Bar chart of extinction rate per group.

    Parameters
    ----------
    rates : pandas.DataFrame
        Output of extinction_rate(): one row per group, with a "rate" column.
    title : str
        Chart title.
    xlabel : str
        Label of the x-axis (what the groups are).

    Returns
    -------
    matplotlib.figure.Figure
        The finished chart.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(rates.index.astype(str), rates["rate"], color=BAR_COLOR)

    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Share of species extinct")

    ax.grid(axis="y", color="#e0e0e0")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    return fig