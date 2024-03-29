# Setup Folders, Tokens, and Dependencies
from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

class MainApplication:
    def __init__(self):
        self.__app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, 'styles.css'], use_pages=True, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ])
        self.set_layout()

    @property
    def app(self):
        return self.__app
    
    def set_layout(self):
        self.app._favicon = ("icon.svg")

        navbar = dbc.NavbarSimple(className='container-fluid', brand="Klima Insights", brand_href="/", color="primary", dark=True, children=[
            dbc.NavItem(dbc.NavLink("Climate History", href="/temperature")),
            dbc.NavItem(dbc.NavLink("Biodiversity Insights", href="/biodiversity")),
            dbc.NavItem(dbc.NavLink("Disaster Occurrences", href="/disaster")),
        ])

        self.app.layout= html.Main(id='main', children=[
            navbar,
            page_container
        ])

Application = MainApplication()
app = Application.app.server

if __name__ == "__main__":
    Application.app.run(port=8080, dev_tools_ui=True, debug=True, host="127.0.0.1")