# TOA AI examples

A tiny, self-contained dataset so you can run the full **ingest → train → replay**
flow without sourcing your own market data.

## Files

- `sample_ohlcv.csv` — 600 rows of synthetic 1-minute OHLCV bars in the generic
  format TOA AI ingests (`timestamp,open,high,low,close,volume`, UTC timestamps).
  This is **synthetic** data for pipeline testing only — not real market data.
- `expected_smoke_output.json` — a representative `smoke-test` result so you can
  compare the **shape** of the output. Exact numbers (loss, ids, action counts)
  vary by platform, PyTorch version, and seed.
- `expected_train_output.json` — a representative `train` result produced by
  ingesting `sample_ohlcv.csv` and training for 1 epoch (the flow in section 2).

## 1. Fastest check — synthetic smoke test (no data needed)

```bash
toa-ai smoke-test --epochs 1
# or, without the installed console script:
python -m toa_ai.cli smoke-test --epochs 1
```

This ingests synthetic bars, trains for 1 epoch, runs the promotion gate, and
replays — printing a JSON result like `expected_smoke_output.json`.

## 2. Run the pipeline on the sample CSV

```bash
# Ingest the sample CSV into a throwaway DB
toa-ai --db-path data/example.sqlite3 ingest-external \
  --path examples/sample_ohlcv.csv \
  --symbol DEMOUSDT \
  --timeframe 1m \
  --format generic

# Train a tiny GRU policy (1 epoch) on it.
# --quiet silences progress logs so stdout is pure JSON; redirect/pipe it anywhere.
toa-ai --quiet --db-path data/example.sqlite3 train \
  --timeframe 1m \
  --sequence-length 64 \
  --epochs 1 \
  --symbols DEMOUSDT > data/train_result.json

# Replay the freshly trained model over the same bars
toa-ai --db-path data/example.sqlite3 replay \
  --model-id latest \
  --symbols DEMOUSDT \
  --timeframe 1m \
  --sequence-length 64 \
  --max-episode-bars 200
```

## Notes

- Every command prints its result as JSON on **stdout** and sends logs to **stderr**,
  so `toa-ai ... train ... | jq` works as-is. Add `--quiet` to also drop the stderr
  progress line for fully silent JSON. See `expected_train_output.json` for the shape.
- By default `replay` starts from a **clean, isolated paper account**, so repeated
  runs are reproducible regardless of leftover positions in the DB. Pass
  `--no-reset-paper-state` to restore prior positions instead.
- `diagnostic_return` is a **research diagnostic only** — never a live-trading or
  promotion criterion on its own.
- The DB written under `data/` is git-ignored; delete it anytime to start fresh.
