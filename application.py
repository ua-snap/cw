"""
Community Winds app
"""

# pylint: disable=invalid-name, line-too-long, too-many-arguments
import os
import copy
import math
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from gui import layout
import luts

# Read data blobs and other items used from env
data = pd.read_csv("roses.csv")
calms = pd.read_csv("calms.csv")
monthly_means = pd.read_csv("monthly_averages.csv")
future_rose = pd.read_csv("future_roses.csv")
percentiles = pd.read_csv("percentiles.csv", index_col=0)

app = dash.Dash(__name__)

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

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
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <!-- Schema.org markup for Google+ -->
        <meta itemprop="name" content="Alaska Community Wind Tool">
        <meta itemprop="description" content="Explore historical wind data for Alaska communities">
        <meta itemprop="image" content="http://windtool.accap.uaf.edu/assets/wind-rose.png">

        <!-- Twitter Card data -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:site" content="@SNAPandACCAP">
        <meta name="twitter:title" content="Alaska Community Wind Tool">
        <meta name="twitter:description" content="Explore historical wind data for Alaska communities">
        <meta name="twitter:creator" content="@SNAPandACCAP">
        <!-- Twitter summary card with large image must be at least 280x150px -->
        <meta name="twitter:image:src" content="http://windtool.accap.uaf.edu/assets/wind-rose.png">

        <!-- Open Graph data -->
        <meta property="og:title" content="Alaska Community Wind Tool" />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="http://windtool.accap.uaf.edu" />
        <meta property="og:image" content="http://windtool.accap.uaf.edu/assets/wind-rose.png" />
        <meta property="og:description" content="Explore historical wind data for Alaska communities" />
        <meta property="og:site_name" content="Alaska Community Wind Tool" />

        <link rel="alternate" hreflang="en" href="http://windtool.accap.uaf.edu" />
        <link rel="canonical" href="http://windtool.accap.uaf.edu"/>
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

app.title = "Alaska Community Wind Tool"
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


@app.callback(Output("means_box", "config"), [Input("communities-dropdown", "value")])
def update_export_filenames(community):
    """ Update filename for file exports """
    c_name = luts.communities.loc[community]["place"]
    configs = luts.fig_configs
    i_configs = luts.fig_download_configs
    i_configs["filename"] = c_name + " Average Wind Speeds, 1980-2015"
    i_configs["height"] = "640"
    configs["toImageButtonOptions"] = i_configs
    return configs


@app.callback(Output("rose", "config"), [Input("communities-dropdown", "value")])
def update_rose_export_filenames(community):
    """ Update filename for file exports """
    c_name = luts.communities.loc[community]["place"]
    configs = luts.fig_configs
    i_configs = luts.fig_download_configs
    i_configs["filename"] = (
        c_name + " Wind Frequency and Strength by Direction, 1980-2015"
    )
    i_configs["width"] = "1280"
    i_configs["height"] = "1280"
    configs["toImageButtonOptions"] = i_configs
    return configs


@app.callback(
    Output("rose_monthly", "config"), [Input("communities-dropdown", "value")]
)
def update_monthly_rose_export_filenames(community):
    """ Update filename for file exports """
    c_name = luts.communities.loc[community]["place"]
    configs = luts.fig_configs
    i_configs = luts.fig_download_configs
    i_configs["filename"] = (
        c_name + " Monthly Wind Frequency and Strength by Direction, 1980-2015"
    )
    i_configs["width"] = "1024"
    i_configs["height"] = "1280"
    configs["toImageButtonOptions"] = i_configs
    return configs


def get_rose_calm_month_annotations(titles, calm):
    """
    Return a list of correctly-positioned %calm indicators
    for the monthly wind rose charts.
    Take the already-generated list of titles and use
    that pixel geometry to position the %calm info.
    """
    calm_annotations = copy.deepcopy(titles)

    k = 0
    for anno in calm_annotations:
        anno["y"] = anno["y"] - 0.1225
        anno["font"] = {"color": "#000", "size": 10}
        calm_text = str(int(round(calm.iloc[k]["percent"] * 100))) + "%"
        if calm.iloc[k]["percent"] > 0.2:
            # If there's enough room, add the "calm" text fragment
            calm_text += " calm"

        anno["text"] = calm_text
        k += 1

    return calm_annotations


def get_rose_traces(d, traces, month, showlegend=False):
    """
    Get all traces for a wind rose, given the data chunk.
    Month is used to tie the subplot to the formatting
    chunks in the multiple-subplot graph.
    """

    # Directly mutate the `traces` array.
    for sr, sr_info in luts.speed_ranges.items():
        dcr = d.loc[(d["speed_range"] == sr)]
        props = dict(
            r=dcr["frequency"].tolist(),
            theta=pd.to_numeric(dcr["direction_class"]) * 10,
            name=sr + " mph",
            hovertemplate="%{r} %{fullData.name} winds from %{theta}<extra></extra>",
            marker_color=sr_info["color"],
            showlegend=showlegend,
            legendgroup="legend",
        )
        traces.append(go.Barpolar(props))

    # Compute the maximum extent of any particular
    # petal on the wind rose.
    max_petal = d.groupby(["direction_class"]).sum().max()
    return max_petal


@app.callback(Output("means_box", "figure"), [Input("communities-dropdown", "value")])
def update_box_plots(community):
    """ Generate box plot for monthly averages """

    d = monthly_means.loc[(monthly_means["sid"] == community)]
    c_name = luts.communities.loc[community]["place"]

    return go.Figure(
        layout=dict(
            font=dict(family="Open Sans", size=10),
            title=dict(
                text="Average monthly wind speed, 1980-2015, " + c_name,
                font=dict(size=18, family="Open Sans"),
                x=0.5,
            ),
            boxmode="group",
            yaxis={
                "title": "Wind speed (mph)",
                "rangemode": "tozero",
                "fixedrange": True,
            },
            height=550,
            margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
            xaxis=dict(
                tickvals=list(luts.months.keys()),
                ticktext=list(luts.months.values()),
                fixedrange=True,
            ),
        ),
        data=[
            go.Box(
                name="Observed average wind speed, 1980-2015",
                fillcolor=luts.speed_ranges["10-14"]["color"],
                x=d.month,
                y=d.speed,
                meta=d.year,
                hovertemplate="%{x} %{meta}: %{y} mph",
                marker=dict(color=luts.speed_ranges["22+"]["color"]),
                line=dict(color=luts.speed_ranges["22+"]["color"]),
            )
        ],
    )


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
    c_mean = int(round(c_mean["percent"]))

    c_name = luts.communities.loc[community]["place"]

    rose_layout = {
        "title": dict(
            text="Annual Wind Speed/Direction Distribution, 1980-2015, " + c_name,
            font=dict(size=18),
        ),
        "height": 700,
        "font": dict(family="Open Sans", size=10),
        "margin": {"l": 0, "r": 0, "b": 20, "t": 75},
        "legend": {"orientation": "h", "x": 0, "y": 1},
        "annotations": [
            {
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "text": str(c_mean) + r"% calm",
                "xref": "paper",
                "yref": "paper",
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
        horizontal_spacing=0.03,
        vertical_spacing=0.04,
        specs=[
            [subplot_spec, subplot_spec, subplot_spec],
            [subplot_spec, subplot_spec, subplot_spec],
            [subplot_spec, subplot_spec, subplot_spec],
            [subplot_spec, subplot_spec, subplot_spec],
        ],
        subplot_titles=list(luts.months.values()),
    )

    max_axes = pd.DataFrame()
    month = 1
    for i in range(1, 5):
        for j in range(1, 4):
            if_show_legend = month == 1  # only show the first legend
            traces = []
            d = data.loc[(data["sid"] == community) & (data["month"] == month)]
            max_axes = max_axes.append(
                get_rose_traces(d, traces, month, if_show_legend), ignore_index=True
            )
            for trace in traces:
                fig.add_trace(trace, row=i, col=j)
            month += 1

    # Determine maximum r-axis and r-step.
    # Adding one and using floor(/2.5) was the
    # result of experimenting with values that yielded
    # about 3 steps in most cases, with a little headroom
    # for the r-axis outer ring.
    rmax = max_axes.max()["frequency"] + 1
    rstep = math.floor(rmax / 2.5)

    # Apply formatting to subplot titles,
    # which are actually annotations.
    for i in fig["layout"]["annotations"]:
        i["y"] = i["y"] + 0.01
        i["font"] = dict(size=12, color="#444")
        i["text"] = "<b>" + i["text"] + "</b>"

    c_name = luts.communities.loc[community]["place"]

    # Generate calms.  Subset by community, re-index
    # for easy access, preprocess percent hole size,
    # drop unused columns.
    c = calms[calms["sid"] == community]
    c = c.reset_index()
    c = c.assign(percent=c["percent"] / 100)

    # Get calms as annotations, then merge
    # them into the subgraph title annotations
    fig["layout"]["annotations"] = fig["layout"][
        "annotations"
    ] + get_rose_calm_month_annotations(fig["layout"]["annotations"], c)

    polar_props = dict(
        bgcolor="#fff",
        angularaxis=dict(
            tickmode="array",
            tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
            ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
            tickfont=dict(color="#444", size=10),
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
            tickangle=0,
            range=[0, rmax],
            tick0=1,
            dtick=rstep,
            ticksuffix="%",
            showticksuffix="last",
            showline=False,  # hide the dark axis line
            tickfont=dict(color="#444"),
        ),
    )
    fig.update_layout(
        title=dict(
            text="Monthly Wind Speed/Direction Distribution, 1980-2015, " + c_name,
            font=dict(family="Open Sans", size=18),
            x=0.5,
        ),
        margin=dict(l=0, t=100, r=0, b=0),
        font=dict(family="Open Sans", size=10),
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
        polar12={**polar_props, **{"hole": c.iloc[11]["percent"]}},
    )
    return fig


@app.callback(
    Output("threshold_graph", "figure"),
    [
        Input("communities-dropdown", "value"),
        Input("duration-dropdown", "value"),
        Input("gcm-dropdown", "value"),
    ],
)
def update_threshold_graph(community, duration, gcm):
    """
    Build chart / visualiztion of threshold/durations
    from model data.
    """

    c_name = luts.communities.loc[community]["place"]

    # Filter by community and selected models.
    # Don't filter by duration, here, because it
    # could result in incomplete list of possible
    # speed buckets.
    dk = percentiles.loc[
        (percentiles["stid"] == community)
        & ((percentiles["gcm"] == gcm) | (percentiles["gcm"] == "ERA"))
    ]

    traces = []
    index = 0

    # Determine wind speed buckets (needs all available data)
    wind_speeds = dk.ws_thr.unique()

    # PADT (Slana) has an exception where the 85th/95th percentiles
    # are idential (!).  Handle that here.
    percentile_lookups = luts.percentiles
    if community == "PADT":
        percentile_lookups = np.delete(percentile_lookups, [3])

    labels = np.char.add(wind_speeds.astype("U"), percentile_lookups)

    # Filter by duration class
    dk = dk.loc[percentiles["dur_thr"] == duration]

    for ws in dk.ws_thr.unique():
        # Need to filter, glue together the 2000's (between ERA/GCM)
        k = dk.loc[dk.ws_thr == ws].groupby(["ts"]).sum().reset_index()
        traces.append(
            go.Bar(
                name=labels[index],
                x=k.ts,
                y=k.events,
                width=10,
                marker=dict(color=luts.colors[index], line=dict(width=0)),
            )
        )
        index += 1

    return go.Figure(
        layout=dict(
            title=dict(
                text="Historical and Future Modeled Wind Event Frequency, 1980-2100, "
                + c_name
                + "<br>"
                + "ERA-Interim/"
                + luts.gcms[gcm]
                + ", "
                + luts.durations[duration],
                x=0.5,
                font=dict(size=18),
            ),
            font=dict(family="Open Sans", size=10),
            yaxis={"title": "Number of Events", "fixedrange": True},
            xaxis=dict(
                title="Years",
                tickvals=list(luts.decades.keys()),
                ticktext=list(luts.decades.values()),
                fixedrange=True,
            ),
            height=400,
            barmode="stack",
        ),
        data=traces,
    )


@app.callback(
    Output("future_delta_percentiles", "figure"),
    [
        Input("communities-dropdown", "value"),
        Input("gcm-dropdown", "value"),
        Input("decadal_selector", "value"),
    ],
)
def update_future_delta_percentiles(community, gcm, decade):
    """
    Build chart / visualiztion of threshold/durations
    from model data -- 3D Chart Attempt TODO FIXME better
    description here please.
    """

    c_name = luts.communities.loc[community]["place"]

    fig = go.Figure()

    # Filter by community & relevant models
    dt = percentiles.loc[(percentiles["stid"] == community)]
    dt = dt.groupby(["gcm", "ts", "ws_thr", "dur_thr"]).sum().reset_index()

    de = dt.loc[(dt.gcm == "ERA") & (dt.ts == 1980)]
    dc = dt.loc[(dt.gcm == gcm) & (dt.ts == decade)]

    dec = de.set_index(["ws_thr", "dur_thr"])
    dcc = dc.set_index(["ws_thr", "dur_thr"])

    # Merge the two dataframes (outer join)
    # Outer join ensures wind events present in either
    # dataframe are included (union)
    dj = dcc.join(dec, how="outer", lsuffix="_model", rsuffix="_ERA")
    dj = dj.fillna(0)  # so we can subtract
    dj["delta"] = dj["events_model"] - dj["events_ERA"]
    dj = dj.reset_index()

    # Compute % change between baseline and model
    # Handle NaN and NA values, then round to integer.
    dj["percent_change"] = (dj["delta"] / dj["events_ERA"]) * 100
    dj["percent_change"] = (
        dj["percent_change"].replace([np.inf], 0).fillna(0).round(0).astype("int8")
    )

    # Group magnitude of changes into 5 quantiles
    dj["bins"] = pd.qcut(dj["delta"].abs(), 5)
    dj["bin_labels"] = pd.qcut(
        dj["delta"].abs(), 5, labels=["least", "some", "middle", "more", "most"]
    )

    # Take absolute value to show magnitude, since
    # now color shows +/-.  "inf" values are possible due
    # to new events; replace them with the mean.
    # nan are also possible (0/0)
    dj["marker_size"] = dj["bin_labels"].apply(lambda label: luts.bubble_bins[label])

    # Format hover text nicely.
    def build_hover_text(row):
        if int(row["delta"]) == 0:
            return "No change"

        if int(row["events_ERA"]) != 0:
            t = "<b>" + str(row["percent_change"]) + "% "
            if int(row["delta"]) > 0:
                t += "more</b> events,<br>"
            else:
                t += "fewer</b> events,<br>"
        else:
            t = "<b>" + str(int(row["delta"])) + " new events</b>,<br>"

        t += str(row["ws_thr"]) + "mph<br>"
        t += luts.durations[row["dur_thr"]]
        return t

    dj["hover_text"] = dj.apply(build_hover_text, axis=1)

    # Annotations show changed number of events.
    def build_annotation_text(row):
        # Add a + sign if the row is positive, and format
        # the numbers nicely.
        sign = "+" if row["delta"] > 0 else ""
        return "<b>" + sign + f'{int(row["delta"]):,}' + "</b>"

    dj["annotations"] = dj.apply(build_annotation_text, axis=1)

    def build_annotation_positions(row):
        # Magic number 20 = trial and error for the
        # threshold at which the bubbles _generally_ look
        # better with the text annotation to the right.
        return "middle center" if row["marker_size"] > 20 else "middle right"

    dj["annotations_positions"] = dj.apply(build_annotation_positions, axis=1)

    # Build the trace for increased frequency events.
    inc_freq_df = dj.loc[dj.delta > 0]
    fig.add_trace(
        go.Scatter(
            x=inc_freq_df.dur_thr,
            y=inc_freq_df.ws_thr,
            mode="markers+text",
            name="Increasing frequency",
            text=inc_freq_df.annotations,
            textposition=inc_freq_df.annotations_positions,
            hovertext=inc_freq_df.hover_text,
            hoverinfo="text",
            marker=dict(
                size=inc_freq_df.marker_size, color=luts.speed_ranges["10-14"]["color"]
            ),
        )
    )

    # Decreasing frequency events.
    dec_freq_df = dj.loc[dj.delta < 0]
    fig.add_trace(
        go.Scatter(
            x=dec_freq_df.dur_thr,
            y=dec_freq_df.ws_thr,
            mode="markers+text",
            name="Decreasing frequency",
            text=dec_freq_df.annotations,
            textposition=dec_freq_df.annotations_positions,
            hovertext=dec_freq_df.hover_text,
            hoverinfo="text",
            marker=dict(size=dec_freq_df.marker_size, color="#bbb"),
        )
    )

    # Trace for new events.
    new_df = dj.loc[(dj.delta > 0) & (dj.events_ERA == 0)]
    fig.add_trace(
        go.Scatter(
            x=new_df.dur_thr,
            y=new_df.ws_thr,
            mode="markers+text",
            name="New events",
            text=new_df.annotations,
            textposition=new_df.annotations_positions,
            hovertext=new_df.hover_text,
            hoverinfo="text",
            marker=dict(size=new_df.marker_size, color="#FE3508"),
        )
    )
    figure_text = (
        "Changes in Number of Wind Events Between ERA-Interim (1980-2000) and "
        + luts.gcms[gcm]
        + " ("
        + luts.decade_selections[decade]
        + ")<br>"
        + c_name
    )

    # We need to specially handle Slana (PADT).
    ytickvals = dj["ws_thr"].unique().astype("U")

    # PADT (Slana) has an exception where the 85th/95th percentiles
    # are idential (!).  Handle that here.
    percentile_lookups = luts.percentiles
    if community == "PADT":
        percentile_lookups = np.delete(percentile_lookups, [3])

    yticktext = np.char.add(ytickvals, percentile_lookups)

    fig.update_layout(
        title=dict(text=figure_text, x=0.5, font=dict(size=18)),
        legend_orientation="h",
        legend={"font": {"size": 14}, "y": -0.2},
        height=600,
        font=dict(family="Open Sans", size=10),
        margin={"l": 50, "r": 50, "b": 35, "t": 85},
        xaxis={
            "tickvals": [1, 6, 12, 24, 48],
            "title": "Duration (hours)",
            "fixedrange": True,
        },
        yaxis={
            "title": "Wind Speed",
            "tickvals": ytickvals,
            "ticktext": yticktext,
            "automargin": True,
            "fixedrange": True,
        },
    )
    return fig


@app.callback(
    Output("future_rose", "figure"),
    [Input("communities-dropdown", "value"), Input("gcm-dropdown", "value")],
)
def update_future_rose(community, gcm):
    """ Generate cumulative future wind rose for selected community
    this is very rough right now.
    """

    # t = top margin in % of figure.
    subplot_spec = dict(type="polar", t=0.01)
    fig = make_subplots(
        rows=1,
        cols=3,
        horizontal_spacing=0.03,
        specs=[[subplot_spec, subplot_spec, subplot_spec]],
        subplot_titles=[
            "ERA-Interim (1980-2009)",
            luts.gcms[gcm] + " (2025-2054)",
            luts.gcms[gcm] + " (2070-2099)",
        ],
    )

    max_axes = pd.DataFrame()

    # ERA
    traces = []
    d = future_rose.loc[
        (future_rose["sid"] == community) & (future_rose["gcm"] == "ERA")
    ]
    max_axes = max_axes.append(get_rose_traces(d, traces, "", True), ignore_index=True)
    for trace in traces:
        fig.add_trace(trace, row=1, col=1)

    # GCM -- 1st decadal group
    traces = []
    d = future_rose.loc[
        (future_rose["sid"] == community)
        & (future_rose["gcm"] == gcm)
        & (future_rose["decadal_group"] == 1)
    ]
    max_axes = max_axes.append(get_rose_traces(d, traces, "", False), ignore_index=True)
    for trace in traces:
        fig.add_trace(trace, row=1, col=2)

    # GCM -- 2nd decadal group
    traces = []
    d = future_rose.loc[
        (future_rose["sid"] == community)
        & (future_rose["gcm"] == gcm)
        & (future_rose["decadal_group"] == 2)
    ]
    max_axes = max_axes.append(get_rose_traces(d, traces, "", False), ignore_index=True)
    for trace in traces:
        fig.add_trace(trace, row=1, col=3)

    # Determine maximum r-axis and r-step.
    # Adding one and using floor(/2.5) was the
    # result of experimenting with values that yielded
    # about 3 steps in most cases, with a little headroom
    # for the r-axis outer ring.
    rmax = max_axes.max()["frequency"] + 1
    rstep = math.floor(rmax / 2.5)

    # Apply formatting to subplot titles,
    # which are actually annotations.
    for i in fig["layout"]["annotations"]:
        i["y"] = i["y"] + 0.04
        i["font"] = dict(size=12, color="#444")
        i["text"] = "<b>" + i["text"] + "</b>"

    c_name = luts.communities.loc[community]["place"]

    polar_props = dict(
        bgcolor="#fff",
        angularaxis=dict(
            tickmode="array",
            tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
            ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
            tickfont=dict(color="#444", size=10),
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
            tickangle=0,
            range=[0, rmax],
            tick0=1,
            dtick=rstep,
            ticksuffix="%",
            showticksuffix="last",
            showline=False,  # hide the dark axis line
            tickfont=dict(color="#444"),
        ),
    )
    fig.update_layout(
        title=dict(
            text="Modeled Wind Speed/Direction Distribution, 1980-2100, " + c_name,
            font=dict(family="Open Sans", size=18),
            x=0.5,
        ),
        margin=dict(l=0, t=75, r=0, b=0),
        font=dict(family="Open Sans", size=10),
        legend=dict(x=0, y=0, orientation="h"),
        height=550,
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        # We need to explicitly define the rotations
        # we need for each named subplot.
        polar1={**polar_props},
        polar2={**polar_props},
        polar3={**polar_props},
    )
    return fig


if __name__ == "__main__":
    application.run(debug=True, port=8080)
