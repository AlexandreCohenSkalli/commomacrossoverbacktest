from src.commomacrossoverbacktest.commo_informations import ExponentialMovingAverageInformation
from pybacktestchain.data_module import DataModule, get_stocks_data
from datetime import datetime, timedelta

# List of commodities (tickers for futures contracts)
commodities = ['GC=F', 'CL=F', 'CT=F', 'OJ=F', 'SB=F', 'ZS=F', 'ZC=F']  # Gold, Crude Oil, Cotton, etc.
start_date = '2020-01-01'  # Start date for data
end_date = '2023-12-31'    # End date for data

try:
    # Download commodity data
    print("Downloading commodity data...")
    commodity_data = get_stocks_data(commodities, start_date, end_date)

    if commodity_data.empty:
        print("No data downloaded.")
    else:
        print("Data successfully downloaded. Preview:")
        print(commodity_data.head())

    # Load the data into a DataModule
    data_module = DataModule(data=commodity_data)

    # Initialize the ExponentialMovingAverageInformation class
    ema_info = ExponentialMovingAverageInformation(
        data_module=data_module,
        short_window=5,
        medium_window=20,
        long_window=250,
        time_column='Date',
        adj_close_column='Close'
    )

    # Compute EMAs and signals for the last date
    t = datetime.strptime(end_date, '%Y-%m-%d')
    information_set = ema_info.compute_information(t)

    # Retrieve and display the generated signals
    signals = information_set['signals']

    # Display the first 5 rows of data per ticker
    print("\nFirst 5 rows of data for each ticker:")
    for ticker, group in commodity_data.groupby('ticker'):
        print(f"\nTicker: {ticker}")
        print(group.head(5))

    # Display the first 5 tickers in the signals
    print("\nFirst 5 tickers in signals:")
    unique_tickers = signals['ticker'].unique()[:5]
    print(unique_tickers)

    # Display the first 5 signals for each ticker
    print("\nFirst 5 signals for each ticker:")
    for ticker, group in signals.groupby('ticker'):
        print(f"\nTicker: {ticker}")
        print(group.head(5))

except Exception as e:
    print("An error occurred:")
    print(e)
