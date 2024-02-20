import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import altair as alt

# Processing dataframe functions
def pre_process_df(df):
    """
    Any standard pre-processing of df
    for all charts
    """
    # datetime
    df['date'] = pd.to_datetime(df['date'])
    return df

def select_member_df(df):
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
    Takes standard df and 
    returns a df with Used and Unused vouchers
    by month
    """
    # group data by month
    by_month = df.groupby(df['date'].dt.to_period('M')).agg('count')['date']
    df_by_month = pd.DataFrame(by_month)
    df_by_month.columns = ['Used']
    # number of working days in each month
    working_days = [21, 21, 19, 21, 20]
    df_by_month['working_days'] = working_days
    # un-used boni
    # df_by_month['Unused'] = df_by_month['working_days'] - df_by_month['Used']
    df_by_month['Unused'] = np.where(df_by_month['working_days'] < df_by_month['Used'], 0, df_by_month['working_days'] - df_by_month['Used'])
    df_by_month.drop('working_days', axis = 1, inplace = True)
    df_by_month['date'] = pd.to_datetime(df_by_month.index.astype(str))
    # Extract month names
    df_by_month['month_name'] = df_by_month['date'].dt.strftime('%B')
    df_by_month.drop('date', axis = 1, inplace = True)
    # convert to long format
    df_by_month = pd.melt(df_by_month, id_vars=['month_name'], var_name='Utilisation')
    return df_by_month

# get Boni summary stats functions
def get_top_boni(df):
    """
    Returns the most visited restaurant
    """
    # get the name of the restaurant with the most visits
    top_restaurant = df['restaurant'].value_counts().idxmax()
    return top_restaurant

def get_longest_streak(df):
    """
    Returns the longest streak 
    i.e. how many consecutive days 
    user went to any restaurant
    """
    # identify the longest streak of consecutive days with a visit to any restaurant
    df['date'] = pd.to_datetime(df['date'])
    df['date_diff'] = df['date'].diff().dt.days
    df['date_diff'] = df['date_diff'].fillna(1)
    print(df)
    df['date_diff'] = df['date_diff'].astype(int)
    df['streak'] = (df['date_diff'] != 1).cumsum()
    streaks = df.groupby('streak').size()
    longest_streak = streaks.max()
    return longest_streak

def run():
    st.set_page_config(
        page_title="Dashboard",
        page_icon="🍕",
        layout="wide"
    )
    # inter page variables
    if 'member' not in st.session_state:
        st.session_state.member = 'Ben'
    # list of members
    if 'members' not in st.session_state:
        # st.session_state.members = ('Ben', 'Hubert', 'Kasia', 'Tonda', 'Tomas', 
        #                             'Oskar', 'Linn', 'Sofia')
        st.session_state.members = ('Ben', 'Oskar', 'Tonda')
        
    if 'combined_df' not in st.session_state:
        combined_df = pre_process_df(pd.read_csv('data/combined_data2.csv'))
        st.session_state.combined_df = combined_df

    if 'last_recorded_date' not in st.session_state:
        st.session_state.last_recorded_date = st.session_state.combined_df['date'].max()

    # hack to deal with persisting text from Dashboard page
    col11, col12, col13 = st.columns([2, 1, 1])
    col21, col22= st.columns([1, 1])
    # Clear the content of the columns before displaying new content on page 2
    col11.empty()
    col12.empty()
    col13.empty()
    col21.empty()
    col22.empty()

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
    # Select who's dashboard to view
    member.selectbox(
        label = 'Piran Member',
        options = st.session_state.members,
        key='member',
        index = st.session_state.members.index(st.session_state.member))
    
    # Load data
    df = select_member_df(st.session_state.combined_df)
    # Initialise columns
    col11, col12 = st.columns([2, 1])
    col21, col22= st.columns([1, 1])

    # Row 1 column 1 - Restaurant visits count
    restaurant_counts = df['restaurant'].value_counts()
    restaurant_counts = pd.DataFrame(restaurant_counts)
    restaurant_counts = restaurant_counts.reset_index()
    restaurant_counts.columns = ['Restaurant', 'Count']
    chart0 = alt.Chart(restaurant_counts.reset_index()).mark_bar().encode(
        x = alt.X('Restaurant:N', sort="-y", axis=alt.Axis(title='Restaurant', labels=True, ticks=True)),
        y = "Count"
    ).configure_mark(
        color = "#23BDF3"
    ).properties(
        title = "Restaurants visited"
    )
    col11.altair_chart(chart0, use_container_width=True)

    # Row 1 column 2 - Summary text
    col12.subheader("Summary")
    top_boni = get_top_boni(df)
    col12.text('🏆 Top Boni: ' + top_boni)
    total_trips = df.shape[0]
    col12.text("🔢 Total Boni Trips: " + str(total_trips))
    unique_boni = len(df['restaurant'].unique())
    col12.text("🆕 Unique Boni Tried: " + str(unique_boni))
    avg_price = round(df['discount_meal_price'].mean(), 2)
    col12.text("💶 Avg Meal Price: " + str(avg_price) + " EURO")
    longest_streak = get_longest_streak(df)
    col12.text("🗓️ Longest Streak: " + str(longest_streak) + " Days")

    # Row 2 column 1 - Boni cost by month
    df_by_month = boni_spend_per_month(df)
    df_by_month['Budget Status'] = np.where(df_by_month['cost'] > 50, 'Over-budget', 'Under-budget')
    # Ensure 'date' column is of datetime type
    df_by_month['date'] = pd.to_datetime(df_by_month.index.astype(str))
    # Extract month names
    df_by_month['month_name'] = df_by_month['date'].dt.strftime('%B')
    month_order = ['October', 'November', 'December', 'January', 'February']
    # Altair chart
    chart = alt.Chart(df_by_month).mark_bar().encode(
        y=alt.Y('month_name:N', sort=month_order, axis=alt.Axis(title='Month', labels=True, ticks=True)),
        x=alt.X('cost:Q', axis=alt.Axis(title='Cost (EURO)')),
        color=alt.Color('Budget Status:N', scale=alt.Scale(domain=['Under-budget', 'Over-budget'], range=['#23BDF3', '#FFA500'])),
        tooltip=['month_name:N', 'cost:Q', 'Budget Status:N']
    ).properties(
        title='Boni Cost by Month'
    )
    col21.altair_chart(chart, use_container_width=True)

    # Row 2 column 2 - Boni utlisation by month
    boni_usage_by_month = boni_usage_per_month(df)
    # altair chart
    chart2 = alt.Chart(boni_usage_by_month).mark_bar().encode(
        y = alt.Y('month_name:N', sort=month_order, axis=alt.Axis(title='Month', labels=True, ticks=True)),
        x = "value",
        color = alt.Color('Utilisation:N', scale=alt.Scale(domain=['Unused', 'Used'], range=['#FFA500', '#23BDF3'])),
        order=alt.Order(
        # Sort the segments of the bars by this field
        'Utilisation',
        sort='descending'
        )
    ).properties(
        title = "Boni Utilisation by Month"
    )
    col22.altair_chart(chart2, use_container_width=True)

run()
