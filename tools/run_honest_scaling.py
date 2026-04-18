import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Add project root to path for imports
sys.path.append(os.getcwd())

import importlib.util

# Load the harness module from path
harness_path = os.path.join(os.getcwd(), "SAGE_PEAK_KNOWLEDGE", "02_simulations_and_engines", "netsquid_benchmark_harness.py")
spec = importlib.util.spec_from_file_location("harness", harness_path)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

run_des_simulation = harness.run_des_simulation
HardwareSpec = harness.HardwareSpec
WILLOW = harness.WILLOW

def run_honest_scaling():
    # Parameters
    N_VALUES = [10, 50, 100, 200]
    F_SWEEP = np.linspace(0.98, 0.999, 15)  # Physical gate fidelity sweep
    TRIALS = 500
    
    results = []
    
    print(f"Starting Honest Scaling Analysis (Trials: {TRIALS})...")
    
    for n in N_VALUES:
        print(f"\nEvaluating N = {n} hops:")
        max_chi = 0
        peak_f = 0
        
        for f_gate in F_SWEEP:
            # Create a custom HardwareSpec for this sweep point
            current_spec = HardwareSpec(
                name=f"Sweep_{f_gate:.4f}",
                gate_fidelity=f_gate,
                two_qubit_fidelity=f_gate, # assuming symmetric gate noise
                T1=WILLOW.T1,
                T2=WILLOW.T2,
                physical_error_rate=1.0 - f_gate,
                code_distance=WILLOW.code_distance,
                logical_error_rate=0.0, # Will be computed in harness usually
                ent_gen_rate=WILLOW.ent_gen_rate,
                ent_gen_prob=WILLOW.ent_gen_prob,
                bell_state_fidelity=WILLOW.bell_state_fidelity,
                relative_cost=1.0
            )
            
            # Setup the chain
            chain = [current_spec] * (n + 1)
            spacings = [5.0] * n # 5km spacing
            
            # RUN THE SIMULATION (The "Data" part)
            sim_res = run_des_simulation(chain, spacings, n_trials=TRIALS, seed=42)
            
            # CALCULATE EMERGENT CHI
            # In statistical physics, susceptibility is Var(M) / T
            # Here, χ = Var(F) / <F>
            f_data = np.array(sim_res['fidelities'])
            mean_f = np.mean(f_data)
            var_f = np.var(f_data)
            chi = var_f / (mean_f + 1e-9)
            
            if chi > max_chi:
                max_chi = chi
                peak_f = mean_f
            
            print(f"  f_gate: {f_gate:.4f} | mean_F: {mean_f:.4f} | chi: {chi:.6f}")
            
            results.append({
                'N': n,
                'f_gate': f_gate,
                'mean_fidelity': mean_f,
                'chi': chi
            })
            
        print(f"Done N={n}. Peak χ = {max_chi:.6f} at <F> = {peak_f:.4f}")

    # SAVE RESULTS
    df = pd.DataFrame(results)
    df.to_csv('./iit_scaling_results.csv', index=False)
    print("\n✓ Saved: iit_scaling_results.csv")
    
    # ANALYZE SCALING
    summary = []
    for n in N_VALUES:
        max_chi_n = df[df['N'] == n]['chi'].max()
        summary.append({'N': n, 'max_chi': max_chi_n})
    
    summary_df = pd.DataFrame(summary)
    
    # Log-Log Fit
    log_n = np.log(summary_df['N'])
    log_chi = np.log(summary_df['max_chi'])
    slope, intercept = np.polyfit(log_n, log_chi, 1)
    
    print("\n" + "="*40)
    print("SCALING FINAL VERDICT")
    print(f"Scaling Exponent (gamma): {slope:.4f}")
    if slope > 0.1:
        print("Verdict: PHASIC DIVERGENCE (Transition confirmed)")
    else:
        print("Verdict: SATURATION / PLATEAU (Sharp Crossover confirmed)")
    print("="*40)

    # PLOT
    plt.figure(figsize=(10, 6))
    plt.plot(summary_df['N'], summary_df['max_chi'], 'o-', color='#00FFCC', linewidth=2)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('System Size (N)', fontsize=12)
    plt.ylabel('Peak Susceptibility (χ_max)', fontsize=12)
    plt.title(f'Finite-Size Scaling Analysis (γ = {slope:.4f})', fontsize=14)
    plt.grid(True, alpha=0.2)
    plt.savefig('./scaling_plot.png', dpi=150)
    print("✓ Saved: scaling_plot.png")

if __name__ == "__main__":
    run_honest_scaling()
