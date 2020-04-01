"""
NWT Mine site future climate tool
"""
# pylint: disable=invalid-name, import-error, line-too-long
import os
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html as ddsih
import luts

path_prefix = os.environ["REQUESTS_PATHNAME_PREFIX"]

map_figure = go.Figure(
    {"data": [luts.map_communities_trace], "layout": luts.map_layout}
)

toc = html.Div(
    id="toc",
    children=[
        ddsih.DangerouslySetInnerHTML(
            """
        <h2 class="title is-5">Table of contents</h2>
        <ol>
            <li><a href="#toc_location">Select location</a></li>
            <li>
                <h3 class="title is-6">Observed data</h3>
                <ol>
                    <li><a href="#toc_g1">Monthly wind speeds</a></li>
                    <li><a href="#toc_g2">Wind rose</a></li>
                    <li><a href="#toc_g3">Monthly wind rose</a></li>
                </ol>
            </li>
            <li>
                <h3 class="title is-6">Modeled data</h3>
                <ol>
                    <li><a href="#toc_gcm">Select GCM</a></li>
                    <li><a href="#toc_g4">Wind speed and duration</a></li>
                    <li><a href="#toc_g5">Change from model baseline</a></li>
                    <li><a href="#toc_g6">Wind directions</a></li>

                </ol>
            </li>
            <li><a href="#toc_about">About these data</a></li>
        </ol>
    """
        )
    ],
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
    className="field dropdown-selector",
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
    className="field dropdown-selector",
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
    className="field dropdown-selector",
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

intro = html.Div(
    className="container",
    children=[
        html.Div(
            className="section survey-link",
            children=[
                html.P(
                    "This tool displays recorded hourly wind data 1980-2015 and projected data 1980-2100 for 67 Alaskan communities.",
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
        )
    ],
)

help_text = html.Div(
    className="section",
    children=[
        html.A(id="toc_about"),
        html.Div(
            className="section help-text",
            children=[
                dcc.Markdown(
                    """

### About wind observation data

 * Wind speed observations source: [Iowa Environmental Mesonet](https://mesonet.agron.iastate.edu/request/download.phtml?network=AK_ASOS), run by Iowa State University. Houses data collected by the [Automated Surface Observing System](https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/automated-surface-observing-system-asos) network and the [Automated Weather Observing System](https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/automated-weather-observing-system-awos).
 * Measurement frequency: Varies between locations, from every 5 minutes to every 3 hours. Winds were measured hourly in most cases; speeds were averaged to the nearest hour in cases where measurements were more frequent.
 * Observing site criteria: We use data from 67 observing sites located across Alaska, mostly at airports (see map). For inclusion here, a station must have made 4 or more hourly wind measurements on at least 75&percnt; of the days during the period 1980&ndash;2015.

##### Data processing and quality control

 * Data were adjusted for homogeneity because some instrument heights (now 10 m) and/or precise locations have changed since 1980.
 * Wind speeds at 28 stations showed a statistically significant change from one part of the record to the next. Therefore we adjusted the data prior to the change using quantile mapping, a typical method for correcting biased meteorological data.
 * Four stations displayed two discontinuities. For these, we applied the quantile mapping adjustments to the later period.
 * We also removed obviously wrong reports (e.g., wind speeds exceeding 100 mph) and short-duration (< 6 hour) spikes in which an hourly wind speed was at least 30 mph greater than in the immediately preceding and subsequent hours.

#### About the modeled historical and future projections of wind

 * [WRF model data source](http://ckan.snap.uaf.edu/dataset/historical-and-projected-dynamically-downscaled-climate-data-for-the-state-of-alaska-and-surrou): Scenarios Network for Alaska + Arctic Planning, International Arctic Research Center, University of Alaska Fairbanks

##### Data processing and quality control

 * The WRF model data used here are available as a gridded product covering Alaska. To display these data for individual communities, we extracted the model output from the grid cell overlapping the community location.
 * Modeled data, both historical and future, are inherently biased. We adjusted these data by quantile mapping the historical output to match the observed data, and applied those same adjustments to the future output. This assumes that the historical and future model output are biased in the same ways.

#### Suggested citation

If you want to cite this web site in a paper, we suggest this format:

 > J. Walsh, K. Redilla, B. Crevensten, T. Kurkowski. Alaska Community Wind Tool. [http://windtool.accap.uaf.edu](http://windtool.accap.uaf.edu)

                """,
                    className="is-size-6 content",
                )
            ],
        ),
    ],
)

columns = html.Div(
    className="columns",
    children=[
        html.Div(className="column is-one-fifth", children=[toc]),
        html.Div(
            className="column",
            children=[
                html.Div(
                    children=[
                        html.Div(
                            className="section",
                            children=[
                                html.A(id="toc_location"),
                                form_fields
                            ]
                        ),
                        html.Div(
                            className="section",
                            children=[
                                html.A(id="toc_g1"),
                                html.H3(
                                    "Average wind speeds by month",
                                    className="title is-4",
                                ),
                                dcc.Graph(
                                    id="means_box",
                                    figure=go.Figure(),
                                    config=luts.fig_configs,
                                ),
                                dcc.Markdown(
                                    """
 * Boxes show the 25&percnt; and 75&percnt; ranges of monthly averages over 35 years.
 * Averages (horizontal lines within boxes) are based on all hourly reports for a month.
 * &ldquo;Whiskers&rdquo; (vertical lines above and below boxes) represent full ranges of typical variation of monthly averages for the different years, extended to the minimum and maximum points contained within 1.5 of the interquartile range (IQR, which is the height of the box shown).
 * Dots indicate outliers, or individual values outside the normal variation (1.5 IQR).
 """,
                                    className="content help-text is-size-6",
                                ),
                            ],
                        ),
                        html.Div(
                            className="section",
                            children=[
                                html.A(id="toc_g2"),
                                html.H3(
                                    "Wind frequency by direction and speed",
                                    className="title is-4 title--rose",
                                ),
                                dcc.Graph(
                                    id="rose",
                                    figure=go.Figure(),
                                    config=luts.fig_configs,
                                ),
                                dcc.Markdown(
                                    """
     * The &ldquo;spokes&rdquo; in the rose point in the compass direction from which the wind was blowing (i.e., a spoke pointing to the right denotes a wind from the east).
     * For each spoke, we show frequencies of wind speed occurrence (1&percnt;, 4&percnt;, 10&percnt;, &hellip;). These are denoted by concentric circles within each wind rose. Hover cursor over plot to display.
     * The &percnt; of calm winds is shown by the size of the hole in the center of the wind rose.
     """,
                                    className="content help-text is-size-6",
                                ),
                            ],
                        ),
                        html.Div(
                            className="section",
                            children=[
                                html.A(id="toc_g3"),
                                html.H3(
                                    "Monthly wind frequency by direction and speed",
                                    className="title is-4 title--rose",
                                ),
                                dcc.Graph(
                                    id="rose_monthly",
                                    figure=go.Figure(),
                                    config=luts.fig_configs,
                                ),
                            ],
                        ),
                        html.Hr(),
                        html.Div(
                            className="section",
                            children=[
                                html.A(id="toc_gcm"),
                                html.H3("Modeled data", className="title is-4"),
                                dcc.Markdown(
                                    """
        The charts below show modeled output from the Weather Research and Forecasting Model (WRF), which we used to improve the accuracy of wind projections from two Global Climate Models (GCMs).

        Select the GCM below to switch which model/GCM output is shown for model data.
        """,
                                    className="content help-text is-size-6",
                                ),
                                gcm_dropdown_field,
                            ],
                        ),
                        html.Div(
                            className="section",
                            children=[
                                html.A(id="toc_g4"),
                                html.H3(
                                    "Historical & future modeled frequency of wind speed by duration",
                                    className="title is-4",
                                ),
                                dcc.Markdown(
                                    """
        Choose the duration threshold to see changing trends over time.
         """,
                                    className="content help-text is-size-6",
                                ),
                                duration_threshold_dropdown_field,
                                dcc.Graph(
                                    id="threshold_graph",
                                    figure=go.Figure(),
                                    config=luts.fig_configs,
                                ),
                                dcc.Markdown(
"""
 * Percentiles (&percnt;ile) are based on the frequency of 1-hour wind events.
""",
className="content help-text is-size-6",
                                )
                            ],
                        ),
                        html.Div(
                            className="section",
                            children=[
                                html.A(id="toc_g5"),
                                html.H3(
                                    "Changes between historical and future projections of wind",
                                    className="title is-4",
                                ),
                                dcc.Markdown(
                                    """
This chart shows the _difference_ in number of events between modeled historical data (ERA-Interim reanalysis, 1980-2015) and future projections (NCAR-CCSM4 or GFDL-CM3, 2015-2100).
         """,
                                    className="content help-text is-size-6",
                                ),
                                dcc.Graph(
                                    id="future_delta_percentiles",
                                    figure=go.Figure(),
                                    config=luts.fig_configs,
                                ),
                                dcc.Markdown(
                                    """
 * Bubble sizes correspond to &percnt;change in the number of events.
 * Numbers show the actual change in events.
 * The number of events are rounded and scaled to allow comparison between ERA-Intrim and NCAR-CCSM4 or GFDL-CM3.
 * Percentiles (&percnt;ile) are based on the frequency of 1-hour wind events.
         """,
                                    className="content help-text is-size-6",
                                ),
                            ],
                        ),
                        html.Div(
                            className="section",
                            children=[
                                html.A(id="toc_g6"),
                                html.H3(
                                    "Wind speed and direction for historical and future projections",
                                    className="title is-4",
                                ),
                                dcc.Markdown(
                                    """
        This chart shows the modeled historical data (ERA-Interim, 1980-2009) and GCM model output for mid-century (2025-2054) and late-century (2070-2099). This allows comparisons between the historical patterns and future projections.
         """,
                                    className="content help-text is-size-6",
                                ),
                                dcc.Graph(
                                    id="future_rose",
                                    figure=go.Figure(),
                                    config=luts.fig_configs,
                                ),
                            ],
                        ),
                    ]
                ),
                help_text,
            ],
        ),
    ],
)

layout = html.Div(children=[header_section, intro, html.Hr(), columns, footer])
