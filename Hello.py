import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import altair as alt
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def boni_spend_per_month(df):
    # group data by month
    by_month = df.groupby(df['date'].dt.to_period('M'))['discount_meal_price'].sum()
    df_by_month = pd.DataFrame(by_month)
    df_by_month.columns = ['cost']
    return df_by_month

def boni_usage_per_month(df):
    # group data by month
    by_month = df.groupby(df['date'].dt.to_period('M')).agg('count')['date']
    df_by_month = pd.DataFrame(by_month)
    df_by_month.columns = ['used']
    # number of working days in each month
    working_days = [21, 21, 19, 21, 20]
    df_by_month['working_days'] = working_days
    # un-used boni
    df_by_month['unused'] = df_by_month['working_days'] - df_by_month['used']
    df_by_month.drop('working_days', axis = 1, inplace = True)
    df_by_month['date'] = pd.to_datetime(df_by_month.index.astype(str))
    # Extract month names
    df_by_month['month_name'] = df_by_month['date'].dt.strftime('%B')
    df.drop('date', axis = 1, inplace = True)
    df_by_month = pd.melt(df_by_month, id_vars=['month_name'], var_name='type')
    return df_by_month

def pre_process_df(df):
    # datetime
    df['date'] = pd.to_datetime(df['date'])

def run():
    st.set_page_config(
        page_title="Dashboard",
        page_icon="🍕"
    )
    img, heading = st.columns([1,8])
    image_path = "boni-removebg-preview.png"  # Replace with the actual path to your image file
    pillow_image = Image.open(image_path)
    scalar = 0.55
    new_image = pillow_image.resize((int(177*scalar), int(197*scalar)))
    img.image(new_image)
    heading.markdown(" # Študentska **prehrana**")

    # Read in data
    df = pd.read_csv('data/data.csv')
    pre_process_df(df)

    # Three columns with different widths
    col11, col12, = st.columns([2, 1])

    # Column 1 row 1
    restaurant_counts = df['restaurant'].value_counts()
    restaurant_counts = pd.DataFrame(restaurant_counts)
    restaurant_counts = restaurant_counts.reset_index()
    restaurant_counts.columns = ['Restaurant', 'Count']
    chart0 = alt.Chart(restaurant_counts.reset_index()).mark_bar().encode(
        x = alt.X('Restaurant:N', sort="-y", axis=alt.Axis(title='Restaurant', labels=True, ticks=True)),
        y = "Count"
    ).configure_mark(
        color = "#23BDF3"
    )
    col11.altair_chart(chart0)
    # col11.pyplot(fig1, clear_figure=True)

    # Column 2 row 1
    # col12.subheader("Summary")
    # col12.write("Top Boni: Zito")
    # col12.write("Total Boni Trips: 57")
    # col12.write("Unique Boni Tried: 25")
    # col12.write("Avg Meal Price: 2.5 EURO")

    # Second row of plots
    col21, col22= st.columns([1, 1])

    # row 2 column 1
    df_by_month = boni_spend_per_month(df)
    df_by_month['Budget Status'] = np.where(df_by_month['cost'] > 50, 'Over-budget', 'Under-budget')

    # Ensure 'date' column is of datetime type
    df_by_month['date'] = pd.to_datetime(df_by_month.index.astype(str))

    # Extract month names
    df_by_month['month_name'] = df_by_month['date'].dt.strftime('%B')
    month_order = ['October', 'November', 'December', 'January', 'February']

    # Altair chart
    chart = alt.Chart(df_by_month).mark_bar().encode(
        x=alt.X('month_name:N', sort=month_order, axis=alt.Axis(title='Month', labels=True, ticks=True)),
        y=alt.Y('cost:Q', axis=alt.Axis(title='Cost (EURO)')),
        color=alt.Color('Budget Status:N', scale=alt.Scale(domain=['Under-budget', 'Over-budget'], range=['skyblue', 'lightcoral'])),
        tooltip=['month_name:N', 'cost:Q', 'Budget Status:N']
    ).properties(
        title='Boni cost by month'
    )
    col21.altair_chart(chart)

    boni_usage_by_month = boni_usage_per_month(df)
    month_order = ['October', 'November', 'December', 'January', 'February']
    # altair chart
    chart2 = alt.Chart(boni_usage_by_month).mark_bar().encode(
        x = alt.X('month_name:N', sort=month_order, axis=alt.Axis(title='Month', labels=True, ticks=True)),
        y = "value",
        color = alt.Color('type:N', scale=alt.Scale(domain=['used', 'unused'], range=['skyblue', 'lightcoral']))
    ).properties(
        title = "Boni utilisation by month"
    )

    col22.altair_chart(chart2)

if __name__ == "__main__":
    run()
