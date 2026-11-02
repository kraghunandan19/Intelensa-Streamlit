
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Player Comparison",
    layout="wide"
)

st.title("Player Comparison")


epl_df = pd.read_excel(
    "epl_players.xlsx"
)

laliga_df = pd.read_excel(
    "laliga_players.xlsx"
)

bundesliga_df = pd.read_excel(
    "bundesliga_players.xlsx"
)

seriaa_df = pd.read_excel(
    "seriaa_players.xlsx"
)

ligue1_df = pd.read_excel(
    "ligue1_players.xlsx"
)


if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame()

if "selected_league" not in st.session_state:
    st.session_state.selected_league = "Premier League"

if "last_added" not in st.session_state:
    st.session_state.last_added = None


def add_player_to_comparison(player_df, player_name):

    st.session_state.master_df = pd.concat(
        [
            st.session_state.master_df,
            player_df
        ],
        ignore_index=True
    )

    # Reset only the player dropdown
    st.session_state.player_select = None

    # Store last added player
    st.session_state.last_added = player_name


def select_league(league):

    st.session_state.selected_league = league

    # Reset team and player when league changes
    st.session_state.team_select = None
    st.session_state.player_select = None


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.button(
        "Premier League",
        use_container_width=True,
        on_click=select_league,
        args=("Premier League",)
    )

with col2:
    st.button(
        "La Liga",
        use_container_width=True,
        on_click=select_league,
        args=("La Liga",)
    )

with col3:
    st.button(
        "Bundesliga",
        use_container_width=True,
        on_click=select_league,
        args=("Bundesliga",)
    )

with col4:
    st.button(
        "Ligue 1",
        use_container_width=True,
        on_click=select_league,
        args=("Ligue 1",)
    )

with col5:
    st.button(
        "Serie A",
        use_container_width=True,
        on_click=select_league,
        args=("Serie A",)
    )

league_dfs = {
    "Premier League": epl_df,
    "La Liga": laliga_df,
    "Bundesliga": bundesliga_df,
    "Ligue 1": ligue1_df,
    "Serie A": seriaa_df
}

selected_league = st.session_state.selected_league

df = league_dfs[selected_league]


st.divider()

st.subheader("Player Selection")

team_options = sorted(
    df["team"].dropna().unique()
)

team = st.selectbox(
    "Select a team",
    options=team_options,
    index=None,
    placeholder="Choose a team...",
    key="team_select"
)

if team is not None:

    player_options = sorted(
        df.loc[df["team"] == team, "player"]
        .dropna()
        .unique()
    )

    player = st.selectbox(
        "Select a player",
        options=player_options,
        index=None,
        placeholder="Choose a player...",
        key="player_select"
    )

else:

    player = None

if team is not None and player is not None:

    filtered_df = df[
        (df["team"] == team) &
        (df["player"] == player)
    ].copy()

    filtered_df["league"] = selected_league

    st.write(f"### {player}")
    st.caption(team)

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    st.button(
        "Add",
        type="primary",
        on_click=add_player_to_comparison,
        args=(filtered_df, player)
    )


if st.session_state.last_added is not None:

    st.success(
        f"{st.session_state.last_added} added to comparison!"
    )


st.divider()

st.subheader("Player Comparison Radar")

master_df = st.session_state.master_df


if not master_df.empty:

    possible_metrics = [
        "apps",
        "min",
        "goals",
        "xG",
        "a",
        "xA",
        "NPxG",
        "NPG",
        
    ]

    metrics = [
        col for col in possible_metrics
        if col in master_df.columns
    ]

    if len(master_df) >= 2 and len(metrics) >= 3:

        radar_df = master_df.copy()

        for col in metrics:

            radar_df[col] = pd.to_numeric(
                radar_df[col],
                errors="coerce"
            )

        normalized_df = radar_df[metrics].copy()

        for col in metrics:

            max_value = normalized_df[col].max()

            if pd.isna(max_value) or max_value == 0:

                normalized_df[col] = 0

            else:

                normalized_df[col] = (
                    normalized_df[col] / max_value
                ) * 100

        fig = go.Figure()

        for idx, row in radar_df.iterrows():

            player_name = row["player"]
            team_name = row["team"]

            values = (
                normalized_df.loc[idx, metrics]
                .fillna(0)
                .tolist()
            )

            actual_values = (
                radar_df.loc[idx, metrics]
                .fillna(0)
                .tolist()
            )

            custom_data = [
                [actual, normalized]
                for actual, normalized in zip(
                    actual_values,
                    values
                )
            ]

            fig.add_trace(

                go.Scatterpolar(

                    r=values,

                    theta=metrics,

                    fill="toself",

                    mode="lines+markers",

                    name=f"{player_name} ({team_name})",

                    opacity=0.65,

                    marker=dict(
                        size=8
                    ),

                    customdata=custom_data,

                    hovertemplate=
                        "<b>%{fullData.name}</b><br>" +
                        "<b>Metric:</b> %{theta}<br>" +
                        "<b>Actual Value:</b> %{customdata[0]:.2f}<br>" +
                        "<b>Normalized:</b> %{customdata[1]:.1f}%" +
                        "<extra></extra>"
                )
            )



        fig.update_layout(

            polar=dict(

                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=True,
                    ticksuffix="%"
                )
            ),

            showlegend=True,

            height=650,

            template="plotly_dark",

            title="Player Statistical Comparison",

            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    elif len(master_df) < 2:

        st.info(
            "Add at least 2 players to generate a comparison."
        )

    else:

        st.warning(
            "Not enough numerical metrics available."
        )

else:

    st.info(
        "Add players using the Add button to generate the radar chart."
    )


st.divider()

st.subheader("Player Comparison Database")

st.dataframe(
    st.session_state.master_df,
    use_container_width=True
)

st.write(
    "Players selected:",
    len(st.session_state.master_df)
)


if st.button("Clear Comparison"):

    st.session_state.master_df = pd.DataFrame()

    st.session_state.last_added = None

    st.rerun()


if not st.session_state.master_df.empty:

    csv = st.session_state.master_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Comparison Database",
        data=csv,
        file_name="player_comparison.csv",
        mime="text/csv"
    )


st.divider()

st.subheader("Player Metrics Comparison")


scatter_dfs = []

for league_name, league_df in league_dfs.items():

    temp_df = league_df.copy()

    temp_df["league"] = league_name

    scatter_dfs.append(temp_df)

scatter_df = pd.concat(
    scatter_dfs,
    ignore_index=True
)

base_metrics = [
    "goals",
    "xG",
    "a",
    "xA",
    "NPxG",
    "NPG",
    "min"
]

for col in base_metrics:

    if col in scatter_df.columns:

        scatter_df[col] = pd.to_numeric(
            scatter_df[col],
            errors="coerce"
        )


if "min" in scatter_df.columns:

    minutes = scatter_df["min"].replace(0, float("nan"))

    per90_metrics = {
        "Goals per 90": "goals",
        "xG per 90": "xG",
        "Assists per 90": "a",
        "xA per 90": "xA",
        "NPxG per 90": "NPxG",
        "NPG per 90": "NPG"
    }

    for new_col, original_col in per90_metrics.items():

        if original_col in scatter_df.columns:

            scatter_df[new_col] = (
                scatter_df[original_col] / minutes
            ) * 90


excluded_columns = [
    "id",
    "player_id",
    "team_id",
    "number",
    "season"
]

numeric_metrics = [

    col for col in scatter_df.select_dtypes(
        include="number"
    ).columns

    if col not in excluded_columns

]

all_leagues = list(league_dfs.keys())

col1, col2, col3 = st.columns([1, 1, 1.5])

with col1:

    default_x = (
        numeric_metrics.index("Goals per 90")
        if "Goals per 90" in numeric_metrics
        else 0
    )

    x_axis = st.selectbox(
        "X Axis",
        options=numeric_metrics,
        index=default_x,
        key="scatter_x_axis"
    )


with col2:

    default_y = (
        numeric_metrics.index("xG per 90")
        if "xG per 90" in numeric_metrics
        else min(1, len(numeric_metrics) - 1)
    )

    y_axis = st.selectbox(
        "Y Axis",
        options=numeric_metrics,
        index=default_y,
        key="scatter_y_axis"
    )


with col3:

    selected_leagues = st.multiselect(
        "Select Leagues",
        options=all_leagues,
        default=all_leagues,
        key="scatter_leagues"
    )

filtered_scatter_df = scatter_df[
    scatter_df["league"].isin(selected_leagues)
].copy()

if not filtered_scatter_df.empty:

    fig_scatter = px.scatter(

        filtered_scatter_df,

        x=x_axis,

        y=y_axis,

        hover_name="player",

        hover_data={
            "team": True,
            "league": True,
            x_axis: ":.2f",
            y_axis: ":.2f"
        },

        opacity=0.65,

        color_discrete_sequence=["#78A9CF"]

    )

    fig_scatter.update_traces(

        marker=dict(
            size=11
        )

    )

    fig_scatter.update_layout(

        template="plotly_dark",

        height=650,

        title="Player Performance Metrics",

        xaxis_title=x_axis,

        yaxis_title=y_axis,

        hovermode="closest"

    )

    st.plotly_chart(

        fig_scatter,

        use_container_width=True

    )

else:

    st.info("Select at least one league to display the graph.")


st.divider()

st.markdown(
    """
    <div style="text-align: center; color: #888888; 
                padding: 15px; font-size: 14px;">
        © Raghunandan Kandula
    </div>
    """,
    unsafe_allow_html=True
)
