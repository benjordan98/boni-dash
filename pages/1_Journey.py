import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
from datetime import timedelta
import time
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


# Processing dataframe functions
# TODO: this is used across multiple pages so abstract it!
def pre_process_df(df):
    df['date'] = pd.to_datetime(df['date'])

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
    plot_container.plotly_chart(fig, use_container_width=True)

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
    plot_container.plotly_chart(fig, use_container_width=True)

def update_summary_stats(df, date, total_euro, unique_boni):
    # update top row
    date.write("Current Date: " + str(get_end_date())[:10])
    total_euro.write("Total Spend: €" + str(round(get_boni_total(df), 2)))
    unique_boni.write("Tried " + str(get_unique_boni(df)) + " Boni")


def run():
    st.set_page_config(
        page_title="Journey",
        page_icon="🗺️",
        layout="wide"
    )

    # TODO: this is on every page - abstract it
    # Displays title and image
    img, heading, member = st.columns([1,8, 2])
    # image
    image_path = "boni-removebg-preview.png"
    pillow_image = Image.open(image_path)
    scalar = 0.55
    new_image = pillow_image.resize((int(177*scalar), int(197*scalar)))
    img.image(new_image)
    # title
    heading.markdown(" # Študentska **prehrana**")

    # Read in data
    df = pd.read_csv('data/data_18_02.csv')
    pre_process_df(df)
    
    # Create dataframe for journey plots
    df_cumsum = cum_sum_restaurant_visits(df)
    df_cumsum = fill_missing_dates(df_cumsum)

    # Place buttons and summary stats at top of page
    date, total_euro_placeholder, unique_boni_placeholder, reset_button, run_button_placeholder, member = st.columns(6)
    # Clear columns
    date.empty()
    total_euro_placeholder.empty()
    unique_boni_placeholder.empty() 
    reset_button.empty()
    run_button_placeholder.empty()

    member.selectbox(
        label = 'Piran Member',
        options = st.session_state.members,
        key='member',
        index = st.session_state.index)
    # update index
    st.session_state.index = st.session_state.members.index(st.session_state.member)

    # set up objects for top row
    #total euro
    total_euro = total_euro_placeholder.empty()
    #unique boni tried
    unique_boni = unique_boni_placeholder.empty()
    # Checkbox for run/pause
    run_button = run_button_placeholder.checkbox("Run / Pause", False)
    # date placeholder
    date = date.empty()
    # Create an empty container for the dynamic plot
    plot_container_stacked = st.empty()
    plot_container_bar = st.empty()

    # If reset button is pressed
    # reset end date to beginning
    # then update plots
    if reset_button.button("Reset Data"):
        st.session_state.end_date = df_cumsum['date'].min() - timedelta(1)
        update_chart_stacked(df_cumsum, plot_container_stacked)
        update_chart_bar(df_cumsum, plot_container_bar)

    # Continually update dynamic chart
    while run_button and (get_end_date() == "" or get_end_date() < df_cumsum['date'].max()):
        # Update session state, summary stats and plots
        update_session_state(df_cumsum)
        update_summary_stats(df, date, total_euro, unique_boni)
        update_chart_stacked(df_cumsum, plot_container_stacked)
        update_chart_bar(df_cumsum, plot_container_bar)
        # one day is 0.25 seconds
        time.sleep(0.25)
        total_euro.empty()
        st.markdown("")

    # For paused version
    update_chart_stacked(df_cumsum, plot_container_stacked)
    update_chart_bar(df_cumsum, plot_container_bar)
    update_summary_stats(df, date, total_euro, unique_boni)

if __name__ == "__main__":
    run()
