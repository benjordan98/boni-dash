import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from utils import add_plotly_animation_controls, create_header_triplet, initialise_session_states


def build_race_chart(df):
    dates = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    frame_labels = [date.strftime("%Y-%m-%d") for date in dates]
    members = sorted(df["Member"].unique())
    restaurants = sorted(df["restaurant"].unique())

    cumulative_visits = {}
    for member in members:
        daily = (
            df[df["Member"] == member]
            .groupby([pd.Grouper(key="date", freq="D"), "restaurant"])
            .size()
            .unstack(fill_value=0)
            .reindex(index=dates, columns=restaurants, fill_value=0)
        )
        cumulative_visits[member] = daily.cumsum()

    colors = {
        restaurant: px.colors.qualitative.Plotly[index % len(px.colors.qualitative.Plotly)]
        for index, restaurant in enumerate(restaurants)
    }
    frames = []
    maximum_total = 0

    for date, label in zip(dates, frame_labels):
        ranked_members = sorted(
            members,
            key=lambda member: cumulative_visits[member].loc[date].sum(),
            reverse=True,
        )
        maximum_total = max(
            maximum_total,
            max(
                (
                    cumulative_visits[member].loc[date].sum()
                    for member in members
                ),
                default=0,
            ),
        )
        traces = [
            go.Bar(
                name=restaurant,
                orientation="h",
                x=[
                    int(cumulative_visits[member].loc[date, restaurant])
                    for member in ranked_members
                ],
                y=ranked_members,
                marker={"color": colors[restaurant]},
            )
            for restaurant in restaurants
        ]
        frames.append(
            go.Frame(
                name=label,
                data=traces,
                layout=go.Layout(
                    yaxis={
                        "categoryorder": "array",
                        "categoryarray": list(reversed(ranked_members)),
                    },
                ),
            )
        )

    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(
        title={
            "text": "Boni Horse Race",
            "x": 0.02,
            "y": 0.98,
            "xanchor": "left",
            "yanchor": "top",
        },
        barmode="stack",
        template="plotly_dark",
        xaxis={"title": "Cumulative Visits", "range": [0, max(maximum_total * 1.1, 1)]},
        yaxis={
            "title": "Member",
            "categoryorder": "array",
            "categoryarray": frames[0].layout.yaxis.categoryarray,
        },
    )
    return add_plotly_animation_controls(
        fig,
        frame_labels,
        button_y=1.02,
        button_yanchor="bottom",
        slider_y=-0.16,
        top_margin=90,
        bottom_margin=80,
    )


def setup_page():
    st.set_page_config(page_title="Dashboard", page_icon="🍕", layout="wide")
    initialise_session_states()
    create_header_triplet()


def run():
    setup_page()
    st.plotly_chart(
        build_race_chart(st.session_state.combined_df),
        width="stretch",
        height=650,
        key="horse_race_chart",
    )


if __name__ == "__main__":
    run()
