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

    def commo_ptf(self, t: datetime, signals: pd.DataFrame, prices: dict):
        """
        Adjust the portfolio based on Buy/Sell signals.
        
        :param t: Current datetime for the backtest.
        :param signals: DataFrame containing 'ticker' and 'Signal' (-1 for Sell, 1 for Buy).
        :param prices: Dictionary of current prices for each ticker.
        """
        # Ensure only active signals are processed and sorted by date
        active_signals = signals[signals['Signal'] != 0]
        active_signals = active_signals.sort_values(by='Date')

        # Calculate allocation per commodity
        num_commodities = len(signals['ticker'].unique())
        allocation_per_commodity = 0.8 * self.get_portfolio_value(prices) / num_commodities

        # Process signals
        for _, row in active_signals.iterrows():
            ticker = row['ticker']
            signal = row['Signal']
            price = prices.get(ticker)

            if price is None:
                if self.verbose:
                    logging.warning(f"Price for {ticker} not available on {t}")
                continue

            if signal == -1:  # Sell signal
                if ticker in self.positions:
                    position = self.positions[ticker]

                    # Close existing long position if any
                    if position.quantity > 0:
                        self.sell(ticker, position.quantity, price, t)

                    # Short an additional 20% of allocation
                    allocation = 0.2 * allocation_per_commodity / price
                    self.sell(ticker, int(allocation), price, t)
                else:
                    # Start a new short position with 20% allocation
                    allocation = 0.2 * allocation_per_commodity / price
                    self.sell(ticker, int(allocation), price, t)

            elif signal == 1:  # Buy signal
                if ticker in self.positions and self.positions[ticker].quantity < 0:
                    # Cover short position
                    quantity_to_cover = abs(self.positions[ticker].quantity)
                    cost_to_cover = quantity_to_cover * price

                    # Check if we have enough cash
                    if cost_to_cover > self.cash:
                        # Use reserved cash
                        reserve_cash = 0.2 * self.get_portfolio_value(prices)
                        additional_cash_needed = cost_to_cover - self.cash

                        if additional_cash_needed <= reserve_cash:
                            # Temporarily use reserved cash to cover the short
                            self.cash += additional_cash_needed
                            self.buy(ticker, quantity_to_cover, price, t)
                            self.cash -= additional_cash_needed  # Restore the reserve
                        else:
                            # Use as much cash as possible
                            max_quantity_coverable = int(self.cash / price)
                            self.buy(ticker, max_quantity_coverable, price, t)
                    else:
                        # Fully cover the short
                        self.buy(ticker, quantity_to_cover, price, t)
                else:
                    # Start a new long position
                    allocation = allocation_per_commodity / price
                    quantity_to_buy = int(allocation)

                    # Ensure we don't exceed available cash
                    if quantity_to_buy * price > self.cash:
                        if self.verbose:
                            logging.warning(f"Not enough cash to buy {quantity_to_buy} of {ticker} at {price} on {t}.")
                        quantity_to_buy = int(self.cash / price)

                    self.buy(ticker, quantity_to_buy, price, t)
