import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from PIL import Image
from datetime import timedelta
import time


# Need to get data for different members
# Need to merge into csv with feature for member name
# Group by name and date
# Merge the two joureny plots
# Stacked bar of frequency or number of unique boni
# Row for each member
# No date field on plot but update over date

# Maybe some other comparison plots

def get_end_date():
    if 'end_date' not in st.session_state:
        return ""
    return st.session_state.end_date

def update_session_state(df_cumsum):
    if 'end_date' not in st.session_state:
        st.session_state.end_date = df_cumsum['date'].min()
    else:
        st.session_state.end_date += timedelta(days=1)

def update_chart2(df_cumsum, plot_container):
    # Get the subset of data up to the specified date
    end_date_subset = st.session_state.end_date
    df_subset = df_cumsum[(df_cumsum['date'] <= end_date_subset) & (df_cumsum['date'] >= end_date_subset)]

    # Melt DataFrame for Plotly Express
    df_melted = df_subset.melt(id_vars='date', var_name='Restaurant', value_name='Cumulative Visits')
    df_melted['Member'] = 'Ben'
 
    # remove restaurants with no visits
    df_melted = df_melted[df_melted['Cumulative Visits'] > 0]

    fig = px.bar(df_melted, x='Cumulative Visits', y='Member',
                 title= "Boni Horse Race",
                 color='Restaurant',
                 labels={'Cumulative Visits': 'Count'},
                 template='plotly_dark',
                 category_orders={'Restaurant': df_melted.groupby('Restaurant')['Cumulative Visits'].sum().sort_values(ascending=False).index})

    # Update the container with the new plot
    plot_container.plotly_chart(fig, use_container_width=True)

def cum_sum_restaurant_visits(df):
    df2 = df.groupby([pd.Grouper(key="date", freq="D"), "restaurant"]).size().unstack().fillna(0).reset_index()
    return df2

def fill_missing_dates(df):
    df_filled = df.set_index('date').resample('D').first().fillna(0).cumsum()
    return df_filled.reset_index()

def pre_process_df(df):
    df['date'] = pd.to_datetime(df['date'])


def run():
    st.set_page_config(
        page_title="Dashboard",
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
    df = pd.read_csv('data/data_18_02.csv')
    # for now just add member column with my name
    df['Member'] = 'Ben'
    
    pre_process_df(df)
    df_cumsum = cum_sum_restaurant_visits(df)
    df_cumsum = fill_missing_dates(df_cumsum)

    # For buttons
    date, total_euro, unique_boni, reset_button, run_pause_button = st.columns(5)
    
    run_pause_button, reset_button = st.columns(2)
    run_button = run_pause_button.checkbox("Run / Pause", True)
    # Create an empty container for the dynamic plot
    plot_container = st.empty()


    if reset_button.button("Reset Data"):
        st.session_state.end_date = df_cumsum['date'].min() - timedelta(1)
        update_chart2(df_cumsum, plot_container)

    while run_button and (get_end_date() == "" or get_end_date() < df_cumsum['date'].max()):
        update_session_state(df_cumsum)
        update_chart2(df_cumsum, plot_container)
        time.sleep(0.25)
        st.markdown("")

    # for paused version
    update_chart2(df_cumsum, plot_container)

if __name__ == "__main__":
    run()