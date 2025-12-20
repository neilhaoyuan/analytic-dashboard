import dash
from dash import html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import data

dash.register_page(__name__, href='/sectors')

layout = html.Div([
    html.Div('Sector Specific Analysis'),

    html.Div([
        dcc.Dropdown(['10 Years', '5 Years', '2 Years', '1 Year', 'Year To Date', '6 Months',
                      '3 Months', '1 Month', '5 Days', '1 Day'],
                     id='sector-period-select-dropdown', value='1 Year', multi=False),

        dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours',
                      '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                     id='sector-interval-select-dropdown', value='1 Day', multi=False)
    ]),

    html.Div([
        html.Div([dcc.Graph(id='comm-sector')], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='cons-disc-sector')], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='cons-stap-sector')], style={'width': '33%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='energy-sector')], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='financial-sector')], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='health-sector')], style={'width': '33%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='indust-sector')], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='materials-sector')], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='real-est-sector')], style={'width': '33%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='tech-sector')], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='util-sector')], style={'width': '33%', 'display': 'inline-block'})
    ]),

    html.Div([dcc.Graph(id='sector-corr-heatmap')])
])

@callback(
        Output('comm-sector', 'figure'),
        Output('cons-disc-sector', 'figure'),
        Output('cons-stap-sector', 'figure'),
        Output('energy-sector', 'figure'),
        Output('financial-sector', 'figure'),
        Output('health-sector', 'figure'),
        Output('indust-sector', 'figure'),
        Output('materials-sector', 'figure'),
        Output('real-est-sector', 'figure'),
        Output('tech-sector', 'figure'),
        Output('util-sector', 'figure'),
        Input('sector-period-select-dropdown', 'value'),
        Input('sector-interval-select-dropdown', 'value')
)
def update_index_graphs(period, interval):
    comm_data = data.get_ohlc_data('XLC', period, interval)
    consdisc_data = data.get_ohlc_data('XLY', period, interval)
    consstap_data = data.get_ohlc_data('XLP', period, interval)
    ener_data = data.get_ohlc_data('XLE', period, interval)
    fin_data = data.get_ohlc_data('XLF', period, interval)
    health_data = data.get_ohlc_data('XLV', period, interval)
    indus_data = data.get_ohlc_data('XLI', period, interval)
    mats_data = data.get_ohlc_data('XLB', period, interval)
    reales_data = data.get_ohlc_data('XLRE', period, interval)
    tech_data = data.get_ohlc_data('XLK', period, interval)
    util_data = data.get_ohlc_data('XLU', period, interval)

    comm = data.create_candlestick_graph(comm_data, 'Communications (XLC)')
    consdisc = data.create_candlestick_graph(consdisc_data, 'Consumer Discretionary (XLY)')
    consstap = data.create_candlestick_graph(consstap_data, 'Consumer Staple (XLP)')
    ener = data.create_candlestick_graph(ener_data, 'Energy (XLE)')
    fin = data.create_candlestick_graph(fin_data, 'Financial (XLF)')
    health = data.create_candlestick_graph(health_data, 'Healthcare (XLV)')
    indus = data.create_candlestick_graph(indus_data, 'Industrial (XLI)')
    mats = data.create_candlestick_graph(mats_data, 'Materials (XLB)')
    reales = data.create_candlestick_graph(reales_data, 'Real Estate (XLRE)')
    tech = data.create_candlestick_graph(tech_data, 'Technology (XLK)')
    util = data.create_candlestick_graph(util_data, 'Utilities (XLU)')

    return comm, consdisc, consstap, ener, fin, health, indus, mats, reales, tech, util

