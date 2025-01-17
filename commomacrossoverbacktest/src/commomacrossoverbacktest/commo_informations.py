from dataclasses import dataclass
from datetime import datetime
from pybacktestchain.data_module import Information, DataModule
from src.commomacrossoverbacktest.exponentialmovingaverage import ExponentialMovingAverage
import pandas as pd
import logging


@dataclass
class CommodityInformation(Information):
    def __init__(self, data_module, time_column, adj_close_column, commodity_column='commodity'):
        # Initialize the parent Information class
        super().__init__(None, data_module, time_column, None, adj_close_column)
        self.commodity_column = commodity_column

    def get_prices(self, t: datetime):
        """
        Retrieve the latest price for each commodity up to the given time.
        """
        data = self.data_module.data[self.data_module.data[self.time_column] <= t]
        prices = data.groupby(self.commodity_column)[self.adj_close_column].last()
        return prices.to_dict()
    

@dataclass
class ExponentialMovingAverageInformation(Information):
    short_window: int = 5
    medium_window: int = 50
    long_window: int = 250

    def compute_information(self, t: datetime):
        """
        Compute EMAs and generate signals for the entire dataset.
        """
        # Use all available data directly, no slicing
        data = self.data_module.data  

        # Ensure that the data is sorted by the time column
        data = data.sort_values(by=self.time_column)

        # Initialize the Exponential Moving Average (EMA) calculator
        ema_calculator = ExponentialMovingAverage(
            short_window=self.short_window,
            medium_window=self.medium_window,
            long_window=self.long_window
        )

        # Calculate EMAs for the entire dataset
        data = ema_calculator.compute_ema(data, price_column=self.adj_close_column)

        # Generate buy/sell signals based on the computed EMAs
        signals = ema_calculator.generate_signals(data)

        # Add the 'ticker' column to the signals DataFrame if it is missing
        if 'ticker' not in signals.columns:
            signals['ticker'] = data['ticker']

        # Return the required information set
        information_set = {
            'signals': signals[['Date', 'Signal', 'Position', 'ticker']],  # Includes key columns: Date, Signal, etc.
            'full_data': data  # Full dataset, including EMAs and signals
        }

        return information_set

