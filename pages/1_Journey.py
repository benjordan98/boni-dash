import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils import add_plotly_animation_controls, create_header_triplet, initialise_session_states


def select_member_df(df):
    return df[df["Member"] == st.session_state.member]


def cum_sum_restaurant_visits(df):
    daily_visits = (
        df.groupby([pd.Grouper(key="date", freq="D"), "restaurant"])
        .size()
        .unstack()
        .fillna(0)
        .reset_index()
    )
    return daily_visits


def fill_missing_dates(df):
    return (
        df.set_index("date")
        .resample("D")
        .first()
        .fillna(0)
        .cumsum()
        .reset_index()
    )


def build_stacked_chart(df_cumsum):
    dates = df_cumsum["date"].tolist()
    frame_labels = [date.strftime("%Y-%m-%d") for date in dates]
    restaurants = [column for column in df_cumsum.columns if column != "date"]
    max_daily_total = df_cumsum[restaurants].sum(axis=1).max()

    frames = []
    for frame_index, label in enumerate(frame_labels):
        frame_traces = [
            go.Bar(
                name=restaurant,
                x=dates[: frame_index + 1],
                y=df_cumsum[restaurant].iloc[: frame_index + 1].tolist(),
            )
            for restaurant in restaurants
        ]
        frames.append(
            go.Frame(
                name=label,
                data=frame_traces,
                layout=go.Layout(title={"text": f"Journey"}),
            )
        )

    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(
        title={"text": f"Journey"},
        barmode="stack",
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Cumulative Visits",
        xaxis={"range": [frame_labels[0], frame_labels[-1]], "autorange": False},
        yaxis={
            "range": [0, max(max_daily_total * 1.1, 1)],
            "autorange": False,
        },
    )
    return add_plotly_animation_controls(
        fig,
        frame_labels,
        button_y=1.02,
        button_yanchor="bottom",
        slider_y=-0.16,
        top_margin=105,
        bottom_margin=80,
    )


def build_restaurant_chart(df_cumsum):
    dates = df_cumsum["date"].tolist()
    frame_labels = [date.strftime("%Y-%m-%d") for date in dates]
    restaurants = [column for column in df_cumsum.columns if column != "date"]
    ranked_restaurants = sorted(
        restaurants,
        key=lambda restaurant: df_cumsum[restaurant].iloc[-1],
    )
    restaurant_positions = {
        restaurant: position
        for position, restaurant in enumerate(ranked_restaurants)
    }
    color_by_visits = {
        "1 visit": "skyblue",
        "2 visits": "lightcoral",
        "2+ visits": "lightgreen",
    }
    frames = []

    for label, (_, row) in zip(frame_labels, df_cumsum.iterrows()):
        values = [int(row[restaurant]) for restaurant in ranked_restaurants]
        visit_labels = [
            "1 visit" if count == 1 else "2 visits" if count == 2 else "2+ visits"
            for count in values
        ]
        trace = go.Bar(
            x=values,
            y=list(range(len(ranked_restaurants))),
            orientation="h",
            marker={
                "color": [color_by_visits[visit] for visit in visit_labels],
            },
            customdata=list(zip(ranked_restaurants, visit_labels)),
            hovertemplate="%{customdata[0]}: %{x} (%{customdata[1]})<extra></extra>",
        )
        frames.append(
            go.Frame(
                name=label,
                data=[trace],
                layout=go.Layout(title={"text": f"Restaurants tried"}),
            )
        )

    max_visits = max(
        (count for frame in frames for count in frame.data[0].x),
        default=1,
    )
    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(
        title={"text": f"Restaurants tried"},
        template="plotly_dark",
        xaxis={
            "title": "Cumulative Visits",
            "range": [0, max_visits * 1.1],
            "autorange": False,
        },
        yaxis={
            "tickmode": "array",
            "tickvals": list(range(len(ranked_restaurants))),
            "ticktext": ranked_restaurants,
            "tickfont": {"size": 10},
            "range": [-0.5, len(restaurants) - 0.5],
            "autorange": False,
        },
        margin={"l": 250},
    )
    return add_plotly_animation_controls(
        fig,
        frame_labels,
        button_y=1.02,
        button_yanchor="bottom",
        slider_y=-0.16,
        top_margin=105,
        bottom_margin=80,
    )


def setup_page():
    st.set_page_config(page_title="Journey", page_icon="🗺️", layout="wide")
    initialise_session_states()
    create_header_triplet()


def setup_member_select_box():
    st.selectbox(
        label="Who are you?",
        options=st.session_state.members,
        key="selected_member",
        index=st.session_state.members.index(st.session_state.member),
        on_change=lambda: setattr(st.session_state, "member", st.session_state.selected_member),
    )


def run():
    setup_page()
    setup_member_select_box()
    df = select_member_df(st.session_state.combined_df)
    df_cumsum = fill_missing_dates(cum_sum_restaurant_visits(df))

    st.plotly_chart(
        build_stacked_chart(df_cumsum),
        width="stretch",
        height=650,
        key="journey_stacked_chart",
    )
    st.plotly_chart(
        build_restaurant_chart(df_cumsum),
        width="stretch",
        height=max(650, 25 * (df_cumsum.shape[1] - 1) + 200),
        key="journey_restaurant_chart",
    )


if __name__ == "__main__":
    run()
