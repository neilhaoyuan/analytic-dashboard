from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])
server = app.server