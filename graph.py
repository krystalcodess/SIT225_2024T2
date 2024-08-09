import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Read the CSV file
df = pd.read_csv('dht22.csv', parse_dates=['Timestamp'])
df.set_index('Timestamp', inplace=True)

# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Plot temperature
ax1.plot(df.index, df['Temperature (°C)'], color='red')
ax1.set_title('Temperature over Time')
ax1.set_ylabel('Temperature (°C)')
ax1.grid(True)

# Plot humidity
ax2.plot(df.index, df['Humidity (%)'], color='blue')
ax2.set_title('Humidity over Time')
ax2.set_ylabel('Humidity (%)')
ax2.grid(True)

plt.tight_layout()
plt.savefig('dht22_data_plot.png')
plt.close()

# Basic statistical analysis
print(df.describe())

# Check for correlation between temperature and humidity
correlation = df['Temperature (°C)'].corr(df['Humidity (%)'])
print(f"Correlation between Temperature and Humidity: {correlation:.2f}")

# Perform a simple linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(df['Temperature (°C)'], df['Humidity (%)'])
print(f"Linear Regression Results:")
print(f"Slope: {slope:.4f}")
print(f"Intercept: {intercept:.4f}")
print(f"R-squared: {r_value**2:.4f}")
print(f"P-value: {p_value:.4f}")

# Plot scatter plot with regression line
plt.figure(figsize=(10, 6))
plt.scatter(df['Temperature (°C)'], df['Humidity (%)'], alpha=0.5)
plt.plot(df['Temperature (°C)'], intercept + slope * df['Temperature (°C)'], color='red', label='Regression Line')
plt.title('Temperature vs Humidity')
plt.xlabel('Temperature (°C)')
plt.ylabel('Humidity (%)')
plt.legend()
plt.grid(True)
plt.savefig('temperature_vs_humidity.png')
plt.close()