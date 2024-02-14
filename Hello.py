import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import altair as alt
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def empty_placeholder_plot(ax):
    ax.set_axis_off()  # Hide axes
    ax.text(0.5, 0.5, "Placeholder Plot", ha="center", va="center", fontsize=12, color="gray")

def calculate_boni_performance(df):
    # TODO: Implement function to calculate 
    return 0.75

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
        page_title="dashboard",
        page_icon="👋",
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
    # add column for whether there was 1 visit, 1 - 2 visits, or more than 2 visits
    restaurant_counts = pd.DataFrame(restaurant_counts)
    restaurant_counts.columns = ['count']
    #TODO: coloring and sorting
    restaurant_counts
    chart0 = alt.Chart(restaurant_counts.reset_index()).mark_bar().encode(
        x = "restaurants",
        y = "count"
        # color = "skyblue"
    )
    col11.altair_chart(chart0)
    # col11.pyplot(fig1, clear_figure=True)

    # Column 2 row 1
    fig2 = plt.figure(figsize=(4, 4.21))
    # colors and values
    colors = ['#4dab6d', "#72c66e", "#c1da64", "#f6ee54", "#fabd57", "#f36d54", "#ee4d55"]
    values = [100,80,60,40,20,0,-20, -40]
    x_axis_vals = [0, 0.44, 0.88,1.32,1.76,2.2,2.64]

    ax2 = fig2.add_subplot(projection="polar");

    ax2.bar(x=[0, 0.44, 0.88,1.32,1.76,2.2,2.64], width=0.5, height=0.5, bottom=2,
        linewidth=3, edgecolor="white",
        color=colors, align="edge");

    plt.annotate("High Performing", xy=(0.16,2.1), rotation=-75, color="white", fontweight="bold");
    plt.annotate("Sustainable", xy=(0.65,2.08), rotation=-55, color="white", fontweight="bold");
    plt.annotate("Maturing", xy=(1.14,2.1), rotation=-32, color="white", fontweight="bold");
    plt.annotate("Developing", xy=(1.62,2.2), color="white", fontweight="bold");
    plt.annotate("Foundational", xy=(2.08,2.25), rotation=20, color="white", fontweight="bold");
    plt.annotate("Volatile", xy=(2.46,2.25), rotation=45, color="white", fontweight="bold");
    plt.annotate("Unsustainable", xy=(3.0,2.25), rotation=75, color="white", fontweight="bold");

    for loc, val in zip([0, 0.44, 0.88,1.32,1.76,2.2,2.64, 3.14], values):
        plt.annotate(val, xy=(loc, 2.5), ha="right" if val<=20 else "left");

    plt.annotate("50", xytext=(0,0), xy=(1.1, 2.0),
                arrowprops=dict(arrowstyle="wedge, tail_width=0.5", color="black", shrinkA=0),
                bbox=dict(boxstyle="circle", facecolor="black", linewidth=2.0, ),
                fontsize=45, color="white", ha="center"
                );


    plt.title("Performance Gauge Chart", loc="center", pad=20, fontsize=35, fontweight="bold");

    ax2.set_axis_off()
    col12.pyplot(fig2, clear_figure=True)

    # Second row of plots
    col21, col22, col23 = st.columns([1, 1, 1])

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
    ).configure_axis(
        labelAngle=45
    )
    col21.altair_chart(chart)

    fig4, ax4 = plt.subplots()
    boni_usage_by_month = boni_usage_per_month(df)
    month_order = ['October', 'November', 'December', 'January', 'February']
    # altair chart
    chart2 = alt.Chart(boni_usage_by_month).mark_bar().encode(
        x = alt.X('month_name:N', sort=month_order, axis=alt.Axis(title='Month', labels=True, ticks=True)),
        y = "value",
        color = alt.Color('type:N', scale=alt.Scale(domain=['used', 'unused'], range=['skyblue', 'lightcoral']))
    )

    col22.altair_chart(chart2)

    col23.subheader("Summary")
    col23.write("Top Boni: Zito")
    col23.write("Total Boni Trips: 57")
    col23.write("Unique Boni Tried: 25")
    col23.write("Avg Meal Price: 2.5 EURO")

if __name__ == "__main__":
    run()
