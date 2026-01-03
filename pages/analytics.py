import dash
from dash import html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import data
from utils.config import ticker_df

dash.register_page(__name__, path='/')  

layout = dbc.Container([
    # Ticker, period, and interval select dropdowns
    dbc.Row([
        dbc.Col([
            html.Label("Select Ticker"),
            dcc.Dropdown(ticker_df["Symbol"], 
                         id='ana-ticker-input', 
                         value=['AAPL', 'GOOGL', 'NVDA'], 
                         multi=False, 
                         style={'backgroundColor': "#28346E", 'color': 'white'},),], width=4),
        dbc.Col([
            html.Label("Select Period"),
            dcc.Dropdown(['1 Year', 'Year To Date', '6 Months', '3 Months', '1 Month', '5 Days', '1 Day'],
                        id='ana-period-select-dropdown', value='1 Month', multi=False)], width=4),

        dbc.Col([
            html.Label("Select Interval"),
            dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours',
                        '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                        id='ana-nterval-select-dropdown', value='1 Day', multi=False)], width=4)
    ], className='mb-3'),

    dbc.Row([dcc.Graph(id='vwap-graph', style={'height': '50vh'})]),

    dbc.Row([dcc.Graph(id='volume-profile', style={'height': '50vh'})]),

    dbc.Row([dcc.Graph(id='rolling-vol', style={'height': '50vh'})]),

    dbc.Row([dcc.Graph(id='rolling-beta', style={'height': '50vh'})]),
])