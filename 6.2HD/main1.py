import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, TextInput, Button, DataTable, TableColumn, HoverTool, Range1d
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from datetime import datetime, timedelta

# Global variables
global_df = None
last_update_time = None

# Simulate loading initial data
def load_initial_data():
    current_time = datetime.now()
    data = {
        'timestamp': [current_time + timedelta(seconds=i) for i in range(100)],
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'z': np.random.randn(100)
    }
    return pd.DataFrame(data)

# Simulate fetching new data
def fetch_new_data(last_timestamp):
    new_data = {
        'timestamp': [last_timestamp + timedelta(seconds=i) for i in range(1, 11)],
        'x': np.random.randn(10),
        'y': np.random.randn(10),
        'z': np.random.randn(10)
    }
    return pd.DataFrame(new_data)

def gyroscope_dashboard(doc):
    global global_df, last_update_time

    # Load initial data
    global_df = load_initial_data()
    last_update_time = datetime.now()

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
        background_fill_color="#f0f0f0",
        width=800,
        height=400
    )

    # Center and enlarge the title
    plot.title.align = 'center'
    plot.title.text_font_size = '20pt'
    plot.title.text_color = "#4a4a4a"

    # Add hover tool
    hover = HoverTool(
        tooltips=[
            ('Timestamp', '@timestamp{%Y-%m-%d %H:%M:%S}'),
            ('X', '@x{0.00}'),
            ('Y', '@y{0.00}'),
            ('Z', '@z{0.00}')
        ],
        formatters={'@timestamp': 'datetime'}
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

    # Function to update the plot and table
    def update():
        if global_df is None or global_df.empty:
            return

        y = y_select.value
        samples = int(samples_input.value)
        df_subset = global_df.tail(samples)

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
        if graph_type.value in ['Line', 'Scatter']:
            plot.xaxis.axis_label = 'Timestamp'
            plot.yaxis.axis_label = 'Value'
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

            # Set y-axis range
            y_min = df_subset[['x', 'y', 'z']].min().min()
            y_max = df_subset[['x', 'y', 'z']].max().max()
            y_range = y_max - y_min
            plot.y_range = Range1d(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

            # Set x-axis range
            time_range = df_subset['timestamp'].max() - df_subset['timestamp'].min()
            plot.x_range = Range1d(df_subset['timestamp'].min() - 0.05 * time_range,
                                   df_subset['timestamp'].max() + 0.05 * time_range)

        elif graph_type.value == 'Distribution':
            plot.xaxis.axis_label = 'Timestamp'
            plot.yaxis.axis_label = 'Value'
            
            if y == 'all':
                for col in ['x', 'y', 'z']:
                    hist, edges = np.histogram(df_subset[col], bins=20, density=True)
                    plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], 
                              fill_color=colors[col], line_color='black', alpha=0.5,
                              legend_label=col.upper())
            else:
                hist, edges = np.histogram(df_subset[y], bins=20, density=True)
                plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], 
                          fill_color=colors[y], line_color='black',
                          legend_label=y.upper())
            
            # Set x-axis range for distribution
            x_min = df_subset[['x', 'y', 'z']].min().min()
            x_max = df_subset[['x', 'y', 'z']].max().max()
            x_range = x_max - x_min
            plot.x_range = Range1d(x_min - 0.1 * x_range, x_max + 0.1 * x_range)
            
            # Set y-axis range for distribution
            plot.y_range = Range1d(0, max(hist) * 1.1)

        plot.legend.click_policy = "hide"

        # Update table with statistics
        update_table_summary(df_subset)

    def update_table_summary(df):
        table_source.data = dict(
            statistic=['X Mean', 'X Median', 'X Std Dev', 'Y Mean', 'Y Median', 'Y Std Dev', 'Z Mean', 'Z Median', 'Z Std Dev', 'Last Update'],
            value=[f"{df['x'].mean():.2f}", f"{df['x'].median():.2f}", f"{df['x'].std():.2f}",
                   f"{df['y'].mean():.2f}", f"{df['y'].median():.2f}", f"{df['y'].std():.2f}",
                   f"{df['z'].mean():.2f}", f"{df['z'].median():.2f}", f"{df['z'].std():.2f}",
                   last_update_time.strftime('%Y-%m-%d %H:%M:%S')]
        )

    # Button callbacks for navigation
    def next_samples():
        update()

    def prev_samples():
        update()

    next_button.on_click(next_samples)
    prev_button.on_click(prev_samples)

    # Function to fetch and integrate new data
    def fetch_and_update():
        global global_df, last_update_time
        last_timestamp = global_df['timestamp'].iloc[-1]
        new_data = fetch_new_data(last_timestamp)
        global_df = pd.concat([global_df, new_data], ignore_index=True)
        last_update_time = datetime.now()
        
        # Update the plot and table summary with the new data
        update()

    # Set up layouts and add to document
    inputs = column(graph_type, y_select, samples_input, next_button, prev_button)
    doc.add_root(row(inputs, plot, data_table, width=1200))
    doc.title = "Gyroscope Data Dashboard"

    # Add periodic callback to fetch new data and update the plot
    doc.add_periodic_callback(fetch_and_update, 10000)  # Every 10 seconds

    # Initial update
    update()

    # Add callback for graph type changes
    graph_type.on_change('value', lambda attr, old, new: update())
    y_select.on_change('value', lambda attr, old, new: update())
    samples_input.on_change('value', lambda attr, old, new: update())

# Create Bokeh application
app = Application(FunctionHandler(gyroscope_dashboard))

# Launch the server
server = Server({'/': app}, num_procs=1)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()

