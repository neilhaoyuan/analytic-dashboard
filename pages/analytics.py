import dash
from dash import html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import data, tech
from utils.config import ticker_df

dash.register_page(__name__, path='/')  

layout = dbc.Container([
    # Ticker, period, and interval select dropdowns
    dbc.Row([
        dbc.Col([
            html.Label("Select Ticker"),
            dcc.Dropdown(ticker_df["Symbol"], 
                         id='ana-ticker-input', 
                         value='AAPL', 
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
                        id='ana-interval-select-dropdown', value='5 Minutes', multi=False)], width=4)
    ], className='mb-3'),

    dbc.Row([dcc.Graph(id='vwap-graph', style={'height': '75vh'})]),

    dbc.Row([dcc.Graph(id='volume-profile', style={'height': '75vh'})]),

    dbc.Row([dcc.Graph(id='rolling-vol', style={'height': '50vh'})]),

    dbc.Row([dcc.Graph(id='rolling-beta', style={'height': '50vh'})]),
])

@callback(
        Output('ana-interval-select-dropdown', 'options'),
        Output('ana-interval-select-dropdown', 'value'),
        Input('ana-period-select-dropdown', 'value'),
        Input('ana-interval-select-dropdown', 'value')
)
# Returns valid intervals and a default interval based on the user selected period
def update_analytic_interval_options(period, interval):
    valid_interval = data.get_valid_interval(period)
    if interval in valid_interval:
        return valid_interval, interval
    else:
        return valid_interval, valid_interval[0]

@callback(
    [Output('vwap-graph', 'figure'),
     Output('volume-profile', 'figure'),
     Output('rolling-vol', 'figure'),
     Output('rolling-beta', 'figure')],
    [Input('ana-ticker-input', 'value'),
     Input('ana-period-select-dropdown', 'value'),
     Input('ana-interval-select-dropdown', 'value')]
)
def update_graphs(ticker, period, interval):
    ohlc_df = data.get_ohlc_data(ticker, period, interval)
    if ohlc_df.empty:
        empty_fig = go.Figure()
        return empty_fig, empty_fig, empty_fig, empty_fig
    
    """
    VWAP Graph
    """
    # Getting base info
    vwap_df = tech.get_intraday_vwap(ohlc_df)
    vwap_df = tech.detect_vwap_events(vwap_df)
    snapback_points = vwap_df[vwap_df['VWAP Event'] == True]

    vwap_fig = go.Figure()

    """
    Volume Profile
    """
    profile_df = tech.get_volume_profile(ohlc_df, num_bins=50)
    profile_info = tech.get_profile_info(profile_df)
    
    vol_profile_fig = go.Figure()
    
    # Build horizontal bar chart
    vol_profile_fig.add_trace(go.Bar(
        y=profile_df['Avg Price'],
        x=profile_df['Total Volume'],
        orientation='h',
        name='Volume',
        marker=dict(color='darkblue'),
    ))
    
    # Add POC line
    vol_profile_fig.add_hline(
        y=profile_info['POC'],
        line_dash='dash',
        line_color='red',
        line_width=2,
        annotation_text=f"POC: ${profile_info['POC']:.2f}",
        annotation_position="right"
    )
    
    # Add Value Area
    vol_profile_fig.add_hrect(
        y0=profile_info['Value Area Low'],
        y1=profile_info['Value Area High'],
        fillcolor='lightblue',
        opacity=0.2,
        line_width=0,
    )
    
    # Add high volume nodes as horizontal lines
    for i in profile_info['High Volume Nodes']:
        vol_profile_fig.add_hline(
            y=i,
            line_dash='dot',
            line_color='yellow',
            line_width=1.5,
            opacity=0.7
    )

    # Update plot layout
    vol_profile_fig.update_layout(
        title=f'{ticker} - Volume Profile',
        xaxis_title='Total Volume',
        yaxis_title='Price ($)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='#1e1e1e',
        font={'color': 'white'},
        showlegend=False,
    )
    
    """
    Rolling volatility
    """    
    vol_df = tech.get_realized_volatility(ohlc_df, interval)
    
    rolling_vol_fig = go.Figure()
    
    # Build scatterplot with lines 
    rolling_vol_fig.add_trace(go.Scatter(
        x=vol_df.index,
        y=vol_df['Annualized Volatility'],
        mode='lines',
        name='Annualized Volatility',
        line=dict(color='orange', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 165, 0, 0.2)',
    ))
    
    # Update plot with names
    rolling_vol_fig.update_layout(
        title=f'{ticker} - Rolling Realized Volatility',
        xaxis_title='Date',
        yaxis_title='Annualized Volatility (%)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='#1e1e1e',
        font={'color': 'white'},
        showlegend=False
    )
    
    """
    Rolling Beta
    """
    # Get S&P 500 benchmark data
    benchmark_df = data.get_ohlc_data('^GSPC', period, interval)
    rolling_beta_series = tech.get_rolling_beta(ohlc_df, benchmark_df)
    
    rolling_beta_fig = go.Figure()
    
    # Add trace of scatterplot, connected with lines
    rolling_beta_fig.add_trace(go.Scatter(
        x=rolling_beta_series.index,
        y=rolling_beta_series,
        mode='lines',
        name='Rolling Beta',
        line=dict(color='purple', width=2),
        fill='tonexty',
        fillcolor='rgba(128, 0, 128, 0.2)',
    ))
    
    # Add horizontal line at beta = 1
    rolling_beta_fig.add_hline(
        y=1.0,
        line_dash='dash',
        line_color='white',
        line_width=2,
        annotation_text="β = 1.0",
        annotation_position="right"
    )
    
    # Update layout with info
    rolling_beta_fig.update_layout(
        title=f'{ticker} - Rolling Beta vs S&P 500',
        xaxis_title='Date',
        yaxis_title='Beta (β)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='#1e1e1e',
        font={'color': 'white'},
        showlegend=False
    )
    
    return vwap_fig, vol_profile_fig, rolling_vol_fig, rolling_beta_fig

    