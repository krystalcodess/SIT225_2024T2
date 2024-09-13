import streamlit as st
import pandas as pd
import numpy as np
import time

# Function to load the data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Simulate new data every 10 seconds by generating random values
def simulate_data(df, batch_size=100):
    last_timestamp = df['timestamp'].max()
    new_data = {
        'timestamp': pd.date_range(start=last_timestamp, periods=batch_size, freq='s'),
        'x': np.random.randn(batch_size),
        'y': np.random.randn(batch_size),
        'z': np.random.randn(batch_size)
    }
    new_df = pd.DataFrame(new_data)
    return pd.concat([df, new_df], ignore_index=True)

# Load initial data
if 'df' not in st.session_state:
    st.session_state.df = load_data('gyroscope_data.csv')

# Sidebar controls for user input
st.sidebar.header("Controls")
graph_type = st.sidebar.selectbox('Select Graph Type', ['Line', 'Scatter', 'Distribution'])
x_axis = st.sidebar.selectbox('Select X-axis', ['timestamp'])
y_axis = st.sidebar.selectbox('Select Y-axis', ['x', 'y', 'z', 'all'])
num_samples = st.sidebar.number_input('Number of Samples', min_value=10, value=100, step=10)

# Main dashboard title
st.title('Gyroscope Data Dashboard')

# Create a single-element container (placeholder)
placeholder = st.empty()

# Continuous update loop
while True:
    # Simulate new data every 10 seconds
    st.session_state.df = simulate_data(st.session_state.df, batch_size=num_samples)

    # Custom function to compute summary statistics for x, y, z axes
    def compute_summary(df):
        summary = {
            'Statistic': ['X Mean', 'X Median', 'X Std Dev', 
                          'Y Mean', 'Y Median', 'Y Std Dev',
                          'Z Mean', 'Z Median', 'Z Std Dev'],
            'Value': [
                df['x'].mean(), df['x'].median(), df['x'].std(),
                df['y'].mean(), df['y'].median(), df['y'].std(),
                df['z'].mean(), df['z'].median(), df['z'].std(),
            ]
        }
        summary_df = pd.DataFrame(summary)
        return summary_df

    # Compute summary statistics for display
    summary_df = compute_summary(st.session_state.df.tail(num_samples))

    # Update the dashboard inside the placeholder
    with placeholder.container():
        st.subheader('Summary Statistics')
        st.dataframe(summary_df)

        # Define colors for x, y, z axes
        color_map = {'x': 'red', 'y': 'blue', 'z': 'black'}

        # Graph Plotting
        st.subheader('Graph')
        if graph_type == 'Line':
            if y_axis == 'all':
                # Combine all axes into one graph with different colors
                combined_df = st.session_state.df.set_index('timestamp').tail(num_samples)
                st.line_chart(combined_df[['x', 'y', 'z']], height=400)
            else:
                st.line_chart(st.session_state.df.set_index('timestamp')[y_axis].tail(num_samples), height=400)
        elif graph_type == 'Scatter':
            if y_axis == 'all':
                # Combine all axes into one scatter plot with different colors
                combined_df = st.session_state.df.tail(num_samples)
                st.plotly_chart({
                    'data': [
                        {'x': combined_df['timestamp'], 'y': combined_df['x'], 'mode': 'markers', 'name': 'x', 'marker': {'color': color_map['x']}},
                        {'x': combined_df['timestamp'], 'y': combined_df['y'], 'mode': 'markers', 'name': 'y', 'marker': {'color': color_map['y']}},
                        {'x': combined_df['timestamp'], 'y': combined_df['z'], 'mode': 'markers', 'name': 'z', 'marker': {'color': color_map['z']}},
                    ],
                    'layout': {'title': 'Combined Scatter Plot', 'xaxis': {'title': 'Timestamp'}, 'yaxis': {'title': 'Value'}}
                })
            else:
                st.scatter_chart(st.session_state.df.set_index('timestamp')[y_axis].tail(num_samples), height=400)
        else:
            if y_axis == 'all':
                combined_df = st.session_state.df.tail(num_samples)
                st.plotly_chart({
                    'data': [
                        {'x': combined_df['x'], 'type': 'histogram', 'name': 'x', 'marker': {'color': color_map['x']}},
                        {'x': combined_df['y'], 'type': 'histogram', 'name': 'y', 'marker': {'color': color_map['y']}},
                        {'x': combined_df['z'], 'type': 'histogram', 'name': 'z', 'marker': {'color': color_map['z']}},
                    ],
                    'layout': {'title': 'Combined Distribution Plot', 'xaxis': {'title': 'Value'}, 'yaxis': {'title': 'Frequency'}}
                })
            else:
                st.bar_chart(st.session_state.df[y_axis].tail(num_samples), height=400)

    # Pause for 10 seconds before refreshing the dashboard
    time.sleep(10)

