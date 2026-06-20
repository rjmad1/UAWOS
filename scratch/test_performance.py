# scratch/test_performance.py
import os
import sys
import time
import pytest

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uawos_context
import uawos_objective
import uawos_pmcms
import uawos_traceability
import uawos_budget
from uawos_dashboard_daemon import run_health_checks


def test_api_performance_benchmarks():
    """Verify performance metrics of core engines against operational latency budgets."""
    tenant_id = "tenant-perf-test"
    tokens = uawos_context.set_context(tenant_id, "Admin", "admin_user")

    try:
        os.environ["OPA_MOCK_ACTIVE"] = "true"
        os.environ["OPENFGA_MOCK_ACTIVE"] = "true"
        os.environ["QDRANT_MOCK_ACTIVE"] = "true"
        os.environ["POSTGRES_MOCK_ACTIVE"] = "true"
        os.environ["CLICKHOUSE_MOCK_ACTIVE"] = "true"
        os.environ["MARQUEZ_MOCK_ACTIVE"] = "true"
        os.environ["SUPERSET_MOCK_ACTIVE"] = "true"
        os.environ["DTRACK_MOCK_ACTIVE"] = "true"
        os.environ["NEO4J_MOCK_ACTIVE"] = "true"
        # Seed cache status
        status_cache = run_health_checks()

        # Benchmark 1: PMCMS Maturity Engine execution time
        print("\nBenchmarking PMCMS Maturity Engine...")
        start_time = time.perf_counter()
        assessment = uawos_pmcms.get_maturity_assessment(status_cache)
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        print(f"  PMCMS assessment duration: {duration_ms:.2f}ms")
        assert duration_ms < 5000.0, f"PMCMS latency exceeded budget: {duration_ms:.2f}ms"

        # Benchmark 2: Objective Conflict Detection (DFS priority graph cycles checks)
        print("Benchmarking DFS Objective Conflict Detection...")
        start_time = time.perf_counter()
        conflicts = uawos_objective.detect_conflicts()
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        print(f"  DFS Conflict Detection duration: {duration_ms:.2f}ms")
        assert duration_ms < 500.0, f"Conflict detection latency exceeded budget: {duration_ms:.2f}ms"

        # Benchmark 3: Traceability Matrix rollups
        print("Benchmarking Requirements Traceability mapping...")
        start_time = time.perf_counter()
        matrix = uawos_traceability.get_traceability_matrix(status_cache)
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        print(f"  Traceability matrix duration: {duration_ms:.2f}ms")
        assert duration_ms < 1000.0, f"Traceability latency exceeded budget: {duration_ms:.2f}ms"

        # Benchmark 4: Budget Ledger rollup
        print("Benchmarking Budget Summary rollup...")
        start_time = time.perf_counter()
        summary = uawos_budget.get_summary()
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        print(f"  Budget Summary duration: {duration_ms:.2f}ms")
        assert duration_ms < 500.0, f"Budget summary latency exceeded budget: {duration_ms:.2f}ms"

        print("=== Latency performance validations passed successfully. ===")

    finally:
        uawos_context.reset_context(tokens)


if __name__ == "__main__":
    test_api_performance_benchmarks()
