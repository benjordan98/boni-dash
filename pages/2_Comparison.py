import streamlit as st
import pandas as pd
import altair as alt
from utils import create_header_triplet, initialise_session_states

# who ate the most boni
def who_ate_most(df):
    return df['Member'].value_counts().idxmax()

def who_most_unique(df):
    return df.groupby('Member')['restaurant'].nunique().idxmax()

def least_avg_boni(df):
    return df.groupby('Member')['discount_meal_price'].agg('mean').idxmin()

def most_avg_boni(df):
    return df.groupby('Member')['discount_meal_price'].agg('mean').idxmax()

def who_most_one_boni(df):
    return df.groupby('Member')['restaurant'].value_counts().idxmax()[0]

def who_ate_most_mcdonalds(df):
    # Filter the DataFrame to include only rows where the restaurant contains "McDonald's"
    mcdonalds_data = df[df['restaurant'].str.contains("McDonald's", case=False, na=False)]
    # Group by Member and count the occurrences
    mcdonalds_counts = mcdonalds_data['Member'].value_counts()
    # Get the member who ate at a McDonald's restaurant the most
    most_mcdonalds_member = mcdonalds_counts.idxmax()
    return most_mcdonalds_member

def who_most_free_boni(df):
    # Filter the DataFrame to include only rows where 'discount_meal_price' is 0
    df = df[df['discount_meal_price'] == 0]
    
    # Group by 'Member' and count the occurrences
    member_counts = df['Member'].value_counts()
    
    # Get the member who had the most free boni
    most_free_boni_member = member_counts.idxmax()
    
    return most_free_boni_member

def who_used_least(df):
    return df['Member'].value_counts().idxmin()

def display_top_statistics(df):
    """Displays top statistics on Boni consumption."""
    most_boni, most_unique_boni, most_frugal, quality = st.columns(4)
    most_boni.text('🏆 Most Boni: ' + who_ate_most(df))
    most_unique_boni.text('🆕 Most Unique Boni: ' + who_most_unique(df))
    most_frugal.text('🏦 Most Frugal: ' + least_avg_boni(df))
    quality.text('🐏 Life is not Sheep: ' + most_avg_boni(df))

    most_one_boni, most_maccies, most_free, least_boni = st.columns(4)
    most_one_boni.text('💤 Most on one Boni: ' + who_most_one_boni(df))
    most_maccies.text("🍔 Most McDonald's: " + who_ate_most_mcdonalds(df))
    most_free.text("👩‍🎓 Most Free Boni: " + who_most_free_boni(df))
    least_boni.text('👎 Least Boni: ' + who_used_least(df))


def plot_boni_diversity(df):
    """Creates and displays the Boni diversity plot."""
    rest_count_by_member = df.groupby(['Member', 'restaurant']).size().reset_index(name='count')
    rest_count_by_member['percentage'] = rest_count_by_member.groupby('Member')['count'].transform(lambda x: x / x.sum() * 100)

    chart = alt.Chart(rest_count_by_member).mark_bar().encode(
        y=alt.Y('Member:N', sort='-x', axis=alt.Axis(title='Member', labels=True, ticks=True)),
        x=alt.X("percentage:Q", title='Percentage'),
        color='restaurant:N',
        order=alt.Order('count', sort='descending')
    ).properties(title="🆕 Diversity")

    st.altair_chart(chart, use_container_width=True)


def plot_money_spent(df):
    """Creates and displays the total money spent by each member."""
    money_spent_by_member = df.groupby(['Member'])['discount_meal_price'].sum().reset_index()
    money_spent_by_member.columns = ['Member', 'Total']

    chart = alt.Chart(money_spent_by_member).mark_bar().encode(
        y=alt.Y('Member:N', sort='-x', axis=alt.Axis(title='Member', labels=True, ticks=True)),
        x=alt.X('Total:Q', title='Total €')
    ).configure_mark(color="#23BDF3").properties(title='💰 Total Spend')

    st.altair_chart(chart, use_container_width=True)


def plot_spend_distribution(df):
    """Creates and displays the distribution of meal prices by member."""
    chart = alt.Chart(df).transform_density(
        'discount_meal_price',
        as_=['discount_meal_price', 'density'],
        groupby=['Member']
    ).mark_line().encode(
        x=alt.X('discount_meal_price:Q', title='Meal Price'),
        y=alt.Y('density:Q', title='Density'),
        color=alt.Color('Member:N', title='Member'),
        tooltip=['discount_meal_price:Q', 'density:Q']
    ).properties(title="Meal Price by Member")

    st.altair_chart(chart, use_container_width=True)


def run():
    st.set_page_config(
        page_title="Journey",
        page_icon="🗺️",
        layout="wide"
    )
    initialise_session_states()
    create_header_triplet()

    df = st.session_state.combined_df

    # Display statistics
    display_top_statistics(df)

    # Display charts
    plot_boni_diversity(df)
    plot_money_spent(df)
    plot_spend_distribution(df)

run()
