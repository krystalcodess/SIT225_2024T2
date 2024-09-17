import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, TextInput, Button, DataTable, TableColumn, HoverTool, Range1d
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from datetime import datetime, timedelta
from collections import deque

class GyroscopeDataHandler:
  def __init__(self, window_size=100):
      self.data_window = deque(maxlen=window_size)
      self.last_update_time = None

  def load_initial_data(self):
      current_time = datetime.now()
      data = {
          'timestamp': [current_time + timedelta(seconds=i) for i in range(100)],
          'x': np.random.randn(100),
          'y': np.random.randn(100),
          'z': np.random.randn(100)
      }
      df = pd.DataFrame(data)
      for _, row in df.iterrows():
          self.data_window.append(row)
      self.last_update_time = current_time

  def fetch_new_data(self):
      last_timestamp = self.data_window[-1]['timestamp']
      new_data = {
          'timestamp': [last_timestamp + timedelta(seconds=i) for i in range(1, 11)],
          'x': np.random.randn(10),
          'y': np.random.randn(10),
          'z': np.random.randn(10)
      }
      new_df = pd.DataFrame(new_data)
      for _, row in new_df.iterrows():
          self.data_window.append(row)
      self.last_update_time = datetime.now()
      return new_df

  def get_current_data(self):
      return pd.DataFrame(list(self.data_window))

class GyroscopeDashboard:
  def __init__(self, data_handler):
      self.data_handler = data_handler
      self.source = ColumnDataSource(data=dict(timestamp=[], x=[], y=[], z=[]))
      self.colors = {'x': 'red', 'y': 'green', 'z': 'blue'}
      self.plot = None

  def create_plot(self):
      self.plot = figure(
          title="Gyroscope Data Visualization",
          x_axis_label='Timestamp',
          y_axis_label='Value',
          x_axis_type='datetime',
          background_fill_color="#f0f0f0",
          width=800,
          height=400
      )

      hover = HoverTool(
          tooltips=[
              ('Timestamp', '@timestamp{%Y-%m-%d %H:%M:%S}'),
              ('X', '@x{0.00}'),
              ('Y', '@y{0.00}'),
              ('Z', '@z{0.00}')
          ],
          formatters={'@timestamp': 'datetime'}
      )
      self.plot.add_tools(hover)
      return self.plot

  def create_widgets(self):
      graph_type = Select(title="Graph Type", options=['Line', 'Scatter', 'Distribution'], value='Line')
      y_select = Select(title="Y-axis", options=['all', 'x', 'y', 'z'], value='all')
      samples_input = TextInput(title="Number of Samples", value='100')
      return graph_type, y_select, samples_input

  def create_table(self):
      table_source = ColumnDataSource(data=dict(statistic=[], value=[]))
      columns = [
          TableColumn(field="statistic", title="Statistic"),
          TableColumn(field="value", title="Value")
      ]
      return DataTable(source=table_source, columns=columns, width=400, height=200), table_source

  def update_plot(self, graph_type, y_select, samples):
      df = self.data_handler.get_current_data().tail(samples)
      new_data = {
          'timestamp': df['timestamp'],
          'x': df['x'],
          'y': df['y'],
          'z': df['z']
      }
      self.source.data = new_data

      self.plot.renderers = []  # Clear existing renderers

      if graph_type in ['Line', 'Scatter']:
          axes = ['x', 'y', 'z'] if y_select == 'all' else [y_select]
          for axis in axes:
              if graph_type == 'Line':
                  self.plot.line('timestamp', axis, source=self.source, color=self.colors[axis], legend_label=axis.upper())
              else:  # Scatter
                  self.plot.scatter('timestamp', axis, source=self.source, color=self.colors[axis], legend_label=axis.upper(), size=5)
      elif graph_type == 'Distribution':
          axes = ['x', 'y', 'z'] if y_select == 'all' else [y_select]
          for axis in axes:
              hist, edges = np.histogram(df[axis], bins=20, density=True)
              self.plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], 
                             fill_color=self.colors[axis], line_color="white", alpha=0.5, legend_label=axis.upper())

      self.plot.legend.click_policy = "hide"

  def update_table(self, table_source):
      df = self.data_handler.get_current_data()
      table_source.data = dict(
          statistic=['X Mean', 'X Median', 'X Std Dev', 'Y Mean', 'Y Median', 'Y Std Dev', 'Z Mean', 'Z Median', 'Z Std Dev', 'Last Update'],
          value=[f"{df['x'].mean():.2f}", f"{df['x'].median():.2f}", f"{df['x'].std():.2f}",
                 f"{df['y'].mean():.2f}", f"{df['y'].median():.2f}", f"{df['y'].std():.2f}",
                 f"{df['z'].mean():.2f}", f"{df['z'].median():.2f}", f"{df['z'].std():.2f}",
                 self.data_handler.last_update_time.strftime('%Y-%m-%d %H:%M:%S')]
      )

def gyroscope_dashboard(doc):
  data_handler = GyroscopeDataHandler()
  data_handler.load_initial_data()

  dashboard = GyroscopeDashboard(data_handler)
  plot = dashboard.create_plot()
  graph_type, y_select, samples_input = dashboard.create_widgets()
  data_table, table_source = dashboard.create_table()

  def update():
      new_data = data_handler.fetch_new_data()
      dashboard.update_plot(graph_type.value, y_select.value, int(samples_input.value))
      dashboard.update_table(table_source)

  def update_on_change(attr, old, new):
      dashboard.update_plot(graph_type.value, y_select.value, int(samples_input.value))

  doc.add_periodic_callback(update, 10000)  # Update every 10 seconds

  inputs = column(graph_type, y_select, samples_input)
  doc.add_root(row(inputs, plot, data_table, width=1200))
  doc.title = "Gyroscope Data Dashboard"

  # Initial update
  update()

  # Add callbacks for widget changes
  graph_type.on_change('value', update_on_change)
  y_select.on_change('value', update_on_change)
  samples_input.on_change('value', update_on_change)

# Create Bokeh application
app = Application(FunctionHandler(gyroscope_dashboard))

# Launch the server
server = Server({'/': app}, num_procs=1)
server.start()

if __name__ == '__main__':
  print('Opening Bokeh application on http://localhost:5006/')
  server.io_loop.add_callback(server.show, "/")
  server.io_loop.start()
