import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import altair as alt
from utils import create_header_triplet, initialise_session_states

def select_member_df(df):
    # order df by date
    df = df.sort_values(by = 'date')
    return df[df['Member'] == st.session_state.member]

def boni_spend_per_month(df):
    """
    Takes standard df and 
    returns boni spend by month df 
    """
    # group data by month
    by_month = df.groupby(df['date'].dt.to_period('M'))['discount_meal_price'].sum()
    df_by_month = pd.DataFrame(by_month)
    df_by_month.columns = ['cost']
    return df_by_month

def boni_usage_per_month(df):
    """
    Takes standard df and returns a df with Used and Unused vouchers by month.
    """
    monthly = (
        df.assign(month=df['date'].dt.to_period('M'))
        .groupby('month')
        .agg(Used=('date', 'count'))
        .reindex(
            pd.period_range(
                start=df['date'].min().to_period('M'),
                end=df['date'].max().to_period('M'),
                freq='M'
            ),
            fill_value=0
        )
    )

    working_days = {
        pd.Period('2023-10', freq='M'): 21,
        pd.Period('2023-11', freq='M'): 21,
        pd.Period('2023-12', freq='M'): 19,
        pd.Period('2024-01', freq='M'): 21,
        pd.Period('2024-02', freq='M'): 20,
    }

    monthly = monthly.reset_index().rename(columns={'index': 'month_period'})
    monthly['Monthly allowance'] = monthly['month_period'].map(working_days)
    monthly['month_name'] = monthly['month_period'].dt.strftime('%b')

    return (
        monthly[['month_name', 'Used', 'Monthly allowance']]
        .rename(columns={'Used': 'Redeemed'})
        .melt(id_vars=['month_name'], var_name='Measure', value_name='value')
    )

# get Boni summary stats functions
def get_top_boni(df):
    """
    Returns the most visited restaurant
    """
    top_restaurant = df['restaurant'].value_counts().idxmax()
    return top_restaurant

def get_longest_streak(df):
    """
    Returns the longest streak 
    i.e. how many consecutive days 
    user went to any restaurant
    """
    df = df.sort_values(by = 'date')
    df = df.drop_duplicates(subset = 'date')
    df['date_diff'] = df['date'].diff().dt.days
    df['date_diff'] = df['date_diff'].fillna(1).astype(int)

    df['streak'] = (df['date_diff'] != 1).cumsum()
    streaks = df.groupby('streak').size()
    longest_streak = streaks.max()

    return longest_streak

def clear_columns():
    # hack to deal with persisting text from Dashboard page
    col11, col12, col13 = st.columns([2, 1, 1])
    col21, col22= st.columns([1, 1])
    # Clear the content of the columns before displaying new content on page 2
    col11.empty()
    col12.empty()
    col13.empty()
    col21.empty()
    col22.empty()

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

def get_restaurant_counts(df):
    """Prepares restaurant visit count data."""
    restaurant_counts = df['restaurant'].value_counts().reset_index()
    restaurant_counts.columns = ['Restaurant', 'Count']
    return restaurant_counts

def display_restaurant_visits(df, col):
    """Displays a bar chart of restaurant visits."""
    restaurant_counts = get_restaurant_counts(df)
    chart = alt.Chart(restaurant_counts).mark_bar().encode(
        x=alt.X('Restaurant:N', sort="-y", axis=alt.Axis(title='Restaurant')),
        y="Count"
    ).configure_mark(color="#23BDF3").properties(title="Restaurants visited")
    col.altair_chart(chart, use_container_width=True)

def display_summary(df, col):
    """Displays key summary metrics for Boni trips."""
    col.subheader("Summary")
    col.text(f'🏆 Top Boni: {get_top_boni(df)}')
    col.text(f"🔢 Total Boni Trips: {df.shape[0]}")
    col.text(f"🆕 Unique Boni Tried: {len(df['restaurant'].unique())}")
    col.text(f"💶 Total Boni Spend: €{df['discount_meal_price'].sum():.2f}")
    col.text(f"💶 Avg Meal Price: {round(df['discount_meal_price'].mean(), 2)} EURO")
    col.text(f"🗓️ Longest Streak: {get_longest_streak(df)} Days")

def prepare_boni_cost_data(df):
    """Processes Boni spend per month data."""
    df_by_month = boni_spend_per_month(df)
    df_by_month['Budget Status'] = np.where(df_by_month['cost'] > 50, 'Over 50EUR budget', 'Under 50EURbudget')
    df_by_month['date'] = pd.to_datetime(df_by_month.index.astype(str))
    df_by_month['month_name'] = df_by_month['date'].dt.strftime('%b')
    return df_by_month

def display_boni_cost_by_month(df, col):
    """Displays Boni spending chart by month."""
    df_by_month = prepare_boni_cost_data(df)
    month_order = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb']
    chart = alt.Chart(df_by_month).mark_bar().encode(
        x=alt.X('month_name:N', sort=month_order, axis=alt.Axis(title='Month')),
        y=alt.Y('cost:Q', axis=alt.Axis(title='Cost (EURO)')),
        color=alt.Color('Budget Status:N', scale=alt.Scale(domain=['Under 50EURbudget', 'Over 50EUR budget'])),
        tooltip=['month_name:N', 'cost:Q', 'Budget Status:N']
    ).properties(title='Boni Cost by Month')
    col.altair_chart(chart, use_container_width=True)

def prepare_boni_utilisation_data(df):
    """Processes Boni utilisation per month data."""
    return boni_usage_per_month(df)

def display_boni_utilisation_by_month(df, col):
    """Displays Boni utilisation by month."""
    boni_usage_by_month = prepare_boni_utilisation_data(df)
    month_order = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb']

    chart = alt.Chart(boni_usage_by_month).mark_bar().encode(
        x=alt.X('month_name:N', sort=month_order, axis=alt.Axis(title='Month')),
        xOffset=alt.XOffset('Measure:N', sort=['Monthly allowance', 'Redeemed']),
        y=alt.Y('value:Q', axis=alt.Axis(title='Credits')),
        color=alt.Color(
            'Measure:N',
            sort=['Monthly allowance', 'Redeemed'],
            scale=alt.Scale(domain=['Monthly allowance', 'Redeemed'], range=['#FFA500', '#23BDF3'])
        ),
        tooltip=['month_name:N', 'Measure:N', 'value:Q']
    ).properties(title='Boni Vouchers: Allowance vs Redeemed')

    col.altair_chart(chart, use_container_width=True)

def run():
    st.set_page_config(
        page_title="Dashboard",
        page_icon="🍕",
        layout="wide"
    )
    
    initialise_session_states()

    clear_columns()

    _, _, member = create_header_triplet()

    # Select who's dashboard to view
    setup_members_select_box(member)
    
     # Load selected member's data
    df = select_member_df(st.session_state.combined_df)

    # Define layout
    col11, col12 = st.columns([2, 1])
    col21, col22 = st.columns([1, 1])

    # Populate dashboard sections
    display_restaurant_visits(df, col11)
    display_summary(df, col12)
    display_boni_cost_by_month(df, col21)
    display_boni_utilisation_by_month(df, col22)

run()
