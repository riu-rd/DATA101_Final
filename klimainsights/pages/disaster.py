# Setup Folders, Tokens, and Dependencies
from dash import Dash, html, dcc, callback, Output, Input, State, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
from environment.settings import MAPBOX_TOKEN

datasets_folder = Path('./data')
px.set_mapbox_access_token(MAPBOX_TOKEN)

# Import Data
temperature_gdf = gpd.read_file(datasets_folder / "temperature.geojson")
disaster_gdf = gpd.read_file(datasets_folder / 'disaster.geojson')
Region_gdf = disaster_gdf.copy()
Region_tot_ave = Region_gdf.drop(columns=['geometry']).groupby('Region').sum()
def region_count(disaster_type,col_name):
    Region_gdf[col_name] = np.nan #Create a new column that contains the number of disasters per region

    for i1,r1 in Region_gdf.iterrows():
        for i2,r2 in Region_tot_ave.iterrows():
            if r1['Region'] == i2:
                Region_gdf.at[i1, col_name] = r2[disaster_type]
            else:
                continue
region_count('Total Disaster Count','Region_tot')
region_count('Storm Count','Region_storm')
region_count('Flood Count','Region_flood')
region_count('Earthquake Count','Region_earth')
region_count('Volcanic Activity Count','Region_vol')
region_count('Mass Movement Count','Region_mass')
region_count('Drought Count','Region_drought')

# Initialize Page
register_page(__name__, path='/disaster', name='Disaster', title='Klima Insights | Disaster')

layout = dbc.Container(className="d-flex justify-content-center align-items-center full-width my-3 z-3", fluid=True, children=[
  dbc.Row(className="align-items-stretch", children=[
      dbc.Col(className="bg-light rounded z-3 d-flex flex-col justify-content-center align-items-center", width=12, md=4, children=[
          html.Div(className='full-width-container text-dark', children=[
              html.Div(className='d-flex flex-row justify-content-start align-items-center mt-2 flex-gap-20', children=[
                  html.H5(className='mt-1', children=["Divide By: "]),
                  dcc.RadioItems(id='division-radio', options=['Region', 'Province'], value='Region', inline=True, labelStyle={"margin-right": "20px"})
              ]),
              html.H4(className="mt-2", children=[
                  "Unveiling the Interplay of Temperature and Disaster Vulnerability in the Philippines"
              ]),
              html.P(className="", children=[
                  "The Philippines, situated along the Pacific Ring of Fire, has long been highly susceptible to a range of disasters, including seismic and volcanic events. However, it's crucial to recognize that the nation's vulnerability to such calamities is not solely attributable to its geographical location. By utilizing the dropdown menu provided, one can explore the occurrences of each disaster type. Furthermore, clicking on specific areas in the map facilitates a deeper visualization of temperature changes in those regions."
              ]),
              dcc.Loading(type="circle", children=[dcc.Graph(id="disaster-line")])
          ])
      ]),
      dbc.Col(className="rounded z-3 disaster-map-height overflow-hidden", width=12, md=8, children=[
          html.Div(className="text-dark z-3 align-self-start", children=[
            html.Div(className='d-flex flex-row justify-content-between align-items-center', children=[
              html.Div(className='w-100', children=[
                  dcc.Dropdown(options=['Total Disaster', 'Storm', 'Flood', 'Earthquake', 'Volcanic Activity', 'Mass Movement', 'Drought'], value='Total Disaster', id='disaster-type-dropdown', multi=False, searchable=False, clearable=False)
              ]),
              dbc.Button("Compare", color="primary z-3", id="open-disaster-modal", n_clicks=0)
            ]),
            html.Div(children=[
                dcc.Loading(type="circle", children=[dcc.Graph(id="disaster-map")])
            ])
          ])
      ]),
      dbc.Modal(
          [
              dbc.ModalHeader(dbc.ModalTitle(className="text-secondary", children=["Disaster Count per Area"])),
              dbc.ModalBody(children=[
                  dbc.Row(children=[
                      dbc.Col(width=12, md=4, children=[
                        html.Div(children=[
                          html.H4(className="mt-2 text-light", children=[
                              "Deeper Insights into Disaster Trends"
                          ]),
                          html.P(className="text-light", children=[
                              "Taking a closer look, we can compare the frequency of disasters in each province or region within a specific island group using the bar graph provided on the right. Noticing the disparity in disaster occurrences among different areas raises awareness of the necessity to take proactive measures, regardless of their scale, to mitigate and minimize future disasters."
                          ]),
                        ])
                      ]),
                      dbc.Col(width=12, md=8, children=[
                        dcc.Dropdown(options=['Luzon', 'Visayas', 'Mindanao'], value='Luzon', id='disaster-bar-dropdown',
                                      multi=False, searchable=False, clearable=False),
                        dcc.Loading(type="circle", children=[dcc.Graph(id="disaster-bar")])
                      ])
                  ])
              ]),
          ],
          id="disaster-modal",
          size="xl",
          is_open=False,
      )
  ])
])

# Compare Modal
@callback(
    Output("disaster-modal", "is_open"),
    Input("open-disaster-modal", "n_clicks"),
    State("disaster-modal", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

# Click Data
@callback(
    Output("disaster-line", "figure"),
    [Input('division-radio', 'value'), Input("disaster-map", "clickData")]
)
def update_line(division, click_data):
    if click_data is not None:
      data = click_data['points'][0]['customdata'][0] 
    else:
      match division:
            case 'Region':
                data = 'RegionI'
            case 'Province':
                data = 'Abra'

    curr_div = ''
    if division == 'Region':
        curr_div = 'Region'
    elif division == 'Province':
        curr_div = 'name'
    else:
        return
    selected_gdf = temperature_gdf[(temperature_gdf[curr_div].isin([data]) == True)].drop(columns=['geometry'])
    island_gdf = pd.melt(selected_gdf, id_vars=['name', 'admin_div', 'island_group', 'Region'], var_name='decade', value_name='value')

    line_fig = px.line(island_gdf, x='decade', y='value',color='name')
    line_fig.update_layout(
        autosize=True,  
        height=500,
        title='Change in Temperature in ' + data,
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

# Map Figure
@callback(
    Output('disaster-map', 'figure'),
    [Input('division-radio', 'value'), Input('disaster-type-dropdown', 'value')]
)
def update_map(division, disaster_type):
    curr_division = ''
    curr_disaster = ''
    if division == 'Region':
        curr_division = 'Region'
        match disaster_type:
            case 'Total Disaster':
                curr_disaster = 'Region_tot'
            case 'Storm':
                curr_disaster = 'Region_storm'
            case 'Flood':
                curr_disaster = 'Region_flood'
            case 'Earthquake':
                curr_disaster = 'Region_earth'
            case 'Volcanic Activity':
                curr_disaster = 'Region_vol'
            case 'Mass Movement':
                curr_disaster = 'Region_mass'
            case 'Drought':
                curr_disaster = 'Region_drought'
            case _:
                return
    elif division == 'Province':
        curr_division = 'Area Name'
        match disaster_type:
            case 'Total Disaster':
                curr_disaster = 'Total Disaster Count'
            case 'Storm':
                curr_disaster = 'Storm Count'
            case 'Flood':
                curr_disaster = 'Flood Count'
            case 'Earthquake':
                curr_disaster = 'Earthquake Count'
            case 'Volcanic Activity':
                curr_disaster = 'Volcanic Activity Count'
            case 'Mass Movement':
                curr_disaster = 'Mass Movement Count'
            case 'Drought':
                curr_disaster = 'Drought Count'
            case _:
                return
    else:
        return

    map_fig = px.choropleth_mapbox(Region_gdf,
                                height=845,
                                geojson=Region_gdf.geometry,
                                locations=Region_gdf.index,
                                color=curr_disaster, # Change based on dropdown value
                                color_continuous_scale='amp',
                                range_color=[Region_gdf[curr_disaster].min(), Region_gdf[curr_disaster].max()],  
                                mapbox_style='streets',  
                                zoom=5,  
                                center={"lat": 12.8797, "lon": 122.7740}, 
                                opacity=0.6,
                                )

    map_fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    map_fig.update_layout(coloraxis_colorbar=dict(title= disaster_type + "<br>Count",yanchor="top",xanchor='left',
                                y=1, x=0, ticks="outside", ticklabelposition="outside left", thickness=10, title_font_color='#0c232c',  
                                tickfont=dict(
                                size=12,
                                color='#0c232c')
                            )
                        )

    hover_template = '<b>%{customdata[0]}</b><br>' + disaster_type + ' Count: %{customdata[1]:.0f}<extra></extra>'

    map_fig.update_traces(hovertemplate=hover_template,
                    customdata=Region_gdf[[curr_division, curr_disaster]])

    return map_fig

# Bar Figure
@callback(
    Output('disaster-bar', 'figure'),
    [Input('division-radio', 'value'), Input('disaster-type-dropdown', 'value'), Input('disaster-bar-dropdown', 'value')]
)
def update_disaster_bar(division, disaster_type, island_group):
    curr_division = ''
    curr_disaster = ''
    if division == 'Region':
        curr_division = 'Region'
        match disaster_type:
            case 'Total Disaster':
                curr_disaster = 'Region_tot'
            case 'Storm':
                curr_disaster = 'Region_storm'
            case 'Flood':
                curr_disaster = 'Region_flood'
            case 'Earthquake':
                curr_disaster = 'Region_earth'
            case 'Volcanic Activity':
                curr_disaster = 'Region_vol'
            case 'Mass Movement':
                curr_disaster = 'Region_mass'
            case 'Drought':
                curr_disaster = 'Region_drought'
            case _:
                return
        island_disaster = Region_gdf[Region_gdf['Island Group'] == island_group].groupby('Region')[curr_disaster].sum().sort_values(ascending=True)
        x = island_disaster.values
        y = island_disaster.index
    elif division == 'Province':
        curr_division = 'Area Name'
        match disaster_type:
            case 'Total Disaster':
                curr_disaster = 'Total Disaster Count'
            case 'Storm':
                curr_disaster = 'Storm Count'
            case 'Flood':
                curr_disaster = 'Flood Count'
            case 'Earthquake':
                curr_disaster = 'Earthquake Count'
            case 'Volcanic Activity':
                curr_disaster = 'Volcanic Activity Count'
            case 'Mass Movement':
                curr_disaster = 'Mass Movement Count'
            case 'Drought':
                curr_disaster = 'Drought Count'
            case _:
                return
        island_disaster = Region_gdf[(Region_gdf['Island Group'] == island_group)].sort_values(by='Total Disaster Count', ascending=True)
        x = curr_disaster
        y = curr_division
    else:
        return
    # Create stacked bar plot using Plotly Express
    bar_fig = px.bar(island_disaster,
                x=x,  
                y=y,  
                title=disaster_type + " in " + island_group + " per " + division,
                orientation='h',  
                height=750,  
                color_discrete_sequence=['lightblue'], 
                )
    bar_fig.update_layout(
        xaxis_title=disaster_type, 
        yaxis_title=division,
    )
    hover_template = '<b>%{customdata[0]}</b><br>' + disaster_type + ' Count: %{x}<extra></extra>'
    bar_fig.update_traces(hovertemplate=hover_template,
                    customdata=Region_gdf[[curr_division]])

    return bar_fig