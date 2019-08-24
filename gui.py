"""
NWT Mine site future climate tool
"""
# pylint: disable=invalid-name, import-error
import os
import json
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from luts import communities, months_lut, map_communities_trace, map_layout

path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

# Google analytics tag
gtag_id = os.environ['GTAG_ID']

map_figure = go.Figure({
    'data': [map_communities_trace],
    'layout': map_layout
})

# We want this HTML structure to get the full-width background color:
# <div class="header">
#   <div class="container"> gives us the centered column
#     <div class="section"> a bit more padding to stay consistent with form
header_section = html.Div(
    className='header',
    children=[
        html.Div(
            className='container',
            children=[
                html.Div(
                    className='section header--section',
                    children=[
                        html.Div(
                            className='header--logo',
                            children=[
                                html.A(
                                    className='header--snap-link',
                                    href='https://snap.uaf.edu',
                                    rel='external',
                                    target='_blank',
                                    children=[
                                        html.Img(src=path_prefix + 'assets/SNAP_acronym_color_square.svg')
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className='header--titles',
                            children=[
                                html.H1(
                                    'Alaskan Community Wind Data',
                                    className='title is-3'
                                ),
                                html.H2(
                                    'Explore historical and modeled wind data for Alaskan communities.  Choose a community to get started.',
                                    className='subtitle is-5'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

footer = html.Footer(
    className='footer has-text-centered',
    children=[
        html.Div(
            children=[
                html.A(
                    href='https://snap.uaf.edu',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/SNAP_color_all.svg'
                        )
                    ]
                ),
                html.A(
                    href='https://uaf.edu/uaf/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/UAF.svg'
                        )
                    ]
                )
            ]
        ),
        dcc.Markdown(
            """
UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual. [Statement of Nondiscrimination](https://www.alaska.edu/nondiscrimination/)
            """,
            className='content is-size-6'
        )
    ]
)

communities_dropdown_field = html.Div(
    className='field',
    children=[
        html.Label('Location', className='label'),
        html.Div(className='control', children=[
            dcc.Dropdown(
                id='communities-dropdown',
                options=[
                    {
                        'label': community.place,
                        'value': index
                    } for index, community in communities.iterrows()
                ],
                value='PAFA'
            )
        ])
    ]
)

form_fields = html.Div(
    className='selectors form',
    children=[
        communities_dropdown_field,
        dcc.Graph(
            id='map',
            figure=map_figure,
            config={
                'displayModeBar': False,
                'scrollZoom': False
            }
        )
    ]
)

main_layout = html.Div(
    className='container',
    children=[
        html.Div(
            className='section section--form',
            children=[
                form_fields,
            ]
        ),
        html.Div(
            className='section graph',
            children=[
                dcc.Graph(
                    id='means',
                    figure=go.Figure()
                ),
                dcc.Graph(
                    id='rose',
                    figure=go.Figure()
                ),
                dcc.Graph(
                    id='rose_monthly',
                    figure=go.Figure()
                )
            ]
        )
    ]
)

help_text = html.Div(
    className='container',
    children=[
        html.Div(
            className='section',
            children=[
                dcc.Markdown('''

## Help text goes here.

                ''', className='is-size-5 content')
            ]
        )
    ]
)

layout = html.Div(
    children=[
        header_section,
        main_layout,
        help_text,
        footer
    ]
)
