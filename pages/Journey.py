import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
from datetime import datetime, timedelta
import time
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def cum_sum_restaurant_visits(df):
    df2 = df.groupby([pd.Grouper(key="date", freq="D"), "restaurant"]).size().unstack().fillna(0).reset_index()
    return df2

def fill_missing_dates(df):
    df_filled = df.set_index('date').resample('D').first().fillna(0).cumsum()
    return df_filled.reset_index()

def pre_process_df(df):
    df['date'] = pd.to_datetime(df['date'])

# Function to update session state
# Function to update session state
def update_session_state(df_cumsum, date):
    if 'end_date' not in st.session_state:
        st.session_state.end_date = df_cumsum['date'].min()
    else:
        st.session_state.end_date += timedelta(days=1)
    date.write(get_end_date())

def get_end_date():
    if 'end_date' not in st.session_state:
        return ""
    return st.session_state.end_date

# Function to update data and plot
def update_chart(df_cumsum, plot_container):
    # Get the subset of data up to the specified date
    end_date_subset = st.session_state.end_date
    df_subset = df_cumsum[df_cumsum['date'] <= end_date_subset]

    # Melt DataFrame for Plotly Express
    df_melted = df_subset.melt(id_vars='date', var_name='Restaurant', value_name='Cumulative Visits')

    # Create a bar chart using Plotly Express
    fig = px.bar(df_melted, x='date', y='Cumulative Visits', color='Restaurant',
                    labels={'Cumulative Visits': 'Y-axis label'},
                    template='plotly_dark')

    # Update the container with the new plot
    plot_container.plotly_chart(fig, use_container_width=True)

def update_chart2(df_cumsum, plot_container):
    # Get the subset of data up to the specified date
    end_date_subset = st.session_state.end_date
    df_subset = df_cumsum[(df_cumsum['date'] <= end_date_subset) & (df_cumsum['date'] >= end_date_subset)]

    # Melt DataFrame for Plotly Express
    df_melted = df_subset.melt(id_vars='date', var_name='Restaurant', value_name='Cumulative Visits')
    df_melted = df_melted.sort_values(by = 'Cumulative Visits', ascending = True)
    # remove restaurants with no visits
    df_melted = df_melted[df_melted['Cumulative Visits'] > 0]

    # Create a bar chart using Plotly Express
    fig = px.bar(df_melted, x='Cumulative Visits', y='Restaurant',
                    labels={'Cumulative Visits': 'Y-axis label'},
                    template='plotly_dark')

    # Update the container with the new plot
    plot_container.plotly_chart(fig, use_container_width=True)

def run():
    st.set_page_config(
        page_title="Journey",
        page_icon="🍕",
        layout="wide"
    )

    # Displays title and image
    img, heading = st.columns([1,8])
    image_path = "boni-removebg-preview.png"
    pillow_image = Image.open(image_path)
    scalar = 0.55
    new_image = pillow_image.resize((int(177*scalar), int(197*scalar)))
    img.image(new_image)
    heading.markdown(" # Študentska **prehrana**")

    # Read in data
    df = pd.read_csv('data/data.csv')
    pre_process_df(df)
    df_cumsum = cum_sum_restaurant_visits(df)
    df_cumsum = fill_missing_dates(df_cumsum)

    # Place buttons at the top
    reset_button, run_pause_button, date = st.columns(3)

    # Checkbox for run/pause
    run_button = run_pause_button.checkbox("Run / Pause", True)
    date = date.empty()

    # Create an empty container for the dynamic plot
    plot_container = st.empty()
    plot_container2 = st.empty()

    if reset_button.button("Reset Data"):
        st.session_state.end_date = df_cumsum['date'].min() - timedelta(1)
        update_chart(df_cumsum, plot_container)

    # Continually update dynamic chart
    while run_button:
        update_session_state(df_cumsum, date)
        update_chart(df_cumsum, plot_container)
        update_chart2(df_cumsum, plot_container2)
        time.sleep(0.5)
        st.markdown("")

    update_chart(df_cumsum, plot_container)

if __name__ == "__main__":
    run()
