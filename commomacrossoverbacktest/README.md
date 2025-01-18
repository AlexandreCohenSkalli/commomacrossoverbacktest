# commomacrossoverbacktest

`commomacrossoverbacktest` is a Python library designed to facilitate the development and implementation of backtesting for moving average crossover strategies applied to commodity underlyings. The library provides robust tools to simulate and evaluate trading strategies, enabling users to refine their approaches based on historical data.

## Features

- **Backtesting Framework**: Simulate and evaluate trading strategies based on exponential moving average crossovers, with short medium and long MA.
- **Commodity Trading**: Focused specifically on commodities like gold (`GC=F`), crude oil (`CL=F`), and others.
- **Customizable Signals**: Easily extend or modify signal generation logic using Exponential Moving Averages (EMAs).
- **Transaction Logs**: Automatic generation of detailed transaction logs and portfolio evolution files.
- **Visualization**: Plot portfolio value evolution over time for comprehensive strategy evaluation.
- **Configurable Parameters**: Adjust initial cash, trading universe, and backtesting periods.
- **Strategy**: Buy when MA_short > MA_medium > MA_long et sell if MA_short < MA_medium < MA_long.


## Installation

Install the package using pip:

```bash
pip install commomacrossoverbacktest
```
## Usage

### Basic Example

Below is an example of running a backtest using a moving average crossover strategy.

```python
from datetime import datetime
from commomacrossoverbacktest.commo_backtest import Backtest

# Define backtest parameters
backtest = Backtest(
    initial_date=datetime(2022, 1, 1),
    final_date=datetime(2023, 1, 1),
    universe=['GC=F', 'CL=F', 'CT=F', 'OJ=F', 'SB=F', 'ZS=F', 'ZC=F'],
    initial_cash=1000000
)

# Run the backtest
pnl_df = backtest.run_backtest()

# Visualize the portfolio value evolution
pnl_df.plot(x='Date', y='Portfolio Value', title="Portfolio Value Over Time")
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`commomacrossovernacktest` was created by Alexandre Cohen-Skalli as part of a project for the course Python Programming for M2 203 at Paris Dauphine University - PSL. 


. It is licensed under the terms of the MIT license.

## Credits

`commomacrossoverbacktest` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).