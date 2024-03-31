from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

APP_TITLE = "Klima Insights"

app = Dash(__name__,
            title=APP_TITLE,
            update_title='Loading...',
            suppress_callback_exceptions=True,
            use_pages=True,
            external_stylesheets=[dbc.themes.SOLAR, 'styles.css'])