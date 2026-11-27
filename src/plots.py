"""Draw the charts of the extinction analysis."""

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import seaborn as sns

BAR_COLOR = "#257de0"
STATUS_ORDER = ["Prehistoric Extinct", "Historically Extinct",
                "Threatened", "Not Threatened"]
MASS_TICKS = [0, 1, 2, 3, 4, 5, 6, 7, 8]
MASS_TICK_LABELS = ["1 g", "10 g", "100 g", "1 kg", "10 kg",
                    "100 kg", "1 t", "10 t", "100 t"]
DIET_ORDER = ["Herbivore", "Carnivore", "Invertivore", "Generalist"]
MORE_COLOR = "#ec4647"    # red: more extinctions than expected
FEWER_COLOR = "#257de0"   # blue: fewer extinctions than expected

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


def plot_mass_violin(df, title="Body mass of mammals by extinction status"):
    """Violin plot of body mass distribution for each extinction status group.

    Groups are ordered like a timeline: prehistoric extinctions,
    historical extinctions, currently threatened, not threatened.
    Data Deficient species are left out because their status is unknown.

    Parameters
    ----------
    df : pandas.DataFrame
        cleaned trait table from clean_traits()
    title : str, optional
        Chart title

    Returns
    -------
    matplotlib.figure.Figure
        the finished violin plot
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.violinplot(data=df, x="status_group", y="log_mass",
                   order=STATUS_ORDER, color=BAR_COLOR, cut=0,
                   inner="quartile", ax=ax)

    counts = df["status_group"].value_counts()
    ax.set_xticks(range(len(STATUS_ORDER)))
    ax.set_xticklabels([f"{group}\n(n = {counts[group]})"
                        for group in STATUS_ORDER])
    ax.set_yticks(MASS_TICKS)
    ax.set_yticklabels(MASS_TICK_LABELS)

    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel("Body mass (log scale)")
    ax.grid(axis="y", color="#e0e0e0")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    return fig


def plot_rate_heatmap(grid, counts, title, xlabel="Diet", ylabel="Body mass"):
    """Heatmap of extinction rates, with the species count in each cell.

    Rows are shown with the largest size class at the top. Cells with
    too few species (NaN in grid) are grey and show only their count.

    Parameters
    ----------
    grid : pandas.DataFrame
        Output of rate_table(): extinction rates from 0 to 1.
    counts : pandas.DataFrame
        Output of count_table() for the same two columns.
    title : str
        Chart title.
    xlabel : str, optional
        Label of the x-axis. Default "Diet".
    ylabel : str, optional
        Label of the y-axis. Default "Body mass".

    Returns
    -------
    matplotlib.figure.Figure
        The finished chart.
    """
    grid = grid.reindex(columns=DIET_ORDER).iloc[::-1]
    counts = counts.reindex(columns=DIET_ORDER).iloc[::-1]

    fig, ax = plt.subplots(figsize=(7.5, 5))
    sns.heatmap(grid, annot=False, cmap="Blues", vmin=0, vmax=1,
                linewidths=2, linecolor="white",
                cbar_kws={"format": mtick.PercentFormatter(1.0),
                          "label": "Share of species extinct"},
                ax=ax)
    ax.set_facecolor("#efefef")

    for i, row in enumerate(grid.index):
        for j, col in enumerate(grid.columns):
            rate = grid.loc[row, col]
            n = counts.loc[row, col]
            if pd.isna(rate):
                text, color = f"n = {n}", "#666666"
            else:
                text = f"{rate:.0%}\nn = {n}"
                color = "white" if rate > 0.5 else "#191919"
            ax.text(j + 0.5, i + 0.5, text, ha="center", va="center",
                    color=color, fontsize=9)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="y", rotation=0)
    ax.tick_params(length=0)

    fig.tight_layout()
    return fig


def plot_anomaly(anomaly, title, ylabel="Order"):
    """Diverging bar chart of observed minus size-expected extinctions.

    Red bars: groups that lost more species than their body sizes
    predict. Blue bars: groups that lost fewer.

    Parameters
    ----------
    anomaly : pandas.DataFrame
        Output of anomaly_by_group(), with a "difference" column.
    title : str
        Chart title.
    ylabel : str, optional
        Label of the y-axis (what the groups are). Default "Order".

    Returns
    -------
    matplotlib.figure.Figure
        The finished chart.
    """
    data = anomaly.sort_values("difference")
    colors = [MORE_COLOR if d > 0 else FEWER_COLOR
              for d in data["difference"]]

    fig, ax = plt.subplots(figsize=(8, 0.35 * len(data) + 1.5))
    ax.barh(data.index.astype(str), data["difference"], color=colors)
    ax.axvline(0, color="#666666", linewidth=1)

    legend_items = [
        mpatches.Patch(color=MORE_COLOR,
                       label="More extinctions than body size predicts"),
        mpatches.Patch(color=FEWER_COLOR,
                       label="Fewer extinctions than body size predicts"),
    ]
    ax.legend(handles=legend_items, loc="upper left", frameon=False)

    ax.set_title(title)
    ax.set_xlabel("Observed minus expected extinctions (number of species)")
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", color="#e0e0e0")
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)

    fig.tight_layout()
    return fig


def plot_mass_trend(table, result, title):
    """Scatter plot of extinction rate per mass step, with the fitted line.

    Dot size grows with the number of species in the step.

    Parameters
    ----------
    table : pandas.DataFrame
        First output of mass_trend(): one row per log-mass step,
        with n_species and rate.
    result : scipy.stats LinregressResult
        Second output of mass_trend(): the fitted line.
    title : str
        Chart title.

    Returns
    -------
    matplotlib.figure.Figure
        The finished chart.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(table.index, table["rate"],
               s=30 + 4 * table["n_species"] ** 0.5,
               color=BAR_COLOR, edgecolor="white", linewidth=1, zorder=3)

    x = [table.index.min(), table.index.max()]
    y = [result.intercept + result.slope * xi for xi in x]
    ax.plot(x, y, color="#666666", linewidth=2, zorder=2)

    if result.pvalue < 0.001:
        p_text = "p < 0.001"
    else:
        p_text = f"p = {result.pvalue:.3f}"
    ax.text(0.02, 0.95,
            f"+{result.slope * 100:.0f} percentage points per ×10 body mass\n"
            f"R² = {result.rvalue ** 2:.2f}, {p_text}",
            transform=ax.transAxes, va="top")

    ax.set_xticks(MASS_TICKS)
    ax.set_xticklabels(MASS_TICK_LABELS)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_title(title)
    ax.set_xlabel("Body mass (log scale)")
    ax.set_ylabel("Share of species extinct")
    ax.grid(color="#e0e0e0")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    return fig