# Setup Folders, Tokens, and Dependencies
from dash import Dash, html, dcc, callback, Output, Input, page_container
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
from flask_caching import Cache

datasets_folder = Path('./data')
px.set_mapbox_access_token(open(".mapbox_token").read())

# Create the Application
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN, 'styles.css'], use_pages=True)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

app.layout = html.Div(id='main', children=[
    dcc.Link("Temperature", href='/'),
    dcc.Link("Biodiversity", href='/biodiversity'),
    html.Hr(),
    page_container
])

# Launch the Application
if __name__ == '__main__':
    app.run(debug=True)