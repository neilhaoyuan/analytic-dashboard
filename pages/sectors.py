import dash
from dash import html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import data

dash.register_page(__name__, href='/sectors')

layout = dbc.Container([
    html.H2("Sector Specific Analysis"),

    # Controls
    dbc.Row([
        dbc.Col([
            html.Label("Select Period"),
            dcc.Dropdown(['10 Years', '5 Years', '2 Years', '1 Year', 'Year To Date', '6 Months',
                        '3 Months', '1 Month', '5 Days', '1 Day'],
                        id='sector-period-select-dropdown', value='1 Year', multi=False, style={'color': 'black'})], width=6),

        dbc.Col([
            html.Label("Select Interval"),
            dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours',
                        '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                        id='sector-interval-select-dropdown', value='1 Day', multi=False, style={'color': 'black'})], width=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='comm-sector', style={'height': '50vh'}), width=4),

        dbc.Col(dcc.Graph(id='cons-disc-sector', style={'height': '50vh'}), width=4),

        dbc.Col(dcc.Graph(id='cons-stap-sector', style={'height': '50vh'}), width=4)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='energy-sector', style={'height': '50vh'}), width=4),

        dbc.Col(dcc.Graph(id='financial-sector', style={'height': '50vh'}), width=4),

        dbc.Col(dcc.Graph(id='health-sector', style={'height': '50vh'}), width=4),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='indust-sector', style={'height': '50vh'}), width=4),

        dbc.Col(dcc.Graph(id='materials-sector', style={'height': '50vh'}), width=4),

        dbc.Col(dcc.Graph(id='real-est-sector', style={'height': '50vh'}), width=4),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='tech-sector', style={'height': '50vh'}), width=4),

        dbc.Col(dcc.Graph(id='util-sector', style={'height': '50vh'}), width=4),
    ], justify="center"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='sector-corr-heatmap', style={'height': '70vh'}), width=8)
    ], justify="center")
], fluid=True)

@callback(
        Output('market-interval-select-dropdown', 'options'),
        Output('market-interval-select-dropdown', 'value'),
        Input('market-period-select-dropdown', 'value')
)
def update_market_interval_options(period):
    # Returns valid intervals and a default
    valid_interval = data.get_valid_interval(period)
    default_interval = valid_interval[0]
    return valid_interval, default_interval

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
        Output('sector-corr-heatmap', 'figure'),
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

    sectors_df = pd.DataFrame({
        'Comms': comm_data['Close'],
        'Cons Disc': consdisc_data['Close'],
        'Cons Staple': consstap_data['Close'],
        'Energy': ener_data['Close'],
        'Financial': fin_data['Close'],
        'Healthcare': health_data['Close'],
        'Industrial': indus_data['Close'],
        'Materials': mats_data['Close'],
        'Real Estate': reales_data['Close'],
        'Technology': tech_data['Close'],
        'Utilities': util_data['Close']
    }).dropna()

    sectors_weekly_close = data.get_weekly_close(sectors_df)
    sectors_corr_matrix = data.get_correlation_data(sectors_weekly_close)

    fig = go.Figure(data=go.Heatmap(
        x=sectors_corr_matrix.columns,
        y=sectors_corr_matrix.index,
        z=sectors_corr_matrix.values,
        colorscale='RdBu_r',
        zmin=-1,
        zmax=1,
        zmid=0,
        texttemplate='%{z:.2f}',
        textfont={"size": 10},
        showscale=False
    )).update_layout(
        title='Sector Correlation Matrix', 
        title_x = 0.1, 
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font={'color': 'white'})

    return comm, consdisc, consstap, ener, fin, health, indus, mats, reales, tech, util, fig