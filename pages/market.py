import dash
from dash import html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import data

dash.register_page(__name__, href='/market')

layout = html.Div([
    html.Div('Broad Market Analysis'),

    html.Div([
        dcc.Dropdown(['10 Years', '5 Years', '2 Years', '1 Year', 'Year To Date', '6 Months',
                      '3 Months', '1 Month', '5 Days', '1 Day'],
                     id='market-period-select-dropdown', value='1 Year', multi=False),

        dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours',
                      '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                     id='market-interval-select-dropdown', value='1 Day', multi=False)
    ]),

    html.Div([
        html.Div([dcc.Graph(id='smp500-graph')], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='nasdaq-graph')], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='smp-tsx-graph')], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='russel-2k-graph')], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='volatility-graph')], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='gold-graph')], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='us-dollar-graph')], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='cad-dollar-graph')], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    
    html.Div([
        html.Div([dcc.Graph(id='5y-treasury-yield-graph')], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='30y-treasury-yield-graph')], style={'width': '50%', 'display': 'inline-block'}),
    ])
])

@callback(
        Output('sector-interval-select-dropdown', 'options'),
        Output('sector-interval-select-dropdown', 'value'),
        Input('sector-period-select-dropdown', 'value')
)
def update_market_interval_options(period):
    # Returns valid intervals and a default
    valid_interval = data.get_valid_interval(period)
    default_interval = valid_interval[0]
    return valid_interval, default_interval

@callback(
        Output('smp500-graph', 'figure'),
        Output('nasdaq-graph', 'figure'),
        Output('smp-tsx-graph', 'figure'),
        Output('russel-2k-graph', 'figure'),
        Output('volatility-graph', 'figure'),
        Output('gold-graph', 'figure'),
        Output('us-dollar-graph', 'figure'),
        Output('cad-dollar-graph', 'figure'),
        Output('5y-treasury-yield-graph', 'figure'),
        Output('30y-treasury-yield-graph', 'figure'),
        Input('market-period-select-dropdown', 'value'),
        Input('market-interval-select-dropdown', 'value')
)
def update_market_graphs(period, interval):
    smp500_data = data.get_ohlc_data("^GSPC", period, interval)
    nasdaq_data = data.get_ohlc_data("^IXIC", period, interval)
    russell2k_data = data.get_ohlc_data("^RUT", period, interval)
    smp_tsx_data = data.get_ohlc_data("^GSPTSE", period, interval)
    volatility_data = data.get_ohlc_data("^VIX", period, interval)
    gold_data = data.get_ohlc_data("GC=F", period, interval)
    usd_data = data.get_ohlc_data("DX-Y.NYB", period, interval)
    cad_data = data.get_ohlc_data("^XDC", period, interval)
    five_yo_yield = data.get_ohlc_data("^FVX", period, interval)
    thirty_yo_yield = data.get_ohlc_data("^TYX", period, interval)
    
    smp500 = data.create_candlestick_graph(smp500_data, "S&P 500")
    nasdaq = data.create_candlestick_graph(nasdaq_data, "NASDAQ")
    russell2k = data.create_candlestick_graph(russell2k_data, "Russell 2000")
    smp_tsx = data.create_candlestick_graph(smp_tsx_data, "S&P/TSX Composite")
    volatility = data.create_candlestick_graph(volatility_data, "Volatility Index")
    gold = data.create_candlestick_graph(gold_data, "Gold Price Index")
    usd = data.create_candlestick_graph(usd_data, "US Dollar Index")
    cad = data.create_candlestick_graph(cad_data, "CA Dollar Index")
    five_yo = data.create_candlestick_graph(five_yo_yield, "5 Year US Treasury Yield")
    thirty_yo = data.create_candlestick_graph(thirty_yo_yield, "30 Year US Treasury Yield")

    return smp500, nasdaq, russell2k, smp_tsx, volatility, gold, usd, cad, five_yo, thirty_yo

