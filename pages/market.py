import dash
from dash import html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from utils import data
from utils.config import market_map

dash.register_page(__name__, href='/market')

layout = dbc.Container([
    html.H2("Broad Market Analysis"),

    # Controls
    dbc.Row([
        dbc.Col([
            html.Label("Select Period"),
            dcc.Dropdown(['10 Years', '5 Years', '2 Years', '1 Year', 'Year To Date', '6 Months',
                        '3 Months', '1 Month', '5 Days', '1 Day'],
                        id='market-period-select-dropdown', value='1 Year', multi=False, style={'color': 'black'})], width=6),

        dbc.Col([
            html.Label("Select Interval"),
            dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours',
                        '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                        id='market-interval-select-dropdown', value='1 Day', multi=False, style={'color': 'black'})], width=6)
    ], className='mb-4'),

    # Creating tabs 
    dbc.Tabs([
        dbc.Tab(label='Charts', tab_id='market-charts'),
        dbc.Tab(label='Summary', tab_id='market-summary')
    ], id='market-tabs'),
    
    dbc.Spinner([
        html.Div(id="market-content", className="p-4"),
        ],delay_show=100),
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
        Output('market-content', 'children'),
        Input('market-tabs', 'active_tab')
)
def render_market_content(active_tab):
    if active_tab == 'market-summary':
        return [
            dbc.Row([
            #Summary
            html.Label("Market Summary"),    
            dbc.Col(html.Div(id='market-table'), width=12)
            ], className='mb-5'),

            dbc.Row([
                html.Label("Recent Market News"),

                dbc.Col([
                    html.Div(
                        id='market-news-cards', 
                        style={
                            'display': 'flex',
                            'overflowX': 'scroll',
                            'overflowY': 'hidden',
                            'whiteSpace': 'nowrap',
                            'padding': '10px 0'})
                    ], width=12),
            ],className='mb-3')
        ]
    elif active_tab == 'market-charts':
        return [
            dbc.Row([
                dbc.Col(dcc.Graph(id='smp500-graph', style={'height': '50vh'}), width=6),

                dbc.Col(dcc.Graph(id='nasdaq-graph', style={'height': '50vh'}), width=6),
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id='smp-tsx-graph', style={'height': '50vh'}), width=6),

                dbc.Col(dcc.Graph(id='russel-2k-graph', style={'height': '50vh'}), width=6),
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id='volatility-graph', style={'height': '50vh'}), width=6),

                dbc.Col(dcc.Graph(id='gold-graph', style={'height': '50vh'}), width=6),
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id='us-dollar-graph', style={'height': '50vh'}), width=6),

                dbc.Col(dcc.Graph(id='cad-dollar-graph', style={'height': '50vh'}), width=6),
            ]),

                
            dbc.Row([
                dbc.Col(dcc.Graph(id='5y-treasury-yield-graph', style={'height': '50vh'}), width=6),

                dbc.Col(dcc.Graph(id='30y-treasury-yield-graph', style={'height': '50vh'}), width=6),
            ])
        ]

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

@callback(
        Output('market-table', 'children'),
        Input('market-period-select-dropdown', 'value'),
        Input('market-interval-select-dropdown', 'value')
)
def update_sector_summary(period, interval):
    summary_df = data.get_summary_table(['^GSPC', '^IXIC', '^RUT', '^GSPTSE', '^VIX', 'GC=F', 'DX-Y.NYB', '^XDC', '^FVX', '^TYX'], None, period, interval, False)

    summary_df['Ticker'] = summary_df['Ticker'].replace(market_map)

    return dbc.Table.from_dataframe(summary_df, striped=True, bordered=True, hover=True)

@callback(
        Output('market-news-cards', 'children'),
        Input('market-period-select-dropdown', 'value'),
        Input('market-interval-select-dropdown', 'value')
)
def update_market_news_cards(period, interval):    
    news_df = data.get_news(['^GSPC', '^IXIC', '^RUT', '^GSPTSE', '^VIX', 'GC=F', 'DX-Y.NYB', '^XDC', '^FVX', '^TYX'], 1)
    
    news_cards = []
    for i, article in news_df.iterrows():
        card = dbc.Card(
            html.A(
                [
                    dbc.CardImg(src=article['image']),
                    dbc.CardBody(html.P(article['title'], 
                                        className="card-text",
                                        style={
                                                'lineHeight': '1.4',
                                                'whiteSpace': 'normal',
                                                'wordBreak': 'break-word',
                                                'overflowWrap': 'break-word',})),
                ],
                href=article['link'],
                target='_blank',
                style={"textDecoration": "none", "color": "inherit"}
            ), style={                'minWidth': '280px',
                'maxWidth': '280px',
                'height': '260px',
                'marginRight': '15px',
                'flex': '0 0 auto',
                'backgroundColor': '#2d2d2d'}
        )
        news_cards.append(card)
    
    return news_cards
