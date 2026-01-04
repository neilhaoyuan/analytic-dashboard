import dash
from dash import html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from utils import data
from utils.config import sector_map

dash.register_page(__name__, href='/sectors')

layout = dbc.Container([
    html.H2("Sector Specific Analysis"),

    # Interval and period selection dropdown controls
    dbc.Row([
        dbc.Col([
            html.Label("Select Period"),
            dcc.Dropdown(['1 Year', 'Year To Date','6 Months', '3 Months', '1 Month', '5 Days', '1 Day'],
                        id='sector-period-select-dropdown', value='1 Month', multi=False, style={'color': 'black'})], width=6),

        dbc.Col([
            html.Label("Select Interval"),
            dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours',
                        '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                        id='sector-interval-select-dropdown', value='1 Day', multi=False, style={'color': 'black'})], width=6)
    ], className='mb-4'),

    # Tabs that allow user to switch between showing the charts and the summary page
    dbc.Tabs([
        dbc.Tab(label='Charts', tab_id='sector-charts'),
        dbc.Tab(label='Summary', tab_id='sector-summary')
    ], id='sector-tabs'),
    
    # A horizontally scrollable element that shows news content
    dbc.Spinner([
        html.Div(id="sector-content", className="p-4"),
        ],delay_show=100),
], fluid=True)

@callback(
        Output('sector-interval-select-dropdown', 'options'),
        Output('sector-interval-select-dropdown', 'value'),
        Input('sector-period-select-dropdown', 'value'),
        Input('sector-interval-select-dropdown', 'value')
)
# Returns valid intervals and a default interval based on the user selected period
def update_sector_interval_options(period, interval):
    valid_interval = data.get_valid_interval(period)
    if interval in valid_interval:
        return valid_interval, interval
    else:
        return valid_interval, valid_interval[0]

@callback(
        Output('sector-content', 'children'),
        Input('sector-tabs', 'active_tab')
)
# Determines which tab the user selected to be in, i.e. charts or summary tab, and displays corresponding information
def render_tab_content(active_tab):

    # If the selected tab is the summary tab, display the summary table and related news articles
    if active_tab == 'sector-summary':
        return [
            dbc.Row([
            html.Label("Sector Summary"),    
            dbc.Col(html.Div(id='sector-table'), width=12)
            ], className='mb-5'),

            dbc.Row([
                html.Label("Recent Sector News"),

                dbc.Col([
                    html.Div(
                        id='sector-news-cards', 
                        style={
                            'display': 'flex',
                            'overflowX': 'scroll',
                            'overflowY': 'hidden',
                            'whiteSpace': 'nowrap',
                            'padding': '10px 0'})
                    ], width=12),
            ], className='mb-3')
        ]
    
    # If the selected tab is the charts tab, display all available sector charts
    elif active_tab == 'sector-charts':
        return [
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
        ]

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
# Callback that updates the market graphs depending on what the user selects as period and interval, returns the chart figures
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

    # Builds individual candlestick charts
    comm = data.create_candlestick_graph(comm_data, 'Communications (XLC)')
    consdisc = data.create_candlestick_graph(consdisc_data, 'Cons Disc (XLY)')
    consstap = data.create_candlestick_graph(consstap_data, 'Cons Staple (XLP)')
    ener = data.create_candlestick_graph(ener_data, 'Energy (XLE)')
    fin = data.create_candlestick_graph(fin_data, 'Financial (XLF)')
    health = data.create_candlestick_graph(health_data, 'Healthcare (XLV)')
    indus = data.create_candlestick_graph(indus_data, 'Industrial (XLI)')
    mats = data.create_candlestick_graph(mats_data, 'Materials (XLB)')
    reales = data.create_candlestick_graph(reales_data, 'Real Estate (XLRE)')
    tech = data.create_candlestick_graph(tech_data, 'Technology (XLK)')
    util = data.create_candlestick_graph(util_data, 'Utilities (XLU)')

    # Dataframe of all sector closes used for weekly calculatiions
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

    # Calculate weekly closes and then correlation matrix 
    sectors_weekly_close = data.get_weekly_close(sectors_df)
    sectors_corr_matrix = data.get_correlation_data(sectors_weekly_close)

    # Build correlation matrix heatmap
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

@callback(
        Output('sector-table', 'children'),
        Input('sector-period-select-dropdown', 'value'),
        Input('sector-interval-select-dropdown', 'value')
)
# Callback that updates the sector summary table using data from the user-selected period and intervals
def update_sector_summary(period, interval):
    summary_df = data.get_summary_table(['XLC', 'XLY', 'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLRE', 'XLK', 'XLU'], None, period, interval, False)
    
    summary_df['Ticker'] = summary_df['Ticker'].replace(sector_map)

    # Builds dashtable, ensures that positive return metrics are colored green, and negative metrics are colored red
    fig = dash_table.DataTable(
        data = summary_df.to_dict('records'),
        columns = [{'name': i, 'id': i} for i in summary_df.columns],
        style_table={'overflowX': 'scroll'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'backgroundColor': '#1e1e1e',
            'color': 'white',
            'border': '1px solid #2d2d2d'},
        style_header={
            'backgroundColor': '#2d2d2d',
            'fontWeight': 'bold',
            'border': '1px solid #3d3d3d',
            'textAlign': 'left'},
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{% Return} < 0',
                    'column_id': '% Return'
                },
                'color': 'red'
            },
            {
                'if': {
                    'filter_query': '{% Return} > 0',
                    'column_id': '% Return'
                },
                'color': 'green'
            },
            {
                'if': {
                    'filter_query': '{Average % Return} < 0',
                    'column_id': 'Average % Return'
                },
                'color': 'red'
            },
            {
                'if': {
                    'filter_query': '{Average % Return} > 0',
                    'column_id': 'Average % Return'
                },
                'color': 'green'
            },
            {
                'if': {
                    'filter_query': '{Average % Return} > 0',
                    'column_id': 'Average % Return'
                },
                'color': 'green'
            }
        ]
    )

    return fig

@callback(
        Output('sector-news-cards', 'children'),
        Input('sector-period-select-dropdown', 'value'),
        Input('sector-interval-select-dropdown', 'value')
)
# Callback that builds the news cards of all the sector indices 
def update_sector_news_cards(period, interval):    
    news_df = data.get_news(['XLC', 'XLY', 'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLRE', 'XLK', 'XLU'], 1)
    
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
