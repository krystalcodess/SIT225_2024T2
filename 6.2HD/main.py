import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import threading
import time

# Initialize the Dash app
app = dash.Dash(__name__)

global_df = None
current_index = 0
batch_size = 100  

# Load the entire data once
def load_data(file_path):
    df = pd.read_csv(file_path)

    # Split the concatenated timestamps
    df['timestamp'] = df['timestamp'].str.split().str[0] + ' ' + df['timestamp'].str.split().str[1]

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Drop rows with invalid timestamps
    df = df.dropna(subset=['timestamp'])

    return df

# Function to simulate the data update every 10 seconds
def simulate_data_update():
    global global_df, current_index
    
    while True:
        time.sleep(10)  # Simulate new data every 10 seconds
        
        # Increment the current index to simulate incoming data
        current_index += batch_size
        
        if current_index >= len(global_df):
            current_index = 0  # Restart from the beginning if we reach the end
        
        print(f"Data updated. Showing rows: {current_index} to {current_index + batch_size}")

# Start the background thread for simulating data updates
threading.Thread(target=simulate_data_update, daemon=True).start()

# Load the entire data
global_df = load_data('gyroscope_data.csv')

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
    global global_df, current_index
    
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    if num_samples is None or num_samples <= 0:
        num_samples = batch_size
    
    # Adjust the current index based on button clicks
    if button_id == 'next-button':
        current_index += num_samples
    elif button_id == 'prev-button':
        current_index = max(0, current_index - num_samples)
    
    # Slice the dataframe to get the current batch of data
    end_index = min(len(global_df), current_index + num_samples)
    df_subset = global_df.iloc[current_index:end_index]
    
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
    app.run_server(debug=True, port = 5000)
