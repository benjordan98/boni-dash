import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta
import time
from streamlit.logger import get_logger
from utils import create_header_triplet, initialise_session_states


LOGGER = get_logger(__name__)

def select_member_df(df):
    return df[df['Member'] == st.session_state.member]

def cum_sum_restaurant_visits(df):
    df2 = df.groupby([pd.Grouper(key="date", freq="D"), "restaurant"]).size().unstack().fillna(0).reset_index()
    return df2

def fill_missing_dates(df):
    """
    Make dataframe continuos by date for dynamic plotting!
    """
    df_filled = df.set_index('date').resample('D').first().fillna(0).cumsum()
    return df_filled.reset_index()


# Get Boni summary statistics
def get_unique_boni(df):
    return len(df[df['date'] < get_end_date()]['restaurant'].unique())

def get_boni_total(df):
    return df[df['date'] < get_end_date()]['discount_meal_price'].sum()


# Session state functions
def update_session_state(df_cumsum):
    if 'end_date' not in st.session_state:
        st.session_state.end_date = df_cumsum['date'].min()
    else:
        st.session_state.end_date += timedelta(days=1)

def get_end_date():
    if 'end_date' not in st.session_state:
        return ""
    return st.session_state.end_date

# Updating Plots and Summary values
def update_chart_stacked(df_cumsum, plot_container):
    # Get the subset of data up to the specified date
    end_date_subset = st.session_state.end_date
    df_subset = df_cumsum[df_cumsum['date'] <= end_date_subset]

    # Melt DataFrame for Plotly Express
    df_melted = df_subset.melt(id_vars='date', var_name='Restaurant', value_name='Cumulative Visits')

    # Create a bar chart using Plotly Express
    fig = px.bar(df_melted, x='date', y='Cumulative Visits', color='Restaurant',
                labels={'Cumulative Visits': 'Count'},
                template='plotly_dark',
                category_orders={'Restaurant': df_melted.groupby('Restaurant')['Cumulative Visits'].sum().sort_values(ascending=False).index})

    # Update the container with the new plot
    plot_container.plotly_chart(fig, use_container_width=True, key=f"bar_chart_{time.time()}")

def update_chart_bar(df_cumsum, plot_container):
    # Get the subset of data up to the specified date
    end_date_subset = st.session_state.end_date
    df_subset = df_cumsum[(df_cumsum['date'] <= end_date_subset) & (df_cumsum['date'] >= end_date_subset)]

    # Melt DataFrame for Plotly Express
    df_melted = df_subset.melt(id_vars='date', var_name='Restaurant', value_name='Cumulative Visits')
    df_melted = df_melted.sort_values(by = 'Cumulative Visits', ascending = True)
    # remove restaurants with no visits
    df_melted = df_melted[df_melted['Cumulative Visits'] > 0]
    df_melted['Visits'] = np.where(df_melted['Cumulative Visits'] == 1, '1 visit', np.where(df_melted['Cumulative Visits'] == 2, '2 visits', '2+ visits'))

    # Create a bar chart using Plotly Express
    color_discrete_map = {
        '1 visit' : 'skyblue',
        '2 visits' : 'lightcoral',
        '2+ visits': 'lightgreen'
    }
    fig = px.bar(df_melted, x='Cumulative Visits', y='Restaurant',
                color='Visits',
                labels={'Cumulative Visits': 'Count'},
                template='plotly_dark',
                color_discrete_map=color_discrete_map)

    # Update the container with the new plot
    plot_container.plotly_chart(fig, use_container_width=True, key=f"bar_chart_{time.time()}")

def update_summary_stats(df, date, total_euro, unique_boni):
    # update top row
    date.write("Current Date: " + str(get_end_date())[:10])
    total_euro.write("Total Spend: €" + str(round(get_boni_total(df), 2)))
    unique_boni.write("Tried " + str(get_unique_boni(df)) + " Boni")


def setup_header():
    """Initializes session states and header UI."""
    st.set_page_config(page_title="Journey", page_icon="🗺️", layout="wide")
    initialise_session_states()
    create_header_triplet()

def load_data():
    """Loads and processes the dataset."""
    df = select_member_df(st.session_state.combined_df)
    df_cumsum = fill_missing_dates(cum_sum_restaurant_visits(df))
    return df, df_cumsum

def on_member_change():
    st.session_state.member = st.session_state.selected_member

def setup_members_select_box(select_box):
    select_box.selectbox(
        label='Who are you?',
        options=st.session_state.members,
        key='selected_member',
        index=st.session_state.members.index(st.session_state.member), 
        on_change=on_member_change 
    )

def setup_top_row_controls():
    """Sets up placeholders for UI elements at the top of the page."""
    date, total_euro, unique_boni, reset_button, run_button, member = st.columns(6)

    setup_members_select_box(member)

    return date, total_euro, unique_boni, reset_button, run_button

def handle_reset(df_cumsum, plot_container_stacked, plot_container_bar):
    """Handles the reset button functionality."""
    if st.session_state.reset_button.button("Reset Data"):
        st.session_state.end_date = df_cumsum['date'].min() - timedelta(1)
        update_chart_stacked(df_cumsum, plot_container_stacked)
        update_chart_bar(df_cumsum, plot_container_bar)

def run_simulation(df, df_cumsum, plot_container_stacked, plot_container_bar, date, total_euro, unique_boni):
    """Runs the dynamic journey simulation."""
    while st.session_state.run_button and (get_end_date() == "" or get_end_date() < df_cumsum['date'].max()):
        update_session_state(df_cumsum)
        update_summary_stats(df, date, total_euro, unique_boni)
        update_chart_stacked(df_cumsum, plot_container_stacked)
        update_chart_bar(df_cumsum, plot_container_bar)
        time.sleep(0.25)  # Simulates time passing
        total_euro.empty()
        st.markdown("")

def update_visuals(df, df_cumsum, plot_container_stacked, plot_container_bar, date, total_euro, unique_boni):
    """Updates visuals when simulation is paused."""
    if 'end_date' not in st.session_state:
        st.session_state.end_date = df_cumsum['date'].min() - timedelta(1)
    update_chart_stacked(df_cumsum, plot_container_stacked)
    update_chart_bar(df_cumsum, plot_container_bar)
    update_summary_stats(df, date, total_euro, unique_boni)

def run():
    setup_header()
    df, df_cumsum = load_data()

    # Set up UI elements
    date, total_euro, unique_boni, reset_button, run_button_placeholder = setup_top_row_controls()

    # Clear columns
    date = date.empty()
    total_euro = total_euro.empty()
    unique_boni = unique_boni.empty()
    reset_button.empty()

    run_button = run_button_placeholder.checkbox("Run / Pause", False)

    plot_container_stacked, plot_container_bar = st.empty(), st.empty()

    # Store button states in session state
    st.session_state.reset_button = reset_button
    st.session_state.run_button = run_button

    # Handle reset button logic
    handle_reset(df_cumsum, plot_container_stacked, plot_container_bar)

    # Run simulation if active
    run_simulation(df, df_cumsum, plot_container_stacked, plot_container_bar, date, total_euro, unique_boni)

    # Update visuals when paused
    update_visuals(df, df_cumsum, plot_container_stacked, plot_container_bar, date, total_euro, unique_boni)

if __name__ == "__main__":
    run()