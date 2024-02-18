import streamlit as st
import plotly.express as px
import pandas as pd


# Need to get data for different members
# Need to merge into csv with feature for member name
# Group by name and date
# Merge the two joureny plots
# Stacked bar of frequency or number of unique boni
# Row for each member
# No date field on plot but update over date

# Maybe some other comparison plots
st.write("Horse Race of Piran Members")

def update_chart(df_cumsum, plot_container):
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

def cum_sum_restaurant_visits(df):
    df2 = df.groupby([pd.Grouper(key="date", freq="D"), "restaurant"]).size().unstack().fillna(0).reset_index()
    return df2

def fill_missing_dates(df):
    df_filled = df.set_index('date').resample('D').first().fillna(0).cumsum()
    return df_filled.reset_index()

def pre_process_df(df):
    df['date'] = pd.to_datetime(df['date'])

# Create an empty container for the dynamic plot
plot_container = st.empty()
