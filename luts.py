# pylint: disable=invalid-name, import-error
"""

Contains common lookup tables between GUI/application code

"""
import os
import pandas as pd
import plotly.graph_objs as go

communities = pd.read_csv("places.csv", index_col="sid")

months = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

# This trace is shared so we can highlight specific communities.
map_communities_trace = go.Scattermapbox(
    lat=communities.loc[:, "latitude"],
    lon=communities.loc[:, "longitude"],
    mode="markers",
    marker={"size": 15, "color": "rgb(80,80,80)"},
    line={"color": "rgb(0, 0, 0)", "width": 2},
    text=communities.place,
    hoverinfo="text",
)

map_layout = go.Layout(
    autosize=True,
    hovermode="closest",
    mapbox=dict(style="stamen-terrain", zoom=2.5, center=dict(lat=63, lon=-160)),
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0),
)


# Common configuration for graph figures
fig_download_configs = dict(filename="winds", width="1280", scale=2)
fig_configs = dict(
    displayModeBar=True,
    showSendToCloud=False,
    toImageButtonOptions=fig_download_configs,
    modeBarButtonsToRemove=[
        "zoom2d",
        "pan2d",
        "select2d",
        "lasso2d",
        "zoomIn2d",
        "zoomOut2d",
        "autoScale2d",
        "resetScale2d",
        "hoverClosestCartesian",
        "hoverCompareCartesian",
        "hoverClosestPie",
        "hoverClosest3d",
        "hoverClosestGl2d",
        "hoverClosestGeo",
        "toggleHover",
        "toggleSpikelines",
    ],
    displaylogo=False,
)

# The lowest bound excludes actual 0 (calm) readings,
# this is deliberate.
speed_ranges = {
    "0-6": {"range": [0.001, 6], "color": "#d0d1e6"},
    "6-10": {"range": [6, 10], "color": "#a6bddb"},
    "10-14": {"range": [10, 14], "color": "#74a9cf"},
    "14-18": {"range": [14, 18], "color": "#3690c0"},
    "18-22": {"range": [18, 22], "color": "#0570b0"},
    "22+": {
        "range": [22, 1000],  # let's hope the upper bound is sufficient :-)
        "color": "#034e7b",
    },
}
