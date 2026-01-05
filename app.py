import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
from flask_caching import Cache
from flask import Flask

server = Flask(__name__)

cache = Cache(server, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 900
})

app = Dash(__name__, 
           server=server,
           use_pages=True, 
           suppress_callback_exceptions=True, 
           external_stylesheets=[dbc.themes.DARKLY])

sidebar = html.Div(
    [
        html.H2("Market Analysis Dashboard", className="sidebar-title"),
        html.Hr(),
        dbc.Nav(    
            [
                dbc.NavItem(dbc.NavLink("Analytic Charts", href="/")),
                dbc.NavItem(dbc.NavLink("Stock Portfolio", href="/portfolio")),
                dbc.NavItem(dbc.NavLink("Broad Market", href="/market")),
                dbc.NavItem(dbc.NavLink("Sector Performance", href="/sectors")),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className='sidebar',
)

content = html.Div(
    dash.page_container,
    className="content"
)

app.layout = html.Div([sidebar, content])

if __name__ == '__main__':
    app.run(debug=True)