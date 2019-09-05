"""
NWT Mine site future climate tool
"""
# pylint: disable=invalid-name, import-error
import os
import json
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from luts import communities, months, map_communities_trace, map_layout

path_prefix = os.environ["REQUESTS_PATHNAME_PREFIX"]

# Google analytics tag
gtag_id = os.environ["GTAG_ID"]

map_figure = go.Figure({"data": [map_communities_trace], "layout": map_layout})

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
                                    "Alaska Community Wind Data",
                                    className="title is-3",
                                ),
                                html.H2(
                                    "Explore historical and modeled wind data for Alaska communities",
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
                        for index, community in communities.iterrows()
                    ],
                    value="PAFA",
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
                html.A(
                    "Let us know how we can make this app better",
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
                html.H3("Average wind speeds by month", className="title is-4"),
                html.P(
                    "This chart shows monthly averages for each year.",
                    className="content is-size-5",
                ),
                dcc.Graph(id="means_box", figure=go.Figure()),
                html.H3("Wind frequency by direction and speed", className="title is-4 title--rose"),
                html.P(
                    "Center hole size shows frequency of calm conditions.",
                    className="content is-size-5",
                ),
                dcc.Graph(id="rose", figure=go.Figure()),
                dcc.Graph(id="rose_monthly", figure=go.Figure()),
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

### Source of wind data

Wind information for Alaska is presented based on the hourly wind reports from 67 observing sites around the state (see map).  For inclusion in the display tool, a station was required to have reported four or more hourly winds on at least 75% of the days in the 35-year period, 1981-2015.  Nearly all the sites are at airports.  Over the last two decades, most stations have been automated and are now part of either the ASOS (Automated Surface Observing System) network or the AWOS (Automated Weather Observing System) network operated by the Federal Aviation Administration.

### Data processing: Quality-control

Because the instruments, their heights above the surface (now 10 meters), or their precise locations have undergone changes at some sites since 1980, the data from all stations were subjected to homogeneity tests.  If the wind speeds at a station showed a statistically significant change from one portion of the record to the next, the data prior to the change were adjusted by quantile mapping, a typical method for correcting biased meteorological data.  28 of the 67 stations underwent this type of adjustment.  Four of the stations displayed two discontinuities, in which case the quantile mapping adjustment to the later period was applied twice. Additional quality-control steps included removal of obviously erroneous reports (e.g., wind speeds exceeding 100 mph) and the removal of short-duration (< 6 hours) spikes in which an hourly wind speed was at least 30 mph greater than in immediately preceding and subsequent hours.

### Displayed information

The displays for each site are designed to highlight the average (climatological) wind speed and direction.  The first display is a composite of box plots of the average monthly wind speeds (mph) by calendar month.  The averages (horizontal lines within boxes) are based on all the hourly reports for a particular calendar month.  The boxes represent the 25%/75% ranges of the monthly averages for the 35 different years.  The whiskers represent the full ranges of the monthly averages for the different years.

The second display consists of wind roses showing the distributions of wind by direction and speed.  The spokes point in the compass direction from which the wind was blowing (i.e., a spoke to the right denotes a wind from the east; a spoke pointing downward denotes a wind from the south).  There are 36 spokes, corresponding to the wind direction code in the hourly wind reports (01, 02,…36).  The concentric circles in each plot denote frequencies of occurrence (3%, 6%, 9%,…).   For each directional spoke, the frequencies of wind speeds in various ranges are displayed.  As shown in the legend to the left of the annual wind rose, darker shades of blue represent progressively higher wind speed categories (lightest shading for winds of 0-6 mph, darkest shading for winds of 22 mph or higher).  The frequency of calm wind reports (speed = 0) is indicated in the open circle at the center of each wind rose.

                """,
                    className="is-size-5 content",
                )
            ],
        )
    ],
)

layout = html.Div(children=[header_section, main_layout, help_text, footer])
