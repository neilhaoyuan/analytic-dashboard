import dash
from dash import html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go
import data
from config import ticker_df

dash.register_page(__name__, path='/')  

# App layout
layout = html.Div([
    html.Div("Portfolio Analysis"),

    # Controls
    html.Div([
        dcc.Dropdown(ticker_df["Symbol"], id='ticker-input', value=['AAPL', 'GOOGL', 'NVDA'], multi=True),

        html.Div("Shares Per Stock"),
        dash_table.DataTable(
                id='shares-table',
                editable=True,
                style_cell={'textAlign': 'center'},
                style_header={'fontWeight': 'bold'}),

        dcc.Dropdown(['10 Years', '5 Years', '2 Years', '1 Year', 'Year To Date', '6 Months',
                      '3 Months', '1 Month', '5 Days', '1 Day'],
                     id='period-select-dropdown', value='1 Year', multi=False),

        dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours',
                      '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                     id='interval-select-dropdown', value='1 Day', multi=False),

        html.Div(id='percent-change-label', style={"fontSize": "20px", "fontWeight": "bold"}),
    ]),

    # Plotting line, candle
    html.Div([
        html.Div([
            dcc.Graph(id='line-graph')], style={'width': '50%', 'display': 'inline-block'}),
            
        html.Div([
            dcc.Dropdown(id='candle-ticker-select', value=None, multi=False),
            dcc.Graph(id='candlestick-graph')], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
    ]),

    # Plotting cumulative graphs and trading volumes
    html.Div([
        html.Div([dcc.Graph(id='cumulative-returns-graph')], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
                    dcc.Dropdown(id='volume-ticker-select', value=None, multi=False, placeholder='Select for volume'),  # ← NEW DROPDOWN
                    dcc.Graph(id='volume-graph')], style={'width': '50%', 'display': 'inline-block'})
    ]),

    # Correlation heatmap and sector breakdown 
    html.Div([
        html.Div([dcc.Graph(id='corr-heatmap')], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='sector-graph')], style={'width': '50%', 'display': 'inline-block'})
    ])
])

@callback(
        Output('interval-select-dropdown', 'options'),
        Output('interval-select-dropdown', 'value'),
        Input('period-select-dropdown', 'value')
)
def update_interval_options(period):
    # Returns valid intervals and a default
    valid_interval = data.get_valid_interval(period)
    default_interval = valid_interval[0]
    return valid_interval, default_interval

@callback(
        Output('shares-table', 'columns'),
        Output('shares-table', 'data'),
        Input('ticker-input', 'value')
)
def update_shares_table(ticker_list):
    
    # No tickers selected
    if not ticker_list:
        return [], []
    
    # Column and row creation, defaults to 100 shares
    columns = [{'name': ticker, 'id': ticker, 'editable': True, 'type': 'numeric'} for ticker in ticker_list]
    data = [{ticker: 100 for ticker in ticker_list}]
    
    return columns, data

@callback(
        Output('line-graph', 'figure'),
        Output('percent-change-label', 'children'),
        Output('candle-ticker-select', 'options'),
        Output('candle-ticker-select', 'value'),
        Output('volume-ticker-select', 'options'),
        Output('volume-ticker-select', 'value'),
        Input('ticker-input', 'value'),
        Input('period-select-dropdown', 'value'),
        Input('interval-select-dropdown', 'value')
)
def update_line_graph(ticker_list, period, interval):
    closes_df, pct_change = data.get_close_data(ticker_list, period, interval)

    # Build percent change label
    if len(ticker_list) == 1:
        pct = pct_change[ticker_list[0]]
        color = "green" if pct >= 0 else "red"
        label = html.Span(f"{ticker_list[0]}: {pct:.2f}%", style={"color": color})
    else:
        label = html.Div([
            html.Div(f"{t}: {pct_change[t]:.2f}%") for t in pct_change
        ])
    
    # Create line graph
    fig = px.line(
        closes_df,
        x=closes_df.index,
        y=closes_df.columns,
        title="Individual Stock Performance"
    )
    
    # Determine candle-stick and volume dropdown
    candle_options = ticker_list
    volume_options = ticker_list

    default_candle = ticker_list[0] if ticker_list else None
    default_volume = ticker_list[0] if ticker_list else None
    
    return fig, label, candle_options, default_candle, volume_options, default_volume

@callback(
    Output('candlestick-graph', 'figure'),
    Input('candle-ticker-select', 'value'),
    Input('period-select-dropdown', 'value'),
    Input('interval-select-dropdown', 'value')
)
def update_candlestick(ticker, period, interval):

    # Empty ticker, no figure generated
    if not ticker:
        return go.Figure()
    
    ohlc_df = data.get_ohlc_data(ticker, period, interval)
    
    fig = go.Figure(go.Candlestick(
        x=ohlc_df.index,
        open=ohlc_df["Open"],
        high=ohlc_df["High"],
        low=ohlc_df["Low"],
        close=ohlc_df["Close"]
    )).update_layout(title=f"Candlestick: {ticker}")
    
    return fig

@callback(
        Output('cumulative-returns-graph', 'figure'),
        Input('ticker-input', 'value'),
        Input('shares-table', 'data'), 
        Input('period-select-dropdown', 'value'),
        Input('interval-select-dropdown', 'value')
)
def update_cumulative_returns(ticker_list, table_data, period, interval):
    shares = table_data[0]
    closes_df, _ = data.get_close_data(ticker_list, period, interval)
    returns_df = data.get_cumulative_returns(closes_df, shares)

    if returns_df.empty:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=returns_df.index,
        y=returns_df['Portfolio Value'],
        line=dict(color='#17becf', width=2),
        fill='tozeroy',
        fillcolor="#c0e6ea"
    )).update_layout(
        title='Cumulative Portfolio Returns',
        xaxis_title='Date',
        yaxis_title='Portfolio Value ($)')
    
    return fig

@callback(
    Output('volume-graph', 'figure'),
    Input('volume-ticker-select', 'value'),
    Input('period-select-dropdown', 'value'),
    Input('interval-select-dropdown', 'value')
)
def update_volume_graph(ticker, period, interval):
    volume = data.get_volume_data(ticker, period, interval)

    # Empty ticker, no figure generated
    if volume.empty:
        return go.Figure()
    
    volume = data.get_volume_data(ticker, period, interval)

    fig = go.Figure(go.Bar(x=volume.index, y=volume)).update_layout(title=f"Trading Volume Per Day")
    
    return fig

@callback(
    Output('corr-heatmap', 'figure'),
    Input('ticker-input', 'value'),
    Input('period-select-dropdown', 'value'),
    Input('interval-select-dropdown', 'value')
)
def update_heatmap(ticker_list, period, interval):

    # Empty or not enough tickers
    if not ticker_list or len(ticker_list) < 2:
        return go.Figure()
    
    closes_df, _ = data.get_close_data(ticker_list, period, interval)
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
        textfont={"size": 10}
    )).update_layout(title='Correlation Matrix')

    return fig

@callback(
    Output('sector-graph', 'figure'),
    Input('ticker-input', 'value'),
)
def update_sector_graph(ticker_list):
    if not ticker_list:
        return go.Figure()
    
    sector_df = data.get_sector_info(ticker_list)
    sector_counts = sector_df.groupby('Sector').size().reset_index(name='Count')

    fig = go.Figure(data=[go.Pie(
        labels=sector_counts['Sector'],
        values=sector_counts['Count'],
        hole=0.3,
        textinfo='label+percent'
    )]).update_layout(
        title='Portfolio Sector Breakdown',
        showlegend=True)
    
    return fig