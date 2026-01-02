import dash
from dash import html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import data
from utils.config import ticker_df

dash.register_page(__name__, path='/')  

# App layout
layout = dbc.Container([
    dcc.Store(id='close-data-storage'),

    html.H2("Portfolio Analysis"),

    # Portfolio stock dropdown, pulls from dataframe of scraped tickers
    dbc.Row([
        dbc.Col([
            html.Label("Select Tickers"),
            dcc.Dropdown(ticker_df["Symbol"], 
                         id='ticker-input', 
                         value=['AAPL', 'GOOGL', 'NVDA'], 
                         multi=True, 
                         style={'backgroundColor': "#28346E", 'color': 'white'},),
        ], width=12)
    ], className='mb-3'),

    # Produces datatable where user can input stock shares bought
    dbc.Row([
        dbc.Col([
            html.Label("Shares Per Stock"),
            dash_table.DataTable(id='shares-table',
                            editable=False,
                            style_cell={'textAlign': 'center',
                                        'backgroundColor': '#2d2d2d',
                                        'color': 'white'},
                            style_header={'fontWeight': 'bold',
                                          'backgroundColor': '#1a1a1a',
                                          'color' : 'white'})], width=12)
    ], className='mb-3'),

    # Interval and period selection dropdown controls
    dbc.Row([
        dbc.Col([
            html.Label("Select Period"),
            dcc.Dropdown(['10 Years', '5 Years', '2 Years', '1 Year', 'Year To Date', '6 Months',
                        '3 Months', '1 Month', '5 Days', '1 Day'],
                        id='period-select-dropdown', value='1 Year', multi=False)], width=6),

        dbc.Col([
            html.Label("Select Interval"),
            dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours',
                        '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                        id='interval-select-dropdown', value='1 Day', multi=False)], width=6)
    ], className='mb-4'),

    # Tabs that allow user to switch between showing the charts and the summary page
    dbc.Tabs([
        dbc.Tab(label='Charts', tab_id='charts'),
        dbc.Tab(label='Summary', tab_id='summary')
    ], id='portfolio-tabs'),
    
    # A horizontally scrollable element that shows news content
    dbc.Spinner([
        html.Div(id="tab-content", className="p-4"),
        ],delay_show=100),
], fluid=True)

@callback(
        Output('interval-select-dropdown', 'options'),
        Output('interval-select-dropdown', 'value'),
        Input('period-select-dropdown', 'value')
)
# Returns valid intervals and a default interval based on the user selected period
def update_interval_options(period):
    valid_interval = data.get_valid_interval(period)
    default_interval = valid_interval[0]
    return valid_interval, default_interval

@callback(
        Output('shares-table', 'columns'),
        Output('shares-table', 'data'),
        Input('ticker-input', 'value')
)
# Callback that updates the share table with any newly inputted shares, this relcalculates many things 
def update_shares_table(ticker_list):
    
    # No tickers selected
    if not ticker_list:
        return [], []
    
    # Column and row creation, defaults to 100 shares
    columns = [{'name': ticker, 'id': ticker, 'editable': True, 'type': 'numeric'} for ticker in ticker_list]
    data = [{ticker: 100 for ticker in ticker_list}]
    
    return columns, data

@callback(
        Output('tab-content', 'children'),
        Input('portfolio-tabs', 'active_tab')
)
# Determines which tab the user selected to be in, i.e. charts or summary tab, and displays corresponding information
def render_tab_content(active_tab):

    # If the selected tab is the summary tab, display the summary table and related news articles
    if active_tab == 'summary':
        return [
            dbc.Row([
            html.Label("Portfolio Summary*"),

            dbc.Col(html.Div(id='summary-table'), width=12),

            html.Label("*All metrics are based on selected period and intervals, i.e. Average % Return is based on the given interval (e.g. Average Hourly/Daily % Return), etc."),
            ], className='mb-5'),

            dbc.Row([
                html.Label("Recent Related News"),

                dbc.Col([
                    html.Div(
                        id='news-cards', 
                        style={
                            'display': 'flex',
                            'overflowX': 'scroll',
                            'overflowY': 'hidden',
                            'whiteSpace': 'nowrap',
                            'padding': '10px 0'})
                    ], width=12),
            ], className='mb-3')
        ]
    
    # If the selected tab is the charts tab, display all  figures
    elif active_tab == 'charts':
        return [
            # Plotting line, cumulative returns
            dbc.Row([
                dbc.Col(dcc.Graph(id='line-graph', style={'height': '50vh'}), width=6),
                    
                dbc.Col(dcc.Graph(id='cumulative-returns-graph', style={'height': '50vh'}), width=6),
            ]),

            # Plotting candle graphs and trading volumes
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='candle-ticker-select', value=None, multi=False),
                    dcc.Graph(id='candlestick-graph', style={'height': '50vh'})], width=6),
                
                dbc.Col([
                    dcc.Dropdown(id='volume-ticker-select', value=None, multi=False, placeholder='Select for volume'),
                    dcc.Graph(id='volume-graph', style={'height': '50vh'})], width=6)
            ]),

            # Correlation heatmap and sector breakdown 
            dbc.Row([
                dbc.Col(dcc.Graph(id='corr-heatmap', style={'height': '50vh'}), width=6),

                dbc.Col(dcc.Graph(id='sector-graph', style={'height': '50vh'}), width=6)
            ])
        ]

@callback(
        Output('close-data-storage', 'data'),
        Input('ticker-input', 'value'),
        Input('period-select-dropdown', 'value'),
        Input('interval-select-dropdown', 'value')
)
# Callback that gets and stores the close data of the user chosen ticker list, used to prevent having to do yFinance calls multiple times
def get_and_store_data(ticker_list, period, interval):
    closes_df = data.get_close_data(ticker_list, period, interval)
    closes_dict = closes_df.to_dict('split')
    
    return closes_dict

@callback(
        Output('line-graph', 'figure'),
        Output('candle-ticker-select', 'options'),
        Output('candle-ticker-select', 'value'),
        Output('volume-ticker-select', 'options'),
        Output('volume-ticker-select', 'value'),
        Input('close-data-storage', 'data'),
        Input('ticker-input', 'value')
)
# Callback that plots the line graph against government close or end
def update_line_graph(closes_dict, ticker_list):
    closes_df = pd.DataFrame(closes_dict['data'], index=closes_dict['index'], columns=closes_dict['columns'])
    closes_df.index = pd.to_datetime(closes_df.index, utc=True)

    # Create line graph
    fig = px.line(
        closes_df,
        x=closes_df.index,
        y=closes_df.columns,
        title="Individual Stock Performance",
    ).update_layout(        
        xaxis_title=None,
        yaxis_title='Value ($)',
        paper_bgcolor='rgba(0, 0, 0, 0)', 
        plot_bgcolor='#1e1e1e',
        font={'color': 'white'})
    
    # Determine candle-stick and volume dropdown
    candle_options = ticker_list
    volume_options = ticker_list

    default_candle = ticker_list[0] if ticker_list else None
    default_volume = ticker_list[0] if ticker_list else None
    
    return fig, candle_options, default_candle, volume_options, default_volume

@callback(
    Output('candlestick-graph', 'figure'),
    Input('candle-ticker-select', 'value'),
    Input('period-select-dropdown', 'value'),
    Input('interval-select-dropdown', 'value')
)
# Callback that generates a candlestick graph
def update_candlestick(ticker, period, interval):

    # Empty ticker, no figure generated
    if not ticker:
        return go.Figure()
    
    ohlc_df = data.get_ohlc_data(ticker, period, interval)
    fig = data.create_candlestick_graph(ohlc_df, f"Candlestick: {ticker}")
    
    return fig

@callback(
        Output('cumulative-returns-graph', 'figure'),
        Input('close-data-storage', 'data'),
        Input('shares-table', 'data')
)
# Callback that builds the cumulative returns graph
def update_cumulative_returns(closes_dict, table_data):
    closes_df = pd.DataFrame(closes_dict['data'], index=closes_dict['index'], columns=closes_dict['columns'])
    closes_df.index = pd.to_datetime(closes_df.index, utc=True)
    
    shares = table_data[0]
    returns_df = data.get_cumulative_returns(closes_df, shares)

    if returns_df.empty:
        return go.Figure()
    
    # Builds figure with trace to add dimension
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=returns_df.index,
        y=returns_df['Portfolio Value'],
        line=dict(color='#399391', width=2),
        fill='tozeroy',
        fillcolor="#529A98",
    )).update_layout(
        title='Cumulative Portfolio Returns',
        xaxis_title=None,
        yaxis_title='Portfolio Value ($)',
        paper_bgcolor='rgba(0, 0, 0, 0)', 
        plot_bgcolor='#1e1e1e',
        font={'color': 'white'})
    
    return fig

@callback(
    Output('volume-graph', 'figure'),
    Input('volume-ticker-select', 'value'),
    Input('period-select-dropdown', 'value'),
    Input('interval-select-dropdown', 'value')
)
# Callback that builds and updates a ticker's volume graph
def update_volume_graph(ticker, period, interval):
    volume = data.get_volume_data(ticker, period, interval)

    # Empty ticker, no figure generated
    if volume.empty:
        return go.Figure()
    
    fig = go.Figure(go.Bar(x=volume.index, y=volume)).update_layout(
        title=f"Trading Volume Per Day", 
        paper_bgcolor='rgba(0, 0, 0, 0)', 
        plot_bgcolor='#1e1e1e',
        font={'color': 'white'})
    
    return fig

@callback(
    Output('corr-heatmap', 'figure'),
    Input('close-data-storage', 'data'),
    Input('ticker-input', 'value'),
)
# Callback that builds the correlation heatmap, only works if tickers amount > 2
def update_heatmap(closes_dict, ticker_list):

    # Empty or not enough tickers
    if not ticker_list or len(ticker_list) < 2:
        return go.Figure()
    
    closes_df = pd.DataFrame(closes_dict['data'], index=closes_dict['index'], columns=closes_dict['columns'])
    closes_df.index = pd.to_datetime(closes_df.index, utc=True)
    closes_df.index = closes_df.index.tz_localize(None)

    # Finds correlation matrix
    weekly_close = data.get_weekly_close(closes_df)
    corr_matrix = data.get_correlation_data(weekly_close)

    fig = go.Figure(data=go.Heatmap(
        x=corr_matrix.columns,
        y=corr_matrix.index,
        z=corr_matrix.values,
        colorscale='RdBu_r',
        zmin=-1,
        zmax=1,
        zmid=0,
        texttemplate='%{z:.2f}',
        textfont={"size": 10},
        showscale=False
    )).update_layout(title='Correlation Matrix', 
                     paper_bgcolor='rgba(0, 0, 0, 0)', 
                     font={'color': 'white'})

    return fig

@callback(
    Output('sector-graph', 'figure'),
    Input('ticker-input', 'value'),
)
# Determines sector breakdown of a portfolio
def update_sector_graph(ticker_list):
    if not ticker_list:
        return go.Figure()
    
    sector_df = data.get_sector_info(ticker_list)

    # Creates a dataframe that consists of: Sectors, Count of that sector, Companies in that sector
    sector_counts = sector_df.groupby('Sector').size().reset_index(name='Count')
    sector_companies = sector_df.groupby('Sector')['Ticker'].agg(', '.join).reset_index()
    sector_companies.columns = ['Sector', 'Companies']
    sector_data = sector_counts.merge(sector_companies, on='Sector')

    fig = go.Figure(data=[go.Pie(
        labels=sector_data['Sector'],
        values=sector_data['Count'],
        hole=0.3,
        textinfo='label+percent',
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Count: %{value}<br>'
            'Companies: %{customdata}<br>'
            '<extra></extra>'),
        customdata=sector_data['Companies']
    )]).update_layout(
        title='Portfolio Sector Breakdown',
        showlegend=False,
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font={'color': 'white'})
    
    return fig

@callback(
        Output('summary-table', 'children'),
        Input('ticker-input', 'value'),
        Input('shares-table', 'data'),
        Input('period-select-dropdown', 'value'),
        Input('interval-select-dropdown', 'value')
)
# Callback that updates the portfolio summary table using data from the user-selected period and intervals
def update_summary_table(ticker_list, table_data, period, interval):
    
    # No tickers selected
    if not ticker_list:
        return [], []
    
    shares = table_data[0]
    summary_df = data.get_summary_table(ticker_list, shares, period, interval, True)

    if summary_df.empty:
        return html.Div()

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
        Output('news-cards', 'children'),
        Input('ticker-input', 'value')
)
# Callback that builds the news cards of all the portfolio tickers
def update_news_cards(ticker_list):
    if not ticker_list:
        return html.Div("Select tickers to see news", className="text-center p-4")
    
    news_df = data.get_news(ticker_list, 3)

    if news_df.empty:
        return html.Div("No news available", className="text-center p-4")
    
    news_cards = []
    for i, article in news_df.iterrows():
        card = dbc.Card(
            html.A(
                [
                    dbc.CardImg(src=article['image'],
                                style={
                                    'height': '150px',
                                    'width': '100%'
                                }),
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
