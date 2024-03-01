# Install Libraries using the Terminal in VSCode
# %pip install Pyarrow
# %pip install pandas
# %pip install numpy
# %pip install dash
# %pip install plotly
# %pip install geopandas
# %pip install dash-bootstrap-components

from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path

# Set Mapbox Token
px.set_mapbox_access_token(open(".mapbox_token").read())

# Import Data
IUCN_gdf = gpd.read_file('IUCN.geojson')

data_canada = px.data.gapminder().query("country == 'Canada'")
sample_fig = px.bar(data_canada, x='year', y='pop')
sample_fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
sample_fig.update_layout(title='temperature on bla bla')

# Creating Figures



# Create the Application
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'styles.css'])

app.layout = html.Div(id='main', children=[
    dbc.Container(children=[
        dbc.Row(children=[
            dcc.Dropdown(
                className='dropdown',
                id='dropdown-bio',
                options=[{'label':'Critically Endangered', 'value':'CR'},
                         {'label':'Endangered', 'value':'EN'},
                         {'label':'Vulnerable', 'value':'VU'}],
                value='CR',
                multi=False,
                clearable=False,
                searchable=False),
            dcc.Loading(dcc.Graph(id='graph-bio')),
            dbc.Container(className='div-temp', children=[
                html.H1(id='h1-bio', children=['Critically Endangered Species']),
                html.P(children=['Well would you look at that, they are endangered. Which means they are en danger']),
                dcc.Loading(dcc.Graph(id='bar-temp', figure=sample_fig))
            ])
        ])
    ])
])

@callback(
    [Output('graph-bio', 'figure'), Output('h1-bio', 'children')],
    Input('dropdown-bio', 'value')
)
def update_rollup(species_type):
    text = "Number of "
    match species_type:
        case "CR":
            scale_color = "bluered"
            label = {'CR':'Number of Critically Endangered Species'}
            species_text = "Critically Endangered Species"
        case "EN":
            scale_color = "orrd"
            label = {'EN':'Number of Endangered Species'}
            species_text = "Endangered Species"
        case "VU":
            scale_color = "magenta"
            label = {'VU':'Number of Vulnerable Species'}
            species_text = "Vulnerable Species"
    

    fig = px.choropleth_mapbox(IUCN_gdf,
                           geojson=IUCN_gdf.geometry,
                           locations=IUCN_gdf.index,
                           color=species_type,
                           color_continuous_scale=scale_color,
                           mapbox_style='streets',
                           zoom=5, 
                           center={"lat": 12.8797, "lon": 121.7740},
                           opacity=0.6,
                           custom_data=['name'],
                           labels=label)

    fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Species: %{z}')

    fig.update_layout(coloraxis_colorbar=dict(title=f"{text}<br>{species_text}<br> &nbsp; ",yanchor="top", xanchor='right',
                                                y=1, x=1, ticks="outside", thickness=50, title_font_color='#0c232c',
                                                tickfont=dict(
                                                size=12,
                                                color='#0c232c')
    ))

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    return fig, species_text

# Launch the Application
if __name__ == '__main__':
    app.run(debug=True)