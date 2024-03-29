# Setup Folders, Tokens, and Dependencies
from dash import html, dcc, callback, Output, Input, State, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import geopandas as gpd
from pathlib import Path

datasets_folder = Path('./data')
px.set_mapbox_access_token(open(".mapbox_token").read())

# Import Data
temp_1 = gpd.read_file(datasets_folder / "temp_1.geojson")
temp_2 = gpd.read_file(datasets_folder / "temp_2.geojson")
temp_3 = gpd.read_file(datasets_folder / "temp_3.geojson")
temp_gdf = gpd.GeoDataFrame(pd.concat([temp_1, temp_2, temp_3], ignore_index=True))

# Initialize Page
register_page(__name__, path='/temperature', name='Temperature', title='Klima Insights | Temperature')

layout = dbc.Container(className="d-flex justify-content-center align-items-center full-height full-width my-3", fluid=True, children=[
  dcc.Interval(
  id="load_interval", 
  n_intervals=0, 
  max_intervals=0, #<-- only run once
  interval=1
  ),
  dbc.Row(children=[
    dbc.Col(className="bg-light rounded", width=12, md=4, children=[
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
                dbc.ModalHeader(dbc.ModalTitle("Average Temperature per Province")),
                dbc.ModalBody(children=[
                    dbc.Row(children=[
                        dbc.Col(width=12, md=4, children=[
                          html.Div(children=[
                            html.H4(className="mt-2", children=[
                                " Unraveling Temperature Trends Across Philippine Provinces from the 1960s to the 2020s"
                            ]),
                            html.P(children=[
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
          dcc.Loading(type="circle", children=[dcc.Graph(id="temp-map")])
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
    island_gdf = temp_gdf[(temp_gdf['island_group'].isin([island_value]) == True)] # Change Island Group based on Dropdown Value
    # Create the Figure with horizontal orientation
    bar_fig = px.bar(island_gdf, y='name', x='value', animation_frame="decade", orientation='h')
    bar_fig.update_layout(
        autosize=True,
        height=750,
        title=f'Average Temperature per Province in {island_value}',
        margin=dict(l=20, r=20, t=50, b=50),
    )
    bar_fig.update_yaxes(title_text="Province Name")  
    bar_fig.update_xaxes(title_text="Temperature (°C)", 
                    range=[0, 34], 
                    tickmode='linear', 
                    dtick=2,  
                    tickangle=0)    

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
            'y': -0.14,  # Position the menu below the graph
            'yanchor': 'top'
        }],
        sliders=[{
            'active': 0,
            'x': 0.98,   
            'y': -0.08,  # Position the slider below the graph
            'xanchor': 'right',
            'yanchor': 'top',
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'t': 10, 'b': 10, 'l': 10, 'r': 10},
            'currentvalue': {
                'font': {'size': 16},
                'prefix': 'Decade:',
                'visible': True,
                'xanchor': 'right',
            },
            'visible': True,
        }]
    )

    return bar_fig

# Map Figure
@callback(
    Output('temp-map', 'figure'),
    Input(component_id="load_interval", component_property="n_intervals")
)
def update_map_fig(n_intervals):
    temp_sliced = temp_gdf[(temp_gdf['decade'].isin(['1960s', '1980s', '2000s', '2020s']) == True)].reset_index()
    map_fig = px.choropleth_mapbox(temp_sliced,
                              geojson=temp_sliced.geometry,
                              locations=temp_sliced.index,
                              color='value',
                              color_continuous_scale='turbo',
                              range_color=[25, 32.5], 
                              mapbox_style='streets',
                              zoom=5, 
                              center={"lat": 12.8797, "lon": 121.7740},
                              opacity=0.6,
                              animation_frame="decade"
                              )
    map_fig.update_layout(coloraxis_colorbar=dict(title="Average<br>Temperature (°C)",yanchor="top",xanchor='right',
                                y=1, x=1, ticks="outside", thickness=10, title_font_color='#0c232c',
                                tickvals=[i for i in range(25, 33)],  
                                tickmode='array',  
                                ticksuffix='°C',
                                tickfont=dict(
                                size=12,
                                color='#0c232c')
                            )
                        )
    map_fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
        updatemenus=[{
            'buttons': [
                    {'visible': True}
            ],
            'direction': 'left',  
            'pad': {'t': 0, 'b': 0, 'l': 0, 'r': 0},  
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,  
            'xanchor': 'right',
            'y': 0.24,  
            'yanchor': 'top'
        }],
        sliders=[{
            'active': 0,
            'x': 0.05,   
            'y': 0.19, 
            'len': 0.5,
            'xanchor': 'left',
            'yanchor': 'top',
            'currentvalue': {
                'font': {'size': 16},
                'prefix': 'Decade:',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 1000, 'easing': 'cubic-in-out'},
            'pad': {'t': 0, 'b': 0, 'l': 0, 'r': 0}
        }]
    )
    hover_template = '<b>%{customdata[0]}</b><br>Average Temp: %{customdata[1]:.2f}°C<extra></extra>'
    map_fig.update_traces(hovertemplate=hover_template,
                      customdata=temp_sliced[['name', 'value']])
    for frame in map_fig.frames:
        frame.data[0].hovertemplate = hover_template
        frame.data[0].customdata = temp_sliced[['name', 'value']]
    
    return map_fig