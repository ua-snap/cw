"""
GUI for Community Winds app 
"""
# pylint: disable=invalid-name, import-error, line-too-long
import os
import plotly.graph_objs as go
from dash import dcc, html
import dash_dangerously_set_inner_html as ddsih
import luts

path_prefix = os.getenv("DASH_REQUESTS_PATHNAME_PREFIX")
assert path_prefix, f"DASH_REQUESTS_PATHNAME_PREFIX needs to be set!"

map_figure = go.Figure(data=luts.map_communities_trace, layout=luts.map_layout)

toc = html.Div(
    id="toc",
    children=[
        ddsih.DangerouslySetInnerHTML(
            """
        <h2 class="title is-5">Navigate the wind tool</h2>
        <ol>
            <li><a href="#toc_location">Choose a location</a></li>
            <li>
                <h3 class="title is-6">Explore observed winds (1980-2014)</h3>
                <ol>
                    <li><a href="#toc_g1">Monthly wind speeds</a></li>
                    <li><a href="#toc_g2">Annual wind speed/direction
</a></li>
                    <li><a href="#toc_g3">Monthly wind speed/direction
</a></li>
                </ol>
            </li>
            <li>
                <h3 class="title is-6">Explore modeled winds (1980-2099)</h3>
                <ol>
                    <li><a href="#toc_gcm">Choose a Global Climate Model</a></li>
                    <li><a href="#toc_g4">Modeled wind event duration</a></li>
                    <li><a href="#toc_g5">Modeled past vs. future wind events</a></li>
                    <li><a href="#toc_g6">Modeled wind speed/direction</a></li>

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
                                    "Explore past and future wind data for Alaska communities",
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
UA is an affirmative action / equal opportunity employer, educational institution and provider, and prohibits illegal discrimination against any individual.  
[Statement of Nondiscrimination](https://www.alaska.edu/nondiscrimination/) and [Privacy Statement](https://www.alaska.edu/records/records/compliance/gdpr/ua-privacy-statement/)

UA is committed to providing accessible websites. [Learn more about UA&rsquo;s notice of web accessibility](https://www.alaska.edu/webaccessibility/).  If we can help you access this website&rsquo;s content, [email us](mailto:uaf-snap-data-tools@alaska.edu)!
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
        html.Label("Choose a Global Climate Model", className="label"),
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

decadal_radios_field = html.Div(
    className="field",
    children=[
        dcc.RadioItems(
            id="decadal_selector",
            labelClassName="radio",
            className="control",
            inline=True,
            options=[
                {"label": decade, "value": group}
                for group, decade in luts.decade_selections.items()
            ],
            value=2080,
        )
    ],
)

form_fields = html.Div(
    className="selectors form",
    children=[
        dcc.Markdown(
            """
            Explore past and future wind data from 67 communities across Alaska. Start by choosing a specific community. Use the navigation menu on the left to explore observed wind patterns from the last 35 years (1980&ndash;2014) or past and future wind projections (1980&ndash;2099).
""",
            className="content is-size-5",
        ),
        ddsih.DangerouslySetInnerHTML(
            """
<p class="content is-size-5 camera-icon">Click the <span>
<svg viewBox="0 0 1000 1000" class="icon" height="1em" width="1em"><path d="m500 450c-83 0-150-67-150-150 0-83 67-150 150-150 83 0 150 67 150 150 0 83-67 150-150 150z m400 150h-120c-16 0-34 13-39 29l-31 93c-6 15-23 28-40 28h-340c-16 0-34-13-39-28l-31-94c-6-15-23-28-40-28h-120c-55 0-100-45-100-100v-450c0-55 45-100 100-100h800c55 0 100 45 100 100v450c0 55-45 100-100 100z m-400-550c-138 0-250 112-250 250 0 138 112 250 250 250 138 0 250-112 250-250 0-138-112-250-250-250z m365 380c-19 0-35 16-35 35 0 19 16 35 35 35 19 0 35-16 35-35 0-19-16-35-35-35z" transform="matrix(1 0 0 -1 0 850)"></path></svg>
</span> icon in the upper&ndash;right of each chart to download it.</p>
            """
        ),
        communities_dropdown_field,
        dcc.Graph(
            id="map",
            figure=map_figure,
            config={"displayModeBar": False, "scrollZoom": False},
        ),
    ],
)

intro = html.Div(
    className="section",
    children=[
        html.Div(
            className="container",
            children=[
                html.P(
                    "This tool displays recorded hourly wind data 1980-2014 and projected data 1980-2099 for 67 Alaska communities.",
                    className="content is-size-4",
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
            className="section",
            children=[
                dcc.Markdown(
                    """

### About wind observation data

 * Wind speed observations source: [Iowa Environmental Mesonet](https://mesonet.agron.iastate.edu/request/download.phtml?network=AK_ASOS), run by Iowa State University. Houses data collected by the [Automated Surface Observing System](https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/automated-surface-observing-system-asos) network and the [Automated Weather Observing System](https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/automated-weather-observing-system-awos).
 * Measurement frequency: Varies between locations, from every 5 minutes to every 3 hours. Winds were measured hourly in most cases; speeds were averaged to the nearest hour in cases where measurements were more frequent.
 * Observing site criteria: We use data from 67 observing sites located across Alaska, mostly at airports (see map). For inclusion here, a station must have made 4 or more hourly wind measurements on at least 75&percnt; of the days during the period 1980&ndash;2014.

##### Data processing and quality control

 * Data were adjusted for homogeneity because some instrument heights (now 10 m) and/or precise locations have changed since 1980.
 * Wind speeds at 28 stations showed a statistically significant change from one part of the record to the next. Therefore we adjusted the data prior to the change using quantile mapping, a typical method for correcting biased meteorological data.
 * Four stations displayed two discontinuities. For these, we applied the quantile mapping adjustments to the later period.
 * We also removed obviously wrong reports (e.g., wind speeds exceeding 100 mph) and short-duration (< 6 hour) spikes in which an hourly wind speed was at least 30 mph greater than in the immediately preceding and subsequent hours.

#### About the modeled historical and future projections of wind

 * [WRF model data source](http://ckan.snap.uaf.edu/dataset/historical-and-projected-dynamically-downscaled-climate-data-for-the-state-of-alaska-and-surrou): Scenarios Network for Alaska + Arctic Planning, International Arctic Research Center, University of Alaska Fairbanks.
 * Modeled data spans from January 1, 1980 through December 31, 2099.
 * Download the wind event data used in this tool here: [doi:10.18739/A29Z90C2X](https://doi.org/10.18739/A29Z90C2X)

##### Data processing and quality control

 * The WRF model data used here are available as a gridded product covering Alaska. To display these data for individual communities, we extracted the model output from the grid cell overlapping the community location.
 * Modeled data, both historical and future, are inherently biased. We adjusted these data by quantile mapping the historical output to match the observed data, and applied those same adjustments to the future output. This assumes that the historical and future model output are biased in the same ways.

#### Acknowledgements

We acknowledge the World Climate Research Programme’s Working Group on Coupled Modeling, which is responsible for CMIP, and we thank all the climate modeling groups for producing and making available their model output. For CMIP, the US Department of Energy's Program for Climate Model Diagnosis and Intercomparison provides coordinating support and leads development of software infrastructure in partnership with the Global Organization for Earth System Science Portals.

                """,
                    className="is-size-6 content",
                )
            ],
        ),
    ],
)

columns = html.Div(
    className="section charts",
    children=[
        html.Div(
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
                                    children=[html.A(id="toc_location"), form_fields],
                                ),
                                html.Div(
                                    className="section",
                                    children=[
                                        html.A(id="toc_g1"),
                                        html.H3(
                                            "Monthly wind speeds",
                                            className="title is-4",
                                        ),
                                        dcc.Markdown(
                                            """
Use this box-plot to explore seasonal changes in wind speed. Each month’s data are averaged over 35 years of observations (1980&ndash;2014).

 * **Boxes** show the middle 50&percnt; of monthly averages.
 * **Horizontal lines within boxes** show averages based on all hourly reports for a month.
 * **Whiskers** (vertical lines above and below boxes) represent the full ranges of typical variation of monthly averages for the different years, extended to the minimum and maximum points contained within 1.5 of the interquartile range (IQR, which is the height of the box shown).
 * **Dots** indicate outliers, or individual values outside the normal variation (1.5 IQR).
 """,
                                            className="content is-size-6",
                                        ),
                                        dcc.Graph(
                                            id="means_box",
                                            figure=go.Figure(),
                                            config=luts.fig_configs,
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="section",
                                    children=[
                                        html.A(id="toc_g2"),
                                        html.H3(
                                            "Annual wind speed/direction",
                                            className="title is-4 title--rose",
                                        ),
                                        dcc.Markdown(
                                            """
This wind rose shows prevailing wind direction and speed for a given location. Data show annual trends averaged over 35 years of observations (1980&ndash;2014).

 * **Spokes** in the rose point in the compass direction from which the wind was blowing (i.e., a spoke pointing to the right denotes a wind from the east).
 * **Colors** within each spoke denote frequencies of wind speed occurrence.  Hover cursor over spoke to show the frequencies.
 * **Size of the center** hole indicates the &percnt; of calm winds.
     """,
                                            className="content is-size-6",
                                        ),
                                        dcc.Graph(
                                            id="rose",
                                            figure=go.Figure(),
                                            config=luts.fig_configs,
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="section",
                                    children=[
                                        html.A(id="toc_g3"),
                                        html.H3(
                                            "Monthly wind speed/direction",
                                            className="title is-4 title--rose",
                                        ),
                                        dcc.Markdown(
                                            """
These wind roses are similar to the one shown above, except data are separated by month. Each rose shows the prevailing wind direction and speed for a given month. Compare the roses to see how wind direction and speed change throughout the year. Each month’s data are averaged over 35 years of observations (1980&ndash;2014).
     """,
                                            className="content is-size-6",
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
                                        html.H3(
                                            "Explore modeled winds (1980-2099)",
                                            className="title is-4",
                                        ),
                                        dcc.Markdown(
                                            """
        Explore these projected data to see how wind may change in the future. Wind data from 1980&ndash;2099 were simulated using two Global Climate Models (GCMs): NCAR&ndash;CCSM4 and GFDL&ndash;CM3. Switch between the two GCMs to explore possible futures.
        """,
                                            className="content is-size-6",
                                        ),
                                        gcm_dropdown_field,
                                    ],
                                ),
                                html.Div(
                                    className="section",
                                    children=[
                                        html.A(id="toc_g4"),
                                        html.H3(
                                            "Modeled wind event duration",
                                            className="title is-4",
                                        ),
                                        dcc.Markdown(
                                            """
Explore how the length and intensity of wind events may change. To start, use the &ldquo;duration threshold&rdquo; to choose the number of hours the storm will last. The graph compares the number of wind events of that duration projected during six time periods (1980&ndash;2099). The colors within each column show how many events may sustain winds of a specific speed, ranging from rare, high speed events to more common, low speed events.

 * **&percnt;ile (percentile)** on the y–axis indicates percentile wind speeds which are based on the frequency of 1-hour wind events.

         """,
                                            className="content is-size-6",
                                        ),
                                        duration_threshold_dropdown_field,
                                        dcc.Graph(
                                            id="threshold_graph",
                                            figure=go.Figure(),
                                            config=luts.fig_configs,
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="section",
                                    children=[
                                        html.A(id="toc_g5"),
                                        html.H3(
                                            "Modeled past vs. future wind events",
                                            className="title is-4",
                                        ),
                                        dcc.Markdown(
                                            """
This chart shows how wind events may change over time.  Some types of wind events (low speed, long duration) may become more common, while others (high speed, high duration) become less common.  To start, choose a future decade to compare to the modeled historical baseline (ERA&ndash;Interim).

 * **Bubble size** corresponds to change in the number of events.
 * **Numbers** show the actual change in modeled events between 1980&ndash;1999 and the selected date interval.
 * **Hover** over points to see &percnt; change in number of events.
 * **&percnt;ile (percentile)** on the y–axis indicates percentile wind speeds which are based on the frequency of 1-hour wind events.
         """,
                                            className="content is-size-6",
                                        ),
                                        decadal_radios_field,
                                        dcc.Graph(
                                            id="future_delta_percentiles",
                                            figure=go.Figure(),
                                            config=luts.fig_configs,
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="section",
                                    children=[
                                        html.A(id="toc_g6"),
                                        html.H3(
                                            "Modeled wind speed/direction",
                                            className="title is-4",
                                        ),
                                        dcc.Markdown(
                                            """
        These wind roses show prevailing wind direction and speed for the historic period (1980&ndash;2009), mid-century (2025&ndash;2054), and late-century (2070&ndash;2099). The modeled historical data uses ERA&ndash;Interim while the future projections use the GCM model output. This allows comparisons between the historical patterns and future projections.
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
    ],
)


layout = html.Div(children=[header_section, intro, html.Hr(), columns, footer])
