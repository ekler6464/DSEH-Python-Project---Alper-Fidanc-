"""Streamlit app: Visualizing how humans shaped mammal extinctions."""

import matplotlib.pyplot as plt
import streamlit as st

from src.analysis import (anomaly_by_group, count_table, extinction_rate,
                          mass_trend, rate_table)
from src.download import download_traits
from src.loading import clean_traits, land_mammals, load_traits
from src.plots import (plot_anomaly, plot_mass_trend, plot_mass_violin,
                       plot_rate_bars, plot_rate_heatmap)

ANOMALY_GROUPS = {
    "Mammal order": "Order.1.2",
    "Island status": "Island.Endemicity",
    "Diet": "diet_type",
}

HOMININS = {
    "Homo_neanderthalensis": "Neanderthals & Denisovans",
    "Homo_floresiensis": "H. floresiensis",
    "Homo_sapiens": "H. sapiens (us)",
}


@st.cache_data
def get_data():
    """Download the data if needed, then load and clean it (cached).

    Returns
    -------
    pandas.DataFrame
        Cleaned trait table from clean_traits().
    """
    download_traits()
    return clean_traits(load_traits())


def show(fig):
    """Display a matplotlib figure in the app, then close it.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The chart to display.
    """
    st.pyplot(fig)
    plt.close(fig)


st.set_page_config(page_title="Human Impact on Mammal Extinctions", layout="centered")
st.title("Human Impact on Mammal Extinctions Since the Last Interglacial Period")
st.write(
    "Over the last ~130,000 years, 353 of 5,831 known mammal species went extinct. "
    "This analysis aims to visualize which species have been more affected.\n\n"
    "Data used for the project is from PHYLACINE 1.2.1 (Faurby et al., 2018), which "
    "contains trait characteristics covering all known mammalian species since the "
    "last interglacial period which began around 130,000 years ago."
)

# ---- Load data -------------------------------------------------------------
try:
    all_species = get_data()
except (RuntimeError, FileNotFoundError) as error:
    st.error(f"The data could not be loaded: {error}")
    st.stop()

# ---- Sidebar options -------------------------------------------------------
st.sidebar.header("Options")
land_only = st.sidebar.checkbox("Land mammals only", value=True)
min_species = st.sidebar.slider("Minimum species per group", 5, 50, 10, 5)
show_hominins = st.sidebar.checkbox("Highlight human species", value=True)

df = land_mammals(all_species) if land_only else all_species
st.sidebar.write(f"{len(df)} species, {df['is_extinct'].sum()} extinct")

# ---- 1. Who went extinct? --------------------------------------------------
st.header("1. Who went extinct?")
st.write("Prehistoric extinctions hit large animals; extinctions since 1500 "
         "hit mostly small, island species.")
highlight = HOMININS if show_hominins else None
show(plot_mass_violin(df, highlight=highlight))

# ---- 2. Size matters -------------------------------------------------------
st.header("2. The bigger the animal, the higher the risk")
show(plot_rate_bars(extinction_rate(df, "mass_bin"),
                    "Extinction rate by body size", "Body mass"))

table, result = mass_trend(df, min_species=min_species)
show(plot_mass_trend(table, result,
                     "Linear trend of extinction rate with body mass"))
st.caption("Each dot is a body-mass step (about x3 in mass); dot size shows "
           "the number of species. The straight line cannot follow the "
           "S-shaped pattern, so it is a rough summary.")

# ---- 3. Size or diet? ------------------------------------------------------
st.header("3. Is it size, or what they ate?")
grid = rate_table(df, "mass_bin", "diet_type", min_species=min_species)
counts = count_table(df, "mass_bin", "diet_type")
show(plot_rate_heatmap(grid, counts, "Extinction rate by body mass and diet"))
st.caption(f"Grey cells: fewer than {min_species} species. Diet type = main "
           "food source if it makes up more than 50% of the diet.")

# ---- 4. Unexpected losses --------------------------------------------------
st.header("4. Who lost more than their size explains?")
choice = st.selectbox("Compare by", list(ANOMALY_GROUPS))
group_col = ANOMALY_GROUPS[choice]
anomaly = anomaly_by_group(df, group_col, min_species=min_species)
show(plot_anomaly(anomaly, f"Observed vs size-expected extinctions by "
                  f"{choice.lower()}", ylabel=""))
with st.expander("Show the table"):
    st.dataframe(anomaly.round(1))
