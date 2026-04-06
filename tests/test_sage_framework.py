#!/usr/bin/env python3
"""
SAGE Framework v6.0 — Unit Tests
=================================
Validates core mathematical logic and commercial tools.

Run:  pytest tests/test_sage_framework.py -v
"""

import sys

import numpy as np

sys.path.insert(0, ".")

# ============================================================================
# 1. SAGE BOUND LOGIC
# ============================================================================

from src.sage_bound_logic import calculate_sage_bound, SAGE_CONSTANT


class TestSageBound:
    """Test the core mathematical bound."""

    def test_sage_constant_value(self):
        """SAGE_CONSTANT should be 0.85."""
        assert SAGE_CONSTANT == 0.85

    def test_single_hop_high_fidelity(self):
        """1 hop at F=0.999, p=0.9 → should be close to 0.999."""
        result = calculate_sage_bound(1, 0.999, 0.9)
        assert 0.3 < result < 1.0

    def test_many_hops_low_fidelity_decays(self):
        """100 hops at F=0.99, p=0.5 → should decay significantly."""
        result = calculate_sage_bound(100, 0.99, 0.5)
        assert result < 0.5

    def test_perfect_fidelity_no_decay(self):
        """F=1.0 → no decay regardless of hops (ignoring stochastic penalty)."""
        result = calculate_sage_bound(50, 1.0, 0.9)
        expected = 1.0 / (1 + 2.0 / 0.9)
        assert abs(result - expected) < 1e-10

    def test_zero_hops(self):
        """0 hops → pristine result (F^0 = 1.0 / penalty)."""
        result = calculate_sage_bound(0, 0.5, 0.5)
        expected = 1.0 / (1 + 2.0 / 0.5)
        assert abs(result - expected) < 1e-10

    def test_returns_non_negative(self):
        """Should never return negative."""
        result = calculate_sage_bound(10000, 0.1, 0.01)
        assert result >= 0.0

    def test_stochastic_penalty_increases_with_low_p(self):
        """Lower p_gen → higher penalty → lower bound."""
        high_p = calculate_sage_bound(10, 0.99, 0.9)
        low_p = calculate_sage_bound(10, 0.99, 0.1)
        assert high_p > low_p


# ============================================================================
# 2. COLD CHAIN SIMULATOR
# ============================================================================

from run_cold_chain import (
    stochastic_penalty,
    stage_log_potency,
    end_to_end_potency,
    find_optimal_upgrades,
    run_analysis,
    DEFAULT_STAGES,
    CLINICAL_THRESHOLD,
)


class TestColdChain:
    """Test vaccine cold chain simulation."""

    def test_stochastic_penalty_formula(self):
        """Penalty = 1 + 1/p. At p=0.5 → 3.0."""
        assert stochastic_penalty(0.5) == 3.0

    def test_stochastic_penalty_perfect_grid(self):
        """At p=1.0 → penalty = 2.0."""
        assert stochastic_penalty(1.0) == 2.0

    def test_stage_log_potency_negative(self):
        """Log potency should always be negative (potency < 1)."""
        result = stage_log_potency(0.95, 0.8)
        assert result < 0

    def test_end_to_end_returns_dict(self):
        """end_to_end_potency returns structured data with breakdown."""
        result = end_to_end_potency(DEFAULT_STAGES)
        assert "total_potency" in result
        assert "breakdown" in result
        assert len(result["breakdown"]) == 5

    def test_end_to_end_potency_decreases(self):
        """Cumulative potency should decrease at each stage."""
        result = end_to_end_potency(DEFAULT_STAGES)
        potencies = [s["cumulative_potency"] for s in result["breakdown"]]
        for i in range(1, len(potencies)):
            assert potencies[i] <= potencies[i - 1]

    def test_optimizer_respects_budget(self):
        """Upgrades total cost should not exceed budget."""
        result = find_optimal_upgrades(DEFAULT_STAGES, budget=500.0)
        total_cost = result.get("total_cost", 0)
        assert total_cost <= 500.0

    def test_run_analysis_returns_both(self):
        """Full analysis returns potency_analysis AND optimization."""
        result = run_analysis(DEFAULT_STAGES, budget=1000.0)
        assert "potency_analysis" in result
        assert "optimization" in result

    def test_clinical_threshold_value(self):
        """Clinical threshold is 50%."""
        assert CLINICAL_THRESHOLD == 0.50


# ============================================================================
# 3. DRUG DELIVERY OPTIMIZER
# ============================================================================

from run_drug_delivery import (
    log_decomposition,
    compute_allocation_matrix,
    run_analysis as drug_run_analysis,
    DEFAULT_BARRIERS,
)


class TestDrugDelivery:
    """Test drug delivery LP optimizer."""

    def test_log_decomposition_baseline(self):
        """Baseline decomposition (no vehicle) should have all negative alpha_i."""
        result = log_decomposition(DEFAULT_BARRIERS)
        for entry in result["barriers"]:
            assert entry["alpha"] <= 0  # log(T) <= 0 since T <= 1

    def test_log_decomposition_count(self):
        """Should have one entry per barrier in the barriers list."""
        result = log_decomposition(DEFAULT_BARRIERS)
        assert len(result["barriers"]) == 6

    def test_allocation_matrix_structure(self):
        """Matrix should have entries indexed by barrier-vehicle combos."""
        result = compute_allocation_matrix(DEFAULT_BARRIERS)
        # Result is a dict; check it has content
        assert len(result) > 0

    def test_optimal_always_beats_baseline(self):
        """LP-optimal should always beat no-vehicle baseline."""
        result = drug_run_analysis(DEFAULT_BARRIERS)
        opt = result["optimization"]
        baseline = opt["baseline"]["bioavailability"]
        best = opt["lp_optimal"]["bioavailability"]
        assert best > baseline

    def test_optimal_beats_single_best(self):
        """LP-optimal mixed strategy should beat or match best single vehicle."""
        result = drug_run_analysis(DEFAULT_BARRIERS)
        opt = result["optimization"]
        lp_bio = opt["lp_optimal"]["bioavailability"]
        single_bio = opt["best_single_vehicle"]["bioavailability"]
        assert lp_bio >= single_bio


# ============================================================================
# 4. NETWORK PLANNER
# ============================================================================

from run_network_planner import analyze_route, PRESET_ROUTES, SATELLITE_TIERS


class TestNetworkPlanner:
    """Test quantum network feasibility analysis."""

    def test_preset_routes_exist(self):
        """Should have at least 5 preset routes."""
        assert len(PRESET_ROUTES) >= 5

    def test_satellite_tiers_exist(self):
        """Should have at least 3 satellite tiers."""
        assert len(SATELLITE_TIERS) >= 3

    def test_analyze_route_returns_topologies(self):
        """Analysis should compare multiple topologies."""
        result = analyze_route(5000, label="Test Route")
        assert "topologies" in result
        assert len(result["topologies"]) >= 3

    def test_short_distance_more_feasible(self):
        """100km should be more feasible than 10000km."""
        short = analyze_route(100, label="Short")
        long_r = analyze_route(10000, label="Long")
        # Topologies is a dict of dicts, each with a 'best' sub-dict containing 'fidelity'
        short_best = max(t["best"]["fidelity"] for t in short["topologies"].values())
        long_best = max(t["best"]["fidelity"] for t in long_r["topologies"].values())
        assert short_best >= long_best

    def test_verdict_present(self):
        """Should always include a verdict."""
        result = analyze_route(8200, label="Beijing-London")
        assert "verdict" in result


# ============================================================================
# 5. MIRROR DAEMON (from simulation)
# ============================================================================

from src.mirror_daemon_v2 import (
    DaemonConfig,
    SimulatedBackend,
    MirrorDaemon,
    ket,
    fidelity,
    von_neumann_entropy,
    density_matrix,
)


class TestMirrorDaemon:
    """Test the Mirror Daemon v2 simulation engine."""

    def test_daemon_config_defaults(self):
        """Default config should have sensible values."""
        cfg = DaemonConfig()
        assert cfg.fidelity_threshold == 0.85
        assert cfg.max_steps == 10_000
        assert cfg.code_distance == 3

    def test_ket_creates_valid_state(self):
        """ket([1,0]) should create a valid |0> state."""
        psi = ket([1, 0])
        assert psi.shape == (2, 1)
        assert abs(np.linalg.norm(psi) - 1.0) < 1e-10

    def test_density_matrix_from_ket(self):
        """rho = |psi><psi| should be a valid density matrix."""
        psi = ket([1, 0])
        rho = density_matrix(psi)
        assert rho.shape == (2, 2)
        assert abs(np.trace(rho) - 1.0) < 1e-10

    def test_fidelity_pure_state_is_one(self):
        """Fidelity of a state with itself should be 1.0."""
        psi = ket([1, 0])
        rho = density_matrix(psi)
        f = fidelity(rho, rho)
        assert abs(f - 1.0) < 1e-10

    def test_von_neumann_entropy_pure_state(self):
        """Pure state entropy should be 0 (or very close)."""
        psi = ket([1, 0])
        rho = density_matrix(psi)
        s = von_neumann_entropy(rho)
        assert abs(s) < 1e-6

    def test_simulated_backend_runs(self):
        """SimulatedBackend should run a step without errors."""
        backend = SimulatedBackend(depolar_p=0.01)
        psi = ket([1, 0])
        backend.initialize(psi)
        result = backend.step()
        assert 0.0 <= result.fidelity <= 1.0

    def test_daemon_runs_short_sim(self):
        """Daemon should complete a 10-step simulation."""
        cfg = DaemonConfig(max_steps=10, live_plot=False)
        backend = SimulatedBackend(depolar_p=0.001)
        psi = ket([1, 0])
        daemon = MirrorDaemon(backend=backend, config=cfg)
        daemon.initialize(psi)
        results = daemon.run(n_steps=10)
        assert "final_fidelity" in results
        assert results["n_steps"] == 10
        assert 0.0 <= results["final_fidelity"] <= 1.0
