import pytest

import scripts.publish_phase1_release as publisher


def test_failed_gate_cannot_move_active_pointer(monkeypatch):
    def forbidden_write(*_args, **_kwargs):
        raise AssertionError("failed gate must not write a pointer")

    monkeypatch.setattr(publisher, "atomic_json", forbidden_write)
    monkeypatch.setattr(publisher, "audit", lambda: {"gate1": "FAIL", "blockers": ["missing evidence"]})
    with pytest.raises(RuntimeError, match="Gate 1 is FAIL"):
        publisher.publish()
