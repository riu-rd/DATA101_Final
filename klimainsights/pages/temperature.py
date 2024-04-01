# Setup Folders, Tokens, and Dependencies
from dash import html, dcc, callback, Output, Input, State, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import geopandas as gpd
from pathlib import Path
from environment.settings import MAPBOX_TOKEN

datasets_folder = Path('./data')
px.set_mapbox_access_token(MAPBOX_TOKEN)

# Import Data
temperature_gdf = gpd.read_file(datasets_folder / "temperature.geojson")

# Initialize Page
register_page(__name__, path='/temperature', name='Temperature', title='Klima Insights | Temperature')

layout = dbc.Container(className="d-flex justify-content-center align-items-center full-height full-width my-3 z-3", fluid=True, children=[
  dbc.Row(children=[
    dbc.Col(className="bg-light rounded z-3", width=12, md=4, children=[
      html.Div(className="full-width-container text-dark", children=[
          html.H3(className="mt-2", children=[
              "Charting the Climate Shift: Examining Temperature Trends in the Philippines Across Decades"
          ]),
          html.P(children=[
              "Delving into the historical records reveals a subtle yet discernible shift in the climate dynamics of the Philippines. From the relatively mild conditions of the 1960s to the present-day realities of the 2020s, there's a noticeable uptick in temperature. While the increase may not be drastic, it remains a cause for concern and warrants careful observation. What was once a region known for its moderate temperatures has gradually warmed, signaling a shift that demands attention. Understanding these incremental changes is essential in navigating the evolving climate landscape and implementing effective measures to mitigate their impact."
          ]),
          html.Div(className="container-fluid d-flex justify-content-center my-3",children=[
                dbc.Button("Compare Provinces", color="primary", id="open-temp-modal", n_clicks=0)
          ]),
          dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(className="text-secondary", children=["Average Temperature per Province"])),
                dbc.ModalBody(children=[
                    dbc.Row(children=[
                        dbc.Col(width=12, md=4, children=[
                          html.Div(children=[
                            html.H4(className="mt-2 text-light", children=[
                                " Unraveling Temperature Trends Across Philippine Provinces from the 1960s to the 2020s"
                            ]),
                            html.P(className="text-light", children=[
                                "Embarking on a comprehensive exploration, we delve into the temperature data per province across the Philippines spanning from the 1960s to the 2020s. Through meticulous analysis, a discernible pattern emerges, indicating a modest uptick in temperatures as the decades progress. While the increase may seem subtle, it's a notable phenomenon worthy of attention. The comparative visualization reveals a trend reflective of broader climate shifts, hinting at the ongoing environmental changes affecting the nation's provinces. These findings underscore the importance of monitoring and understanding regional temperature variations, as they hold implications for both local communities and broader climate resilience efforts."
                            ]),
                          ])
                        ]),
                        dbc.Col(className="temp-bar-container", width=12, md=8, children=[
                          dcc.Dropdown(options=['Luzon', 'Visayas', 'Mindanao'], value='Luzon', id='temp-bar-dropdown',
                                       multi=False, searchable=False, clearable=False),
                          dcc.Loading(type="circle", children=[dcc.Graph(id="temp-bar")])
                        ])
                    ])
                ]),
            ],
            id="temp-modal",
            size="xl",
            is_open=False,
        ),
        ])
    ]),
    dbc.Col(className="rounded", width=12, md=8, children=[
      html.Div(className="text-dark", children=[
          dcc.Dropdown(options=['1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s'], value='1960s', id='temp-map-dropdown',
                                       multi=False, searchable=False, clearable=False),
          dcc.Loading(type="circle", children=[dcc.Graph(id="temp-map", responsive=True)])
        ])
    ])
  ])
])

# Compare Modal
@callback(
    Output("temp-modal", "is_open"),
    Input("open-temp-modal", "n_clicks"),
    State("temp-modal", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

# Bar Figure
@callback(
    Output('temp-bar', 'figure'),
    Input('temp-bar-dropdown', 'value')
)
def update_bar_fig(island_value):
    selected_gdf = temperature_gdf[(temperature_gdf['island_group'].isin(['Luzon']) == True)].drop(columns=['geometry'])
    island_gdf = pd.melt(selected_gdf, id_vars=['name', 'admin_div', 'island_group', 'Region'], var_name='decade', value_name='value')
    # Create the Figure with horizontal orientation
    bar_fig = px.bar(island_gdf, y='name', x='value', animation_frame="decade", orientation='h')
    bar_fig.update_layout(
        height=750,
        title=f'Average Temperature per Province<br>in {island_value}',
        margin=dict(l=20, r=20, t=75, b=50),
        yaxis=dict(
            title="Province Name",
            tickfont=dict(size=11)  # Adjust tick font size to prevent overlap
        ),
        xaxis=dict(
            title="Temperature (°C)",
            range=[0, 35],
            tickmode='linear',
            dtick=5,
            tickfont=dict(size=13),  # Adjust tick font size to prevent overlap
            tickangle=0
        ),
        font=dict(  # Adjust font size for main title
            size=12
        )
    )
    hover_template = "Average Temperature in<br>" + \
                     "<b>%{y}</b><br>" + \
                     "during the %{customdata[0]}:<br>" + \
                     "%{customdata[1]:.2f}°C"
    bar_fig.update_traces(hovertemplate=hover_template,
                           customdata=island_gdf[['decade', 'value']])

    for frame in bar_fig.frames:
        frame.data[0].hovertemplate = hover_template
        frame.data[0].customdata = island_gdf[['decade', 'value']]
    bar_fig.update_layout(
        updatemenus=[{
            'direction': 'left',
            'pad': {'t': 10, 'b': 10, 'l': 10, 'r': 10},
            'showactive': False,
            'type': 'buttons',
            'x': 0.06,
            'xanchor': 'right',
            'y': -0.14,
            'yanchor': 'top'
        }],
        sliders=[{
            'active': 0,
            'x': 0.98,
            'y': -0.08,
            'xanchor': 'right',
            'yanchor': 'top',
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'t': 10, 'b': 10, 'l': 10, 'r': 10},
            'currentvalue': {
                'font': {'size': 15},
                'prefix': 'Decade:',
                'visible': True,
                'xanchor': 'right',
            },
            'visible': True,
        }]
    )

    highest_temp_1960 = island_gdf[island_gdf['decade'] == '1960s']['value'].max()  # Highest temperature for the decade 1960
    bar_fig.add_shape(  # Line representing highest temperature in the 1960s
        type="line",
        x0=highest_temp_1960,
        y0=-1,
        x1=highest_temp_1960,
        y1=island_gdf.name.nunique()-0.5,
        line=dict(
            color="red",
            width=1,
            dash="dash",
        ),
    )

    bar_fig.add_annotation(
        x=highest_temp_1960 + 1,
        y=island_gdf.name.nunique() / 1.3,  # Adjust the y position of the label
        text="Highest Temp in the 1960s",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=0,  # Adjust the arrow position
        font=dict(
            color="red",
            size=12
        ),
        align="left",
        textangle=90  # Tilt the text 90 degrees
    )

    return bar_fig

# Map Figure
@callback(
    Output('temp-map', 'figure'),
    Input('temp-map-dropdown', 'value')
)
def update_map_fig(decade_value):
    map_fig = px.choropleth_mapbox(temperature_gdf,
                                    geojson=temperature_gdf.geometry,
                                    locations=temperature_gdf.index,
                                    color=decade_value,
                                    color_continuous_scale='turbo',
                                    range_color=[25, 33],
                                    mapbox_style='streets',
                                    zoom=5,
                                    center={"lat": 12.8797, "lon": 122.7740},
                                    opacity=0.6,
                                    )
    map_fig.update_layout(
        coloraxis_colorbar=dict(title=f"{decade_value}<br>Average<br>Temperature(°C)", yanchor="top", xanchor='left',
                                y=1, x=0, ticks="outside", ticklabelposition="outside left", thickness=10, title_font_color='#0c232c',
                                tickvals=[i for i in range(25, 33)],
                                tickmode='array',
                                ticksuffix='°C',
                                tickfont=dict(
                                    size=12,
                                    color='#0c232c')
                                )
    )
    map_fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
    )
    hover_template = '<b>%{customdata[0]}</b><br>during the '+ decade_value +'<br>Average Temp: %{customdata[1]:.2f}°C<extra></extra>'
    map_fig.update_traces(hovertemplate=hover_template,
                           customdata=temperature_gdf[['name', decade_value]])

    return map_fig