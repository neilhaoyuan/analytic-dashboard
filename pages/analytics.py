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
            dcc.Dropdown(['1 Month', '5 Days', '1 Day'],
                        id='ana-period-select-dropdown', value='1 Month', multi=False)], width=4),

        dbc.Col([
            html.Label("Select Interval"),
            dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour'],
                        id='ana-interval-select-dropdown', value='5 Minutes', multi=False)], width=4)
    ], className='mb-3'),

    dbc.Spinner([
        html.Div(id="analytic-content", className="p-4"),
        ],delay_show=100),
], fluid=True)

@callback(
    Output("analytic-content", "children"),
    Input("ana-ticker-input", "value"),
    Input("ana-period-select-dropdown", "value"),
    Input("ana-interval-select-dropdown", "value"),
)
def render_page(ticker, period, interval):
    return [
        dbc.Row(dcc.Graph(id="vwap-graph", style={"height": "75vh"})),
        dbc.Row(dcc.Graph(id="volume-profile", style={"height": "75vh"})),
        dbc.Row(dcc.Graph(id="rolling-vol", style={"height": "50vh"})),
        dbc.Row(dcc.Graph(id="rolling-beta", style={"height": "50vh"})),
    ]

@callback(
    Output('vwap-graph', 'figure'),
    Output('volume-profile', 'figure'),
    Output('rolling-vol', 'figure'),
    Output('rolling-beta', 'figure'),
    Input('ana-ticker-input', 'value'),
    Input('ana-period-select-dropdown', 'value'),
    Input('ana-interval-select-dropdown', 'value')
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

    # Add candlestick graph (semi-transparent)
    vwap_fig.add_trace(go.Candlestick(
        x=vwap_df.index,
        open=vwap_df['Open'],
        high=vwap_df['High'],
        low=vwap_df['Low'],
        close=vwap_df['Close'],
        name='Price',
    ))

    # Add VWAP line
    vwap_fig.add_trace(go.Scatter(
        x=vwap_df.index,
        y=vwap_df['VWAP'],
        mode='lines',
        name='VWAP',
        line={'color': 'lightblue', 'width': 2},
    ))

    # Add +1 std band
    vwap_fig.add_trace(go.Scatter(
        x=vwap_df.index,
        y=vwap_df['VWAP'] + 2 * vwap_df['VWAP Std'],
        mode='lines',
        line={'width': 0},
        showlegend=False,
        hoverinfo='skip'
    ))

    # Add -1 std band with fill
    vwap_fig.add_trace(go.Scatter(
        x=vwap_df.index,
        y=vwap_df['VWAP'] - 2 * vwap_df['VWAP Std'],
        mode='lines',
        line={'width': 0},
        fill='tonexty',
        fillcolor='rgba(100, 100, 100, 0.15)',
        name='±2σ',
        hoverinfo='skip'
    ))

    # Mark snapback events
    if not snapback_points.empty:
        hover_text = []
        for i in snapback_points.index:
            time = i.strftime('%Y-%m-%d %H:%M')
            price = snapback_points['Close'].loc[i]
            max_z = snapback_points['Max Z Distance'].loc[i]

            hover_text.append(
                f"<b>Snapback</b><br>" +
                f"@ {time}<br>" +
                f"@ ${price:.2f}<br>" +
                f"From {max_z:.1f}σ Away")

        vwap_fig.add_trace(go.Scatter(
            x=snapback_points.index,
            y=snapback_points['Close'],
            mode='markers',
            name='Snapback Event',
            marker={'color': "#ed9511", 'size': 9},
            hovertext=hover_text,
            hoverinfo='text',
            ))

    # Update layout
    vwap_fig.update_layout(
        title=f'{ticker} - VWAP Analysis',
        xaxis_title='',
        yaxis_title='Price ($)',
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='#1e1e1e',
        font={'color': 'white'},
        legend={'x': 0.8, 
                'y': 0.98, 
                'xanchor': 'left', 
                'yanchor': 'top', 
                'bgcolor': 'rgba(0,0,0,0.5)'},
    )

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
        marker={'color': 'darkblue'}
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
        fillcolor='green',
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
        line={'color': 'orange', 'width': 2},
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
        line={'color': 'purple', 'width': 2},
        fill='tozeroy',
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
        title=f'{ticker} - Rolling Beta to S&P 500',
        xaxis_title='Date',
        yaxis_title='Beta (β)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='#1e1e1e',
        font={'color': 'white'},
        showlegend=False
    )
    
    return data.remove_market_gaps(vwap_fig), data.remove_market_gaps(vol_profile_fig), data.remove_market_gaps(rolling_vol_fig), data.remove_market_gaps(rolling_beta_fig)

    