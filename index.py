from dash import html, dcc
from app import app
import dash

app.layout = html.Div([
    html.Div([
        dcc.Link('Portfolio', href='/'),
        dcc.Link('Market', href='/market'),
        dcc.Link('Sectors', href='/sectors'),
        dcc.Link('Custom', href='/custom'),
    ]),
    
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)