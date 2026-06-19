"""Regression tests for the replay/paper state-isolation fix.

Before the fix, ``PaperBroker`` always restored positions from the DB while
resetting cash to ``initial_cash``. A position left in the DB by a previous run
therefore inflated ``start_equity`` and silently distorted ``diagnostic_return``
on the next replay.

Replay now starts from a clean, isolated paper account by default
(``ReplayConfig.reset_paper_state=True`` -> ``PaperBroker(load_positions=False)``).
The old restore behaviour is still available via ``--no-reset-paper-state``.
"""

from __future__ import annotations

from toa_ai.config import ReplayConfig
from toa_ai.execution import PaperBroker
from toa_ai.storage import TOAMemory

INITIAL_CASH = 10_000_000.0


def _memory_with_stale_position(tmp_path):
    memory = TOAMemory(tmp_path / "state.sqlite3")
    # Simulate a position left in the DB by a previous replay/paper run:
    # qty=100, avg_price=50, market_price=60.
    memory.upsert_position("TOA001", 100.0, 50.0, 60.0, {"source": "paper"})
    return memory


def test_replay_defaults_to_isolated_state():
    assert ReplayConfig().reset_paper_state is True


def test_isolated_broker_ignores_stale_db_positions(tmp_path):
    memory = _memory_with_stale_position(tmp_path)

    broker = PaperBroker(memory, initial_cash=INITIAL_CASH, load_positions=False)

    # Clean account: no positions restored, equity == initial cash.
    assert broker.account.positions == {}
    assert broker.account.equity == INITIAL_CASH


def test_optout_restores_stale_db_positions(tmp_path):
    memory = _memory_with_stale_position(tmp_path)

    broker = PaperBroker(memory, initial_cash=INITIAL_CASH, load_positions=True)

    # Opt-out (--no-reset-paper-state) keeps the old restore behaviour, which
    # inflates equity by the restored position's market value (100 * 60).
    assert "TOA001" in broker.account.positions
    assert broker.account.equity == INITIAL_CASH + 100.0 * 60.0
