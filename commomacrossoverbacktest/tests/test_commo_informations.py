from pybacktestchain.data_module import DataModule, get_stocks_data
from src.commomacrossoverbacktest.commo_informations import CommodityInformation
from datetime import datetime, timedelta
import pandas as pd

# Liste des commodités (tickers pour les contrats futures)
commodities = ['GC=F', 'CL=F']  # Or et pétrole (tickers disponibles sur Yahoo Finance)
start_date = '2023-01-01'
end_date = '2023-12-31'

try:
    # Téléchargez les données des commodités
    print("Téléchargement des données des commodités...")
    commodity_data = get_stocks_data(commodities, start_date, end_date)

    # Vérifiez si des données ont été téléchargées
    if commodity_data.empty:
        print("Aucune donnée téléchargée pour les commodités.")
    else:
        print("Données téléchargées avec succès. Aperçu :")
        print(commodity_data.head())

    # Charger les données dans DataModule
    data_module = DataModule(data=commodity_data)

    # Initialiser CommodityInformation
    commodity_info = CommodityInformation(
        data_module=data_module,
        s=timedelta(days=360),  # Taille de la fenêtre temporelle
        time_column='Date',
        adj_close_column='Close',
        commodity_column='ticker'
    )

    # Tester avec une date donnée
    t = datetime(2023, 1, 10)  # Date pour laquelle on veut les données
    print(f"Extraction des prix des commodités pour la date {t}...")
    prices = commodity_info.get_prices(t)

    # Afficher les prix des commodités
    print("Prix des commodités :")
    print(prices)

except Exception as e:
    # En cas d'erreur, afficher un message
    print("Une erreur s'est produite :")
    print(e)
