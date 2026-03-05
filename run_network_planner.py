#!/usr/bin/env python3
"""
SAGE Multi-Route Network Planner — Commercial Tool
====================================================
Interactive CLI for quantum network feasibility analysis.
Wires together satellite_hybrid_relay.py topologies + little_guy_optimizer.py.

Revenue use-case:
  - Telecom infrastructure planning
  - Government quantum network RFPs
  - Defense/intelligence secure communication feasibility studies
  - Academic grant proposals (provide hard numbers)

Usage:
  python run_network_planner.py --route beijing-london
  python run_network_planner.py --distance 11000
  python run_network_planner.py --list-routes
"""

import argparse
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.sage_theorems_unified import SAGE_CONSTANT
from src.satellite_hybrid_relay import (
    topology_fiber_only,
    topology_single_satellite,
    topology_dual_satellite,
    topology_segmented,
    HW_WILLOW,
    HW_QUERA,
    HW_LEO_CURRENT,
    HW_LEO_ADVANCED,
    HW_LEO_OPTIMISTIC,
)
from src.little_guy_optimizer import optimize_heterogeneous_mix

# ============================================================================
# PRESET ROUTES
# ============================================================================

PRESET_ROUTES = {
    "beijing-london": {"distance": 8200, "label": "Beijing → London"},
    "beijing-nyc": {"distance": 11000, "label": "Beijing → New York City"},
    "london-nyc": {"distance": 5570, "label": "London → New York City"},
    "tokyo-berlin": {"distance": 9000, "label": "Tokyo → Berlin"},
    "sydney-london": {"distance": 17000, "label": "Sydney → London"},
    "sf-tokyo": {"distance": 8300, "label": "San Francisco → Tokyo"},
    "mumbai-london": {"distance": 7200, "label": "Mumbai → London"},
    "moscow-beijing": {"distance": 5800, "label": "Moscow → Beijing"},
}

SATELLITE_TIERS = {
    "LEO_current": {
        "hw": HW_LEO_CURRENT,
        "label": "LEO Current (Micius-class, p=0.003)",
    },
    "LEO_2027": {"hw": HW_LEO_ADVANCED, "label": "LEO 2027+ (Next-gen, p=0.01)"},
    "LEO_optimistic": {
        "hw": HW_LEO_OPTIMISTIC,
        "label": "LEO 2030+ (Optimistic, p=0.05)",
    },
}


def analyze_route(
    distance_km: float, label: str = "Custom Route", satellite_tier: str = "LEO_2027"
) -> dict:
    """
    Full feasibility analysis for a given route distance.
    Tests fiber-only, single-satellite, dual-satellite, and segmented topologies.
    """
    sat_info = SATELLITE_TIERS.get(satellite_tier, SATELLITE_TIERS["LEO_2027"])
    sat_hw = sat_info["hw"]
    sat_label = sat_info["label"]

    results = {
        "route": label,
        "distance_km": distance_km,
        "sage_constant": SAGE_CONSTANT,
        "satellite_tier": sat_label,
        "topologies": {},
    }

    # --- Topology 1: Fiber Only ---
    fiber_best = {"N": None, "fidelity": 0}
    fiber_sweep = []
    for N in [10, 15, 20, 25, 30, 40, 50, 75, 100]:
        fid, info = topology_fiber_only(distance_km, N, dict(HW_WILLOW))
        feasible = fid >= SAGE_CONSTANT
        fiber_sweep.append({"N": N, "fidelity": round(fid, 6), "feasible": feasible})
        if fid > fiber_best["fidelity"]:
            fiber_best = {"N": N, "fidelity": round(fid, 6)}

    results["topologies"]["fiber_only"] = {
        "label": "Pure Fiber (Willow nodes)",
        "best": fiber_best,
        "feasible": fiber_best["fidelity"] >= SAGE_CONSTANT,
        "sweep": fiber_sweep,
    }

    # --- Topology 2: Single Satellite ---
    single_best = {"N": None, "fidelity": 0}
    single_sweep = []
    for N in [10, 15, 20, 25, 30, 40]:
        fid, info = topology_single_satellite(
            distance_km, N, dict(HW_WILLOW), dict(sat_hw)
        )
        feasible = fid >= SAGE_CONSTANT
        single_sweep.append(
            {"N_ground": N, "fidelity": round(fid, 6), "feasible": feasible}
        )
        if fid > single_best["fidelity"]:
            single_best = {"N_ground": N, "fidelity": round(fid, 6)}

    results["topologies"]["single_satellite"] = {
        "label": f"Single LEO ({sat_label})",
        "best": single_best,
        "feasible": single_best["fidelity"] >= SAGE_CONSTANT,
        "sweep": single_sweep,
    }

    # --- Topology 3: Dual Satellite ---
    dual_best = {"N": None, "fidelity": 0}
    dual_sweep = []
    for N in [10, 15, 20, 25, 30]:
        fid, info = topology_dual_satellite(
            distance_km, N, dict(HW_WILLOW), dict(sat_hw)
        )
        feasible = fid >= SAGE_CONSTANT
        dual_sweep.append(
            {"N_ground": N, "fidelity": round(fid, 6), "feasible": feasible}
        )
        if fid > dual_best["fidelity"]:
            dual_best = {"N_ground": N, "fidelity": round(fid, 6)}

    results["topologies"]["dual_satellite"] = {
        "label": f"Dual LEO ({sat_label})",
        "best": dual_best,
        "feasible": dual_best["fidelity"] >= SAGE_CONSTANT,
        "sweep": dual_sweep,
    }

    # --- Topology 4: Segmented (3-6 segments) ---
    seg_best = {"N": None, "segments": None, "fidelity": 0}
    seg_sweep = []
    for n_seg in [3, 4, 5, 6]:
        for N in [20, 30, 40, 50]:
            fid, info = topology_segmented(
                distance_km, N, dict(HW_WILLOW), dict(sat_hw), n_segments=n_seg
            )
            feasible = fid >= SAGE_CONSTANT
            seg_sweep.append(
                {
                    "N_total": N,
                    "segments": n_seg,
                    "fidelity": round(fid, 6),
                    "feasible": feasible,
                }
            )
            if fid > seg_best["fidelity"]:
                seg_best = {"N": N, "segments": n_seg, "fidelity": round(fid, 6)}

    results["topologies"]["segmented"] = {
        "label": f"Segmented Multi-Relay ({sat_label})",
        "best": seg_best,
        "feasible": seg_best["fidelity"] >= SAGE_CONSTANT,
        "sweep": seg_sweep,
    }

    # --- Heterogeneous Mix ---
    het_results = []
    for n_total in [20, 30, 40, 50]:
        r = optimize_heterogeneous_mix(distance_km, n_total)
        het_results.append(r)
    results["heterogeneous_optimization"] = het_results

    # --- Overall Verdict ---
    any_feasible = any(t["feasible"] for t in results["topologies"].values())
    best_topology = max(
        results["topologies"].items(), key=lambda x: x[1]["best"]["fidelity"]
    )

    results["verdict"] = {
        "feasible": any_feasible,
        "best_topology": best_topology[0],
        "best_topology_label": best_topology[1]["label"],
        "best_fidelity": best_topology[1]["best"]["fidelity"],
        "best_config": best_topology[1]["best"],
    }

    return results


# ============================================================================
# CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="SAGE Multi-Route Network Planner — Quantum Network Feasibility"
    )
    parser.add_argument(
        "--route",
        type=str,
        default=None,
        choices=list(PRESET_ROUTES.keys()),
        help="Preset route (e.g., beijing-london, beijing-nyc)",
    )
    parser.add_argument(
        "--distance",
        type=float,
        default=None,
        help="Custom distance in km (overrides --route)",
    )
    parser.add_argument(
        "--satellite-tier",
        type=str,
        default="LEO_2027",
        choices=list(SATELLITE_TIERS.keys()),
        help="Satellite hardware tier",
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as raw JSON (for API consumption)",
    )
    parser.add_argument(
        "--list-routes", action="store_true", help="List all preset routes and exit"
    )

    args = parser.parse_args()

    if args.list_routes:
        print("📍 Available Preset Routes:")
        for key, route in PRESET_ROUTES.items():
            print(f"  {key:<20} {route['label']:<30} ({route['distance']:,} km)")
        return

    # Determine distance
    if args.distance:
        distance = args.distance
        label = f"Custom Route ({distance:.0f} km)"
    elif args.route:
        route = PRESET_ROUTES[args.route]
        distance = route["distance"]
        label = route["label"]
    else:
        route = PRESET_ROUTES["beijing-london"]
        distance = route["distance"]
        label = route["label"]

    result = analyze_route(distance, label, args.satellite_tier)

    if args.json_output:
        print(json.dumps(result, indent=2))
        return result

    # Pretty print
    v = result["verdict"]
    print("🛰️  SAGE Multi-Route Network Planner v6.0")
    print("=" * 65)
    print(f"  Route: {label}")
    print(f"  Distance: {distance:,.0f} km")
    print(f"  Satellite Tier: {SATELLITE_TIERS[args.satellite_tier]['label']}")
    print(f"  SAGE Constant: {SAGE_CONSTANT}")
    print()

    # Topology comparison
    print("📊 Topology Comparison:")
    print(f"  {'Topology':<45} {'Best F':>8} {'Status':>12}")
    print("  " + "-" * 68)

    for key, topo in result["topologies"].items():
        best_f = topo["best"]["fidelity"]
        status = "✅ FEASIBLE" if topo["feasible"] else "❌ INFEASIBLE"
        marker = " ★" if key == v["best_topology"] else ""
        print(f"  {topo['label']:<45} {best_f:>8.4f} {status:>12}{marker}")

    # Verdict
    print()
    print("🏆 VERDICT:")
    print("=" * 65)
    if v["feasible"]:
        print(f"  ✅ ROUTE IS FEASIBLE via {v['best_topology_label']}")
        print(f"     Best fidelity: {v['best_fidelity']:.4f} (above {SAGE_CONSTANT})")
        cfg = v["best_config"]
        for k, val in cfg.items():
            if k != "fidelity":
                print(f"     {k}: {val}")
    else:
        print(f"  ❌ ROUTE IS INFEASIBLE with current hardware")
        print(f"     Best achievable: {v['best_fidelity']:.4f} (need {SAGE_CONSTANT})")
        print(f"     Recommendation: Upgrade satellite tier or reduce distance.")

    # Heterogeneous mix
    print()
    print("🔧 Heterogeneous Node Optimization (Fiber-Only):")
    for h in result["heterogeneous_optimization"]:
        if h["feasible"]:
            print(
                f"  n_total={h['n_total']:3d} → Willow={h['n_willow']:2d} "
                f"({h['willow_fraction']:.0%}) + QuEra={h['n_quera']:2d} "
                f"| F={h['fidelity']:.4f} ✅"
            )
        else:
            print(f"  n_total={h['n_total']:3d} → Infeasible at all Willow ratios ❌")

    return result


if __name__ == "__main__":
    main()
