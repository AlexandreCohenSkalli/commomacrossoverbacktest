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