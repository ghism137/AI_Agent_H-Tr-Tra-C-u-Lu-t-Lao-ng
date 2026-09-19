"""Safe Phase 1 candidate builder; publishing requires a separate quality gate."""

from __future__ import annotations

from scripts.build_phase1_stage import main as build_stage
from scripts.build_registry import main as build_registry
from scripts.inventory_sources import main as inventory_sources
from scripts.quarantine_legacy_relations import main as quarantine_legacy_relations


def run_pipeline() -> None:
    inventory_sources()
    build_registry()
    quarantine_legacy_relations()
    build_stage()


if __name__ == "__main__":
    run_pipeline()
