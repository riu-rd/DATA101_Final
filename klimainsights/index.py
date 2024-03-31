from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

from app import app
from environment.settings import APP_HOST, APP_PORT, APP_DEBUG

server = app.server

def serve_content():
    navbar = dbc.NavbarSimple(className='container-fluid z-3', brand="Klima Insights", brand_href="/", color="primary", dark=True, children=[
            dbc.NavItem(dbc.NavLink("Climate History", href="/temperature")),
            dbc.NavItem(dbc.NavLink("Biodiversity Insights", href="/biodiversity")),
            dbc.NavItem(dbc.NavLink("Disaster Occurrences", href="/disaster")),
    ])

    return html.Main(id='main', children=[
            html.Div(
                id="leaves",
                children=[
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I(),
                    html.I()
                ]),
            navbar,
            page_container
    ])

app._favicon = ("icon.svg")
app.layout = serve_content()

if __name__ == '__main__':
    app.run_server(debug=APP_DEBUG, host=APP_HOST, port=APP_PORT)