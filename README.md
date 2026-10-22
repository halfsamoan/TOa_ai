# TOA AI

A research package for OHLCV ingestion, GRU policy training, and sequential paper replay.

## Implementation

- **Storage:** keeps bars, model registrations, decisions, risk-gate results, and simulated fills in SQLite.
- **Training data:** builds rolling feature sequences from completed bars and trains action, expected-return, and risk outputs.
- **Model selection:** promotes a challenger only after validation-loss, sample-count, and action-distribution checks.
- **Replay:** recomputes features from the available history and applies the risk governor before the paper broker.

The package was separated from [Auto Trader](https://github.com/halfsamoan/auto_trader). It is not a live brokerage integration.

[Policy model](toa_ai/policy.py) · [Replay](toa_ai/replay.py) · [Promotion checks](toa_ai/promotion.py)

## Run the synthetic workflow

Use a Python version supported by [pyproject.toml](pyproject.toml). From the repository root:

```sh
python -m pip install .
toa-ai smoke-test --epochs 1
```

The command runs ingestion, training, promotion checks, and replay with synthetic data. It requires no brokerage credentials. Results go to stdout as JSON and progress logs go to stderr.

## Data and evaluation

Input paths support OHLCV CSV, Binance kline CSV/ZIP, and local caches. See the [sample-data workflow](examples/README.md).

Replay starts from an isolated paper account by default. Return metrics are diagnostics rather than the sole promotion criterion. The current VWAP-distance feature uses cumulative input-period VWAP, not a session-anchored calculation; this matters for multi-day intraday datasets.

[Commands, model structure, and validation](CONTRIBUTING.md)

## License

[BSD 2-Clause](LICENSE).
