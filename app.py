from dash import Dash
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