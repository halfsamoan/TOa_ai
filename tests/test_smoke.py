"""End-to-end smoke test: synthetic ingest -> train -> promote -> replay.

Mirrors ``toa-ai smoke-test --epochs 1`` but runs against a throwaway DB under
``tmp_path`` so it never touches a developer's real data directory.
"""

from __future__ import annotations

import json
from pathlib import Path

from toa_ai.smoke import run_smoke_workflow


def test_smoke_workflow_runs_end_to_end(tmp_path):
    db_path = tmp_path / "smoke.sqlite3"

    result = run_smoke_workflow(db_path, epochs=1)

    # --- training produced a registered model on disk ---
    train = result["train"]
    assert train["model_id"]
    assert Path(train["model_path"]).exists()
    assert isinstance(train["metrics"], dict)
    assert train["metrics"]["total_samples"] > 0

    # --- promotion gate ran (smoke uses permissive thresholds -> promoted) ---
    assert result["promotion"]["promoted"] is True

    # --- replay produced diagnostics on a clean, isolated paper account ---
    replay = result["replay"]
    assert replay["status"] == "ok"
    assert replay["start_equity"] == 10_000_000.0
    assert "diagnostic_return" in replay
    assert replay["profit_metrics_are_diagnostic_only"] is True

    # The CLI prints this dict as JSON, so it must be serializable.
    json.dumps(result, default=str)
