#!/usr/bin/env python3
"""
SAGE Cold Chain Simulator — Commercial Tool
============================================
Models an N-stage vaccine supply chain using the Stochastic Penalty (1+1/p)
from Paper 3: "The Stochastic Penalty in Sequential Systems."

Revenue use-case:
  - WHO / NGO cold chain audits
  - Pharma logistics optimization
  - Insurance risk quantification for vaccine shipments

Math (from Paper 3, §2):
  Potency_total = exp(Σ log(r_i) * (1 + 1/p_i))
  where:
    r_i = base retention at stage i (thermal degradation)
    p_i = power grid reliability at stage i
    (1+1/p_i) = one-way stochastic penalty (cold chain variant)
"""

import argparse
import json
import math
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ============================================================================
# CORE MATH
# ============================================================================

# Default 5-stage cold chain from Paper 3 §2.3
DEFAULT_STAGES = [
    {
        "name": "Manufacturer → National",
        "base_retention": 0.98,
        "grid_reliability": 0.99,
        "temp_tolerance_hrs": 48,
    },
    {
        "name": "National → Regional",
        "base_retention": 0.95,
        "grid_reliability": 0.95,
        "temp_tolerance_hrs": 24,
    },
    {
        "name": "Regional → District",
        "base_retention": 0.90,
        "grid_reliability": 0.80,
        "temp_tolerance_hrs": 12,
    },
    {
        "name": "District → Health Post",
        "base_retention": 0.85,
        "grid_reliability": 0.60,
        "temp_tolerance_hrs": 8,
    },
    {
        "name": "Health Post → Outreach",
        "base_retention": 0.80,
        "grid_reliability": 0.40,
        "temp_tolerance_hrs": 4,
    },
]

# Upgrade options with costs (normalized units)
UPGRADE_OPTIONS = {
    "solar_cold_box": {
        "reliability_boost": 0.45,
        "cost": 500,
        "label": "Solar Cold Box",
    },
    "backup_generator": {
        "reliability_boost": 0.30,
        "cost": 1200,
        "label": "Backup Generator",
    },
    "phase_change_pack": {
        "reliability_boost": 0.15,
        "cost": 150,
        "label": "Phase-Change Cooling Packs",
    },
    "insulated_container": {
        "reliability_boost": 0.05,
        "cost": 80,
        "label": "Better Insulated Container",
    },
}

CLINICAL_THRESHOLD = 0.50  # Minimum potency for clinical efficacy


def stochastic_penalty(p: float) -> float:
    """The cold chain stochastic penalty: (1 + 1/p).
    One-way disruption (vs quantum's round-trip 1+2/p)."""
    if p <= 0:
        return float("inf")
    return 1.0 + (1.0 / p)


def stage_log_potency(base_retention: float, grid_reliability: float) -> float:
    """Log-potency contribution for a single stage under stochastic penalty."""
    if base_retention <= 0:
        return -100.0
    penalty = stochastic_penalty(grid_reliability)
    return math.log(base_retention) * penalty


def end_to_end_potency(stages: list[dict]) -> dict:
    """
    Calculate end-to-end vaccine potency across all stages.
    Returns detailed per-stage breakdown + total.
    """
    total_log = 0.0
    breakdown = []

    for i, stage in enumerate(stages):
        r = stage["base_retention"]
        p = stage["grid_reliability"]
        penalty = stochastic_penalty(p)
        log_contrib = stage_log_potency(r, p)
        total_log += log_contrib

        # Deterministic comparison (no power failures)
        det_log = math.log(r) if r > 0 else -100.0

        breakdown.append(
            {
                "stage": i + 1,
                "name": stage["name"],
                "base_retention": r,
                "grid_reliability": p,
                "penalty": round(penalty, 2),
                "log_contribution": round(log_contrib, 6),
                "det_log_contribution": round(det_log, 6),
                "penalty_amplification": round(penalty, 2),
                "cumulative_potency": round(math.exp(total_log), 4),
            }
        )

    total_potency = math.exp(total_log)

    # Deterministic baseline (no stochastic penalty)
    det_total = math.exp(
        sum(math.log(s["base_retention"]) for s in stages if s["base_retention"] > 0)
    )

    return {
        "total_potency": round(total_potency, 4),
        "deterministic_potency": round(det_total, 4),
        "stochastic_loss": round(det_total - total_potency, 4),
        "feasible": total_potency >= CLINICAL_THRESHOLD,
        "clinical_threshold": CLINICAL_THRESHOLD,
        "n_stages": len(stages),
        "breakdown": breakdown,
    }


def find_optimal_upgrades(stages: list[dict], budget: float) -> dict:
    """
    LP-inspired greedy optimizer: finds the best stage upgrades
    to maximize end-to-end potency within a budget.

    Strategy: rank stages by marginal return per dollar spent on
    reliability improvements, then greedily allocate.
    """
    # Calculate marginal return for each upgrade at each stage
    candidates = []
    for i, stage in enumerate(stages):
        p_current = stage["grid_reliability"]
        for upgrade_key, upgrade in UPGRADE_OPTIONS.items():
            p_new = min(1.0, p_current + upgrade["reliability_boost"])
            if p_new <= p_current:
                continue  # No improvement

            # Marginal improvement in log-potency
            current_log = stage_log_potency(stage["base_retention"], p_current)
            new_log = stage_log_potency(stage["base_retention"], p_new)
            delta_log = new_log - current_log  # Should be positive (less negative)

            if delta_log > 0 and upgrade["cost"] > 0:
                marginal_return = delta_log / upgrade["cost"]
                candidates.append(
                    {
                        "stage_idx": i,
                        "stage_name": stage["name"],
                        "upgrade": upgrade_key,
                        "upgrade_label": upgrade["label"],
                        "cost": upgrade["cost"],
                        "delta_log_potency": round(delta_log, 6),
                        "marginal_return_per_dollar": round(marginal_return, 8),
                        "new_reliability": round(p_new, 4),
                    }
                )

    # Sort by marginal return (best first)
    candidates.sort(key=lambda x: x["marginal_return_per_dollar"], reverse=True)

    # Greedy allocation
    remaining_budget = budget
    selected_upgrades = []
    upgraded_stages = [dict(s) for s in stages]  # Deep copy

    for candidate in candidates:
        if candidate["cost"] <= remaining_budget:
            idx = candidate["stage_idx"]
            # Check if this stage was already upgraded
            already_upgraded = any(u["stage_idx"] == idx for u in selected_upgrades)
            if already_upgraded:
                continue

            selected_upgrades.append(candidate)
            remaining_budget -= candidate["cost"]
            upgraded_stages[idx]["grid_reliability"] = candidate["new_reliability"]

    # Calculate new potency
    original_result = end_to_end_potency(stages)
    upgraded_result = end_to_end_potency(upgraded_stages)

    return {
        "original_potency": original_result["total_potency"],
        "upgraded_potency": upgraded_result["total_potency"],
        "improvement": round(
            upgraded_result["total_potency"] - original_result["total_potency"], 4
        ),
        "improvement_factor": round(
            upgraded_result["total_potency"]
            / max(original_result["total_potency"], 1e-10),
            2,
        ),
        "budget": budget,
        "spent": round(budget - remaining_budget, 2),
        "remaining": round(remaining_budget, 2),
        "feasible_after_upgrade": upgraded_result["feasible"],
        "selected_upgrades": selected_upgrades,
        "all_candidates_ranked": candidates[:10],  # Top 10 for reference
    }


def run_analysis(stages: list[dict], budget: float = 1000.0) -> dict:
    """Full cold chain analysis: potency + optimization."""
    potency = end_to_end_potency(stages)
    optimization = find_optimal_upgrades(stages, budget)

    return {
        "potency_analysis": potency,
        "optimization": optimization,
        "sage_version": "6.0",
        "model": "cold_chain_stochastic_penalty",
        "paper": "Paper 3: The Stochastic Penalty in Sequential Systems",
    }


# ============================================================================
# CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="SAGE Cold Chain Simulator — Vaccine Supply Chain Analysis"
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=1000.0,
        help="Budget for infrastructure upgrades (in normalized cost units)",
    )
    parser.add_argument(
        "--stages-json",
        type=str,
        default=None,
        help="JSON file with custom stage definitions",
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as raw JSON (for API consumption)",
    )

    args = parser.parse_args()

    # Load stages
    if args.stages_json:
        with open(args.stages_json) as f:
            stages = json.load(f)
    else:
        stages = DEFAULT_STAGES

    # Run analysis
    result = run_analysis(stages, args.budget)

    if args.json_output:
        print(json.dumps(result, indent=2))
        return result

    # Pretty print
    potency = result["potency_analysis"]
    opt = result["optimization"]

    print("🧊 SAGE Cold Chain Simulator v6.0")
    print("=" * 60)
    print(f"  Stages: {potency['n_stages']}")
    print(f"  Clinical Threshold: {CLINICAL_THRESHOLD:.0%}")
    print()

    print("📊 Per-Stage Breakdown:")
    print(
        f"  {'#':<3} {'Stage':<30} {'Ret':>5} {'Grid':>5} {'Penalty':>8} {'Cumulative':>11}"
    )
    print("  " + "-" * 67)
    for s in potency["breakdown"]:
        status = "✅" if s["cumulative_potency"] >= CLINICAL_THRESHOLD else "❌"
        print(
            f"  {s['stage']:<3} {s['name']:<30} {s['base_retention']:>5.2f} "
            f"{s['grid_reliability']:>5.2f} {s['penalty']:>7.2f}× "
            f"{s['cumulative_potency']:>9.1%} {status}"
        )

    print()
    print(
        f"  Deterministic Potency (no outages):  {potency['deterministic_potency']:.1%}"
    )
    print(f"  Stochastic Potency (with outages):   {potency['total_potency']:.1%}")
    print(f"  Stochastic Loss:                     {potency['stochastic_loss']:.1%}")
    status = "✅ FEASIBLE" if potency["feasible"] else "❌ INFEASIBLE"
    print(f"  Clinical Feasibility:                {status}")

    print()
    print(f"💰 Optimization (Budget: ${args.budget:.0f})")
    print("=" * 60)

    if opt["selected_upgrades"]:
        for u in opt["selected_upgrades"]:
            print(
                f"  → Stage {u['stage_idx'] + 1} ({u['stage_name']}): {u['upgrade_label']}"
            )
            print(
                f"    Cost: ${u['cost']}  |  Grid: → {u['new_reliability']:.0%}  |  Return: {u['marginal_return_per_dollar']:.6f}/dollar"
            )
        print()
        print(f"  Original Potency:  {opt['original_potency']:.1%}")
        print(f"  Upgraded Potency:  {opt['upgraded_potency']:.1%}")
        print(f"  Improvement:       {opt['improvement_factor']}×")
        print(f"  Budget Spent:      ${opt['spent']:.0f} / ${opt['budget']:.0f}")
        status = (
            "✅ FEASIBLE" if opt["feasible_after_upgrade"] else "❌ STILL INFEASIBLE"
        )
        print(f"  After Upgrade:     {status}")
    else:
        print("  No beneficial upgrades found within budget.")

    return result


if __name__ == "__main__":
    main()
