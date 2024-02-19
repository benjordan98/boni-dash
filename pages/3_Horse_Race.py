import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from PIL import Image
from datetime import timedelta
import time
from streamlit_js_eval import streamlit_js_eval

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
        df_subset = df_cumsum[(df_cumsum['date'] <= end_date_subset) & (df_cumsum['date'] >= end_date_subset)]
        # Melt DataFrame for Plotly Express
        df_melted_member = df_subset.melt(id_vars='date', var_name='Restaurant', value_name='Cumulative Visits')
        df_melted_member['Member'] = member
        df_melted = pd.concat([df_melted, df_melted_member])
 
    # remove restaurants with no visits
    df_melted = df_melted[df_melted['Cumulative Visits'] > 0]
    # sort member by which member has the most visits!
    # df_melted

    fig = px.bar(df_melted, x='Cumulative Visits', y='Member',
                 title= "Boni Horse Race",
                 color='Restaurant',
                 labels={'Cumulative Visits': 'Count'},
                 template='plotly_dark',
                 category_orders={'Restaurant': df_melted.groupby('Restaurant')['Cumulative Visits'].sum().sort_values(ascending=False).index,
                                  'Member': df_melted.groupby('Member')['Cumulative Visits'].sum().sort_values(ascending=False).index})

    # sort by members most boni
    # Update the container with the new plot
    plot_container.plotly_chart(fig, use_container_width=True)

def reset(df, plot_container):
    st.session_state.end_date = df['date'].min() - timedelta(1)
    update_chart(df, plot_container)


def run():
    st.set_page_config(
        page_title="Dashboard",
        page_icon="🍕",
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

    # TODO: should make df a session state
    # Read in data
    df = pd.read_csv('data/combined_data.csv')
    pre_process_df(df)

    # # clear from previous pages
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.empty()
    col2.empty()
    col3.empty()
    col4.empty()
    col5.empty()
    col6.empty()
    
    date_placeholder, run_button_placeholder, reset_button = st.columns(3)
    run_button = run_button_placeholder.checkbox("Run / Pause", False)
    date = date_placeholder.empty()
    # Create an empty container for the dynamic plot
    plot_container = st.empty()

    if reset_button.button("Reset Data"):
        reset(df, plot_container)

    while run_button and (get_end_date() == "" or get_end_date() < df['date'].max()):
        update_session_state(df)
        update_chart(df, plot_container)
        date.write("Current Date: " + str(get_end_date())[:10])
        time.sleep(0.25)
        st.markdown("")

    # for paused version
    if 'end_date' not in st.session_state:
        st.session_state.end_date = df['date'].min() - timedelta(1)

    update_chart(df, plot_container)
    # update date
    date.write("Current Date: " + str(get_end_date())[:10])

if __name__ == "__main__":
    run()