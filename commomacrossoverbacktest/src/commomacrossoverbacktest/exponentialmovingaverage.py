import pandas as pd
import numpy as np
import math
import yfinance as yf
import datetime
import matplotlib.pyplot as plt

class ExponentialMovingAverage:
    """
    A class to compute Exponential Moving Averages (EMA) for financial instruments.
    """

    def __init__(self, short_window: int = 5, medium_window: int = 20, long_window: int = 50):
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
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy and sell signals based on Exponential Moving Average crossovers.

        :param df: DataFrame with EMA_Short, EMA_Medium, and EMA_Long columns.
        :return: DataFrame with added 'Signal' and 'Position' columns:
                - 'Signal': 1 for buy, -1 for sell, 0 for hold.
                - 'Position': Tracks the current position ('Buy', 'Sell', or None).
        """
        # Initialize Signal and Position columns
        df['Signal'] = 0
        df['Position'] = None

        # Track the current position
        position = None

        for i in range(len(df)):
            # Buy condition: EMA_Short > EMA_Medium > EMA_Long
            if (
                df['EMA_Short'][i] > df['EMA_Medium'][i] and
                df['EMA_Medium'][i] > df['EMA_Long'][i] and
                position != 'Long'
            ):
                df.at[i, 'Signal'] = 1
                df.at[i, 'Position'] = 'Buy'
                position = 'Long'
            # Sell condition: EMA_Short < EMA_Medium < EMA_Long
            elif (
                df['EMA_Short'][i] < df['EMA_Medium'][i] and
                df['EMA_Medium'][i] < df['EMA_Long'][i] and
                position != 'Short'
            ):
                df.at[i, 'Signal'] = -1
                df.at[i, 'Position'] = 'Sell'
                position = 'Short'
            else:
                df.at[i, 'Signal'] = 0
                df.at[i, 'Position'] = position
                
        filtered_df = df[df['Signal'] != 0]
       
        return df, filtered_df
    