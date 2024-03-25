# Setup Folders, Tokens, and Dependencies
from dash import Dash, html, page_container
import dash_bootstrap_components as dbc
from flask_caching import Cache

# Create the Application
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, 'styles.css'], use_pages=True)
app._favicon = ("icon.svg")
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

navbar = dbc.NavbarSimple(className='container-fluid', brand="EcoSphere Watch", brand_href="/", color="primary", dark=True, children=[
    dbc.NavItem(dbc.NavLink("Climate History", href="/temperature")),
    dbc.NavItem(dbc.NavLink("Biodiversity Insights", href="/biodiversity")),
    dbc.NavItem(dbc.NavLink("Disaster Occurrences", href="/disaster")),
])

# Application Layout
app.layout = html.Main(id='main', children=[
    navbar,
    page_container
])

# Launch the Application
if __name__ == '__main__':
    app.run(debug=True)