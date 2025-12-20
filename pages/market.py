import dash
from dash import html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import data
from config import ticker_df

dash.register_page(__name__, href='/market')

# App layout
layout = html.Div()