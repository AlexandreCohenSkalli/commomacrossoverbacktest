import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pybacktestchain.data_module import get_stocks_data  # Importer la fonction du package
from src.commomacrossoverbacktest.exponentialmovingaverage import ExponentialMovingAverage

# Step 1: Define the parameters to retrieve the data
tickers = ['GC=F', 'CL=F']  # List of tickers (e.g., gold and oil)
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # Start date (one year ago)
end_date = datetime.now().strftime('%Y-%m-%d')  # Today's date

# Step 2: Retrieve the data using the pybacktestchain package
data = get_stocks_data(tickers, start_date, end_date)

# Step 3: Filter the data for a single ticker (example with 'CL=F')
ticker_data1 = data[data['ticker'] == 'CL=F'].copy()  # Use only data for 'CL=F'
ticker_data2 = data[data['ticker'] == 'GC=F'].copy()  # Use only data for 'CL=F'

# Step 4: Initialize the class to calculate the EMAs
ema_calculator1 = ExponentialMovingAverage(short_window=5, medium_window=20, long_window=50)
ema_calculator2 = ExponentialMovingAverage(short_window=5, medium_window=20, long_window=50)

# Step 5: Calculate the EMAs
result1 = ema_calculator1.compute_ema(df=ticker_data1, price_column='Close', date_column='Date')
result2 = ema_calculator2.compute_ema(df=ticker_data2, price_column='Close', date_column='Date')

# Step 6: Visualize the results for the first dataset (CL=F)
plt.figure(figsize=(12, 6))
plt.plot(ticker_data1['Date'], ticker_data1['Close'], label='Close Price', color='blue')
plt.plot(result1['Date'], result1['EMA_Short'], label='5-Day EMA', color='green')
plt.plot(result1['Date'], result1['EMA_Medium'], label='20-Day EMA', color='orange')
plt.plot(result1['Date'], result1['EMA_Long'], label='50-Day EMA', color='red')
plt.legend()
plt.title("Exponential Moving Averages (CL=F)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid()
plt.show()

# Step 6: Visualize the results for the second dataset (GC=F)
plt.figure(figsize=(12, 6))
plt.plot(ticker_data2['Date'], ticker_data2['Close'], label='Close Price', color='blue')
plt.plot(result2['Date'], result2['EMA_Short'], label='5-Day EMA', color='green')
plt.plot(result2['Date'], result2['EMA_Medium'], label='20-Day EMA', color='orange')
plt.plot(result2['Date'], result2['EMA_Long'], label='50-Day EMA', color='red')
plt.legend()
plt.title("Exponential Moving Averages (GC=F)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid()
plt.show()
