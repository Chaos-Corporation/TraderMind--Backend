import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Sample OHLCV data (replace this with your API data)
data = {
    'timestamp': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05',
                  '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09', '2021-01-10'],
    'open': [100, 105, 110, 115, 120, 125, 130, 135, 140, 145],
    'high': [110, 115, 120, 125, 130, 135, 140, 145, 150, 155],
    'low': [95, 100, 105, 110, 115, 120, 125, 130, 135, 140],
    'close': [105, 110, 115, 120, 125, 130, 135, 140, 145, 150],
    'volume': [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
}

# Convert the data to a DataFrame
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Define the lookback period
lookback_period = 5  # Number of candlesticks to look back

# Calculate the high and low prices over the lookback period
high_price = df['high'][-lookback_period:].max()
low_price = df['low'][-lookback_period:].min()

# Calculate Fibonacci retracement levels
def calculate_fibonacci_retracement(high, low):
    diff = high - low
    levels = {
        '0%': high,
        '23.6%': high - 0.236 * diff,
        '38.2%': high - 0.382 * diff,
        '50%': high - 0.5 * diff,
        '61.8%': high - 0.618 * diff,
        '100%': low
    }
    return levels

fibonacci_levels = calculate_fibonacci_retracement(high_price, low_price)

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(df['timestamp'], df['close'], label='Close Price')
plt.title(f'Fibonacci Retracement (Lookback Period: {lookback_period} Candlesticks)')
plt.xlabel('Date')
plt.ylabel('Price')

# Plot Fibonacci levels
for level in fibonacci_levels:
    plt.axhline(fibonacci_levels[level], linestyle='--', alpha=0.5, label=f'{level} ({fibonacci_levels[level]:.2f})')

plt.legend()
plt.show()
