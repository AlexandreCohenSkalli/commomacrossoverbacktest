import pandas as pd
import logging
from datetime import datetime
import os
from dataclasses import dataclass
from src.commomacrossoverbacktest.commo_broker import CommoBroker
from src.commomacrossoverbacktest.commo_informations import ExponentialMovingAverageInformation
from pybacktestchain.data_module import DataModule, get_stocks_data
from pybacktestchain.utils import generate_random_name
import matplotlib.pyplot as plt


# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class Backtest:
    initial_date: datetime
    final_date: datetime
    universe: list  # Liste des tickers (e.g., ['GC=F', 'CL=F', ...])
    information_class: type = ExponentialMovingAverageInformation
    time_column: str = 'Date'
    adj_close_column: str = 'Close'
    initial_cash: float = 1000000
    verbose: bool = True
    broker: CommoBroker = None  # Le broker sera initialisé dans __post_init__

    def __post_init__(self):
        if self.broker is None:
            self.broker = CommoBroker(cash=self.initial_cash)
        self.backtest_name = generate_random_name()

    def run_backtest(self):
        logging.info(f"Running backtest from {self.initial_date} to {self.final_date}.")

        # Charger les données du marché
        df = get_stocks_data(
            self.universe,
            self.initial_date.strftime('%Y-%m-%d'),
            self.final_date.strftime('%Y-%m-%d')
        )

        # Initialiser le module de données et la classe d'information
        data_module = DataModule(df)
        info = self.information_class(
            data_module=data_module,
            time_column=self.time_column,
            adj_close_column=self.adj_close_column,
        )

        # Suivre l'évolution du P&L
        pnl_history = []

        # Boucle sur chaque jour de la période du backtest
        for t in pd.date_range(self.initial_date, self.final_date, freq='D'):
            # Obtenir les prix et les signaux pour le jour courant
            prices = info.get_prices(t)
            information_set = info.compute_information(t)
            signals = information_set['signals']

            # Ajuster le portefeuille avec les signaux via le broker
            self.broker.commo_ptf(t, signals, prices)

            # Calculer la valeur actuelle du portefeuille
            portfolio_value = self.broker.get_portfolio_value(prices)
            pnl_history.append((t, portfolio_value))

        # Créer un DataFrame pour l'évolution du P&L
        pnl_df = pd.DataFrame(pnl_history, columns=['Date', 'Portfolio Value'])

        # Sauvegarder les résultats
        self.save_results(pnl_df)

        logging.info(f"Backtest completed. Final portfolio value: {pnl_df['Portfolio Value'].iloc[-1]}")

        return pnl_df

    def save_results(self, pnl_df):
        # Sauvegarde des résultats
        if not os.path.exists('backtests'):
            os.makedirs('backtests')

        transaction_log_path = f"backtests/{self.backtest_name}_transactions.csv"
        portfolio_evolution_path = f"backtests/{self.backtest_name}_portfolio.csv"

        # Enregistrer les transactions avec des colonnes bien formatées
        self.broker.get_transaction_log().to_csv(
            transaction_log_path, index=False, sep=',', float_format='%.2f'
        )
        
        # Enregistrer l'évolution du portefeuille
        pnl_df.to_csv(
            portfolio_evolution_path, index=False, sep=',', float_format='%.2f'
        )

        logging.info(f"Results saved to {transaction_log_path} and {portfolio_evolution_path}")



# Lancer le backtest
if __name__ == "__main__":
    backtest = Backtest(
        initial_date=datetime(2022, 1, 1),
        final_date=datetime(2023, 1, 1),
        universe=['GC=F', 'CL=F', 'CT=F', 'OJ=F', 'SB=F', 'ZS=F', 'ZC=F'],
        initial_cash=1000000
    )

    pnl_df = backtest.run_backtest()

    # Visualiser l'évolution du P&L
    plt.figure(figsize=(12, 6))
    plt.plot(pnl_df['Date'], pnl_df['Portfolio Value'], label="Portfolio Value")
    plt.title("Portfolio P&L Evolution")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid()
    plt.show()
