from dataclasses import dataclass
from datetime import datetime
from pybacktestchain.data_module import Information, DataModule
from src.commomacrossoverbacktest.exponentialmovingaverage import ExponentialMovingAverage
import pandas as pd


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
            short_window=self.short_window,  # Short-term EMA window (e.g., 5 days)
            medium_window=self.medium_window,  # Medium-term EMA window (e.g., 20 days)
            long_window=self.long_window  # Long-term EMA window (e.g., 250 days)
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

    
    def commo_ptf(self, t: datetime, signals: pd.DataFrame, prices: dict):
        """
        Adjust the portfolio based on Buy/Sell signals.
        
        :param t: Current datetime for the backtest.
        :param signals: DataFrame containing 'ticker' and 'Signal' (-1 for Sell, 1 for Buy).
        :param prices: Dictionary of current prices for each ticker.
        """
        # Ensure only active signals are processed
        active_signals = signals[signals['Signal'] != 0]

        # Sell all positions where the signal is -1
        for _, row in active_signals.iterrows():
            ticker = row['ticker']
            signal = row['Signal']
            price = prices.get(ticker)

            if price is None:
                if self.verbose:
                    logging.warning(f"Price for {ticker} not available on {t}")
                continue

            if signal == -1:  # Sell signal
                # Sell the entire position for this ticker
                if ticker in self.positions and self.positions[ticker].quantity > 0:
                    self.sell(ticker, self.positions[ticker].quantity, price, t)

        # Calculate the cash available for new Buy signals
        total_cash_to_invest = self.cash * 0.80  # Use 80% of available cash
        num_buy_signals = (active_signals['Signal'] == 1).sum()

        if num_buy_signals > 0:
            # Allocate equal weight for each Buy signal
            cash_per_ticker = total_cash_to_invest / num_buy_signals

            for _, row in active_signals.iterrows():
                ticker = row['ticker']
                signal = row['Signal']
                price = prices.get(ticker)

                if signal == 1:  # Buy signal
                    if price is None:
                        if self.verbose:
                            logging.warning(f"Price for {ticker} not available on {t}")
                        continue

                    # Calculate the quantity to buy with the allocated cash
                    quantity_to_buy = int(cash_per_ticker / price)

                    if quantity_to_buy > 0:
                        self.buy(ticker, quantity_to_buy, price, t)

        # Log the final portfolio status
        if self.verbose:
            logging.info(f"Portfolio updated at {t}. Cash: {self.cash}, Positions: {self.positions}")
        


            





