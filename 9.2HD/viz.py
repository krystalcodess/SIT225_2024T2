import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

file_path_csv = 'serial_monitor_export.csv'
df_csv = pd.read_csv(file_path_csv, sep=";", engine='python')

# Clean the data
df_csv['Value'] = df_csv['Value'].str.replace(r'\r\n', '', regex=True)
distance_data = df_csv[df_csv['Value'].str.contains('cm')]
distance_data['Distance (cm)'] = distance_data['Value'].str.extract('(\d+)').astype(float)

# Define color function
def get_color(x):
    if x > 40:
        return 'darkgreen'
    elif 30 < x <= 40:
        return 'forestgreen'
    elif 20 < x <= 30:
        return 'gold'
    elif 10 < x <= 20:
        return 'orangered'
    else:
        return 'darkred'

# Apply color function to create a list of colors
colors = [get_color(x) for x in distance_data['Distance (cm)']]

# Initialize Dash app
app = dash.Dash(__name__)

# Create Dash layout
app.layout = html.Div([
    html.H1("Distance Measurements Dashboard"),
    dcc.Graph(
        id='distance-bar-chart',
        figure={
            'data': [
                go.Bar(
                    x=distance_data.index,
                    y=distance_data['Distance (cm)'],
                    marker_color=colors,  # Use the color list here
                    hovertemplate='<b>Index:</b> %{x}<br><b>Distance:</b> %{y} cm',
                )
            ],
            'layout': go.Layout(
                title='Distance Measurements Over Time',
                xaxis=dict(title='Index (Time Points)'),
                yaxis=dict(title='Distance (cm)', range=[0, max(distance_data['Distance (cm)']) + 10]),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='black'),
                height=600
            )
        }
    )
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)