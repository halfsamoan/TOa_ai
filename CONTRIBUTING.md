# Commands, model structure, and validation

## Installation

From the repository root:

```sh
python -m pip install .
toa-ai --help
```

The package declares its supported Python versions and NumPy, pandas, and PyTorch dependencies in `pyproject.toml`. For contributor tests:

```sh
python -m pip install -e ".[dev]"
```

## Synthetic workflow

```sh
toa-ai smoke-test --epochs 1
```

This initializes synthetic bars, trains a model, checks promotion, and runs paper replay. JSON goes to stdout; progress goes to stderr. `--quiet` suppresses progress output.

## Local data workflow

Use the sample CSV committed in the repository:

```sh
toa-ai ingest-external --path examples/sample_ohlcv.csv --symbol SAMPLE --timeframe 1m --format generic
toa-ai train --timeframe 1m --symbols SAMPLE --epochs 1
toa-ai replay --model-id latest --symbols SAMPLE --timeframe 1m
```

The CSV requires timestamp, open, high, low, close, and volume values. Input also supports Binance kline CSV/ZIP and caches named by symbol and timeframe. See `toa-ai ingest-external --help` and `toa-ai ingest-cache --help` for the exact parser options.

## Commands

| Command | Role |
|---|---|
| `init-db` | Create the SQLite schema |
| `ingest-cache` | Load local symbol/timeframe caches |
| `ingest-external` | Load external OHLCV data |
| `train` | Register a trained challenger |
| `promote` | Check challenger promotion conditions |
| `replay` | Run sequential paper replay |
| `paper-once` | Make a paper decision from the latest available bars |
| `status` | Inspect symbols and registered models |
| `smoke-test` | Exercise the synthetic end-to-end path |

## Model and replay contracts

The policy uses a GRU encoder over rolling feature sequences with action, expected-return, risk, and holding outputs. The action set is `NO_ACTION`, `OPEN_LONG`, `HOLD_LONG`, `REDUCE_LONG`, and `CLOSE_LONG`.

Inputs use completed bars up to the current decision time. Replay computes features from the available history rather than reading future bars into the model input. Future observations are used for training labels, not as input context.

Replay resets to an isolated paper account by default. `--no-reset-paper-state` restores prior paper positions; `paper-once` preserves accumulated state. Return metrics are diagnostics and are not the sole promotion criterion.

The current VWAP-distance feature uses cumulative input-period VWAP rather than a session-anchored value. Changing that definition changes feature semantics and requires retraining.

## Validation

```sh
python -m compileall toa_ai
python -m pytest -q
toa-ai smoke-test --epochs 1
```

Check paper-state isolation, deterministic data handling, promotion gates, and the absence of live broker calls. Local databases, model artifacts, market-data caches, credentials, and account identifiers must remain outside Git.

## License

[BSD 2-Clause](LICENSE).
