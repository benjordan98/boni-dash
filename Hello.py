import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
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
    df_by_month.columns = ['count']
    # number of working days in each month
    working_days = [21, 21, 19, 21, 20]
    df_by_month['working_days'] = working_days
    # un-used boni
    df_by_month['unused'] = df_by_month['working_days'] - df_by_month['count']
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
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    # plot the count of visits and colour by visit type
    restaurant_counts['count'].plot(kind='bar', ax=ax1, color = np.where(restaurant_counts['count'] == 1, 'skyblue', np.where(restaurant_counts['count'] == 2, 'lightcoral', 'lightgreen')))
    ax1.set_xlabel('Number of visits')
    ax1.set_ylabel('Count')
    ax1.set_title('Boni restaurant visits')
    col11.pyplot(fig1, clear_figure=True)

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
    fig3, ax3 = plt.subplots()
    df_by_month = boni_spend_per_month(df)
    colors = np.where(df_by_month['cost'] > 50, 'lightcoral', 'skyblue')
    bars = df_by_month['cost'].plot(kind='bar', ax=ax3, color=colors)
    # Relabel x-ticks
    ax3.set_xticklabels(['October', 'November', 'December', 'January', 'February'])
    # Rotate x-tick labels by 45 degrees
    plt.xticks(rotation=45)
    ax3.set_xlabel('Month')
    ax3.set_ylabel('Cost (EURO)')
    # Had some trouble with the legend so I did it manually
    legend_labels = ['Under-budget', 'Over-budget']
    legend_colors = ['skyblue', 'lightcoral']
    legend_handles = [plt.Line2D([0], [0], color=color, lw=4) for color in legend_colors]
    ax3.legend(legend_handles, legend_labels, title='Budget Status')
    ax3.set_title('Boni cost by month')
    col21.pyplot(fig3)

    fig4, ax4 = plt.subplots()
    boni_usage_by_month = boni_usage_per_month(df)
    boni_usage_by_month[['count', 'unused']].plot(kind='bar', ax=ax4, color=['skyblue', 'lightcoral'], stacked=True)
    # relabel x-ticks
    ax4.set_xticklabels(['October', 'November', 'December', 'January', 'February'])
    # make y-ticks integers
    ax4.yaxis.get_major_locator().set_params(integer=True)
    # rotate 45 degrees
    plt.xticks(rotation=45)
    ax4.set_xlabel('Month')
    ax4.set_ylabel('Count')
    ax4.set_title('Boni usage by month')
    # add legend
    ax4.legend(['Used', 'Unused'])
    col22.pyplot(fig4, clear_figure=True)

    col23.subheader("Summary")
    col23.write("Top Boni: Zito")
    col23.write("Total Boni Trips: 57")
    col23.write("Unique Boni Tried: 25")
    col23.write("Avg Meal Price: 2.5 EURO")

if __name__ == "__main__":
    run()
