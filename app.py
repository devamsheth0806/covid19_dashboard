import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import datetime

app = dash.Dash(__name__)
app.title = 'Covid-19 Dashboard'

server = app.server

# Colors for styling
colors = {
    'background': '#2D2D2D',
    'text': '#E1E2E5',
    'confirmed_text': '#3CA4FF',
    'deaths_text': '#f44336',
    'recovered_text': '#81FF33',
    'active_text': '#f1f772',
}

# Data URLs
url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

# Read Data
df_confirmed = pd.read_csv(url_confirmed)
df_deaths = pd.read_csv(url_deaths)
df_recovered = pd.read_csv(url_recovered)

# Process Data
df_confirmed_total = df_confirmed.iloc[:, 4:].sum(axis=0)
df_deaths_total = df_deaths.iloc[:, 4:].sum(axis=0)
df_recovered_total = df_recovered.iloc[:, 4:].sum(axis=0)

df_deaths_confirmed = df_deaths.copy()
df_deaths_confirmed['confirmed'] = df_confirmed.iloc[:, -1]

# Align `df_deaths_t` and `df_recovered_t` with `df_confirmed_t`
df_deaths_t = df_deaths.reindex(df_confirmed.index)
df_recovered_t = df_recovered.reindex(df_confirmed.index)

# Fix misalignment of `df_active_t`
df_active_t = df_confirmed_total.subtract(df_deaths_total.add(df_recovered_total))
df_active_t.clip(lower=0, inplace=True)

# Fix `.str.split()` issue
df_confirmed_t.columns = df_confirmed_t.columns.astype(str).str.split("|", n=1)

# Ensure consistent indexing
df_confirmed_t.index = pd.to_datetime(df_confirmed_t.index)
df_deaths_t.index = pd.to_datetime(df_confirmed_t.index)
df_recovered_t.index = pd.to_datetime(df_confirmed_t.index)

# Dash App Layout
app.layout = html.Div([
    html.H1('Covid-19 Dashboard', style={'textAlign': 'center', 'color': colors['text']}),

    html.Div([
        html.Div([
            html.H4('Total Cases', style={'color': colors['confirmed_text']}),
            html.P(f"{df_confirmed_total[-1]:,d}", style={'color': colors['confirmed_text'], 'fontSize': 30}),
            html.P('Past 24hrs increase: +' + f"{df_confirmed_total[-1] - df_confirmed_total[-2]:,d}")
        ], className='three columns'),

        html.Div([
            html.H4('Active Cases', style={'color': colors['active_text']}),
            html.P(f"{df_active_t[-1]:,d}", style={'color': colors['active_text'], 'fontSize': 30}),
            html.P('Past 24hrs increase: +' + f"{df_active_t[-1] - df_active_t[-2]:,d}")
        ], className='three columns'),

        html.Div([
            html.H4('Total Deaths', style={'color': colors['deaths_text']}),
            html.P(f"{df_deaths_total[-1]:,d}", style={'color': colors['deaths_text'], 'fontSize': 30}),
            html.P('Mortality Rate: ' + str(round(df_deaths_total[-1] / df_confirmed_total[-1] * 100, 3)) + '%')
        ], className='three columns'),

        html.Div([
            html.H4('Total Recovered', style={'color': colors['recovered_text']}),
            html.P(f"{df_recovered_total[-1]:,d}", style={'color': colors['recovered_text'], 'fontSize': 30}),
            html.P('Recovery Rate: ' + str(round(df_recovered_total[-1] / df_confirmed_total[-1] * 100, 3)) + '%')
        ], className='three columns'),
    ], className='row'),

    html.Div([
        dcc.RadioItems(
            id='graph-type',
            options=[{'label': i, 'value': i} for i in ['Total Cases', 'Daily Cases']],
            value='Total Cases',
            labelStyle={'display': 'inline-block'}
        ),
        dcc.Graph(id='global-graph')
    ], className='row')
])


@app.callback(
    Output('global-graph', 'figure'),
    [Input('graph-type', 'value')]
)
def update_graph(graph_type):
    if graph_type == 'Daily Cases':
        df_confirmed_total_daily = df_confirmed_total.diff().dropna()
        df_deaths_total_daily = df_deaths_total.diff().dropna()
        df_recovered_total_daily = df_recovered_total.diff().dropna()
    else:
        df_confirmed_total_daily = df_confirmed_total
        df_deaths_total_daily = df_deaths_total
        df_recovered_total_daily = df_recovered_total

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_confirmed_total.index, y=df_confirmed_total_daily,
                             mode='lines+markers', name='Confirmed', line=dict(color='#3372FF')))
    fig.add_trace(go.Scatter(x=df_deaths_total.index, y=df_deaths_total_daily,
                             mode='lines+markers', name='Deaths', line=dict(color='#FF3333')))
    fig.add_trace(go.Scatter(x=df_recovered_total.index, y=df_recovered_total_daily,
                             mode='lines+markers', name='Recovered', line=dict(color='#33FF51')))

    fig.update_layout(title='Covid-19 Cases', hovermode='x', paper_bgcolor=colors['background'],
                      plot_bgcolor=colors['background'])
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
