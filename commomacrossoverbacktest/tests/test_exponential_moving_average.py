import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pybacktestchain.data_module import get_stocks_data  # Importer la fonction du package
from commomacrossoverbacktest.src.exponentialmovingaverage import ExponentialMovingAverage

# Étape 1 : Définir les paramètres pour récupérer les données
tickers = ['AAPL', 'MSFT']  # Liste de tickers (par exemple)
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # Début sur un an
end_date = datetime.now().strftime('%Y-%m-%d')  # Aujourd'hui

# Étape 2 : Récupérer les données via le package pybacktestchain
data = get_stocks_data(tickers, start_date, end_date)

# Étape 3 : Filtrer les données pour un seul ticker (exemple avec 'AAPL')
ticker_data = data[data['ticker'] == 'AAPL'].copy()  # Utiliser uniquement 'AAPL'

# Étape 4 : Initialiser la classe pour calculer les EMA
ema_calculator = ExponentialMovingAverage(short_window=5, medium_window=20, long_window=50)

# Étape 5 : Calculer les EMA
result = ema_calculator.compute_ema(df=ticker_data, price_column='Close', date_column='Date')

# Étape 6 : Visualiser les résultats
plt.figure(figsize=(12, 6))
plt.plot(ticker_data['Date'], ticker_data['Close'], label='Close Price', color='blue')
plt.plot(result['Date'], result['EMA_Short'], label='5-Day EMA', color='green')
plt.plot(result['Date'], result['EMA_Medium'], label='20-Day EMA', color='orange')
plt.plot(result['Date'], result['EMA_Long'], label='50-Day EMA', color='red')
plt.legend()
plt.title("Exponential Moving Averages (AAPL)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid()
plt.show()
