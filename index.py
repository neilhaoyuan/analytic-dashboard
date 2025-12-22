from dash import html, dcc
from app import app
import dash
import dash_bootstrap_components as dbc


app.layout = dbc.Container([
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("Market Analysis Dashboard", href="/", className="ms-2"),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Portfolio", href="/")),
                dbc.NavItem(dbc.NavLink("Market", href="/market")),
                dbc.NavItem(dbc.NavLink("Sectors", href="/sectors")),
            ], className="ms-auto", navbar=True),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    ),
    
    dash.page_container
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)