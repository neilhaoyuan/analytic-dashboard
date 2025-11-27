# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
from data import get_stock_data

# Initialize the app
app = Dash()

# App layout
app.layout = [html.Div('Testing'),
              html.Div([dcc.Input(placeholder='Enter a valid ticker...',type='text',value='^GSPC', id='ticker-input'),
                        dcc.Dropdown(['10 Years', '5 Years', '2 Years', '1 Year', 'Year To Date', '6 Months', '3 Months', '1 Month', '5 Days', '1 Day'],
                                     value = '1 Year', id='period-select-dropdown', multi=False),
                        dcc.Dropdown(['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours', '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
                                     value='1 Day', id='interval-select-dropdown', multi=False),
                        dcc.Graph(id='stock-graph')])]

@callback(
    Output('stock-graph', 'figure'),
    Input('ticker-input', 'value'),
    Input('period-select-dropdown', 'value'),
    Input('interval-select-dropdown', 'value')
)
def update_graph(ticker, period, interval):
    df = get_stock_data(ticker, period, interval)
    fig = px.line(df, x=df.index, y='Close', title=f'{ticker}: {period}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)