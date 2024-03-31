# Setup Folders, Tokens, and Dependencies
from dash import Dash, html, dcc, callback, Output, Input, register_page
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
temp_gdf = gpd.read_file(datasets_folder / 'biodiversity_land.geojson')

# Initialize Page
register_page(__name__, path='/biodiversity', name='Biodiversity', title='Klima Insights | Biodiversity')

layout = html.Div(children=[
  html.H1(["BIODIVERSITY"])

])