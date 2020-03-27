# pylint: disable=invalid-name, import-error
"""

Contains common lookup tables between GUI/application code

"""
import os
import pandas as pd
import numpy as np
import plotly.graph_objs as go

communities = pd.read_csv("places.csv", index_col="sid")

# Needs to be a numpy array for ease of building relevant
# strings for some code
# 50, 75, 85, 95, 99
percentiles = np.array([
    "mph (50th %ile)<br><b>Common<b>",
    "mph (75th %ile)<br>",
    "mph (85th %ile)<br><b>Occasional</b>",
    "mph (95th %ile)<br>",
    "mph (99th %ile)<br><b>Rare</b>",
])

durations = {
    1: "1 continuous hour or more",
    6: "6+ hours",
    12: "12+ hours",
    24: "24+ hours",
    48: "48+ hours",
}

gcms = {
    "CCSM4": "NCAR-CCSM4",
    "CM3": "GFDL-CM3",
}

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
    marker={"size": 10, "color": "rgb(80,80,80)"},
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

# Gradient-colors, from gentlest to darker/more saturated.
# Some charts need to access these directly.
colors = [
    "#d0d1e6",
    "#a6bddb",
    "#74a9cf",
    "#3690c0",
    "#0570b0",
    "#034e7b"
]

# The lowest bound excludes actual 0 (calm) readings,
# this is deliberate.
speed_ranges = {
    "0-6": {"range": [0.001, 6], "color": colors[0]},
    "6-10": {"range": [6, 10], "color": colors[1]},
    "10-14": {"range": [10, 14], "color": colors[2]},
    "14-18": {"range": [14, 18], "color": colors[3]},
    "18-22": {"range": [18, 22], "color": colors[4]},
    "22+": {
        "range": [22, 1000],  # let's hope the upper bound is sufficient :-)
        "color": colors[5],
    },
}
