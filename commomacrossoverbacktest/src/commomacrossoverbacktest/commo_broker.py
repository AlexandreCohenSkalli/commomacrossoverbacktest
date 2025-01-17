import pandas as pd
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import pickle

from src.commomacrossoverbacktest.commo_informations import CommodityInformation, ExponentialMovingAverageInformation
from pybacktestchain.broker import Broker, Position
from pybacktestchain.utils import generate_random_name
from pybacktestchain.data_module import DataModule
from numba import jit


@dataclass
class CommoBroker(Broker):
     def __init__(self, cash: float):
        """
        Initializes the CommoBroker with a starting cash balance and necessary attributes.
        """
        super().__init__(cash)  # Initialize with parent Broker class
        self.positions = {}  # Dictionary of current positions
        self.realized_pnl = []  # List of realized P&L
        self.portfolio_value = []  # Track portfolio value over time

     def get_portfolio_value(self, market_prices: dict):
        """
        Calculates the total portfolio value including cash and positions.
        """
        portfolio_value = self.cash
        for ticker, position in self.positions.items():
            current_price = market_prices.get(ticker)
            if current_price is not None:
                portfolio_value += position.quantity * current_price
        return portfolio_value

     def sell(self, ticker: str, quantity: int, price: float, date: datetime):
        """
        Executes a sell order for the specified ticker, handling both closing long positions 
        and initiating/increasing short positions.
        """
        # Check if the ticker already exists in the portfolio
        if ticker in self.positions:
            position = self.positions[ticker]
            new_quantity = position.quantity - quantity
            
            # Update cash balance
            self.cash += price * quantity

            # If the new quantity is zero, remove the position
            if new_quantity == 0:
                del self.positions[ticker]
            else :
                # Update the position with the new quantity
                position.quantity = new_quantity
        else:
            # No existing position, initiate a short position
            self.positions[ticker] = Position(ticker, -1*quantity, price)
            self.cash += price * quantity

        # Log the transaction
        self.log_transaction(date, 'SELL', ticker, quantity, price)
    
     def buy(self, ticker: str, quantity: int, price: float, date: datetime):
        """
        Executes a buy order for the specified ticker, using both available cash and reserved cash if necessary.
        """
        total_cost = quantity * price

        # Calculate reserved cash (20% of the portfolio value)
        reserve_cash = 0.2 * self.get_portfolio_value({})  # Reserved cash (20% of total portfolio value)
        available_cash = self.cash + reserve_cash  # Include reserved cash in available funds

        if total_cost > available_cash:
            # Use as much as possible from available funds
            max_quantity = int(available_cash / price)
            logging.warning(
                f"Not enough cash to buy {quantity} shares of {ticker} at {price}. "
                f"Available cash: {available_cash}. Buying {max_quantity} instead."
            )
            quantity = max_quantity

        # Proceed only if there is sufficient cash to buy at least one share
        if quantity > 0:
            self.cash -= quantity * price  # Deduct the cash spent
            if ticker in self.positions:
                position = self.positions[ticker]
                new_quantity = position.quantity + quantity
                new_entry_price = ((position.entry_price * position.quantity) + (price * quantity)) / new_quantity
                position.quantity = new_quantity
                position.entry_price = new_entry_price
            else:
                self.positions[ticker] = Position(ticker, quantity, price)

            # Log the transaction
            self.log_transaction(date, 'BUY', ticker, quantity, price)
        else:
            logging.warning(f"Unable to buy any shares of {ticker} due to insufficient funds.")


     def commo_ptf(self, t: datetime, signals: pd.DataFrame, prices: dict):
        """
        Adjust the portfolio based on Buy/Sell signals.

        :param t: Current datetime for the backtest.
        :param signals: DataFrame containing 'ticker' and 'Signal' (-1 for Sell, 1 for Buy).
        :param prices: Dictionary of current prices for each ticker.
        """
        # S'assurer que seuls les signaux actifs sont traités
        active_signals = signals[signals['Signal'] != 0]
        active_signals = active_signals.sort_values(by='Date')

        # Calcul de l'allocation par commodité
        num_commodities = len(signals['ticker'].unique())
        allocation_per_commodity = 0.8 * self.get_portfolio_value(prices) / num_commodities

        # Traitement des signaux
        for _, row in active_signals.iterrows():
            ticker = row['ticker']
            signal = row['Signal']
            price = prices.get(ticker)

            # Sauter si le prix n'est pas disponible
            if price is None or pd.isna(price):
                logging.warning(f"Price for {ticker} not available on {t}. Skipping.")
                continue

            if signal == -1:  # Signal de vente
                if ticker in self.positions:
                    position = self.positions[ticker]

                    # Fermer une position longue existante
                    if position.quantity > 0:
                        self.sell(ticker, position.quantity, price, t)

                # Shorter une portion supplémentaire (20% de l'allocation)
                #allocation = 0.2 * allocation_per_commodity / price
                #self.sell(ticker, int(allocation), price, t)

            elif signal == 1:  # Signal d'achat
                if ticker in self.positions and self.positions[ticker].quantity < 0:
                    # Couvrir une position courte
                    quantity_to_cover = abs(self.positions[ticker].quantity)
                    cost_to_cover = quantity_to_cover * price

                    # Vérifier si on a assez de cash
                    if cost_to_cover > self.cash:
                        reserve_cash = 0.2 * self.get_portfolio_value(prices)
                        additional_cash_needed = cost_to_cover - self.cash

                        if additional_cash_needed <= reserve_cash:
                            # Utilisation temporaire de la réserve
                            self.cash += additional_cash_needed
                            self.buy(ticker, quantity_to_cover, price, t)
                            self.cash -= additional_cash_needed  # Restaurer la réserve
                        else:
                            # Acheter autant que possible
                            max_quantity_coverable = int(self.cash / price)
                            self.buy(ticker, max_quantity_coverable, price, t)
                    else:
                        # Couvrir entièrement la position courte
                        self.buy(ticker, quantity_to_cover, price, t)
                else:
                    # Débuter une nouvelle position longue
                    allocation = allocation_per_commodity / price
                    quantity_to_buy = int(allocation)

                    # Vérification pour ne pas dépasser le cash disponible, incluant la réserve
                    reserve_cash = 0.2 * self.get_portfolio_value(prices)
                    available_cash = self.cash + reserve_cash

                    if quantity_to_buy * price > available_cash:
                        if self.verbose:
                            logging.warning(f"Not enough cash to buy {quantity_to_buy} of {ticker} at {price} on {t}.")
                        quantity_to_buy = int(available_cash / price)

                    self.buy(ticker, quantity_to_buy, price, t)
