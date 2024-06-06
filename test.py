import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np

app = dash.Dash(__name__)

df = pd.read_csv('accid_taz.csv')
df['DEAD'] = df['DEAD'].replace(np.nan, 0)  

vehicle_types = ['MOTORCYCLE', 'TRUCK', 'BICYCLE', 'PRIVATE']
injury_age_groups = ['INJ0_19', 'INJ20_64', 'INJ65_']

app.layout = html.Div(children=[
    dcc.Dropdown(
        id='vehicle-dropdown',
        options=[{'label': i, 'value': i} for i in vehicle_types],
        value=vehicle_types,
        multi=True
    ),
    dcc.Dropdown(
        id='age-dropdown',
        options=[
            {'label': 'Age 0-19', 'value': 'INJ0_19'},
            {'label': 'Age 20-64', 'value': 'INJ20_64'},
            {'label': 'Age 65+', 'value': 'INJ65_'}
        ],
        value=injury_age_groups,
        multi=True
    ),
    dcc.RangeSlider(
        id='fatality-slider',
        min=df['DEAD'].min(),
        max=df['DEAD'].max(),
        value=[df['DEAD'].min(), df['DEAD'].max()],
        marks={str(dead): str(dead) for dead in df['DEAD'].unique()},
        step=None
    ),
    dcc.Graph(id='bar-chart')
])

@app.callback(
    Output('bar-chart', 'figure'),
    [Input('vehicle-dropdown', 'value'),
     Input('age-dropdown', 'value'),
     Input('fatality-slider', 'value')]
)
def update_graph(selected_vehicle_types, selected_age_groups, selected_fatalities_range):
    filtered_df = df[df[selected_vehicle_types].apply(lambda x: x > 0).any(axis=1)]
    filtered_df = filtered_df[filtered_df[selected_age_groups].apply(lambda x: x > 0).any(axis=1)]
    filtered_df = filtered_df[(filtered_df['DEAD'] >= selected_fatalities_range[0]) & (filtered_df['DEAD'] <= selected_fatalities_range[1])]
    by_city = filtered_df.groupby('CITY').size().reset_index(name='counts')
    by_city = by_city.sort_values('counts', ascending=True)

    return {
        'data': [
            {'y': by_city['CITY'], 'x': by_city['counts'], 'type': 'bar', 'name': 'SF', 'orientation': 'h'},
        ],
        'layout': {
            'title': 'Accidents by City',
            'height': 20000,
            'xaxis': {'range': [0, df.groupby('CITY').size().max()]},

            
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True)