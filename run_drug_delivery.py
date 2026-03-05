#!/usr/bin/env python3
"""
SAGE Drug Delivery LP Optimizer — Commercial Tool
===================================================
Computes the R&D Capital Allocation Matrix from Paper 3, §3:
"Pharmaceutical R&D Capital Allocation"

Revenue use-case:
  - Pharma R&D pipeline prioritization
  - Drug delivery vehicle selection
  - Barrier investment ranking (where to spend next R&D dollar)

Math (from Paper 3, §3.2):
  Bioavailability = exp(Σ log(T_barrier_i))
  α_i = log(T_barrier_i)  (log-decomposition)
  Marginal Return Index = |Δα_i| / Σ|α_i|

LP Optimization:
  min cost  subject to  Σ α_optimized_i ≥ log(B_threshold)
  where each barrier can be equipped with one delivery vehicle
"""

import argparse
import json
import math
import sys
from itertools import product as iterproduct

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ============================================================================
# BARRIER & VEHICLE DATA (from Paper 3, Table 2)
# ============================================================================

# Default: Oral drug targeting the brain (6 biological barriers)
DEFAULT_BARRIERS = [
    {"name": "Stomach Acid", "transmission_baseline": 0.60, "icon": "🧪"},
    {"name": "Intestinal Wall", "transmission_baseline": 0.30, "icon": "🧬"},
    {"name": "Liver First-Pass", "transmission_baseline": 0.50, "icon": "🫁"},
    {"name": "Blood-Brain Barrier", "transmission_baseline": 0.02, "icon": "🧠"},
    {"name": "Cellular Uptake", "transmission_baseline": 0.40, "icon": "🔬"},
    {"name": "Nuclear Entry", "transmission_baseline": 0.70, "icon": "⚛️"},
]

# Delivery vehicles and their barrier-specific improvements
DELIVERY_VEHICLES = {
    "none": {
        "label": "No Vehicle (Baseline)",
        "cost_per_barrier": 0,
        "improvements": {
            "Stomach Acid": 1.0,
            "Intestinal Wall": 1.0,
            "Liver First-Pass": 1.0,
            "Blood-Brain Barrier": 1.0,
            "Cellular Uptake": 1.0,
            "Nuclear Entry": 1.0,
        },
    },
    "viral_vector": {
        "label": "Viral Vector (AAV)",
        "cost_per_barrier": 50,  # M$ normalized
        "improvements": {
            "Stomach Acid": 0.90 / 0.60,  # → 90% transmission
            "Intestinal Wall": 0.60 / 0.30,  # → 60%
            "Liver First-Pass": 0.55 / 0.50,  # → 55% (modest for liver)
            "Blood-Brain Barrier": 0.03 / 0.02,  # → 3% (poor BBB crossing)
            "Cellular Uptake": 0.99 / 0.40,  # → 99% (viral vectors excel)
            "Nuclear Entry": 0.99 / 0.70,  # → 99%
        },
    },
    "nanoparticle": {
        "label": "Lipid Nanoparticle (LNP)",
        "cost_per_barrier": 35,
        "improvements": {
            "Stomach Acid": 0.75 / 0.60,  # → 75%
            "Intestinal Wall": 0.45 / 0.30,  # → 45%
            "Liver First-Pass": 0.60 / 0.50,  # → 60%
            "Blood-Brain Barrier": 0.10 / 0.02,  # → 10% (best for BBB!)
            "Cellular Uptake": 0.50 / 0.40,  # → 50%
            "Nuclear Entry": 0.75 / 0.70,  # → 75%
        },
    },
    "pegylated": {
        "label": "PEGylated Polymer",
        "cost_per_barrier": 20,
        "improvements": {
            "Stomach Acid": 0.70 / 0.60,  # → 70%
            "Intestinal Wall": 0.35 / 0.30,  # → 35%
            "Liver First-Pass": 0.99 / 0.50,  # → 99% (PEG avoids liver)
            "Blood-Brain Barrier": 0.025 / 0.02,  # → 2.5% (poor)
            "Cellular Uptake": 0.45 / 0.40,  # → 45%
            "Nuclear Entry": 0.99 / 0.70,  # → 99%
        },
    },
}


def log_decomposition(
    barriers: list[dict], vehicle_config: dict[str, str] | None = None
) -> dict:
    """
    Compute the log-decomposition (α_i) for each barrier.
    Optionally apply delivery vehicle improvements.
    """
    results = []
    total_log = 0.0

    for barrier in barriers:
        name = barrier["name"]
        t_base = barrier["transmission_baseline"]

        # Apply vehicle improvement if specified
        t_effective = t_base
        vehicle_used = "none"
        if vehicle_config and name in vehicle_config:
            veh_key = vehicle_config[name]
            if veh_key in DELIVERY_VEHICLES:
                improvement = DELIVERY_VEHICLES[veh_key]["improvements"].get(name, 1.0)
                t_effective = min(1.0, t_base * improvement)
                vehicle_used = veh_key

        alpha = math.log(max(t_effective, 1e-30))
        total_log += alpha

        results.append(
            {
                "barrier": name,
                "icon": barrier.get("icon", ""),
                "transmission_baseline": round(t_base, 4),
                "transmission_effective": round(t_effective, 4),
                "alpha": round(alpha, 4),
                "vehicle": vehicle_used,
            }
        )

    bioavailability = math.exp(total_log)

    return {
        "bioavailability": round(bioavailability * 100, 4),  # As percentage
        "total_log": round(total_log, 4),
        "barriers": results,
    }


def compute_allocation_matrix(barriers: list[dict]) -> dict:
    """
    Compute the R&D Capital Allocation Matrix.
    For each barrier × vehicle combination, calculate marginal return.
    """
    baseline = log_decomposition(barriers)
    total_alpha_baseline = sum(abs(b["alpha"]) for b in baseline["barriers"])

    matrix = []
    for barrier in barriers:
        name = barrier["name"]
        baseline_alpha = math.log(max(barrier["transmission_baseline"], 1e-30))

        for veh_key, vehicle in DELIVERY_VEHICLES.items():
            if veh_key == "none":
                continue

            improvement = vehicle["improvements"].get(name, 1.0)
            t_new = min(1.0, barrier["transmission_baseline"] * improvement)
            new_alpha = math.log(max(t_new, 1e-30))

            delta_alpha = new_alpha - baseline_alpha  # Positive = improvement
            pct_of_total = abs(baseline_alpha) / total_alpha_baseline * 100

            cost = vehicle["cost_per_barrier"]
            marginal_return = delta_alpha / cost if cost > 0 else 0.0

            matrix.append(
                {
                    "barrier": name,
                    "vehicle": veh_key,
                    "vehicle_label": vehicle["label"],
                    "alpha_baseline": round(baseline_alpha, 4),
                    "alpha_optimized": round(new_alpha, 4),
                    "delta_alpha": round(delta_alpha, 4),
                    "pct_of_total_loss": round(pct_of_total, 1),
                    "cost": cost,
                    "marginal_return_per_dollar": round(marginal_return, 6),
                }
            )

    # Sort by marginal return (best first)
    matrix.sort(key=lambda x: x["marginal_return_per_dollar"], reverse=True)

    return {
        "baseline_bioavailability": baseline["bioavailability"],
        "total_alpha_baseline": round(total_alpha_baseline, 4),
        "allocation_matrix": matrix,
    }


def find_optimal_vehicle_selection(barriers: list[dict]) -> dict:
    """
    Exhaustive search (tractable for ≤6 barriers × ≤4 vehicles = 4^6 = 4096 combos)
    to find the globally optimal vehicle assignment.
    """
    vehicle_keys = list(DELIVERY_VEHICLES.keys())
    n_barriers = len(barriers)

    best_config = None
    best_bio = -1
    best_cost = float("inf")

    # Also track best single-vehicle strategy
    best_single = None
    best_single_bio = -1

    for combo in iterproduct(vehicle_keys, repeat=n_barriers):
        config = {barriers[i]["name"]: combo[i] for i in range(n_barriers)}
        result = log_decomposition(barriers, config)
        bio = result["bioavailability"]

        # Total cost
        total_cost = sum(
            DELIVERY_VEHICLES[combo[i]]["cost_per_barrier"] for i in range(n_barriers)
        )

        if bio > best_bio or (bio == best_bio and total_cost < best_cost):
            best_bio = bio
            best_cost = total_cost
            best_config = config

        # Check single-vehicle strategies
        if len(set(combo)) == 1:
            if bio > best_single_bio:
                best_single_bio = bio
                best_single = combo[0]

    # Get detailed breakdown for optimal
    optimal_result = log_decomposition(barriers, best_config)
    baseline_result = log_decomposition(barriers)
    single_result = log_decomposition(
        barriers, {b["name"]: best_single for b in barriers} if best_single else None
    )

    return {
        "baseline": {
            "bioavailability": baseline_result["bioavailability"],
            "config": "No vehicles",
        },
        "best_single_vehicle": {
            "bioavailability": single_result["bioavailability"],
            "vehicle": best_single,
            "vehicle_label": DELIVERY_VEHICLES[best_single]["label"]
            if best_single
            else "None",
            "improvement_vs_baseline": round(
                single_result["bioavailability"]
                / max(baseline_result["bioavailability"], 1e-10),
                1,
            ),
        },
        "lp_optimal": {
            "bioavailability": optimal_result["bioavailability"],
            "config": best_config,
            "total_cost": best_cost,
            "improvement_vs_baseline": round(
                optimal_result["bioavailability"]
                / max(baseline_result["bioavailability"], 1e-10),
                1,
            ),
            "improvement_vs_single": round(
                optimal_result["bioavailability"]
                / max(single_result["bioavailability"], 1e-10),
                1,
            ),
            "barriers": optimal_result["barriers"],
        },
    }


def run_analysis(barriers: list[dict]) -> dict:
    """Full drug delivery analysis."""
    allocation = compute_allocation_matrix(barriers)
    optimization = find_optimal_vehicle_selection(barriers)

    return {
        "allocation_matrix": allocation,
        "optimization": optimization,
        "sage_version": "6.0",
        "model": "drug_delivery_lp",
        "paper": "Paper 3: The Stochastic Penalty in Sequential Systems, §3",
    }


# ============================================================================
# CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="SAGE Drug Delivery LP Optimizer — R&D Capital Allocation"
    )
    parser.add_argument(
        "--target",
        type=str,
        default="brain",
        choices=["brain"],
        help="Target organ (currently: brain)",
    )
    parser.add_argument(
        "--barriers-json",
        type=str,
        default=None,
        help="JSON file with custom barrier definitions",
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as raw JSON (for API consumption)",
    )

    args = parser.parse_args()

    # --- Input Validation ---
    if args.barriers_json:
        try:
            with open(args.barriers_json) as f:
                barriers = json.load(f)
        except FileNotFoundError:
            parser.error(f"Barriers file not found: {args.barriers_json}")
        except json.JSONDecodeError as e:
            parser.error(f"Invalid JSON in barriers file: {e}")
        # Validate barrier structure
        required_keys = {"name", "transmission_baseline"}
        for i, barrier in enumerate(barriers):
            missing = required_keys - set(barrier.keys())
            if missing:
                parser.error(f"Barrier {i + 1} missing required keys: {missing}")
            if not (0.0 < barrier["transmission_baseline"] <= 1.0):
                parser.error(
                    f"Barrier {i + 1} transmission_baseline must be in (0, 1], "
                    f"got {barrier['transmission_baseline']}"
                )
    else:
        barriers = DEFAULT_BARRIERS

    result = run_analysis(barriers)

    if args.json_output:
        print(json.dumps(result, indent=2))
        return result

    # Pretty print
    alloc = result["allocation_matrix"]
    opt = result["optimization"]

    print("💊 SAGE Drug Delivery LP Optimizer v6.0")
    print("=" * 65)
    print(f"  Target: Oral → Brain ({len(barriers)} biological barriers)")
    print(f"  Baseline Bioavailability: {alloc['baseline_bioavailability']:.4f}%")
    print()

    # Allocation Matrix (Top 10)
    print("📊 R&D Capital Allocation Matrix (Top 10 by Marginal Return):")
    print(
        f"  {'Barrier':<22} {'Vehicle':<22} {'Δα':>6} {'% Loss':>7} {'Return/$ ':>10}"
    )
    print("  " + "-" * 70)
    for entry in alloc["allocation_matrix"][:10]:
        print(
            f"  {entry['barrier']:<22} {entry['vehicle_label']:<22} "
            f"{entry['delta_alpha']:>+6.3f} {entry['pct_of_total_loss']:>6.1f}% "
            f"{entry['marginal_return_per_dollar']:>9.5f}"
        )

    print()
    print("🏆 Optimization Results:")
    print("=" * 65)

    bl = opt["baseline"]
    sv = opt["best_single_vehicle"]
    lp = opt["lp_optimal"]

    print(f"  {'Strategy':<35} {'Bioavailability':>15} {'Improvement':>12}")
    print("  " + "-" * 65)
    print(f"  {'No vehicle (baseline)':<35} {bl['bioavailability']:>14.4f}% {'—':>12}")
    print(
        f"  {'Best single (' + sv['vehicle_label'][:15] + ')':<35} {sv['bioavailability']:>14.4f}% {str(sv['improvement_vs_baseline']) + '×':>12}"
    )
    print(
        f"  {'LP-optimal mixed strategy':<35} {lp['bioavailability']:>14.4f}% {str(lp['improvement_vs_baseline']) + '×':>12}"
    )

    print()
    print(f"  LP advantage over best single vehicle: {lp['improvement_vs_single']}×")
    print(f"  Total R&D cost (LP-optimal): ${lp['total_cost']}M")

    print()
    print("  LP-Optimal Vehicle Assignment:")
    for b in lp["barriers"]:
        veh = DELIVERY_VEHICLES.get(b["vehicle"], {})
        label = veh.get("label", b["vehicle"]) if veh else b["vehicle"]
        print(
            f"    {b['icon']} {b['barrier']:<22} → {label:<22} "
            f"(T: {b['transmission_baseline']:.2f} → {b['transmission_effective']:.2f})"
        )

    return result


if __name__ == "__main__":
    main()
