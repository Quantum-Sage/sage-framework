import json
import argparse
import numpy as np
from src.sage_bound_logic import calculate_sage_bound, SAGE_CONSTANT
from src.availability_gap_model import calculate_survival_probability

def run_vv_benchmark(profile_path):
    # 1. Load Hardware Profile
    with open(profile_path, 'r') as f:
        profile = json.load(f)
    
    print("\n" + "="*60)
    print(f"📊 SAGE V&V BENCHMARK: {profile['name']}")
    print(f"Architecture: {profile['architecture']}")
    print("="*60)
    
    # 2. Extract Params
    f_node = profile['fidelity_node']
    p_gen = profile['p_gen']
    max_hops = profile.get('max_hops', 16)
    
    # 3. Calculate Performance Curve
    print(f"\n[SPECS] Node Fidelity: {f_node:.4e} | Gen Prob: {p_gen:.4f}")
    print("-" * 60)
    print(f"{'Hops':<6} | {'Theoretical Fidelity':<20} | {'Status':<10} | {'Risk Mitigation'}")
    print("-" * 60)
    
    snapping_point = None
    for n in range(1, max_hops + 1):
        bound = calculate_sage_bound(n, f_node, p_gen)
        status = "✨ PASS" if bound >= SAGE_CONSTANT else "❌ FAIL"
        
        # Identify the first point of failure
        if bound < SAGE_CONSTANT and snapping_point is None:
            snapping_point = n
            
        risk_msg = "Sufficient" if bound >= SAGE_CONSTANT else "MESH MANDATORY"
        print(f"{n:<6} | {bound:<20.4f} | {status:<10} | {risk_msg}")

    # 4. Reliability Divergence (The No-Cloning Gap)
    gap_results = calculate_survival_probability(30.0) # 30-day MTBF
    
    # 5. DARPA-Spec Risk Report Summary
    print("\n" + "="*60)
    print("🛡️ DARPA STAGE B RISK MITIGATION SUMMARY")
    print("="*60)
    if snapping_point:
        print(f"CRITICAL SNAP POINT: Node N={snapping_point}")
        print(f"REASON: Cumulative decoherence exceeds SAGE Constant (S=0.851).")
        print(f"AVAILABILITY RISK: {gap_results['gap_magnitude']} Reliability Divergence.")
        print(f"MITIGATION: Topological Mesh Consensus (SAGE Layer 2) is REQUIRED.")
    else:
        print("STATUS: Architecture stable within 16-node transcontinental reach.")
        print("V&V RATING: Low Risk - Utility Scale Feasible.")
    
    print("\n[VERIFICATION] Based on Sequential Degradation Bound (Sage Bound 2026).")
    print("="*60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAGE V&V Benchmarker for DARPA QBI Performers")
    parser.add_argument("--profile", required=True, help="Path to hardware profile JSON")
    args = parser.parse_args()
    
    run_vv_benchmark(args.profile)
