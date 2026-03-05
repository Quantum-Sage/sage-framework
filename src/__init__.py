"""
SAGE Framework — Core Package
==============================
The SAGE (Sequential Allocation for Guaranteed Entanglement) Framework
provides universal linear programming bounds for sequential degradation
systems: quantum networks, organ transport, and vaccine cold chains.

Usage:
    from src import SAGE_CONSTANT, calculate_sage_bound
    from src import validate_all_theorems
"""

__version__ = "6.0"

# ── Core Mathematical Constants & Functions ──────────────────────────
from .sage_bound_logic import calculate_sage_bound, SAGE_CONSTANT

# ── Theorem Engine ───────────────────────────────────────────────────
from .sage_theorems_unified import (
    validate_all_theorems,
    theorem_comparison_data,
    alpha_det,
    alpha_stochastic,
    n_w_star_uniform,
    n_w_star_stochastic,
    purify_fidelity,
    monte_carlo_fidelity,
)

# ── Simulation Engine ────────────────────────────────────────────────
from .mirror_daemon_v2 import (
    DaemonConfig,
    SimulatedBackend,
    MirrorDaemon,
    ket,
    density_matrix,
    fidelity,
    von_neumann_entropy,
)

__all__ = [
    # Constants
    "SAGE_CONSTANT",
    "__version__",
    # Core math
    "calculate_sage_bound",
    # Theorems
    "validate_all_theorems",
    "theorem_comparison_data",
    "alpha_det",
    "alpha_stochastic",
    "n_w_star_uniform",
    "n_w_star_stochastic",
    "purify_fidelity",
    "monte_carlo_fidelity",
    # Simulation
    "DaemonConfig",
    "SimulatedBackend",
    "MirrorDaemon",
    "ket",
    "density_matrix",
    "fidelity",
    "von_neumann_entropy",
]
