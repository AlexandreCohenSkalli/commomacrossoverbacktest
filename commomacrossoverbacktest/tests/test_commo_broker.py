import pytest
import pandas as pd
from datetime import datetime
from src.commomacrossoverbacktest.commo_broker import CommoBroker  # Chemin vers votre module
from pybacktestchain.broker import Position

def test_commobroker_initialization():
    broker = CommoBroker(cash=1000)
    assert broker.cash == 1000
    assert isinstance(broker.positions, dict)
    assert isinstance(broker.realized_pnl, list)
    assert isinstance(broker.portfolio_value, list)

def test_commobroker_buy():
    broker = CommoBroker(cash=1000)
    broker.buy(ticker="CL=F", quantity=10, price=60, date=datetime(2024, 1, 1))  # Achat de pétrole

    assert broker.cash == 400
    assert "CL=F" in broker.positions
    assert broker.positions["CL=F"].quantity == 10
    assert broker.positions["CL=F"].entry_price == 60
    assert not broker.transaction_log.empty

def test_commobroker_sell():
    broker = CommoBroker(cash=1000)
    broker.buy(ticker="CL=F", quantity=10, price=60, date=datetime(2024, 1, 1))
    broker.sell(ticker="CL=F", quantity=5, price=70, date=datetime(2024, 1, 2))  # Vente partielle

    assert broker.cash == 750  # 1000 - (10*60) + (5*70)
    assert broker.positions["CL=F"].quantity == 5
    assert broker.positions["CL=F"].entry_price == 60
    assert len(broker.transaction_log) == 2  # Un achat et une vente

def test_commobroker_get_portfolio_value():
    broker = CommoBroker(cash=3000)
    broker.buy(ticker="GC=F", quantity=1, price=1500, date=datetime(2024, 1, 1))  # Attempt to buy 1 shares at 1500
    market_prices = {"GC=F": 1600}
    portfolio_value = broker.get_portfolio_value(market_prices)

    # Assert the reserved cash was used to partially complete the purchase
    assert "GC=F" in broker.positions  # Ensure the position was created
    assert broker.positions["GC=F"].quantity == 1  # Only 1 share could be purchased
    assert broker.positions["GC=F"].entry_price == 1500
    assert portfolio_value == 3100  

def test_commobroker_commo_ptf():
    broker = CommoBroker(cash=5000)

    # Signaux et prix simulés pour des commodities
    signals = pd.DataFrame([
        {"ticker": "CL=F", "Signal": 1, "Date": datetime(2024, 1, 1)},  # Achat pétrole
        {"ticker": "GC=F", "Signal": -1, "Date": datetime(2024, 1, 1)}  # Short or
    ])
    prices = {"CL=F": 60, "GC=F": 1500}

    broker.commo_ptf(t=datetime(2024, 1, 1), signals=signals, prices=prices)

    # Vérifie la position sur CL=F
    assert "CL=F" in broker.positions
    assert broker.positions["CL=F"].quantity > 0  # Position longue

    
    # Vérifie le solde de trésorerie mis à jour
    assert broker.cash < 5000

def test_commobroker_handle_unavailable_prices():
    broker = CommoBroker(cash=1000)

    # Signaux et prix, avec un prix manquant pour ZC=F (maïs)
    signals = pd.DataFrame([
        {"ticker": "CL=F", "Signal": 1, "Date": datetime(2024, 1, 1)},
        {"ticker": "ZC=F", "Signal": -1, "Date": datetime(2024, 1, 1)}
    ])
    prices = {"CL=F": 60}  # Prix de ZC=F non fourni

    broker.commo_ptf(t=datetime(2024, 1, 1), signals=signals, prices=prices)

    # Vérifie que CL=F a une position créée
    assert "CL=F" in broker.positions
    assert broker.positions["CL=F"].quantity > 0

    # Vérifie que ZC=F n'a pas de position créée
    assert "ZC=F" not in broker.positions

#def test_commobroker_short_covering():
    #broker = CommoBroker(cash=2000)

    # Crée une position courte initiale
    #broker.sell(ticker="SB=F", quantity=10, price=20, date=datetime(2024, 1, 1))  # Vente de sucre

    # Simule un signal d'achat pour couvrir la position courte
    #signals = pd.DataFrame([
    #    {"ticker": "SB=F", "Signal": 1, "Date": datetime(2024, 1, 2)}
    #])
    #prices = {"SB=F": 22}

    #broker.commo_ptf(t=datetime(2024, 1, 2), signals=signals, prices=prices)

    # Vérifie que la position courte est couverte
    #assert "SB=F" not in broker.positions
    #assert broker.cash < 2000  # Cash diminue après couverture
