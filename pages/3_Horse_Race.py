import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import timedelta
import time
from utils import create_header_triplet, pre_process_df, initialise_session_states

# Processing dataframe functions
def cum_sum_restaurant_visits(df):
    df2 = df.groupby([pd.Grouper(key="date", freq="D"), "restaurant"]).size().unstack().fillna(0).reset_index()
    return df2

def fill_missing_dates(df):
    """
    Make dataframe continuous by date for dynamic plotting!
    """
    # add a new row for the last recorded date of all members
    if df['date'].max() < st.session_state.last_recorded_date:
        new_row = pd.DataFrame(0, index=[0], columns=df.columns)
        new_row['date'] = st.session_state.last_recorded_date
        df = pd.concat([df, new_row], ignore_index=True)
    # then fill in the gaps
    df_filled = df.set_index('date').resample('D').first().fillna(0).cumsum()
    return df_filled.reset_index()

# Session state functions
def update_session_state(df):
    if 'end_date' not in st.session_state:
        st.session_state.end_date = df['date'].min()
    else:
        st.session_state.end_date += timedelta(days=1)

def get_end_date():
    if 'end_date' not in st.session_state:
        return ""
    return st.session_state.end_date

# Update chart
def update_chart(df, plot_container):
    # Get the subset of data up to the specified date
    end_date_subset = st.session_state.end_date
    df_melted = pd.DataFrame()
    # for each member perform following separately and then combine the df
    for member in df['Member'].unique():
        df_member = df[df['Member'] == member]
        df_cumsum = cum_sum_restaurant_visits(df_member)
        # fill missing values
        df_cumsum = fill_missing_dates(df_cumsum)
        # Padd the df with zeros to max date for member in dataframe
        df_subset = df_cumsum[(df_cumsum['date'] <= end_date_subset) & (df_cumsum['date'] >= end_date_subset)]
        # Melt DataFrame for Plotly Express
        df_melted_member = df_subset.melt(id_vars='date', var_name='Restaurant', value_name='Cumulative Visits')
        df_melted_member['Member'] = member
        df_melted = pd.concat([df_melted, df_melted_member])
 
    # remove restaurants with no visits
    df_melted = df_melted[df_melted['Cumulative Visits'] > 0]
    # sort member by which member has the most visits!

    fig = px.bar(df_melted, x='Cumulative Visits', y='Member',
                 title= "Boni Horse Race",
                 color='Restaurant',
                 labels={'Cumulative Visits': 'Count'},
                 template='plotly_dark',
                 category_orders={'Restaurant': df_melted.groupby('Restaurant')['Cumulative Visits'].sum().sort_values(ascending=False).index,
                                  'Member': df_melted.groupby('Member')['Cumulative Visits'].sum().sort_values(ascending=False).index})

    # sort by members most boni
    # Update the container with the new plot
    plot_container.plotly_chart(fig, use_container_width=True, key=f"bar_chart_{time.time()}")

def reset(df, plot_container):
    st.session_state.end_date = df['date'].min() - timedelta(1)
    update_chart(df, plot_container)


def setup_page():
    st.set_page_config(
        page_title="Dashboard",
        page_icon="🍕",
        layout="wide"
    )
    initialise_session_states()
    create_header_triplet()

def clear_previous_page():
    cols = st.columns(6)
    for col in cols:
        col.empty()

def create_controls():
    date_placeholder, run_button_placeholder, reset_button_placeholder = st.columns(3)
    run_button = run_button_placeholder.checkbox("Run / Pause", False)
    date_display = date_placeholder.empty()
    plot_container = st.empty()
    
    return run_button, date_display, plot_container, reset_button_placeholder

def reset_if_requested(reset_button, horse_race_df, plot_container):
    if reset_button.button("Reset Data"):
        reset(horse_race_df, plot_container)

def run_simulation(run_button, horse_race_df, date_display, plot_container):
    while run_button and (get_end_date() == "" or get_end_date() < horse_race_df['date'].max()):
        update_session_state(horse_race_df)
        update_chart(horse_race_df, plot_container)
        date_display.write("Current Date: " + str(get_end_date())[:10])
        time.sleep(0.25)
        st.markdown("")

def update_paused_state(horse_race_df, date_display, plot_container):
    if 'end_date' not in st.session_state:
        st.session_state.end_date = horse_race_df['date'].min() - timedelta(1)
    update_chart(horse_race_df, plot_container)
    date_display.write("Current Date: " + str(get_end_date())[:10])

def run():
    setup_page()
    clear_previous_page()
    horse_race_df = st.session_state.combined_df
    run_button, date_display, plot_container, reset_button = create_controls()
    reset_if_requested(reset_button, horse_race_df, plot_container)
    run_simulation(run_button, horse_race_df, date_display, plot_container)
    update_paused_state(horse_race_df, date_display, plot_container)

if __name__ == "__main__":
    run()