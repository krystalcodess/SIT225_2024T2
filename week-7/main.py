import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import os

# Create an output directory if it doesn't exist
output_dir = 'analysis_output'
os.makedirs(output_dir, exist_ok=True)

# Function to print analysis results
def print_analysis(text):
    print(text)

# Step 1: Load the data
df = pd.read_csv('dht22_data.csv', parse_dates=['Timestamp'])

# Function to perform analysis
def analyze_data(df, title, plot_filename, degree=1):
    if len(df) == 0:
        return None, f"Error: No data points remaining for analysis of {title}"

    # Step 2: Prepare the data
    X = df[['Temperature (°C)']].values
    y = df['Humidity (%)'].values

    # Step 3: Create and train the model
    poly_features = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly_features.fit_transform(X)
    model = LinearRegression()
    model.fit(X_poly, y)

    # Step 4: Create test temperature values and predict humidity
    temp_min, temp_max = X.min(), X.max()
    test_temp = np.linspace(temp_min, temp_max, 100).reshape(-1, 1)
    test_temp_poly = poly_features.transform(test_temp)
    test_humidity = model.predict(test_temp_poly)

    # Step 5: Create scatter plot and line plot
    plt.figure(figsize=(12, 8))
    plt.scatter(X, y, color='blue', alpha=0.5, label='Data points')
    plt.plot(test_temp, test_humidity, color='red', label='Trend line')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Humidity (%)')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    
    # Save the plot
    plt.savefig(os.path.join(output_dir, plot_filename))
    plt.close()

    # Analyze the trend line
    analysis = f"\nAnalysis for {title}:\n"
    analysis += f"Number of data points: {len(df)}\n"
    analysis += f"Temperature range: {temp_min:.2f}°C to {temp_max:.2f}°C\n"
    analysis += f"Humidity range: {y.min():.2f}% to {y.max():.2f}%\n"
    analysis += "a. The trend line shows the general relationship between temperature and humidity.\n"
    analysis += "b. There are several outliers, especially in humidity values.\n"

    return model, analysis

# Initial analysis
initial_model, initial_analysis = analyze_data(df, "Initial Temperature vs Humidity", "initial_plot.png", degree=2)
print_analysis(initial_analysis)

# Step 6: Filter outliers based on humidity
q_low = df["Humidity (%)"].quantile(0.05)
q_high = df["Humidity (%)"].quantile(0.95)
df_filtered = df[(df["Humidity (%)"] > q_low) & (df["Humidity (%)"] < q_high)]

# Step 7: Repeat analysis with filtered data
filtered_model, filtered_analysis = analyze_data(df_filtered, "Filtered Temperature vs Humidity", "filtered_plot.png", degree=2)
print_analysis(filtered_analysis)

comparison = "\nComparison of scenarios:\n"
comparison += f"Initial data points: {len(df)}\n"
comparison += f"Filtered data points: {len(df_filtered)}\n"
comparison += "The filtering process removed some extreme humidity values.\n"
comparison += "This results in a trend line that better represents the majority of the data points.\n"
print_analysis(comparison)

# Step 8: Further filter outliers
q_low = df_filtered["Humidity (%)"].quantile(0.10)
q_high = df_filtered["Humidity (%)"].quantile(0.90)
df_more_filtered = df_filtered[(df_filtered["Humidity (%)"] > q_low) & (df_filtered["Humidity (%)"] < q_high)]

# Repeat analysis with more filtered data
more_filtered_model, more_filtered_analysis = analyze_data(df_more_filtered, "More Filtered Temperature vs Humidity", "more_filtered_plot.png", degree=2)
print_analysis(more_filtered_analysis)

final_comparison = "\nComparison after further filtering:\n"
final_comparison += f"Initial data points: {len(df)}\n"
final_comparison += f"First filtered data points: {len(df_filtered)}\n"
final_comparison += f"More filtered data points: {len(df_more_filtered)}\n"
final_comparison += "The second round of filtering further refined the dataset.\n"
final_comparison += "This results in a trend line that represents the core relationship between temperature and humidity,\n"
final_comparison += "excluding more of the extreme variations.\n"
print_analysis(final_comparison)

print("\nAnalysis complete. PNG plots have been saved in the 'analysis_output' directory.")