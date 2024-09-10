import pandas as pd
import numpy as np
import threading
import time
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, TextInput, Button, DataTable, TableColumn, HoverTool

# Global variables
global_df = None
current_index = 0
batch_size = 100

# Simulate the data updates every 10 seconds
def simulate_data_update():
    global global_df, current_index

    while True:
        time.sleep(10)  # Simulate new data every 10 seconds

        # Simulate new data and update global_df
        # Here we assume that new data is appended to the global dataframe
        new_data = {
            'timestamp': pd.date_range(start=global_df['timestamp'].iloc[-1], periods=batch_size, freq='s'),
            'x': np.random.randn(batch_size),
            'y': np.random.randn(batch_size),
            'z': np.random.randn(batch_size)
        }
        
        # Append the new data to the global dataframe
        new_df = pd.DataFrame(new_data)
        global_df = pd.concat([global_df, new_df], ignore_index=True)

        # Call the Bokeh callback to update the plot
        curdoc().add_next_tick_callback(update)

# Start the background thread for simulating data updates
threading.Thread(target=simulate_data_update, daemon=True).start()

# Load the entire data (initial data)
def load_data(filename):
    # Simulating loading of gyroscope data from a file
    data = {
        'timestamp': pd.date_range(start='2024-08-11', periods=1000, freq='s'),
        'x': np.random.randn(1000),
        'y': np.random.randn(1000),
        'z': np.random.randn(1000)
    }
    return pd.DataFrame(data)

global_df = load_data('gyroscope_data.csv')
global_df['timestamp'] = pd.to_datetime(global_df['timestamp'])

# Create a data source for the plot
source = ColumnDataSource(data=dict(timestamp=[], x=[], y=[], z=[]))

# Define colors for x, y, z
colors = {'x': 'red', 'y': 'green', 'z': 'blue'}

# Create the plot
plot = figure(
    title="Gyroscope Data Visualization",
    x_axis_label='Timestamp',
    y_axis_label='Value',
    x_axis_type='datetime',
    background_fill_color="#f0f0f0"
)

# Center and enlarge the title
plot.title.align = 'center'
plot.title.text_font_size = '20pt'
plot.title.text_color = "#4a4a4a"

# Add hover tool
hover = HoverTool(
    tooltips=[
        ('Timestamp', '@timestamp{%F %T}'),
        ('X', '@x{0.00}'),
        ('Y', '@y{0.00}'),
        ('Z', '@z{0.00}')
    ],
    formatters={
        '@timestamp': 'datetime',
    }
)
plot.add_tools(hover)

# Widgets
graph_type = Select(title="Graph Type", options=['Line', 'Scatter', 'Distribution'], value='Line')
y_select = Select(title="Y-axis", options=['all', 'x', 'y', 'z'], value='all')
samples_input = TextInput(title="Number of Samples", value='100')
next_button = Button(label="Next")
prev_button = Button(label="Previous")

# Table for summary statistics
table_source = ColumnDataSource(data=dict(statistic=[], value=[]))
columns = [
    TableColumn(field="statistic", title="Statistic"),
    TableColumn(field="value", title="Value")
]
data_table = DataTable(source=table_source, columns=columns, width=400, height=200)

# Sample range for navigation
sample_start = 0

# Function to update the plot and table
def update():
    global global_df, sample_start
    if global_df is None or global_df.empty:
        return

    y = y_select.value
    samples = int(samples_input.value)
    sample_end = sample_start + samples
    sample_end = min(sample_end, len(global_df))

    df_subset = global_df.iloc[sample_start:sample_end]

    # Update the data source for the plot
    source.data = dict(
        timestamp=df_subset['timestamp'],
        x=df_subset['x'],
        y=df_subset['y'],
        z=df_subset['z']
    )

    # Clear existing renderers
    plot.renderers = []

    # Update the plot based on graph type
    if graph_type.value == 'Distribution':
        if y == 'all':
            for col in ['x', 'y', 'z']:
                hist, edges = np.histogram(df_subset[col], bins=20)
                plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=colors[col], line_color='black', legend_label=col.upper())
        else:
            hist, edges = np.histogram(df_subset[y], bins=20)
            plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=colors[y], line_color='black', legend_label=y.upper())
    else:
        if y == 'all':
            for col in ['x', 'y', 'z']:
                if graph_type.value == 'Line':
                    plot.line('timestamp', col, source=source, color=colors[col], legend_label=col.upper())
                else:  # Scatter
                    plot.scatter('timestamp', col, source=source, color=colors[col], legend_label=col.upper(), size=5, marker='circle')
        else:
            if graph_type.value == 'Line':
                plot.line('timestamp', y, source=source, color=colors[y], legend_label=y.upper())
            else:  # Scatter
                plot.scatter('timestamp', y, source=source, color=colors[y], legend_label=y.upper(), size=5, marker='circle')

    plot.legend.click_policy = "hide"

    # Update table with statistics
    table_source.data = dict(
        statistic=['X Mean', 'X Median', 'X Std Dev', 'Y Mean', 'Y Median', 'Y Std Dev', 'Z Mean', 'Z Median', 'Z Std Dev'],
        value=[f"{df_subset['x'].mean():.2f}", f"{df_subset['x'].median():.2f}", f"{df_subset['x'].std():.2f}",
               f"{df_subset['y'].mean():.2f}", f"{df_subset['y'].median():.2f}", f"{df_subset['y'].std():.2f}",
               f"{df_subset['z'].mean():.2f}", f"{df_subset['z'].median():.2f}", f"{df_subset['z'].std():.2f}"]
    )

# Button callbacks for navigation
def next_samples():
    global sample_start
    sample_start += int(samples_input.value)
    sample_start = min(sample_start, len(global_df) - int(samples_input.value))
    update()

def prev_samples():
    global sample_start
    sample_start -= int(samples_input.value)
    sample_start = max(sample_start, 0)
    update()

next_button.on_click(next_samples)
prev_button.on_click(prev_samples)

# Set up layouts and add to document
inputs = column(graph_type, y_select, samples_input, next_button, prev_button)
curdoc().add_root(row(inputs, plot, data_table, width=1200))
curdoc().title = "Gyroscope Data Dashboard"

# Add periodic callback to update the plot
curdoc().add_periodic_callback(update, 10000)

# Initial update
update()
