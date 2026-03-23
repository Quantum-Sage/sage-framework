"""
SAGE Framework — Centralized Constants
========================================
Single source of truth for all hardware profiles, physical constants,
standard routes, and visualization colors.

Import from here — do NOT redefine these values in other modules.

Usage:
    from src.constants import HARDWARE, C_FIBER, ROUTE_BEIJING_LONDON
"""

from .sage_bound_logic import SAGE_CONSTANT  # noqa: F401 — re-export

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================

C_FIBER = 200_000  # km/s — speed of light in fiber
C_FREESPACE = 300_000  # km/s — speed of light in vacuum

# From Bozkurt et al. (Nat. Phys. 2025): acoustic delay lines extend T2 by 30x
PHONON_MEMORY_LIFETIME_MULTIPLIER = 30

# ============================================================================
# HARDWARE PROFILES
# ============================================================================
#
# Canonical specs for all quantum hardware platforms.
# Keys: F_gate (gate fidelity), T2 (coherence time, seconds),
#        p_gen (entanglement generation probability),
#        cost_units (relative cost), color/label (visualization).
#
# Sources:
#   Willow  — Google Quantum AI (2026 Nature Physics, dynamic surface codes, 0.143% error)
#   QuEra   — QuEra Computing (neutral atom, high T2)
#   Helios  — Hypothetical mid-range fluxonium platform
#   NISQ    — Current noisy intermediate-scale baseline
#
HARDWARE = {
    "Willow": {
        "F_gate": 0.99857, # 1 - 0.00143 (Jan 2026)
        "T2": 1.0,         # 1.0 s baseline (30s with new phonon multiplier)
        "p_gen": 0.10,
        "cost_units": 8,
        "color": "#00A8E8",
        "label": "Willow (Google 2026)",
    },
    "QuEra": {
        "F_gate": 0.9920,
        "T2": 2.0,  # 2.0 s (neutral atom specialty)
        "p_gen": 0.05,
        "cost_units": 1,
        "color": "#FF6B35",
        "label": "QuEra (Neutral Atom)",
    },
    "Helios": {
        "F_gate": 0.9950,
        "T2": 0.500,
        "p_gen": 0.08,
        "cost_units": 4,
        "color": "#FFD700",
        "label": "Helios (Mid-range)",
    },
    "NISQ": {
        "F_gate": 0.9700,
        "T2": 0.010,
        "p_gen": 0.01,
        "cost_units": 0.3,
        "color": "#FF4444",
        "label": "NISQ (Baseline)",
    },
}

# ============================================================================
# STANDARD ROUTES
# ============================================================================

ROUTES = {
    "beijing-nyc": {"distance": 11_000, "label": "Beijing → NYC"},
    "beijing-london": {"distance": 8_200, "label": "Beijing → London"},
    "london-nyc": {"distance": 5_500, "label": "London → NYC"},
    "tokyo-sf": {"distance": 8_300, "label": "Tokyo → San Francisco"},
}

ROUTE_BEIJING_NYC = 11_000  # km
ROUTE_BEIJING_LONDON = 8_200  # km

# ============================================================================
# VISUALIZATION PALETTE
# ============================================================================

COLORS = {
    "bg": "#0D1117",
    "gold": "#FFD700",
    "cyan": "#00FFE0",
    "red": "#FF4444",
    "white": "#E6EDF3",
    "grid": "#21262D",
    "orange": "#FF8C00",
    "green": "#00FF41",
    "purple": "#9C27B0",
}
