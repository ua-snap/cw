"""
Community Winds app
"""

# pylint: disable=invalid-name, line-too-long, too-many-arguments
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from gui import layout
import luts

# Read pickled data blobs and other items used from env
data = pd.read_pickle("roses.pickle")
means = pd.read_pickle("means.pickle")
calms = pd.read_pickle("calms.pickle")

# We set the requests_pathname_prefix to enable
# custom URLs.
# https://community.plot.ly/t/dash-error-loading-layout/8139/6
app = dash.Dash(
    __name__, requests_pathname_prefix=os.environ["REQUESTS_PATHNAME_PREFIX"]
)

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

# The next config sets a relative base path so we can deploy
# with custom URLs.
# https://community.plot.ly/t/dash-error-loading-layout/8139/6

# Customize this layout to include Google Analytics
gtag_id = os.environ["GTAG_ID"]
app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-3978613-12"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());

          gtag('config', '{gtag_id}');
        </script>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

app.title = "Community Winds"
app.layout = layout


@app.callback(Output("communities-dropdown", "value"), [Input("map", "clickData")])
def update_place_dropdown(selected_on_map):
    """ If user clicks on the map, update the drop down. """

    # Look up ID by name -- kind of backwards, but
    # it's because we can't bundle much data into
    # map click handles.
    # TODO look at customdata property here
    if selected_on_map is not None:
        c = luts.communities[
            luts.communities["place"] == selected_on_map["points"][0]["text"]
        ]
        return c.index.tolist()[0]
    # Return a default
    return "PAFA"


@app.callback(Output("map", "figure"), [Input("communities-dropdown", "value")])
def update_selected_community_on_map(community):
    """ Draw a second trace on the map with one community highlighted. """
    return {
        "data": [
            luts.map_communities_trace,
            go.Scattermapbox(
                lat=[luts.communities.loc[community]["latitude"]],
                lon=[luts.communities.loc[community]["longitude"]],
                mode="markers",
                marker={"size": 20, "color": "rgb(207, 38, 47)"},
                line={"color": "rgb(0, 0, 0)", "width": 2},
                text=luts.communities.loc[community]["place"],
                hoverinfo="text",
            ),
        ],
        "layout": luts.map_layout,
    }


def get_rose_traces(d, traces, month, showlegend=False):
    """
    Get all traces for a wind rose, given the data chunk.
    Month is used to tie the subplot to the formatting
    chunks in the multiple-subplot graph.
    """
    for sr, sr_info in luts.speed_ranges.items():
        dcr = d.loc[(d["speed_range"] == sr)]
        props = dict(
            r=dcr["frequency"].tolist(),
            theta=pd.to_numeric(dcr["direction_class"]) * 10,
            name=sr,
            marker_color=sr_info["color"],
            showlegend=showlegend,
            legendgroup="legend",
        )
        traces.append(go.Barpolar(props))


@app.callback(Output("means", "figure"), [Input("communities-dropdown", "value")])
def update_means(community):
    """ Create a bar plot of average wind speeds. """

    d = means.loc[(means["station"] == community)]

    # If the standard deviation is greater than the
    # mean, ensure it doesn't descend below zero
    d = d.assign(lower_bound=np.where((d["mean"] - d["sd"] > 0), d["sd"], d["mean"]))

    c_name = luts.communities.loc[community]["place"]

    fig = go.Figure(
        layout=dict(
            title=dict(
                text="Average monthly wind speed (mph), 1980-2015, " + c_name,
                font=dict(family="Open Sans"),
            ),
            margin=dict(l=0, t=100, r=0, b=100),
            showlegend=True,
            legend=dict(x=0, y=0, orientation="h"),
            height=550,
            paper_bgcolor="#fff",
            plot_bgcolor="#fff",
        ),
        data=[
            go.Bar(
                name="Average wind speed (mph)",
                marker=dict(color=luts.speed_ranges["14-18"]["color"]),
                x=[month for num, month in luts.months_lut.items()],
                y=d["mean"],
                error_y=dict(
                    array=d["sd"],
                    arrayminus=d["lower_bound"],
                    visible=True,
                    color=luts.speed_ranges["22+"]["color"],
                ),
            )
        ],
    )

    return fig


@app.callback(Output("rose", "figure"), [Input("communities-dropdown", "value")])
def update_rose(community):
    """ Generate cumulative wind rose for selected community """
    traces = []

    # Subset for community & 0=year
    d = data.loc[(data["sid"] == community) & (data["month"] == 0)]
    get_rose_traces(d, traces, "", True)

    # Compute % calm, use this to modify the hole size
    c = calms[calms["sid"] == community]
    c_mean = c.mean()
    c_mean = round(c_mean["percent"], 1)

    c_name = luts.communities.loc[community]["place"]

    rose_layout = {
        "title": "Wind Speed Distribution, 1980-2015, " + c_name,
        "height": 700,
        "margin": {"l": 0, "r": 0, "b": 100, "t": 50},
        "legend": {"orientation": "h", "x": 0, "y": 1},
        "annotations": [
            {
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "text": str(c_mean) + r"% calm",
                "xref": "paper",
                "yref": "paper"
            }
        ],
        "polar": {
            "legend": {"orientation": "h"},
            "angularaxis": {
                "rotation": 90,
                "direction": "clockwise",
                "tickmode": "array",
                "tickvals": [0, 45, 90, 135, 180, 225, 270, 315],
                "ticks": "",  # hide tick marks
                "ticktext": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
                "tickfont": {"color": "#444"},
                "showline": False,  # no boundary circles
                "color": "#888",  # set most colors to #888
                "gridcolor": "#efefef",
            },
            "radialaxis": {
                "color": "#888",
                "gridcolor": "#efefef",
                "title": {"text": "Frequency", "side": "right"},
                "ticksuffix": "%",
                "showticksuffix": "last",
                "tickcolor": "rgba(0, 0, 0, 0)",
                "tick0": 0,
                "dtick": 3,
                "ticklen": 10,
                "showline": False,  # hide the dark axis line
                "tickfont": {"color": "#444"},
            },
            "hole": c_mean / 100,
        },
    }

    return {"layout": rose_layout, "data": traces}


@app.callback(
    Output("rose_monthly", "figure"), [Input("communities-dropdown", "value")]
)
def update_rose_monthly(community):
    """
    Create a grid of subplots for all wind roses.
    """

    # t = top margin in % of figure.
    subplot_spec = dict(type="polar", t=0.01)
    fig = make_subplots(
        rows=4,
        cols=3,
        horizontal_spacing=0,
        vertical_spacing=0.04,
        specs=[
            [subplot_spec, subplot_spec, subplot_spec],
            [subplot_spec, subplot_spec, subplot_spec],
            [subplot_spec, subplot_spec, subplot_spec],
            [subplot_spec, subplot_spec, subplot_spec],
        ],
        subplot_titles=list(luts.months_lut.values()),
    )

    month = 1
    for i in range(1, 5):
        for j in range(1, 4):
            if_show_legend = month == 1  # only show the first legend
            traces = []
            d = data.loc[(data["sid"] == community) & (data["month"] == month)]
            get_rose_traces(d, traces, month, if_show_legend)
            for trace in traces:
                fig.add_trace(trace, row=i, col=j)
            month += 1

    # Apply formatting to subplot titles,
    # which are actually annotations.
    for i in fig["layout"]["annotations"]:
        i["y"] = i["y"] + 0.01
        i["font"] = dict(size=12, color="#444")

    c_name = luts.communities.loc[community]["place"]

    # Generate calms.  Subset by community, re-index
    # for easy access, preprocess percent hole size,
    # drop unused columns.
    c = calms[calms["sid"] == community]
    c = c.reset_index()
    c = c.assign(percent=c["percent"] / 100)

    polar_props = dict(
        bgcolor="#fff",
        angularaxis=dict(
            tickmode="array",
            tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
            ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
            tickfont=dict(color="#444", size=10),
            ticksuffix="%",
            showticksuffix="last",
            showline=False,  # no boundary circles
            color="#888",  # set most colors to #888
            gridcolor="#efefef",
            rotation=90,  # align compass to north
            direction="clockwise",  # degrees go clockwise
        ),
        radialaxis=dict(
            color="#888",
            gridcolor="#efefef",
            ticks="",  # hide tick marks
            tick0=0,
            dtick=3,
            showline=False,  # hide the dark axis line
            tickfont=dict(color="#444"),
        )
    )
    fig.update_layout(
        title=dict(
            text="Monthly Wind Speed/Direction Distribution (%), 1980-2015, " + c_name,
            font=dict(family="Open Sans"),
        ),
        margin=dict(l=50, t=100, r=50, b=0),
        font_size=10,
        legend=dict(x=0, y=0, orientation="h"),
        height=1500,
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        # We need to explicitly define the rotations
        # we need for each named subplot.
        # TODO is there a more elegant way to
        # generate this list of things?
        polar1={**polar_props, **{"hole": c.iloc[0]["percent"]}},
        polar2={**polar_props, **{"hole": c.iloc[1]["percent"]}},
        polar3={**polar_props, **{"hole": c.iloc[2]["percent"]}},
        polar4={**polar_props, **{"hole": c.iloc[3]["percent"]}},
        polar5={**polar_props, **{"hole": c.iloc[4]["percent"]}},
        polar6={**polar_props, **{"hole": c.iloc[5]["percent"]}},
        polar7={**polar_props, **{"hole": c.iloc[6]["percent"]}},
        polar8={**polar_props, **{"hole": c.iloc[7]["percent"]}},
        polar9={**polar_props, **{"hole": c.iloc[8]["percent"]}},
        polar10={**polar_props, **{"hole": c.iloc[9]["percent"]}},
        polar11={**polar_props, **{"hole": c.iloc[10]["percent"]}},
        polar12={**polar_props, **{"hole": c.iloc[11]["percent"]}}
    )
    return fig


if __name__ == "__main__":
    application.run(debug=True, port=8080)
