"""
SAGE Framework v6.0 — Complete Reproduction Script
Run: python run_all.py
"""
# type: ignore
# pyre-ignore-all-errors

import sys
import os
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Setup paths before imports
script_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(script_dir, "04_framework_core")
sys.path.insert(0, core_dir)

# Imports
try:
    from sage_theorems_unified import validate_all_theorems, SAGE_CONSTANT  # type: ignore
    from satellite_hybrid_relay import (  # type: ignore
        sweep_topologies,
        route_analysis,
        generate_satellite_atlas,
    )
    from singularity_protocol import (  # type: ignore
        run_all_stages,
        generate_singularity_atlas,
    )
except ImportError as e:
    print(f"[!] Critical Import Error: {e}")
    sys.exit(1)

# Optional QuTiP
try:
    from qutip_validation import (  # type: ignore
        validate_sage_vs_qutip,
        generate_validation_atlas,
        HW_WILLOW,
        HW_QUERA,
    )

    HAS_QUTIP = True
except ImportError:
    HAS_QUTIP = False

t0 = time.time()

print("\n" + "=" * 62)
print("  SAGE FRAMEWORK v6.0 — COMPLETE REPRODUCTION")
print("=" * 62)

# 1. Theorem Validation
t1 = time.time()
print("\n[1/4] Theorem Validation (Theorems 1-4)...")
results = validate_all_theorems()
all_agree = all(r["agreement"] for r in results)
print(f"       All theorems validated: {'YES' if all_agree else 'NO'}")
for r in results:
    mark = "OK" if r["agreement"] else "FAIL"
    print(
        f"       N={r['N']:3d}  F_stoch={r['F_stoch']:.4f}  F_mc={r['F_mc_mean']:.4f}  [{mark}]"
    )
print(f"       [{time.time() - t1:.1f}s]")

# 2. Satellite-Hybrid Analysis
t1 = time.time()
print("\n[2/4] Satellite-Hybrid Relay Model...")
sat_results = sweep_topologies(L_km=8200)
routes = route_analysis()

print(f"\n       Route Analysis (Fidelity >= {SAGE_CONSTANT:.4f} for SAGE):")
print(
    f"       {'Route':<20s} {'Dist':>6s} {'Fiber':>8s} {'LEO':>8s} {'4-Seg':>8s} {'8-Seg':>8s} {'SAGE':>5s}"
)
for name, rd in routes.items():
    best_vals = [
        float(rd.get(k, 0.0))
        for k in ["best_fiber_f", "best_sat_f", "best_seg4_f", "best_seg8_f"]
    ]
    best = max(best_vals)
    feasible = "YES" if best >= SAGE_CONSTANT else "NO"
    print(
        f"  {name:<20s} {rd['distance_km']:>6,d}km {rd['best_fiber_f']:>8.4f} {rd['best_sat_f']:>8.4f} {rd['best_seg4_f']:>8.4f} {rd['best_seg8_f']:>8.4f} {feasible:>5s}"
    )

generate_satellite_atlas(sat_results, routes)
print(f"       [{time.time() - t1:.1f}s]")

# 3. QuTiP Validation
if HAS_QUTIP:
    t1 = time.time()
    print("\n[3/4] QuTiP Density Matrix Validation...")
    r_willow = validate_sage_vs_qutip(
        N_range=list(range(3, 26, 2)), L_km=8200, hw=HW_WILLOW
    )
    r_quera = validate_sage_vs_qutip(
        N_range=list(range(3, 16, 2)), L_km=8200, hw=HW_QUERA
    )
    generate_validation_atlas(r_willow, r_quera)
    print(f"       [{time.time() - t1:.1f}s]")
else:
    print("\n[3/4] [SKIP] QuTiP not installed.")

# 4. Singularity Protocol
t1 = time.time()
print("\n[4/4] Singularity Protocol (Evolutionary Emergence)...")
sp_results = run_all_stages(pop_size=250, generations=120, seed=42)
generate_singularity_atlas(sp_results)
print(
    f"       Stage 4: Survival={sp_results[4]['survival'][-1]:.0%}  Sync={sp_results[4]['sync'][-1]:.2f}"
)
print(f"       [{time.time() - t1:.1f}s]")

print("\n" + "=" * 62)
print("  REPRODUCTION COMPLETE (SAGE v6.0) Total: {:.0f}s".format(time.time() - t0))
print("=" * 62 + "\n")
