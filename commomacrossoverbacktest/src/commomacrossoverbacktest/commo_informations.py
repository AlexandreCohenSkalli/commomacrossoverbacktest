from dataclasses import dataclass
from datetime import datetime
from pybacktestchain.data_module import Information, DataModule
from src.commomacrossoverbacktest.exponentialmovingaverage import ExponentialMovingAverage


@dataclass
class CommodityInformation(Information):
    def __init__(self, data_module, s, time_column, adj_close_column, commodity_column='commodity'):
        # Initialize the parent Information class
        super().__init__(s, data_module, time_column, None, adj_close_column)
        # Set commodity column
        self.commodity_column = commodity_column

    # Override methods where the column name is used
    def get_prices(self, t: datetime):
        # Get data within the relevant time window
        data = self.slice_data(t)
        
        # Retrieve the latest price for each commodity
        prices = data.groupby(self.commodity_column)[self.adj_close_column].last()
        # Convert to dictionary: commodity as key, price as value
        prices = prices.to_dict()
        return prices
    
@dataclass
class ExponentialMovingAverageInformation(Information):
    short_window: int = 5
    medium_window: int = 50
    long_window: int = 250

    def compute_information(self, t: datetime):
        """
        Compute EMAs and generate signals for the given time window.
        """
        # Slice data to get relevant time window
        data = self.slice_data(t)

        # Ensure data is sorted by time
        data = data.sort_values(by=self.time_column)

        # Initialize EMA calculator
        ema_calculator = ExponentialMovingAverage(
            short_window=self.short_window,
            medium_window=self.medium_window,
            long_window=self.long_window
        )

        # Compute EMAs
        data = ema_calculator.compute_ema(data, price_column=self.adj_close_column)

        # Instanciation de l'objet ExponentialMovingAverage
        ema_calculator = ExponentialMovingAverage(
            short_window=self.short_window,
            medium_window=self.medium_window,
            long_window=self.long_window
        )

        # Appel de la méthode via l'objet
        signals = ema_calculator.generate_signals(data)

        # Ajouter la colonne 'ticker' aux signaux si elle n'est pas présente
        if 'ticker' not in signals.columns:
            signals['ticker'] = data['ticker']

        # Return the relevant information set
        information_set = {
            'signals': signals[['Date', 'Signal', 'Position', 'ticker']],
            'full_data': data  # Includes EMAs and signals
        }
        return information_set

    
    


        





