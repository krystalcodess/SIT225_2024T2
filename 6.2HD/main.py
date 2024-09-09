import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import threading
import time
import os

# Initialize the Dash app
app = dash.Dash(__name__)

# Global variable to store the dataframe
global_df = None

# Load and clean the initial data
def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)
    
    # Split the concatenated timestamps
    df['timestamp'] = df['timestamp'].str.split().str[0] + ' ' + df['timestamp'].str.split().str[1]
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Drop rows with invalid timestamps
    df = df.dropna(subset=['timestamp'])
    
    return df

# Function to check for new CSV files and update the global dataframe
def update_data():
    global global_df
    while True:
        time.sleep(10)  # Check every 10 seconds
        new_files = [f for f in os.listdir('.') if f.endswith('.csv') and f != 'gyroscope_data.csv']
        if new_files:
            new_df = load_and_clean_data(new_files[0])
            if global_df is None:
                global_df = new_df
            else:
                global_df = pd.concat([global_df, new_df], ignore_index=True)
            os.remove(new_files[0])  # Remove the processed file
            print(f"New data added. Total rows: {len(global_df)}")

# Start the background thread for data updates
threading.Thread(target=update_data, daemon=True).start()

# Load initial data
global_df = load_and_clean_data('gyroscope_data.csv')

# Define the layout of the app
app.layout = html.Div([
    html.Div([
        html.H1('Gyroscope Data Dashboard', 
                style={'textAlign': 'center', 'marginBottom': '30px'})
    ], style={'backgroundColor': '#f9d2ed', 'padding': '20px'}),
    
    html.Div([
        dcc.Dropdown(
            id='graph-type',
            options=[
                {'label': 'Scatter Plot', 'value': 'scatter'},
                {'label': 'Line Chart', 'value': 'line'},
                {'label': 'Distribution Plot', 'value': 'distribution'}
            ],
            value='line',
            style={'width': '200px'}
        ),
        dcc.Dropdown(
            id='x-axis',
            options=[{'label': col, 'value': col} for col in ['timestamp', 'x', 'y', 'z']],
            value='timestamp',
            style={'width': '200px'}
        ),
        dcc.Dropdown(
            id='y-axis',
            options=[{'label': col, 'value': col} for col in ['x', 'y', 'z']],
            value='x',
            style={'width': '200px'}
        ),
        dcc.Input(
            id='num-samples',
            type='number',
            placeholder='Number of samples',
            value=100,
            style={'width': '150px'}
        ),
        html.Button('Previous', id='prev-button', n_clicks=0),
        html.Button('Next', id='next-button', n_clicks=0)
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '40px 0'}),
    
    dcc.Graph(id='main-graph'),
    
    dash_table.DataTable(
        id='summary-table',
        columns=[
            {"name": "Statistic", "id": "statistic"},
            {"name": "Value", "id": "value"}
        ],
        data=[],
        style_table={'width': '300px', 'margin': '20px auto'}
    ),
    
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # in milliseconds
        n_intervals=0
    )
], style={'backgroundColor': '#FFF0F5', 'minHeight': '100vh', 'padding': '20px'})

# Callback to update the graph and table
@app.callback(
    [Output('main-graph', 'figure'),
     Output('summary-table', 'data')],
    [Input('graph-type', 'value'),
     Input('x-axis', 'value'),
     Input('y-axis', 'value'),
     Input('num-samples', 'value'),
     Input('prev-button', 'n_clicks'),
     Input('next-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('main-graph', 'figure')]
)
def update_graph(graph_type, x_axis, y_axis, num_samples, prev_clicks, next_clicks, n_intervals, current_fig):
    global global_df
    
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    if num_samples is None or num_samples <= 0:
        num_samples = 100  
    
    if current_fig is None or 'layout' not in current_fig:
        start_index = max(0, len(global_df) - num_samples)
    else:
        start_index = current_fig['layout']['xaxis']['range'][0]
        start_index = global_df.index[global_df['timestamp'] >= pd.to_datetime(start_index, errors='coerce')][0]
    
    if button_id == 'next-button':
        start_index += num_samples
    elif button_id == 'prev-button':
        start_index = max(0, start_index - num_samples)
    
    start_index = int(start_index)  # Ensure start_index is an integer
    end_index = min(len(global_df), start_index + num_samples)
    df_subset = global_df.iloc[start_index:end_index]
    
    # Error handling for x_axis and y_axis selection
    if x_axis not in df_subset.columns or y_axis not in df_subset.columns:
        return {
            'data': [],
            'layout': go.Layout(title='Error: Invalid axis selection')
        }, []
    
    # Color mapping for x, y, z
    color_map = {'x': 'red', 'y': 'green', 'z': 'blue'}
    
    if graph_type == 'scatter':
        traces = [
            go.Scatter(
                x=df_subset[x_axis],
                y=df_subset[col],
                mode='markers',
                name=col,
                marker=dict(color=color_map[col])
            ) for col in ['x', 'y', 'z'] if col in df_subset.columns
        ]
    elif graph_type == 'line':
        traces = [
            go.Scatter(
                x=df_subset[x_axis],
                y=df_subset[col],
                mode='lines',
                name=col,
                line=dict(color=color_map[col])
            ) for col in ['x', 'y', 'z'] if col in df_subset.columns
        ]
    else:  # distribution
        traces = [
            go.Histogram(
                x=df_subset[col],
                name=col,
                marker=dict(color=color_map[col])
            ) for col in ['x', 'y', 'z'] if col in df_subset.columns
        ]
    
    layout = go.Layout(
        title=f'{graph_type.capitalize()} Plot of Gyroscope Data',
        xaxis={'title': x_axis},
        yaxis={'title': 'Value'}
    )
    
    figure = {'data': traces, 'layout': layout}
    
    summary_data = [
        {'statistic': f'{col.upper()} Mean', 'value': f"{df_subset[col].mean():.2f}"}
        for col in ['x', 'y', 'z'] if col in df_subset.columns
    ] + [
        {'statistic': f'{col.upper()} Median', 'value': f"{df_subset[col].median():.2f}"}
        for col in ['x', 'y', 'z'] if col in df_subset.columns
    ] + [
        {'statistic': f'{col.upper()} Std Dev', 'value': f"{df_subset[col].std():.2f}"}
        for col in ['x', 'y', 'z'] if col in df_subset.columns
    ]
    
    return figure, summary_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)