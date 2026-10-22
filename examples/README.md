# TOA AI examples

The sample CSV contains synthetic one-minute OHLCV bars for testing ingestion, training, and replay without external market data.

## Files

| File | Purpose |
|---|---|
| `sample_ohlcv.csv` | Synthetic OHLCV input with UTC timestamps |
| `expected_smoke_output.json` | Representative output structure for the synthetic workflow |
| `expected_train_output.json` | Representative output structure for sample-CSV training |

Saved outputs document their structure. Model IDs, losses, and action counts can vary with the platform, seed, and PyTorch version.

## Synthetic smoke test

After installing the package, run from the repository root:

```sh
toa-ai smoke-test --epochs 1
```

## Sample CSV workflow

Use a separate local database:

```sh
toa-ai --db-path data/example.sqlite3 ingest-external --path examples/sample_ohlcv.csv --symbol DEMOUSDT --timeframe 1m --format generic
toa-ai --db-path data/example.sqlite3 train --timeframe 1m --sequence-length 64 --epochs 1 --symbols DEMOUSDT
toa-ai --db-path data/example.sqlite3 replay --model-id latest --symbols DEMOUSDT --timeframe 1m --sequence-length 64 --max-episode-bars 200
```

The sample is pipeline input, not historical market evidence. Replay starts from an isolated paper account unless `--no-reset-paper-state` is supplied. Return values are research diagnostics.

JSON results go to stdout and progress goes to stderr. Add `--quiet` before the subcommand to suppress progress output. Generated databases and model files remain local.

[Package commands and validation](../CONTRIBUTING.md)
