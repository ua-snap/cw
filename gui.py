"""
NWT Mine site future climate tool
"""
# pylint: disable=invalid-name, import-error, line-too-long
import os
import json
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import luts

path_prefix = os.environ["REQUESTS_PATHNAME_PREFIX"]

# Google analytics tag
gtag_id = os.environ["GTAG_ID"]

map_figure = go.Figure(
    {"data": [luts.map_communities_trace], "layout": luts.map_layout}
)

# We want this HTML structure to get the full-width background color:
# <div class="header">
#   <div class="container"> gives us the centered column
#     <div class="section"> a bit more padding to stay consistent with form
header_section = html.Div(
    className="header",
    children=[
        html.Div(
            className="container",
            children=[
                html.Div(
                    className="section header--section",
                    children=[
                        html.Div(
                            className="header--logo",
                            children=[
                                html.A(
                                    className="header--snap-link",
                                    href="https://accap.uaf.edu",
                                    rel="external",
                                    target="_blank",
                                    children=[
                                        html.Img(
                                            src=path_prefix
                                            + "assets/ACCAP_full_wide.svg"
                                        )
                                    ],
                                )
                            ],
                        ),
                        html.Div(
                            className="header--titles",
                            children=[
                                html.H1(
                                    "Alaska Community Wind Data", className="title is-3"
                                ),
                                html.H2(
                                    "Explore historical wind data for Alaska communities",
                                    className="subtitle is-5",
                                ),
                            ],
                        ),
                    ],
                )
            ],
        )
    ],
)

footer = html.Footer(
    className="footer has-text-centered",
    children=[
        html.Div(
            children=[
                html.A(
                    href="https://accap.uaf.edu",
                    target="_blank",
                    className="level-item",
                    children=[html.Img(src=path_prefix + "assets/ACCAP_full_wide.svg")],
                ),
                html.A(
                    href="https://snap.uaf.edu",
                    target="_blank",
                    className="level-item",
                    children=[html.Img(src=path_prefix + "assets/SNAP_color_all.svg")],
                ),
                html.A(
                    href="https://uaf.edu/uaf/",
                    target="_blank",
                    className="level-item",
                    children=[html.Img(src=path_prefix + "assets/UAF.svg")],
                ),
            ]
        ),
        dcc.Markdown(
            """
UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual. [Statement of Nondiscrimination](https://www.alaska.edu/nondiscrimination/)
            """,
            className="content is-size-6",
        ),
    ],
)

communities_dropdown_field = html.Div(
    className="field",
    children=[
        html.Label("Choose a location", className="label"),
        html.Div(
            className="control",
            children=[
                dcc.Dropdown(
                    id="communities-dropdown",
                    options=[
                        {"label": community.place, "value": index}
                        for index, community in luts.communities.iterrows()
                    ],
                    value="PAFA",
                )
            ],
        ),
    ],
)

gcm_dropdown_field = html.Div(
    className="field",
    children=[
        html.Label("Select GCM", className="label"),
        html.Div(
            className="control",
            children=[
                dcc.Dropdown(
                    id="gcm-dropdown",
                    options=[
                        {"label": gcm, "value": index}
                        for index, gcm in luts.gcms.items()
                    ],
                    value="CCSM4",
                )
            ],
        ),
    ],
)

duration_threshold_dropdown_field = html.Div(
    className="field",
    children=[
        html.Label("Select duration threshold", className="label"),
        html.Div(
            className="control",
            children=[
                dcc.Dropdown(
                    id="duration-dropdown",
                    options=[
                        {"label": duration, "value": index}
                        for index, duration in luts.durations.items()
                    ],
                    value=1,
                )
            ],
        ),
    ],
)

form_fields = html.Div(
    className="selectors form",
    children=[
        communities_dropdown_field,
        dcc.Graph(
            id="map",
            figure=map_figure,
            config={"displayModeBar": False, "scrollZoom": False},
        ),
    ],
)

main_layout = html.Div(
    className="container",
    children=[
        html.Div(
            className="section survey-link",
            children=[
                html.P(
                    "This tool visualizes hourly wind data recorded between 1980-2015 for 67 Alaskan communities.",
                    className="content is-size-4",
                ),
                html.A(
                    "Let us know how we can make this tool better",
                    className="button is-link is-medium",
                    rel="external",
                    target="_blank",
                    href="https://uaf-iarc.typeform.com/to/hOnb5h",
                ),
            ],
        ),
        html.Div(className="section section--form", children=[form_fields]),
        html.Div(
            className="section graph",
            children=[
                html.Hr(),
                html.H3("Average wind speeds by month", className="title is-4"),
                dcc.Markdown(
                    """

Below is a series of box plots of average monthly wind speeds for the entire 35-year time span.

 * Boxes represent the 25% and 75% ranges of monthly averages over 35 years.
 * Averages (horizontal lines within boxes) are based on all hourly reports for a month.
 * “Whiskers” (vertical lines above and below boxes) represent full ranges of typical variation of monthly averages for the different years, extended to the minimum and maximum points contained within 1.5 of the interquartile range (IQR, which is the height of the box shown).
 * Dots indicate outliers, or individual values outside the normal variation (1.5 IQR).
 """,
                    className="content help-text is-size-6",
                ),
                dcc.Graph(id="means_box", figure=go.Figure(), config=luts.fig_configs),
                html.Hr(),
                html.H3(
                    "Wind frequency by direction and speed",
                    className="title is-4 title--rose",
                ),
                dcc.Markdown(
                    """

Below is a collection of “wind roses” showing distributions of wind by speed and direction at the location of interest.

 * The “spokes” in the rose point in the compass direction from which the wind was blowing (i.e., a spoke pointing to the right denotes a wind from the east).
 * There are 36 spokes corresponding to the wind direction code in the hourly wind reports (01, 02, … 3).
 * For each spoke, we display frequencies of wind speed occurrence (1%, 4%, 10%, &hellip;). These are denoted by concentric circles within each wind rose.
 * The % of calm winds is shown by the size of the hole in the center of the wind rose.

 """,
                    className="content help-text is-size-6",
                ),
                dcc.Graph(id="rose", figure=go.Figure(), config=luts.fig_configs),
                dcc.Graph(
                    id="rose_monthly", figure=go.Figure(), config=luts.fig_configs
                ),
                html.Hr(),
                html.H3(
                    "Future modeled frequency of wind speed and duration",
                    className="title is-4",
                ),
                dcc.Markdown(
                    """
*Fixme Wording Help Needed* The chart below shows modeled output from the [Weather Research and Forecasting Model](https://www.mmm.ucar.edu/weather-research-and-forecasting-model) (WRF).  Choose the model, wind speed threshold and duration threshold to see changing trends over time.
 """,
                    className="content help-text is-size-6",
                ),
                gcm_dropdown_field,
                duration_threshold_dropdown_field,
                dcc.Graph(
                    id="threshold_graph", figure=go.Figure(), config=luts.fig_configs
                ),
                html.H4(
                    "Changes between model baseline and future model projections",
                    className="title is-5",
                ),
                dcc.Markdown(
                    """
*Fixme Wording Help Needed* The next chart shows the difference between the ERA-Interim reanalysis, which can be thought of as a model-based simulation of historical data (1980-2015), and future model selections (either CCSM4 or CM3, as selected in the section above), 2015-2100.  This can show relative patterns of changing wind events for a location.  Gray shows a reduction in events, blue shows an increase, and red shows new events.
 """,
                    className="content help-text is-size-6",
                ),
                dcc.Graph(
                    id="future_delta_percentiles", figure=go.Figure(), config=luts.fig_configs
                ),
                dcc.Graph(id="future_rose", figure=go.Figure(), config=luts.fig_configs),
            ],
        ),
    ],
)

help_text = html.Div(
    className="container",
    children=[
        html.Div(
            className="section help-text",
            children=[
                dcc.Markdown(
                    """

#### About these wind data

 * **Source**: [Iowa Environmental Mesonet](https://mesonet.agron.iastate.edu/request/download.phtml?network=AK_ASOS) run by Iowa State University. Houses data collected by the [Automated Surface Observing System](https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/automated-surface-observing-system-asos) network and the [Automated Weather Observing System](https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/automated-weather-observing-system-awos).
 * **Measurement frequency**: Varies between locations, from every 5 minutes to every 3 hours. Winds were measured hourly in most cases; speeds were averaged to the nearest hour in cases where measurements were more frequent.
 * **Observing site criteria**: We use data from 67 observing sites located across Alaska, mostly at airports (see map). For inclusion here, a station must have made 4 or more hourly wind measurements on at least 75% of the days during the period 1980-2015.

#### Data processing and quality control

 * Data were adjusted for homogeneity because some instrument heights (now 10 m) and/or precise locations have changed since 1980.
 * Wind speeds at 28 stations showed a statistically significant change from one part of the record to the next. Therefore we adjusted the data prior to the change using quantile mapping, a typical method for correcting biased meteorological data.
 * Four stations displayed two discontinuities. For these, we applied the quantile mapping adjustments to the later period.
 * We also removed obviously wrong reports (e.g., wind speeds exceeding 100 mph) and short-duration (< 6 hour) spikes in which an hourly wind speed was at least 30 mph greater than in the immediately preceding and subsequent hours.

                """,
                    className="is-size-5 content",
                )
            ],
        )
    ],
)

layout = html.Div(children=[header_section, main_layout, help_text, footer])
