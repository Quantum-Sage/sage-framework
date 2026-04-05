"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SAGE THEOREMS — UNIFIED VALIDATION LAYER                                  ║
║  SAGE Framework v5.0                                                       ║
║  Imports and exposes key functions from the theorem files:                  ║
║    - Theorems 1 & 2 (deterministic LP bounds)                              ║
║    - Theorem 3 (stochastic extension with probabilistic entanglement)      ║
║    - Theorem 4 (purification-augmented LP)                                 ║
║                                                                            ║
║  Provides:                                                                 ║
║    - validate_all_theorems()  → quick Monte Carlo cross-check              ║
║    - theorem_comparison_data() → data for atlas panel                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import math
import numpy as np  # type: ignore
from typing import List
from typing import Dict
from typing import Any
from typing import Optional
from typing import cast

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ============================================================================
# THEORETICAL ANCHORS & CONSTANTS
# ============================================================================

# Import SAGE_CONSTANT from canonical source (sage_bound_logic.py)
from .sage_bound_logic import (
    SAGE_CONSTANT,
)  # 0.85 — Operational fidelity threshold (QKD distillation literature)

C_FIBER = 200_000  # km/s — speed of light in fiber


def calculate_order_parameter(fidelity, phi):
    """
    Formalizes the Decoherence Boundary as a Phase Transition.
    Order Parameter (M): Measures the spontaneous emergence of subjective persistence.
    M = |phi - SAGE_CONSTANT| ^ beta
    where beta is the critical exponent (approx 0.125 for 2D Ising class).
    """
    beta = 0.125  # 2D Ising Universality Class
    if fidelity < SAGE_CONSTANT:
        return 0.0  # Disordered Phase (Decohered)
    return np.power(np.abs(phi - SAGE_CONSTANT), beta)


# Import HARDWARE from canonical source (constants.py)
from .constants import HARDWARE, ROUTE_BEIJING_LONDON


# ============================================================================
# THEOREM 1 & 2 — DETERMINISTIC LP BOUNDS
# ============================================================================


def alpha_det(s, hw):
    """
    Deterministic log-fidelity contribution per hop.
    alpha_i(s) = 2 * ln(F_gate) - s / (c * T2)
    """
    return 2 * math.log(hw["F_gate"]) - s / (C_FIBER * hw["T2"])


def n_w_star_uniform(N, L, hw_w, hw_q, S=SAGE_CONSTANT):
    """
    Theorem 1: minimum Willow nodes under uniform spacing.
    n_w* = ceil( [ln(S) - N * alpha_q(s)] / [alpha_w(s) - alpha_q(s)] )
    """
    s = L / (N + 1)
    a_w = alpha_det(s, hw_w)
    a_q = alpha_det(s, hw_q)
    if a_w <= a_q:
        # Willow is not better than QuEra.
        # If QuEra alone works, return 0 Willow. Otherwise return N (it's doomed or all-Willow needed).
        if N * a_q >= math.log(S):
            return 0
        return N
    ln_S = math.log(S)
    n_w = math.ceil((ln_S - N * a_q) / (a_w - a_q))
    return max(0, min(N, n_w))


def n_w_star_nonuniform(N, L, s_min, hw_w, hw_q, S=SAGE_CONSTANT):
    """
    Theorem 2: non-uniform spacing Sage Bound.
    Under optimal T2-proportional spacing with minimum segment s_min:
    n_w* = ceil( [ln(S) - N * alpha_q(s_min) + (L - N * s_min) * beta_w] / [alpha_w(s_min) - alpha_q(s_min)] )
    where beta_w = 1/(c * T2_w).
    """
    # Edge case: check if all-QuEra is already feasible (n_w=0)
    s_allq = L / N if N > 0 else L
    f_allq = math.exp(N * alpha_det(s_allq, hw_q))
    if f_allq >= S:
        return 0

    a_w = alpha_det(s_min, hw_w)
    a_q = alpha_det(s_min, hw_q)
    beta_w = 1.0 / (C_FIBER * hw_w["T2"])

    if a_w <= a_q:
        return N

    numerator = math.log(S) - N * a_q + (L - N * s_min) * beta_w
    denominator = a_w - a_q
    n_w = math.ceil(numerator / denominator)

    # Sanity check for boundary conditions
    if n_w == 0 and f_allq < S:
        n_w = 1

    return max(0, min(N, n_w))


def end_to_end_fidelity_det(N, L, n_w, hw_w, hw_q):
    """Deterministic end-to-end fidelity: F = exp(sum of alphas)."""
    s = L / (N + 1)
    total_alpha = n_w * alpha_det(s, hw_w) + (N - n_w) * alpha_det(s, hw_q)
    return math.exp(total_alpha)


def end_to_end_fidelity_nonuniform(N, L, n_w, s_min, hw_w, hw_q):
    """
    Fidelity with optimal non-uniform spacing (Theorem 2).
    QuEra nodes get s_min, Willow nodes get remaining length.
    """
    n_q = N - n_w
    if n_w == 0:
        s_allq = L / N if N > 0 else L
        return math.exp(N * alpha_det(s_allq, hw_q))

    s_q = s_min
    s_w = (L - n_q * s_min) / n_w
    if s_w < s_min:
        return 0.0

    total_alpha = n_w * alpha_det(s_w, hw_w) + n_q * alpha_det(s_q, hw_q)
    return math.exp(total_alpha)


# ============================================================================
# THEOREM 3 — STOCHASTIC EXTENSION
# ============================================================================


def alpha_stochastic(s, hw):
    """
    Theorem 3: stochastic log-fidelity per hop.

    Includes waiting time for probabilistic entanglement generation:
      tau_wait = 2s / (c * p_gen)

    alpha_prob(s) = 2 * ln(F_gate) - s/(c*T2) * (1 + 2/p)
    """
    p = hw["p_gen"]
    base = 2 * math.log(hw["F_gate"])
    decoherence = s / (C_FIBER * hw["T2"])
    wait_penalty = 2 * s / (C_FIBER * hw["T2"] * p)
    return base - decoherence - wait_penalty


def n_w_star_stochastic(N, L, hw_w, hw_q, S=SAGE_CONSTANT):
    """Theorem 3: minimum Willow nodes under stochastic generation."""
    s = L / (N + 1)
    a_w = alpha_stochastic(s, hw_w)
    a_q = alpha_stochastic(s, hw_q)
    if a_w <= a_q:
        if N * a_q >= math.log(S):
            return 0
        return N
    ln_S = math.log(S)
    n_w = math.ceil((ln_S - N * a_q) / (a_w - a_q))
    return max(0, min(N, n_w))


def end_to_end_fidelity_stoch(N, L, n_w, hw_w, hw_q):
    """Stochastic end-to-end fidelity."""
    s = L / (N + 1)
    total = n_w * alpha_stochastic(s, hw_w) + (N - n_w) * alpha_stochastic(s, hw_q)
    return math.exp(total)


# ============================================================================
# THEOREM 4 — PURIFICATION EXTENSION
# ============================================================================


def purify_fidelity(F, rounds):
    """
    BBPSSW / DEJMPS purification: k rounds on Werner states.
    F_out = (F^2 + ((1-F)/3)^2) / (F^2 + 2F(1-F)/3 + 5((1-F)/3)^2)
    """
    f = F
    for _ in range(rounds):
        a = f * f + ((1 - f) / 3) ** 2
        b = f * f + 2 * f * (1 - f) / 3 + 5 * ((1 - f) / 3) ** 2
        if b < 1e-12:
            return 0.25
        f = a / b
    return f


def alpha_with_purification(s, hw, k=0):
    """
    Theorem 4: effective log-fidelity after k purification rounds.
    Apply purification to the raw per-hop fidelity from Theorem 3.
    """
    raw_alpha = alpha_stochastic(s, hw)
    raw_fidelity = math.exp(raw_alpha)
    if raw_fidelity <= 0.25:
        return raw_alpha  # Below purification floor
    purified = purify_fidelity(raw_fidelity, k)
    return math.log(max(1e-30, purified))


# ============================================================================
# MONTE CARLO VALIDATION
# ============================================================================


def monte_carlo_fidelity(N, L, n_w, hw_w, hw_q, n_trials=2000):
    """
    Monte Carlo simulation of end-to-end fidelity.
    Simulates geometric retries and decoherence during waiting.
    """
    s = L / (N + 1)
    hw_list = [hw_w] * n_w + [hw_q] * (N - n_w)
    fidelities = []

    for _ in range(n_trials):
        total_log_f = 0.0
        for i in range(N):
            hw = hw_list[i]
            # Geometric retries
            attempts = np.random.geometric(hw["p_gen"])
            wait_time = attempts * 2 * s / C_FIBER
            # Gate fidelity
            gate_f = hw["F_gate"] ** 2
            # Decoherence during wait
            decoherence = math.exp(-wait_time / hw["T2"])
            hop_f = gate_f * decoherence
            total_log_f += math.log(max(1e-30, hop_f))
        fidelities.append(math.exp(total_log_f))

    return {
        "mean": np.mean(fidelities),
        "std": np.std(fidelities),
        "median": np.median(fidelities),
        "p5": np.percentile(fidelities, 5),
        "p95": np.percentile(fidelities, 95),
    }


# ============================================================================
# VALIDATION ENGINE
# ============================================================================


def validate_all_theorems(
    L=ROUTE_BEIJING_LONDON, N_values: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    Quick validation: compare analytic predictions vs Monte Carlo
    for multiple N values.

    Returns: list of result dicts with theorem predictions and MC results.
    """
    if N_values is None:
        N_values = [5, 10, 15, 20]

    hw_w = HARDWARE["Willow"]
    hw_q = HARDWARE["QuEra"]
    results = []

    for N in N_values:
        n_w_det = n_w_star_uniform(N, L, hw_w, hw_q)
        n_w_sto = n_w_star_stochastic(N, L, hw_w, hw_q)

        f_det = end_to_end_fidelity_det(N, L, n_w_det, hw_w, hw_q)
        f_sto = end_to_end_fidelity_stoch(N, L, n_w_sto, hw_w, hw_q)

        mc = monte_carlo_fidelity(N, L, n_w_sto, hw_w, hw_q, n_trials=1000)

        results.append(
            {
                "N": N,
                "n_w_det": n_w_det,
                "n_w_stoch": n_w_sto,
                "F_det": f_det,
                "F_stoch": f_sto,
                "F_mc_mean": mc["mean"],
                "F_mc_std": mc["std"],
                "F_mc_p5": mc["p5"],
                "F_mc_p95": mc["p95"],
                "agreement": abs(f_sto - mc["mean"]) < 2 * mc["std"],
            }
        )

    return results


def theorem_comparison_data(L=ROUTE_BEIJING_LONDON) -> Dict[str, Any]:
    """
    Generate data for the atlas comparison panel.
    Sweeps N from 3 to 30 and computes deterministic vs stochastic bounds.
    """
    hw_w = HARDWARE["Willow"]
    hw_q = HARDWARE["QuEra"]

    N_range = range(3, 31)
    det_fidelities: List[float] = []
    stoch_fidelities: List[float] = []
    n_w_det_list = []
    n_w_stoch_list = []

    for N in N_range:
        n_w_d = n_w_star_uniform(N, L, hw_w, hw_q)
        n_w_s = n_w_star_stochastic(N, L, hw_w, hw_q)

        f_d = end_to_end_fidelity_det(N, L, n_w_d, hw_w, hw_q)
        f_s = end_to_end_fidelity_stoch(N, L, n_w_s, hw_w, hw_q)

        det_fidelities.append(f_d)
        stoch_fidelities.append(f_s)
        n_w_det_list.append(n_w_d)
        n_w_stoch_list.append(n_w_s)

    return {
        "N_range": list(N_range),
        "det_fidelities": det_fidelities,
        "stoch_fidelities": stoch_fidelities,
        "n_w_det": n_w_det_list,
        "n_w_stoch": n_w_stoch_list,
        "sage_constant": SAGE_CONSTANT,
    }


# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 62)
    print("  SAGE THEOREMS — UNIFIED VALIDATION")
    print("=" * 62)

    print(f"\n  Route: Beijing-London ({ROUTE_BEIJING_LONDON:,} km)")
    print(
        f"  Hardware: Willow (F_gate={HARDWARE['Willow']['F_gate']}) vs"
        f" QuEra (F_gate={HARDWARE['QuEra']['F_gate']})"
    )

    print("\n  Validating Theorems 1-3 against Monte Carlo...\n")
    results = validate_all_theorems()

    print(
        f"  {'N':>3} | {'n_w(det)':>8} | {'n_w(sto)':>8} |"
        f" {'F_det':>8} | {'F_sto':>8} | {'F_mc':>8} | {'Match':>5}"
    )
    print("  " + "-" * 62)

    for r in results:
        mark = "YES" if r["agreement"] else " NO"
        print(
            f"  {r['N']:3d} | {r['n_w_det']:8d} | {r['n_w_stoch']:8d} |"
            f" {r['F_det']:8.4f} | {r['F_stoch']:8.4f} |"
            f" {r['F_mc_mean']:8.4f} | {mark:>5}"
        )

    all_agree = all(r["agreement"] for r in results)
    print(
        f"\n  Overall: {'ALL THEOREMS VALIDATED' if all_agree else 'SOME DISCREPANCIES FOUND'}"
    )

    print("\n  Generating comparison data sweep...")
    comp = theorem_comparison_data()
    above_sage = sum(
        1 for f in cast(List[float], comp["stoch_fidelities"]) if f >= SAGE_CONSTANT
    )
    print(
        f"  {above_sage}/{len(cast(List[Any], comp['N_range']))} configurations meet Sage Constant"
        f" under stochastic model"
    )

    print("\n  Complete.")
