import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timedelta
import time

# Abstract base class for data sources (Adapter pattern)
class DataSource(ABC):
  @abstractmethod
  def get_data(self, last_timestamp):
      pass

# Concrete implementation for simulated data
class SimulatedDataSource(DataSource):
  def get_data(self, last_timestamp):
      new_data = {
          'timestamp': [last_timestamp + timedelta(seconds=i) for i in range(1, 11)],
          'x': np.random.randn(10),
          'y': np.random.randn(10),
          'z': np.random.randn(10)
      }
      return pd.DataFrame(new_data)

# Data handler class
class DataHandler:
  def __init__(self, data_source: DataSource, window_size=100):
      self.data_source = data_source
      self.data_window = deque(maxlen=window_size)
      self.last_update = datetime.now()

  def update_data(self):
      new_data = self.data_source.get_data(self.last_update)
      for _, row in new_data.iterrows():
          self.data_window.append(row)
      self.last_update = new_data['timestamp'].iloc[-1]

  def get_current_data(self):
      return pd.DataFrame(list(self.data_window))

# Dashboard class
class Dashboard:
  def __init__(self, data_handler: DataHandler):
      self.data_handler = data_handler
      self.fig = go.Figure()

  def update_plot(self, graph_type, y_axis, num_samples):
      df = self.data_handler.get_current_data().tail(num_samples)
      
      self.fig = go.Figure()

      if graph_type in ['Line', 'Scatter']:
          for axis in ['x', 'y', 'z']:
              if y_axis == 'all' or y_axis == axis:
                  self.fig.add_trace(go.Scatter(
                      x=df['timestamp'],
                      y=df[axis],
                      mode='lines' if graph_type == 'Line' else 'markers',
                      name=axis.upper()
                  ))
          self.fig.update_layout(
              title='Gyroscope Data',
              xaxis_title='Timestamp',
              yaxis_title='Value',
              height=600
          )
      elif graph_type == 'Distribution':
          for axis in ['x', 'y', 'z']:
              if y_axis == 'all' or y_axis == axis:
                  self.fig.add_trace(go.Histogram(
                      x=df[axis],
                      name=axis.upper(),
                      opacity=0.6
                  ))
          self.fig.update_layout(
              title='Gyroscope Data Distribution',
              xaxis_title='Value',
              yaxis_title='Frequency',
              height=600,
              barmode='overlay'
          )

      return self.fig

  def compute_summary(self, df):
      summary = {
          'Statistic': ['X Mean', 'X Median', 'X Std Dev', 
                        'Y Mean', 'Y Median', 'Y Std Dev',
                        'Z Mean', 'Z Median', 'Z Std Dev'],
          'Value': [
              f"{df['x'].mean():.2f}", f"{df['x'].median():.2f}", f"{df['x'].std():.2f}",
              f"{df['y'].mean():.2f}", f"{df['y'].median():.2f}", f"{df['y'].std():.2f}",
              f"{df['z'].mean():.2f}", f"{df['z'].median():.2f}", f"{df['z'].std():.2f}",
          ]
      }
      return pd.DataFrame(summary)

# Streamlit app
def main():
  st.set_page_config(page_title="Gyroscope Data Dashboard", layout="wide")
  st.title('Gyroscope Data Dashboard')

  # Initialize session state
  if 'dashboard' not in st.session_state:
      data_source = SimulatedDataSource()
      data_handler = DataHandler(data_source)
      st.session_state.dashboard = Dashboard(data_handler)

  # Sidebar controls
  st.sidebar.header("Controls")
  graph_type = st.sidebar.selectbox('Select Graph Type', ['Line', 'Scatter', 'Distribution'])
  y_axis = st.sidebar.selectbox('Select Y-axis', ['x', 'y', 'z', 'all'])
  num_samples = st.sidebar.number_input('Number of Samples', min_value=10, value=100, step=10)

  # Create placeholders for dynamic content
  plot_placeholder = st.empty()
  summary_placeholder = st.empty()

  # Main loop for continuous updates
  while True:
      # Update data
      st.session_state.dashboard.data_handler.update_data()

      # Update plot
      fig = st.session_state.dashboard.update_plot(graph_type, y_axis, num_samples)
      plot_placeholder.plotly_chart(fig, use_container_width=True)

      # Update summary statistics
      df = st.session_state.dashboard.data_handler.get_current_data().tail(num_samples)
      summary_df = st.session_state.dashboard.compute_summary(df)
      summary_placeholder.dataframe(summary_df)


      time.sleep(10)

if __name__ == "__main__":
  main()
