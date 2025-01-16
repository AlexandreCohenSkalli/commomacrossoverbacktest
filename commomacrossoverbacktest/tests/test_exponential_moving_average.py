import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pybacktestchain.data_module import get_stocks_data  # Import the function from the package
from src.commomacrossoverbacktest.exponentialmovingaverage import ExponentialMovingAverage

# Step 1: Define the parameters to retrieve the data
ticker = 'CL=F'  # Use only 'CL=F' for this test
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # Start date (one year ago)
end_date = datetime.now().strftime('%Y-%m-%d')  # Today's date

# Step 2: Retrieve the data using the pybacktestchain package
data = get_stocks_data([ticker], start_date, end_date)

# Step 3: Filter the data for the specific ticker ('CL=F')
ticker_data = data[data['ticker'] == ticker].copy()

# Step 4: Initialize the class to calculate the EMAs
ema_calculator = ExponentialMovingAverage(short_window=5, medium_window=20, long_window=50)

# Step 5: Calculate the EMAs
result = ema_calculator.compute_ema(df=ticker_data, price_column='Close', date_column='Date')

# Step 6: Generate buy/sell/hold signals
result, filtered_result = ema_calculator.generate_signals(result)

# Step 7: Visualize the filtered DataFrame
print(filtered_result[['Date', 'Close', 'EMA_Short', 'EMA_Medium', 'EMA_Long', 'Signal', 'Position']].tail())

# Step 8: Plot the results
plt.figure(figsize=(12, 6))
plt.plot(result['Date'], result['Close'], label='Close Price', color='blue')
plt.plot(result['Date'], result['EMA_Short'], label='5-Day EMA', color='green')
plt.plot(result['Date'], result['EMA_Medium'], label='20-Day EMA', color='orange')
plt.plot(result['Date'], result['EMA_Long'], label='50-Day EMA', color='red')

# Highlight buy/sell signals
plt.scatter(filtered_result['Date'][filtered_result['Signal'] == 1],
            filtered_result['Close'][filtered_result['Signal'] == 1],
            label='Buy Signal', marker='^', color='green', alpha=1)

plt.scatter(filtered_result['Date'][filtered_result['Signal'] == -1],
            filtered_result['Close'][filtered_result['Signal'] == -1],
            label='Sell Signal', marker='v', color='red', alpha=1)

plt.legend()
plt.title("Exponential Moving Averages with Buy/Sell Signals (CL=F)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid()
plt.show()
