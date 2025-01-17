import pandas as pd
import numpy as np
import math
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class ExponentialMovingAverage:
    """
    A class to compute Exponential Moving Averages (EMA) for financial instruments.
    """

    def __init__(self, short_window: int = 5, medium_window: int = 20, long_window: int = 250):
        """
        Initialize the ExponentialMovingAverage class.

        :param short_window: The short-term EMA window (e.g., 5-period EMA).
        :param medium_window: The medium-term EMA window (e.g., 20-period EMA).
        :param long_window: The long-term EMA window (e.g., 50-period EMA).
        """
        self.short_window = short_window
        self.medium_window = medium_window
        self.long_window = long_window

    def compute_ema(self, df: pd.DataFrame, price_column: str, date_column: str = None) -> pd.DataFrame:
        """
        Compute exponential moving averages (EMAs) for the given DataFrame.

        :param df: The input DataFrame with price data.
        :param price_column: The name of the column containing prices.
        :param date_column: The name of the date column (optional, ensures sorting by date).
        :return: The original DataFrame with added EMA columns.
        """
        if date_column:
            df = df.sort_values(by=date_column)

        # Calculate EMAs
        df['EMA_Short'] = df[price_column].ewm(span=self.short_window, adjust=False).mean()
        df['EMA_Medium'] = df[price_column].ewm(span=self.medium_window, adjust=False).mean()
        df['EMA_Long'] = df[price_column].ewm(span=self.long_window, adjust=False).mean()

        return df
    
    def generate_signals(self, df: pd.DataFrame, filter_signals: bool = True) -> pd.DataFrame:
        """
        Generate buy and sell signals based on Exponential Moving Average crossovers,
        with support for multiple tickers.
        """
        # Check for necessary columns
        if 'ticker' not in df.columns:
            raise ValueError("The 'ticker' column is missing from the DataFrame.")
        if not {'EMA_Short', 'EMA_Medium', 'EMA_Long'}.issubset(df.columns):
            raise ValueError("EMA columns are missing from the DataFrame. Ensure compute_ema is called first.")

        # Sort data by ticker and date
        grouped = df.sort_values(by=['ticker', 'Date']).groupby('ticker')

        # Initialize an empty DataFrame for the results
        signals_df = pd.DataFrame()

        for ticker, group in grouped:
            group = group.dropna(subset=['EMA_Short', 'EMA_Medium', 'EMA_Long']).copy()

            # Initialize Signal column
            group['Signal'] = 0

            # Track the current position (Buy, Sell, or None)
            position = None

            for i in range(1, len(group)):
                # Buy signal: EMA_Short crosses above EMA_Medium and EMA_Long
                if (
                    group['EMA_Short'].iloc[i] > group['EMA_Medium'].iloc[i] > group['EMA_Long'].iloc[i] and
                    group['EMA_Short'].iloc[i - 1] <= group['EMA_Medium'].iloc[i - 1] and
                    position != 'Long'
                ):
                    group.at[group.index[i], 'Signal'] = 1
                    position = 'Long'

                # Sell signal: EMA_Short crosses below EMA_Medium and EMA_Long
                elif (
                    group['EMA_Short'].iloc[i] < group['EMA_Medium'].iloc[i] < group['EMA_Long'].iloc[i] and
                    group['EMA_Short'].iloc[i - 1] >= group['EMA_Medium'].iloc[i - 1] and
                    position != 'Short'
                ):
                    group.at[group.index[i], 'Signal'] = -1
                    position = 'Short'

            # Append results for this ticker
            signals_df = pd.concat([signals_df, group])

        # Add column 'Position' (Buy or Sell)
        signals_df['Position'] = signals_df['Signal'].apply(lambda x: 'Buy' if x == 1 else ('Sell' if x == -1 else None))

        # Return filtered or full dataset
        if filter_signals:
            return signals_df[signals_df['Signal'] != 0]
        return signals_df
