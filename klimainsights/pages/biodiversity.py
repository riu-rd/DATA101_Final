# Setup Folders, Tokens, and Dependencies
from dash import html, dcc, callback, Output, Input, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import geopandas as gpd
from pathlib import Path
from environment.settings import MAPBOX_TOKEN

datasets_folder = Path('./data')
px.set_mapbox_access_token(MAPBOX_TOKEN)

# Import Data
biodiversity_gdf = gpd.read_file(datasets_folder / 'biodiversity.geojson')
temperature_gdf = gpd.read_file(datasets_folder / 'temperature.geojson')

merged_data = pd.merge(biodiversity_gdf, temperature_gdf, on='name', how='left')

# Initialize Page
register_page(__name__, path='/biodiversity', name='Biodiversity', title='Biodiversity Insights')

layout = dbc.Container(className="d-flex justify-content-center align-items-center full-width my-3 z-3", fluid=True, children=[
    dbc.Row(className="align-items-stretch", children=[
        dbc.Col(className="bg-light rounded z-3 d-flex flex-col justify-content-center align-items-center", width=12, md=4, children=[
            html.Div(className='full-width-container text-dark', children=[
                html.H4(className="mt-2", children=[
                    "Exploring Biodiversity in the Philippines"
                ]),
                html.P(className="", children=[
                    "Discover the rich biodiversity of the Philippines and understand its distribution across different regions. Use the selector to filter by geographic region and explore the geospatial distribution of biodiversity as well as the composition of endangered species."
                ]),
                dcc.Loading(type="circle", children=[dcc.Graph(id="biodiversity-choropleth")])
            ])
        ]),
        dbc.Col(className="rounded z-3 biodiversity-map-height overflow-hidden", width=12, md=8, children=[
            html.Div(className="text-dark z-3 align-self-start", children=[
                html.Div(className='d-flex flex-row justify-content-between align-items-center', children=[
                    html.Div(className='w-100', children=[
                        dcc.Dropdown(options=['Luzon', 'Visayas', 'Mindanao'], value='Luzon', id='region-dropdown', multi=False, searchable=False, clearable=False)
                    ]),
                    dbc.Button("Filter", color="primary z-3", id="filter-biodiversity", n_clicks=0)
                ]),
                html.Div(children=[
                    dcc.Loading(type="circle", children=[dcc.Graph(id="endangered-species-bar")])
                ])
            ])
        ])
    ])
])


# Choropleth Map Figure
@callback(
    Output('biodiversity-choropleth', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_choropleth(region):
    filtered_data = biodiversity_gdf[biodiversity_gdf['island_group'] == region]

    # Create choropleth map using Plotly Express
    choropleth_fig = px.choropleth_mapbox(filtered_data,
                                           geojson=filtered_data.geometry,
                                           locations=filtered_data.index,
                                           color='total_species',  # Change based on biodiversity metric
                                           color_continuous_scale='amp',
                                           range_color=[filtered_data['total_species'].min(), filtered_data['total_species'].max()],
                                           mapbox_style='streets',
                                           zoom=5,
                                           center={"lat": 12.8797, "lon": 122.7740},
                                           opacity=0.6
                                           )

    choropleth_fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    choropleth_fig.update_layout(coloraxis_colorbar=dict(title="Total Species Count", yanchor="top", xanchor='left',
                                                          y=1, x=0, ticks="outside", ticklabelposition="outside left",
                                                          thickness=10, title_font_color='#0c232c',
                                                          tickfont=dict(size=12, color='#0c232c')
                                                          )
                                 )

    hover_template = '<b>%{customdata[0]}</b><br>Total Species Count: %{z:.0f}<extra></extra>'

    choropleth_fig.update_traces(hovertemplate=hover_template,
                                 customdata=filtered_data[['name', 'total_species']])

    return choropleth_fig


# Endangered Species Bar Figure
@callback(
    Output('endangered-species-bar', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_endangered_species_bar(region):
    filtered_data = biodiversity_gdf[biodiversity_gdf['island_group'] == region]

    # Create horizontal bar plot using Plotly Express
    bar_fig = px.bar(filtered_data,
                     x='total_species',
                     y='name',
                     title="Endangered Species Composition in " + region,
                     orientation='h',
                     height=750,
                     color_discrete_sequence=['lightblue']
                     )

    bar_fig.update_layout(
        xaxis_title="Total Species Count",
        yaxis_title="Province",
    )

    hover_template = '<b>%{y}</b><br>Total Species Count: %{x}<extra></extra>'
    bar_fig.update_traces(hovertemplate=hover_template)

    return bar_fig
