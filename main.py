# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import data

# Initialize the app
app = Dash()

# App layout
app.layout = html.Div([
    html.Div("Neil's Dashboard"),

    html.Div([
        dcc.Dropdown(['Basic', 'Candlestick'], id='graph-type', value='Basic', multi=False),

        dcc.Input(id='ticker-input', placeholder='Enter a valid ticker...', type='text', value='AAPL'),

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

#@callback(
#    Output('ticker-store', 'data'),
#    Input('ticker-input', 'value'))
#def add_tickers()


@callback(
    Output('stock-graph', 'figure'),
    Output('percent-change-label', 'children'),
    Input('ticker-input', 'value'),
    Input('period-select-dropdown', 'value'),
    Input('interval-select-dropdown', 'value'),
    Input('graph-type', 'value'))
def update_graph(ticker, period, interval, type):
    df, pct_change = data.get_close_data(ticker, period, interval)
    if pct_change >= 0:
        color = "green"
    else:
        color = "red"
    label = html.Span(f"{pct_change:.2f}%", style={"color": color})

    if (type == 'Basic'):
        fig = px.line(df, x=df.index, y='Close', title=f'{ticker}: {period}')
    elif (type == 'Candlestick'):
        fig = go.Figure(go.Candlestick(
            x = df.index,
            open = df['Open'],
            high = df['High'],
            low = df['Low'],
            close = df['Close']))
    return fig, label

# Run the app
if __name__ == '__main__':
    app.run(debug=True)