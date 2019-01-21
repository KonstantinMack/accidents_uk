import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html


# Read and manipulate data

data1 = pd.read_csv("accidents_2005_to_2007.csv", low_memory=False)
data2 = pd.read_csv("accidents_2009_to_2011.csv", low_memory=False)
data3 = pd.read_csv("accidents_2012_to_2014.csv", low_memory=False)
df = pd.concat([data1, data2, data3])
df["Date"] = df["Date"] + " " + df["Time"]
df["Date"] = pd.to_datetime(df.Date, format="%d/%m/%Y %H:%M")
df = df.set_index("Date")
df.dropna(subset=["Latitude", "Longitude", "Time"], inplace=True)
df = df.drop_duplicates()
df = df[df["Urban_or_Rural_Area"] <= 2]
df = df[df["Speed_limit"] >= 20]
df1 = df.loc[:,["Accident_Severity", "Urban_or_Rural_Area", "Speed_limit"]]
df1["Year"] = df1.index.year
df1["Month"] = df1.index.month
df1["Day"] = df1.index.weekday
df1["Hour"] = df1.index.hour

day_dict = {
    0: "1 - Monday",
    1: "2 - Tuesday",
    2: "3 - Wednesday",
    3: "4 - Thursday",
    4: "5 - Friday",
    5: "6 - Saturday",
    6: "7 - Sunday"
}

urban_dict = {
    1: "Urban",
    2: "Rural"
}

df1["Day"] = df1.Day.map(day_dict)
df1["Urban_or_Rural_Area"] = df1.Urban_or_Rural_Area.map(urban_dict)


# Dashboard

app = dash.Dash()

app.layout = html.Div([
    html.H1('Accidents'),
    dcc.RadioItems(
        id='my-radio',
        options=[
            {'label': 'Year', 'value': 'Year'},
            {'label': 'Month', 'value': 'Month'},
            {'label': 'Day', 'value': 'Day'},
            {'label': 'Hour', 'value': 'Hour'}
        ],
        value='Year'
    ),
    dcc.Graph(id='my-graph'),

    html.H1('Pie Charts'),
    dcc.Dropdown(
        id='my-dropdown2',
        options=[
            {'label': 'Urban or Rural', 'value': "Urban_or_Rural_Area"},
            {'label': 'Speed Limit', 'value': "Speed_limit"},
        ],
        value="Urban_or_Rural_Area"
    ),
    dcc.Graph(id='my-graph2'),

    html.H1('Maps'),
    dcc.RadioItems(
        id='my-radio3',
        options=[
            {'label': 'Slight', 'value': "map_uk.html"},
            {'label': 'Fatal', 'value': "map_fatal.html"},
            {'label': 'LSOA', 'value': "map_lsoa.html"},
            {'label': 'Police Dep.', 'value': "map_police.html"},
            {'label': 'Streets horizontally', 'value': "map_str_hor.html"},
            {'label': 'Streets vertically', 'value': "map_str_ver.html"}
        ],
        value="map_uk.html"
    ),
    html.Iframe(id='map', width='90%', height='650')
])


@app.callback(Output('my-graph', 'figure'), [Input('my-radio', 'value')])
def update_graph(selected_dropdown_value):
    df = df1.groupby([selected_dropdown_value, "Accident_Severity"]).size().unstack("Accident_Severity")
    if selected_dropdown_value == "Month":
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        df = (df.divide(days, axis=0) * 30.417).round()
    return {
            'data': [
                {'x': df.index, 'y': df[3].values,
                 'type': 'bar', 'name': 'Slight'},
                {'x': df.index, 'y': df[2].values,
                 'type': 'bar', 'name': 'Serious'},
                {'x': df.index, 'y': df[1].values,
                 'type': 'bar', 'name': 'Fatal'},
            ],
            'layout': {
                'title': 'Accidents per Time-unit',
                'barmode':'stack'
            }
        }


@app.callback(Output('my-graph2', 'figure'), [Input('my-dropdown2', 'value')])
def update_graph2(category):
    df = df1.groupby([category, "Accident_Severity"]).size().unstack(level=1)
    return {
                "data": [
            {
              "values": df[1].values,
              "labels": df.index,
              "domain": {"x": [0, .33]},
              "name": "Fatal",
              "hoverinfo":"label+percent",
              "hole": .4,
              "type": "pie"
            },
            {
              "values": df[2].values,
              "labels": df.index,
              "domain": {"x": [.33, 0.67]},
              "name": "Serious",
              "hoverinfo":"label+percent",
              "hole": .4,
              "type": "pie"
            },
            {
              "values": df[3].values,
              "labels": df.index,
              "domain": {"x": [.67, 1]},
              "name": "Slight",
              "hoverinfo":"label+percent",
              "hole": .4,
              "type": "pie"
            }],
          "layout": {
                "title":"Accident Proportions",
                "annotations": [
                    {
                        "font": {
                            "size": 20
                        },
                        "showarrow": False,
                        "text": "Fatal",
                        "x": 0.145,
                        "y": 0.5
                    },
                    {
                        "font": {
                            "size": 20
                        },
                        "showarrow": False,
                        "text": "Serious",
                        "x": 0.5,
                        "y": 0.5
                    },
                    {
                        "font": {
                            "size": 20
                        },
                        "showarrow": False,
                        "text": "Slight",
                        "x": 0.86,
                        "y": 0.5
                    }
                ]
            }
        }


@app.callback(Output('map', 'srcDoc'), [Input('my-radio3', 'value')])
def update_graph3(html_file):
    return open(html_file, 'r').read()


if __name__ == '__main__':
    app.run_server(debug=True)
