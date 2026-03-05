"""
SATELLITE-HYBRID RELAY MODEL
SAGE Framework v5.1

Closes the intercontinental gap identified in Theorem Validation:
  "0/28 fiber-only configurations meet Sage Constant at 8,200 km"

Physics Model:
  - Ground-to-LEO uplink: ~500 km free-space optical channel
  - LEO-to-LEO relay: inter-satellite optical link (no fiber)
  - LEO-to-Ground downlink: ~500 km free-space
  - Fiber segments: ground-level repeater chains to/from uplink stations

Key insight from CIRO framework (Core Memory 2):
  "Identity is a Signature, not a Substrate" — the signal can transit
  through fundamentally different media (fiber → free-space → fiber)
  as long as Information Homeostasis is maintained via QEC.

Reference hardware:
  - Micius satellite (Pan et al. 2017): p_gen ~ 0.003 at 1,200 km
  - Recent advances (2025): p_gen ~ 0.01 at 500 km LEO
  - Ground station Willow nodes: same as Sage Bound theorems
"""
# type: ignore
# pyre-ignore-all-errors

import sys
import math
from typing import List, Dict, Any, Optional, cast

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import matplotlib.gridspec as gridspec  # type: ignore

# ============================================================================
# CONSTANTS
# ============================================================================

from .sage_bound_logic import SAGE_CONSTANT  # 0.851

C_FIBER = 200_000  # km/s in fiber
C_FREESPACE = 300_000  # km/s in free space (vacuum)

# Ground-level hardware (from Sage Bound theorems)
HW_WILLOW = cast(
    Dict[str, Any],
    {
        "F_gate": 0.9985,
        "T2": 1.000,
        "p_gen": 0.10,
        "label": "Willow",
        "color": "#00A8E8",
    },
)
HW_QUERA = cast(
    Dict[str, Any],
    {
        "F_gate": 0.9920,
        "T2": 2.0,
        "p_gen": 0.05,
        "label": "QuEra",
        "color": "#FF6B35",
    },
)
HW_HELIOS = cast(
    Dict[str, Any],
    {
        "F_gate": 0.9950,
        "T2": 0.500,
        "p_gen": 0.08,
        "label": "Helios",
        "color": "#FFD700",
    },
)

# Satellite link hardware
HW_LEO_CURRENT = cast(
    Dict[str, Any],
    {
        "F_gate": 0.9900,  # Gate fidelity for satellite QM operations
        "T2": 0.050,  # Short T2 — satellite QMs are compact/noisy
        "p_gen": 0.003,  # Micius-class: very low success rate
        "label": "LEO (2024)",
        "color": "#9C27B0",
    },
)
HW_LEO_ADVANCED = cast(
    Dict[str, Any],
    {
        "F_gate": 0.9950,  # Improved gate fidelity
        "T2": 0.200,  # Better memory (cryogenic payload)
        "p_gen": 0.01,  # 3x improvement over Micius
        "label": "LEO (2027+)",
        "color": "#E040FB",
    },
)
HW_LEO_OPTIMISTIC = cast(
    Dict[str, Any],
    {
        "F_gate": 0.9980,  # Near-Willow gate fidelity
        "T2": 0.500,  # Advanced cryogenic satellite memory
        "p_gen": 0.05,  # Significant improvement in coupling efficiency
        "label": "LEO (2030+)",
        "color": "#CE93D8",
    },
)

# Visual
BG = "#0D1117"
GOLD = "#FFD700"
CYAN = "#00FFE0"
RED = "#FF4444"
WHITE = "#E6EDF3"
GRID = "#21262D"


# ============================================================================
# PHYSICS: FIBER AND FREE-SPACE CHANNELS
# ============================================================================


def alpha_fiber(s_km: float, hw: Dict[str, Any]) -> float:
    """
    Log-fidelity per fiber hop (Theorem 3, stochastic).
    Includes waiting time for probabilistic entanglement generation.
    """
    p = hw["p_gen"]
    base = 2 * math.log(hw["F_gate"])
    decoherence = s_km / (C_FIBER * hw["T2"])
    wait_penalty = 2 * s_km / (C_FIBER * hw["T2"] * p)
    return base - decoherence - wait_penalty


def alpha_freespace(
    s_km: float, hw_sat: Dict[str, Any], hw_ground: Optional[Dict[str, Any]] = None
) -> float:
    """
    Log-fidelity per free-space hop (satellite link).

    CRITICAL PHYSICS: Ground-station-initiated entanglement.
    The satellite generates entangled photon pairs and sends them
    to two ground stations. The ground stations store the received
    qubits in their long-T2 Willow memories. The satellite's short
    T2 is irrelevant — it never holds a qubit for longer than the
    photon transit time.

    This is how Micius actually operates:
      1. Satellite creates entangled pair
      2. Sends photon A to Ground Station A, photon B to Ground Station B
      3. Ground stations store in quantum memory (Willow T2 = 1.0s)
      4. If detection fails, retry → wait time = round trip / p_gen
      5. Decoherence during wait happens in GROUND memory (long T2)

    Key differences from fiber:
      - Speed: C_FREESPACE (vacuum) → shorter round trips
      - No fiber absorption → but atmospheric loss + pointing error
      - p_gen is low (free-space coupling efficiency)
      - Wait-time decoherence uses GROUND T2, not satellite T2
    """
    if hw_ground is None:
        hw_ground = HW_WILLOW  # Default: ground station uses Willow

    p = hw_sat["p_gen"]
    base = 2 * math.log(hw_sat["F_gate"])

    # Round trip time at speed of light in vacuum
    # Decoherence during wait uses GROUND station T2 (long-lived memory)
    t2_effective = hw_ground["T2"]  # Ground station memory!

    decoherence = s_km / (C_FREESPACE * float(t2_effective))
    wait_penalty = 2 * s_km / (C_FREESPACE * float(t2_effective) * float(p))

    # Atmospheric absorption + turbulence penalty
    # ~3 dB at zenith → already folded into p_gen
    # Pointing/tracking: ~0.0005 per 100 km (refined from literature)
    pointing_loss = 0.0005 * (s_km / 100)

    return base - decoherence - wait_penalty - pointing_loss


# ============================================================================
# HYBRID NETWORK TOPOLOGIES
# ============================================================================


def topology_fiber_only(
    L_km: float, N: int, hw_ground: Dict[str, Any]
) -> tuple[float, Dict[str, Any]]:
    """Pure fiber network — the baseline that fails at >4000 km."""
    s = L_km / (N + 1)
    total_alpha = N * alpha_fiber(s, hw_ground)
    return math.exp(total_alpha), {"type": "fiber_only", "N": N, "s_km": s}


def topology_single_satellite(
    L_km: float,
    N_ground: int,
    hw_ground: Dict[str, Any],
    hw_sat: Dict[str, Any],
    sat_altitude_km: float = 500,
) -> tuple[float, Dict[str, Any]]:
    """
    LEO satellite at midpoint:
      [Ground A] --fiber-- [Uplink Station] --free-space-- [LEO]
      --free-space-- [Downlink Station] --fiber-- [Ground B]

    Ground segments: each has N_ground/2 repeaters using fiber
    Satellite segment: 2 free-space hops (up + down), ~500 km each
    """
    ground_half = L_km / 2
    n_per_side = max(1, N_ground // 2)
    s_ground = ground_half / (n_per_side + 1)

    # Ground segment fidelity (both sides)
    ground_alpha = 2 * n_per_side * alpha_fiber(s_ground, hw_ground)

    # Satellite segment: uplink + downlink
    # Each is approximately sat_altitude_km (at zenith)
    # At typical elevation angles, effective path ~ 1.2 * altitude
    effective_sat_distance = sat_altitude_km * 1.2
    sat_alpha = 2 * alpha_freespace(effective_sat_distance, hw_sat)

    total_alpha = ground_alpha + sat_alpha

    info = {
        "type": "single_satellite",
        "N_ground": N_ground,
        "s_ground_km": s_ground,
        "sat_altitude_km": sat_altitude_km,
        "sat_path_km": effective_sat_distance,
        "ground_alpha": ground_alpha,
        "sat_alpha": sat_alpha,
    }
    return math.exp(total_alpha), info


def topology_dual_satellite(
    L_km: float,
    N_ground: int,
    hw_ground: Dict[str, Any],
    hw_sat: Dict[str, Any],
    sat_altitude_km: float = 500,
) -> tuple[float, Dict[str, Any]]:
    """
    Two LEO satellites at L/3 and 2L/3 points:
      [Ground A] --fiber-- [Uplink 1] --free-space-- [LEO 1]
      --inter-sat link-- [LEO 2] --free-space-- [Downlink 2]
      --fiber-- [Ground B]

    Ground segments: 2 segments of L/3 each
    Satellite segments: 3 free-space hops (up, across, down)
    Inter-satellite: ~2000 km at LEO altitude
    """
    ground_third = L_km / 3
    n_per_segment = max(1, N_ground // 2)
    s_ground = ground_third / (n_per_segment + 1)

    # Ground segments
    ground_alpha = 2 * n_per_segment * alpha_fiber(s_ground, hw_ground)

    # Satellite hops: up, inter-satellite, down
    effective_up_down = sat_altitude_km * 1.2
    inter_sat_distance = L_km / 3  # rough: satellites separated by ~L/3 at altitude

    sat_alpha = 2 * alpha_freespace(effective_up_down, hw_sat) + alpha_freespace(
        inter_sat_distance, hw_sat
    )

    total_alpha = ground_alpha + sat_alpha

    info = {
        "type": "dual_satellite",
        "N_ground": N_ground,
        "s_ground_km": s_ground,
        "inter_sat_km": inter_sat_distance,
    }
    return math.exp(total_alpha), info


def topology_segmented(
    L_km: float,
    N_total: int,
    hw_ground: Dict[str, Any],
    hw_sat: Dict[str, Any],
    n_segments: int = 4,
    sat_altitude_km: float = 500,
) -> tuple[float, Dict[str, Any]]:
    """
    SEGMENTED MULTI-RELAY: The realistic architecture.

    Split the total route into n_segments fiber segments, each connected
    by satellite bridges. Each fiber segment is ~L/n_segments km with
    N_total/n_segments ground repeaters.

    Example for Beijing-London at 8,200 km with 4 segments:
      [Beijing] --2050km fiber-- [Urumqi] --sat bridge-- [Tehran]
      --2050km fiber-- [Tehran] --sat bridge-- [Istanbul]
      --2050km fiber-- [Istanbul] --sat bridge-- [Vienna]
      --2050km fiber-- [London]

    This is how a real quantum internet would work.
    """
    seg_length = L_km / n_segments
    n_per_segment = max(1, N_total // n_segments)
    s_ground = seg_length / (n_per_segment + 1)

    # Total ground alpha: n_segments fiber chains
    ground_alpha = n_segments * n_per_segment * alpha_fiber(s_ground, hw_ground)

    # Total satellite alpha: (n_segments - 1) satellite bridges
    # Each bridge: uplink (500km) + downlink (500km)
    effective_sat_distance = sat_altitude_km * 1.2
    sat_alpha = (n_segments - 1) * 2 * alpha_freespace(effective_sat_distance, hw_sat)

    total_alpha = ground_alpha + sat_alpha

    info = {
        "type": "segmented",
        "n_segments": n_segments,
        "seg_length_km": seg_length,
        "n_per_segment": n_per_segment,
        "s_ground_km": s_ground,
        "n_sat_bridges": n_segments - 1,
    }
    return math.exp(total_alpha), info


# ============================================================================
# SWEEP ENGINE
# ============================================================================


def sweep_topologies(
    L_km: float = 8200, N_range: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Compare fiber-only vs satellite-hybrid across N values.
    Tests all satellite hardware tiers.
    """
    if N_range is None:
        N_range = list(range(3, 31))

    results: Dict[str, Any] = {
        "N_range": N_range,
        "fiber_only": [],
        "sat_current": [],
        "sat_advanced": [],
        "sat_optimistic": [],
        "dual_sat_optimistic": [],
        "seg4_optimistic": [],
        "seg8_optimistic": [],
    }

    for N in N_range:
        # Fiber only (Willow everywhere — best case)
        f_fiber, _ = topology_fiber_only(L_km, N, HW_WILLOW)
        results["fiber_only"].append(f_fiber)

        # Single satellite at midpoint — 3 tiers
        f_cur, _ = topology_single_satellite(L_km, N, HW_WILLOW, HW_LEO_CURRENT)
        f_adv, _ = topology_single_satellite(L_km, N, HW_WILLOW, HW_LEO_ADVANCED)
        f_opt, _ = topology_single_satellite(L_km, N, HW_WILLOW, HW_LEO_OPTIMISTIC)
        results["sat_current"].append(f_cur)
        results["sat_advanced"].append(f_adv)
        results["sat_optimistic"].append(f_opt)

        # Dual satellite (optimistic only — best case)
        f_dual, _ = topology_dual_satellite(L_km, N, HW_WILLOW, HW_LEO_OPTIMISTIC)
        results["dual_sat_optimistic"].append(f_dual)

        # Segmented architectures (the key to closing the gap)
        f_seg4, _ = topology_segmented(
            L_km, N, HW_WILLOW, HW_LEO_OPTIMISTIC, n_segments=4
        )
        f_seg8, _ = topology_segmented(
            L_km, N, HW_WILLOW, HW_LEO_OPTIMISTIC, n_segments=8
        )
        results["seg4_optimistic"].append(f_seg4)
        results["seg8_optimistic"].append(f_seg8)

    return results


def find_minimum_N_for_sage(
    results: Dict[str, Any], topology_key: str
) -> Optional[int]:
    """Find the smallest N where fidelity >= SAGE_CONSTANT."""
    for i, f in enumerate(results[topology_key]):
        if f >= SAGE_CONSTANT:
            return results["N_range"][i]
    return None  # Never reaches Sage


def route_analysis(
    routes: Optional[Dict[str, float]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Analyze multiple intercontinental routes.
    Returns summary dict for each route.
    """
    if routes is None:
        routes = {
            "Beijing-London": 8_200,
            "Beijing-NYC": 11_000,
            "London-NYC": 5_500,
            "Tokyo-Berlin": 9_000,
            "Sydney-London": 17_000,
        }

    analysis: Dict[str, Dict[str, Any]] = {}
    for name, dist in routes.items():
        sweep = sweep_topologies(L_km=dist)

        min_N_fiber = find_minimum_N_for_sage(sweep, "fiber_only")
        min_N_opt = find_minimum_N_for_sage(sweep, "sat_optimistic")
        min_N_seg4 = find_minimum_N_for_sage(sweep, "seg4_optimistic")
        min_N_seg8 = find_minimum_N_for_sage(sweep, "seg8_optimistic")

        # Best achievable fidelity at N=30
        best_fiber = max(sweep["fiber_only"]) if sweep["fiber_only"] else 0
        best_sat = max(sweep["sat_optimistic"]) if sweep["sat_optimistic"] else 0
        best_seg4 = max(sweep["seg4_optimistic"]) if sweep["seg4_optimistic"] else 0
        best_seg8 = max(sweep["seg8_optimistic"]) if sweep["seg8_optimistic"] else 0

        analysis[name] = {
            "distance_km": dist,
            "min_N_fiber": min_N_fiber,
            "min_N_sat_opt": min_N_opt,
            "min_N_seg4": min_N_seg4,
            "min_N_seg8": min_N_seg8,
            "best_fiber_f": best_fiber,
            "best_sat_f": best_sat,
            "best_seg4_f": best_seg4,
            "best_seg8_f": best_seg8,
            "fiber_feasible": min_N_fiber is not None,
            "sat_feasible": min_N_opt is not None,
            "seg4_feasible": min_N_seg4 is not None,
            "seg8_feasible": min_N_seg8 is not None,
        }

    return analysis


# ============================================================================
# VISUALIZATION
# ============================================================================


def generate_satellite_atlas(
    results_8200: Dict[str, Any],
    route_analysis_data: Dict[str, Dict[str, Any]],
    save_path: str = "satellite_hybrid_atlas.png",
) -> str:
    """
    4-panel publication figure:
      Panel 1: Topology comparison (fiber vs satellite tiers) at 8,200 km
      Panel 2: Route feasibility matrix
      Panel 3: Satellite technology roadmap (p_gen vs achievable fidelity)
      Panel 4: The "Identity Bridge" — min N required per route
    """
    fig = plt.figure(figsize=(22, 14), facecolor=BG)
    fig.suptitle(
        "SATELLITE-HYBRID RELAY MODEL  --  Closing the Intercontinental Gap",
        color=GOLD,
        fontsize=18,
        fontweight="bold",
        y=0.98,
        fontfamily="monospace",
    )
    fig.text(
        0.5,
        0.955,
        '"Identity is a Signature, not a Substrate" -- CIRO Framework',
        ha="center",
        color=CYAN,
        fontsize=10,
        fontfamily="monospace",
        alpha=0.7,
    )

    gs = gridspec.GridSpec(
        2, 2, hspace=0.35, wspace=0.3, left=0.06, right=0.96, top=0.92, bottom=0.06
    )

    def style_ax(ax: plt.Axes, title: str) -> None:
        ax.set_facecolor(BG)
        ax.set_title(
            title,
            color=GOLD,
            fontsize=12,
            fontweight="bold",
            fontfamily="monospace",
            pad=10,
        )
        ax.tick_params(colors=WHITE, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(GRID)
        ax.grid(True, alpha=0.15, color=GRID)

    r = results_8200

    # ------------------------------------------------------------------
    # PANEL 1: Topology Comparison at 8,200 km
    # ------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1, "TOPOLOGY COMPARISON (Beijing-London, 8,200 km)")

    ax1.plot(
        r["N_range"],
        r["fiber_only"],
        color=RED,
        lw=2.5,
        label="Fiber Only (Willow)",
        marker="o",
        ms=3,
    )
    ax1.plot(
        r["N_range"],
        r["sat_current"],
        color="#9C27B0",
        lw=1.5,
        label="+ LEO 2024 (p=0.003)",
        ls="--",
    )
    ax1.plot(
        r["N_range"],
        r["sat_advanced"],
        color="#E040FB",
        lw=2.0,
        label="+ LEO 2027+ (p=0.01)",
        marker="s",
        ms=3,
    )
    ax1.plot(
        r["N_range"],
        r["sat_optimistic"],
        color="#CE93D8",
        lw=2.5,
        label="+ LEO 2030+ (p=0.05)",
        marker="D",
        ms=3,
    )
    ax1.plot(
        r["N_range"],
        r["dual_sat_optimistic"],
        color=CYAN,
        lw=2.0,
        label="Dual LEO 2030+",
        ls=":",
        marker="^",
        ms=3,
    )

    ax1.axhline(SAGE_CONSTANT, color=GOLD, ls="--", lw=1.5, alpha=0.5)
    ax1.text(
        28,
        SAGE_CONSTANT + 0.02,
        f"Sage ({SAGE_CONSTANT})",
        color=GOLD,
        fontsize=8,
        ha="right",
        fontfamily="monospace",
    )
    ax1.fill_between(r["N_range"], 0, SAGE_CONSTANT, alpha=0.05, color=RED)

    ax1.set_xlabel("Number of Ground Repeaters (N)", color=WHITE, fontsize=9)
    ax1.set_ylabel("End-to-End Fidelity", color=WHITE, fontsize=9)
    ax1.legend(
        fontsize=7,
        facecolor=BG,
        edgecolor=GRID,
        labelcolor=WHITE,
        framealpha=0.8,
        loc="upper left",
    )
    ax1.set_ylim(0, 1.05)

    # ------------------------------------------------------------------
    # PANEL 2: Route Feasibility Matrix
    # ------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2, "ROUTE FEASIBILITY MATRIX")

    routes = list(route_analysis_data.keys())
    distances = [route_analysis_data[r]["distance_km"] for r in routes]
    fiber_f = [route_analysis_data[r]["best_fiber_f"] for r in routes]
    sat_f = [route_analysis_data[r]["best_sat_f"] for r in routes]

    x = np.arange(len(routes))
    width = 0.35

    ax2.bar(x - width / 2, fiber_f, width, color=RED, alpha=0.8, label="Fiber Only")
    ax2.bar(
        x + width / 2,
        sat_f,
        width,
        color="#CE93D8",
        alpha=0.8,
        label="Sat-Hybrid (2030+)",
    )

    ax2.axhline(SAGE_CONSTANT, color=GOLD, ls="--", lw=1.5, alpha=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(
        [f"{r}\n({d:,} km)" for r, d in zip(routes, distances)], fontsize=7, color=WHITE
    )
    ax2.set_ylabel("Best Achievable Fidelity (N=30)", color=WHITE, fontsize=9)
    ax2.legend(
        fontsize=8, facecolor=BG, edgecolor=GRID, labelcolor=WHITE, framealpha=0.8
    )
    ax2.set_ylim(0, 1.1)

    # Annotate feasibility
    for i, route in enumerate(routes):
        rd = route_analysis_data[route]
        if rd["sat_feasible"]:
            ax2.text(
                i + width / 2,
                rd["best_sat_f"] + 0.02,
                "OK",
                ha="center",
                color=CYAN,
                fontsize=8,
                fontweight="bold",
            )
        else:
            ax2.text(
                i + width / 2,
                rd["best_sat_f"] + 0.02,
                "GAP",
                ha="center",
                color=RED,
                fontsize=8,
                fontweight="bold",
            )

    # ------------------------------------------------------------------
    # PANEL 3: Technology Roadmap (p_gen sensitivity)
    # ------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    style_ax(ax3, "SATELLITE TECHNOLOGY ROADMAP")

    p_gen_values = np.logspace(-3, -0.7, 50)  # 0.001 to 0.2
    N_fixed = 15
    L_fixed = 8200

    fidelities_by_p = []
    for p in p_gen_values:
        hw_test = cast(
            Dict[str, Any],
            {
                "F_gate": 0.9960,  # mid-range
                "T2": 0.300,
                "p_gen": p,
            },
        )
        f, _ = topology_single_satellite(L_fixed, N_fixed, HW_WILLOW, hw_test)
        fidelities_by_p.append(f)

    ax3.semilogx(p_gen_values, fidelities_by_p, color=CYAN, lw=2.5)
    ax3.axhline(SAGE_CONSTANT, color=GOLD, ls="--", lw=1.5, alpha=0.5)

    # Mark the three hardware tiers
    for hw, marker in [
        (HW_LEO_CURRENT, "o"),
        (HW_LEO_ADVANCED, "s"),
        (HW_LEO_OPTIMISTIC, "D"),
    ]:
        f_point, _ = topology_single_satellite(L_fixed, N_fixed, HW_WILLOW, hw)
        ax3.plot(
            hw["p_gen"],
            f_point,
            marker=marker,
            ms=12,
            color=hw["color"],
            markeredgecolor=WHITE,
            markeredgewidth=1.5,
            zorder=10,
        )
        ax3.text(
            hw["p_gen"] * 1.3,
            f_point,
            hw["label"],
            color=hw["color"],
            fontsize=8,
            fontfamily="monospace",
            va="center",
        )
    ax3.fill_between(p_gen_values, 0, SAGE_CONSTANT, alpha=0.05, color=RED)

    # Find critical p_gen
    for i, (p, f) in enumerate(zip(p_gen_values, fidelities_by_p)):
        if f >= SAGE_CONSTANT:
            ax3.axvline(p, color=GOLD, ls=":", alpha=0.4)
            ax3.text(
                p,
                0.1,
                f"p*={p:.3f}",
                color=GOLD,
                fontsize=8,
                fontfamily="monospace",
                rotation=90,
                va="bottom",
            )
            break

    ax3.set_xlabel("Satellite p_gen (log scale)", color=WHITE, fontsize=9)
    ax3.set_ylabel("Achievable Fidelity (N=15, 8200 km)", color=WHITE, fontsize=9)
    ax3.fill_between(p_gen_values, 0, SAGE_CONSTANT, alpha=0.05, color=RED)

    # Find critical p_gen
    for i, (p, f) in enumerate(zip(p_gen_values, fidelities_by_p)):
        if f >= SAGE_CONSTANT:
            ax3.axvline(p, color=GOLD, ls=":", alpha=0.4)
            ax3.text(
                p,
                0.1,
                f"p*={p:.3f}",
                color=GOLD,
                fontsize=8,
                fontfamily="monospace",
                rotation=90,
                va="bottom",
            )
            break

    # ------------------------------------------------------------------
    # PANEL 4: Min N Required
    # | Parameter | Current (Willow) | Required (8,200 km) | Improvement Factor |
    # |-----------|-----------------|--------------------|-----------------|
    # | p_gen | 0.10 | > 0.40 | 4× |
    # | T₂ | 1.0 s | > 10 s | 10× |
    # | F_gate | 0.9985 | ≥ 0.999 | ~2× error reduction |
    # ------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 1])
    style_ax(ax4, "THE IDENTITY BRIDGE: Min Repeaters Required")

    # For each route, find min N under satellite-optimistic
    route_distances = np.linspace(1000, 18000, 50)
    min_Ns: List[Optional[int]] = []
    for d in route_distances:
        found = False
        for N in range(3, 100):
            f, _ = topology_single_satellite(d, N, HW_WILLOW, HW_LEO_OPTIMISTIC)
            if f >= SAGE_CONSTANT:
                min_Ns.append(N)
                found = True
                break
        if not found:
            min_Ns.append(None)

    # Plot achievable routes
    valid_d = [d for d, n in zip(route_distances, min_Ns) if n is not None]
    valid_n = [n for n in min_Ns if n is not None]
    unreachable_d = [d for d, n in zip(route_distances, min_Ns) if n is None]

    if valid_d:
        ax4.plot(valid_d, valid_n, color=CYAN, lw=2.5, marker="o", ms=3)
    if unreachable_d:
        ax4.axvspan(min(unreachable_d), max(unreachable_d), alpha=0.1, color=RED)
        ax4.text(
            np.mean(unreachable_d),
            50,
            "UNREACHABLE\n(with LEO 2030+)",
            ha="center",
            color=RED,
            fontsize=9,
            fontweight="bold",
            fontfamily="monospace",
        )

    # Mark specific routes
    for name, rd in route_analysis_data.items():
        if rd["min_N_sat_opt"] is not None:
            ax4.plot(
                rd["distance_km"],
                rd["min_N_sat_opt"],
                "D",
                color=GOLD,
                ms=10,
                markeredgecolor=WHITE,
                markeredgewidth=1.5,
                zorder=10,
            )
            ax4.text(
                rd["distance_km"] + 200,
                rd["min_N_sat_opt"],
                f"{name}\n(N={rd['min_N_sat_opt']})",
                color=WHITE,
                fontsize=7,
                fontfamily="monospace",
            )

    ax4.set_xlabel("Route Distance (km)", color=WHITE, fontsize=9)
    ax4.set_ylabel("Minimum Repeater Nodes Required", color=WHITE, fontsize=9)
    ax4.set_xlim(0, 19000)

    # Save
    plt.savefig(save_path, dpi=180, facecolor=BG)
    print(f"  [Satellite-Hybrid] Atlas saved -> {save_path}")
    return save_path


# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 62)
    print("  SATELLITE-HYBRID RELAY MODEL")
    print("  Closing the Intercontinental Gap")
    print("=" * 62)

    print("\n  Sweeping topologies at 8,200 km (Beijing-London)...")
    results = sweep_topologies(L_km=8200)

    # Find critical thresholds
    for key, label in [
        ("fiber_only", "Fiber Only"),
        ("sat_current", "LEO 2024"),
        ("sat_advanced", "LEO 2027+"),
        ("sat_optimistic", "LEO 2030+"),
        ("dual_sat_optimistic", "Dual LEO 2030+"),
        ("seg4_optimistic", "4-Seg + LEO 2030+"),
        ("seg8_optimistic", "8-Seg + LEO 2030+"),
    ]:
        min_N = find_minimum_N_for_sage(results, key)
        best_f = max(results[key]) if results[key] else 0
        if min_N is not None and min_N >= 0:
            print(f"    {label:22s}  min N={min_N:3d}  best F={best_f:.4f}")
        else:
            print(f"    {label:22s}  UNFEASIBLE  best F={best_f:.4f}")

    print("\n  Analyzing intercontinental routes...")
    routes = route_analysis()

    print(
        f"\n  {'Route':<20s} {'Dist':>7s} {'Fiber':>8s} {'1-Sat':>8s}"
        f" {'4-Seg':>8s} {'8-Seg':>8s} {'Best':>8s}"
    )
    print("  " + "-" * 65)
    for name, rd_raw in routes.items():
        rd = cast(Dict[str, Any], rd_raw)
        best_vals = [
            float(rd.get("best_fiber_f", 0.0)),
            float(rd.get("best_sat_f", 0.0)),
            float(rd.get("best_seg4_f", 0.0)),
            float(rd.get("best_seg8_f", 0.0)),
        ]
        best = max(best_vals)
        feasible = "YES" if best >= SAGE_CONSTANT else "NO"
        print(
            f"  {name:<20s} {rd['distance_km']:>6,d}km"
            f" {rd['best_fiber_f']:>8.4f} {rd['best_sat_f']:>8.4f}"
            f" {rd['best_seg4_f']:>8.4f} {rd['best_seg8_f']:>8.4f}"
            f" {feasible:>5s}"
        )

    print("\n  Generating 4-panel atlas...")
    generate_satellite_atlas(results, routes)

    print("\n  Complete.")
