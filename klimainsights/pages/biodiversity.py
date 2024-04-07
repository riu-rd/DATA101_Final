# Setup Folders, Tokens, and Dependencies
from dash import html, dcc, callback, Output, Input, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import geopandas as gpd
import dash_daq as daq
from pathlib import Path
from environment.settings import MAPBOX_TOKEN

datasets_folder = Path('./data')
px.set_mapbox_access_token(MAPBOX_TOKEN)

# Import Data
biodiversity_gdf = gpd.read_file(datasets_folder / 'biodiversity.geojson')
temperature_gdf = gpd.read_file(datasets_folder / 'temperature.geojson')

melt_value = temperature_gdf.drop(columns=[col for col in temperature_gdf.columns if 'TempDiff' in col])
melt_value.columns = [col.split('_')[0] if '_value' in col else col for col in melt_value.columns]
melt_value = melt_value.melt(id_vars=['name', 'geometry', 'admin_div', 'island_group', 'Region'], 
                            var_name='decade', 
                            value_name='value')
melt_tempdiff = temperature_gdf.drop(columns=[col for col in temperature_gdf.columns if 'value' in col])
melt_tempdiff.columns = [col.split('_')[0] if '_TempDiff' in col else col for col in melt_tempdiff.columns]
melt_tempdiff = melt_tempdiff.melt(id_vars=['name', 'geometry', 'admin_div', 'island_group', 'Region'], 
                            var_name='decade', 
                            value_name='TempDiff')
temp_melted_gdf = pd.merge(melt_value, melt_tempdiff, on=['name', 'geometry', 'admin_div', 'island_group', 'Region', 'decade'])

# Initialize Page
register_page(__name__, path='/biodiversity', name='Biodiversity', title='Biodiversity Insights')

layout = dbc.Container(className="d-flex justify-content-center align-items-center full-width my-3 z-3", fluid=True, children=[
    dbc.Row(className="align-items-stretch", children=[
        dbc.Col(className="bg-light rounded z-3 d-flex flex-col justify-content-center align-items-center", width=12, md=4, children=[
            html.Div(className='full-width-container text-dark', children=[
                daq.BooleanSwitch(
                                id='bio-switch',
                                on=False,
                                color="#b58900",
                                label="Show Avg Temp Increase Per Province"
                            ),
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
                    html.Div(className='w-50', children=[
                        dcc.Dropdown(options=['Luzon', 'Visayas', 'Mindanao'], value='Luzon', id='region-dropdown', multi=False, searchable=False, clearable=False)
                    ]),
                    html.Div(className='w-50', children=[
                        dcc.Dropdown(options=[{'label': 'Total', 'value': 'total_species'},
                                {'label': 'Critically Endangered', 'value': 'Critically Endangered'},
                                {'label': 'Endangered', 'value': 'Endangered'},
                                {'label': 'Vulnerable', 'value': 'Vulnerable'}],
                                value='total_species', id='species-dropdown', 
                                multi=False, searchable=False, clearable=False)
                    ])
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
    [Input('region-dropdown', 'value'), Input('species-dropdown', 'value')]
)
def update_choropleth(region, species_type):
    # if region == "Sea":
    #     filtered_data = biodiversity_gdf[(biodiversity_gdf['area_type'].isin(['Sea']))].reset_index().drop(columns='index')
    #     cen = {"lat": 12.8797, "lon": 122.7740}
    #     zum = 4
    # else:
    filtered_data = biodiversity_gdf[biodiversity_gdf['island_group'] == region].reset_index().drop(columns='index')
    if region == "Luzon":
        cen = {"lat": filtered_data.geometry.centroid.y.values[0]-2.5, "lon": filtered_data.geometry.centroid.x.values[0]}
        zum = 5
    elif region == "Visayas":
        cen = {"lat": filtered_data.geometry.centroid.y.values[0]-1, "lon": filtered_data.geometry.centroid.x.values[0]+1.7}
        zum = 5.7
    else:
        cen = {"lat": filtered_data.geometry.centroid.y.values[0]-1, "lon": filtered_data.geometry.centroid.x.values[0]-1}
        zum = 5.5
    
    if species_type == "total_species":
        txt = "Total"
    else:
        txt = species_type
    # Create choropleth map using Plotly Express
    choropleth_fig = px.choropleth_mapbox(filtered_data,
                                            height=550,
                                           geojson=filtered_data.geometry,
                                           locations=filtered_data.index,
                                           color=species_type,  # Change based on biodiversity metric
                                           color_continuous_scale='dense',
                                           range_color=[filtered_data[species_type].min(), filtered_data[species_type].max()],
                                           mapbox_style='streets',
                                           zoom=zum,
                                           center=cen,
                                           opacity=0.6
                                           )
    choropleth_fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    choropleth_fig.update_layout(coloraxis_colorbar=dict(title= txt + " Species Count", yanchor="top", xanchor='left',
                                                          y=1, x=0, ticks="outside", ticklabelposition="outside left",
                                                          thickness=10, title_font_color='#0c232c',
                                                          tickfont=dict(size=12, color='#0c232c')
                                                          )
                                 )

    hover_template = '<b>%{customdata[0]}</b><br>' + txt + ' Count: %{z:.0f}<extra></extra>'
    choropleth_fig.update_traces(hovertemplate=hover_template,
                                 customdata=filtered_data[['name', species_type]])
    return choropleth_fig

# Bar Figure
@callback(
    Output('endangered-species-bar', 'figure'),
    [Input('region-dropdown', 'value'), Input('species-dropdown', 'value'), Input('bio-switch', 'on'), Input('biodiversity-choropleth', 'clickData')]
)
def update_bar(region, species_type, bio_switch, click_data):
    # if region == "Sea":
    #     filtered_data = biodiversity_gdf[(biodiversity_gdf['area_type'].isin(['Sea']))].reset_index().drop(columns='index')
    # else:
    
    filtered_data = biodiversity_gdf[biodiversity_gdf['island_group'] == region].sort_values(by=species_type, ascending=True, ignore_index=True)
    
    if species_type == "total_species":
        txt = "Total"
    else:
        txt = species_type
    
    if bio_switch:
        if click_data is not None:
            data = click_data['points'][0]['customdata'][0] 
        else:
            data = filtered_data['name'].iloc[-1]

        island_gdf = temp_melted_gdf[(temp_melted_gdf['name'].isin([data]) == True)].drop(columns=['geometry'])
        line_fig = px.line(island_gdf, x='decade', y='value',color='name')
        line_fig.update_layout(
            autosize=True,  
            height=750,
            title='Change in Avg Temperature in ' + data,
            yaxis=dict(
                range=[25, 32],
                tickmode='linear',
                dtick=0.5
            ),
            margin=dict(l=20, r=20, t=100, b=100),
            updatemenus=[{
                'direction': 'left',  
                'pad': {'t': 0, 'b': 0, 'l': 0, 'r': 0},  
                'showactive': False,
                'type': 'buttons',
                'x': 0.06,  
                'xanchor': 'right',
                'y': -0.46,  
                'yanchor': 'top'
            }],
            xaxis_tickangle=-45 
        )
        hover_template = '<b>' + data + '</b><br>Average Temperature in<br>the %{x}:<br>%{y:.2f}°C<extra></extra>'
        line_fig.update_traces(hovertemplate=hover_template)

        return line_fig

    else:
        bar_fig = px.bar(filtered_data,
                        x=species_type,
                        y='name',
                        title=txt + " Species Composition in " + region,
                        orientation='h',
                        height=750,
                        color_discrete_sequence=['lightblue']
                        )
        bar_fig.update_layout(
            xaxis_title=txt + " Count",
            yaxis_title="Province",
        )
        hover_template = '<b>%{y}</b><br>' + txt + ' Count: %{x}<extra></extra>'
        bar_fig.update_traces(hovertemplate=hover_template)
        return bar_fig