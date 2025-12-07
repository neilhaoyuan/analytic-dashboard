from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import data

# Initialize the app
app = Dash()

ticker_df = pd.read_csv("total_tickers.csv")

# App layout
app.layout = html.Div([
    html.Div("Neil's Dashboard"),

    html.Div([
        dcc.Dropdown(['Basic', 'Candlestick'], id='graph-type', value='Basic', multi=False),

        dcc.Dropdown(ticker_df["Symbol"], id='ticker-input', value=['AAPL'], multi=True),

        html.Div(id='display-ticker-list'),

        dcc.Dropdown(['10 Years', '5 Years', '2 Years', '1 Year', 'Year To Date', '6 Months',
                      '3 Months', '1 Month', '5 Days', '1 Day'],
                     id='period-select-dropdown', value='1 Year', multi=False),

        dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours',
                      '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                     id='interval-select-dropdown', value='1 Day', multi=False),

        html.Div(id="percent-change-label", style={"fontSize": "20px", "fontWeight": "bold"}),

        dcc.Graph(id='stock-graph')
    ])
])

@callback(
        Output('interval-select-dropdown', 'options'),
        Output('interval-select-dropdown', 'value'),
        Input('period-select-dropdown', 'value'),)
def update_interval_options(period):
    # Returns valid intervals and a default
    valid_interval = data.get_valid_interval(period)
    default_interval = valid_interval[0]
    return valid_interval, default_interval

@callback(
        Output('stock-graph', 'figure'),
        Output('percent-change-label', 'children'),
        Input('ticker-input', 'value'),
        Input('period-select-dropdown', 'value'),
        Input('interval-select-dropdown', 'value'),
        Input('graph-type', 'value'))
def update_graph(ticker_list, period, interval, type):
    closes_df, pct_change = data.get_close_data(ticker_list, period, interval)

    # Build percent change label
    if len(ticker_list) == 1:
        pct = list(pct_change.values())[0]
        color = "green" if pct >= 0 else "red"
        label = html.Span(f"{pct:.2f}%", style={"color": color})
    else:
        label = html.Div([
            html.Div(f"{t}: {pct_change[t]:.2f}%") for t in pct_change
        ])

    # Basic multi-line graph
    if type == "Basic":
        fig = px.line(
            closes_df,
            x=closes_df.index,
            y=closes_df.columns,
            title=", ".join(ticker_list)
        )
        return fig, label

    # Candlestick graph
    if type == "Candlestick":
        if len(ticker_list) != 1:
            return go.Figure(), "Candlestick only works with a single ticker."
        
        ohlc_df = data.get_ohlc_data(ticker_list[0], period, interval)

        fig = go.Figure(go.Candlestick(
            x=ohlc_df.index,
            open=ohlc_df["Open"],
            high=ohlc_df["High"],
            low=ohlc_df["Low"],
            close=ohlc_df["Close"]
        ))
        fig.update_layout(title=ticker_list[0])
        return fig, label

    return go.Figure(), label

# Run the app
if __name__ == '__main__':
    app.run(debug=True)