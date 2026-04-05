"""
SAGE Availability Gap Model — The 191,311x Reliability Divergence
================================================================

Formal quantification of the 'No-Cloning Gap' in state survival.
This script compares classical High Availability (HA) survival 
(via checkpoint/restore) against quantum Poisson survival 
(subject to the no-cloning theorem).
"""

import numpy as np

def calculate_survival_probability(mtbf_days: float, period_days: float = 365.0) -> dict:
    """
    Calculates the probability of state survival for classical and quantum systems.
    
    Args:
        mtbf_days: Mean Time Between Failures of the underlying hardware (e.g., 30 days).
        period_days: Observation window (default: 1 year).
    
    Returns:
        Dictionary containing classical survival, quantum survival, and the divergence ratio.
    """
    
    # 1. Quantum Survival (Poisson Process) 
    # Because quantum state cannot be cloned, ANY hardware failure destroys the state.
    # Survival requires zero failures over the period T.
    # P(N=0) = e^(-T/MTBF)
    p_quantum = np.exp(-period_days / mtbf_days)
    
    # 2. Classical Survival (High Availability)
    # Classical state can be periodically backed up. Survival is dominated by 
    # checkpoint frequency and restore reliability, not the MTBF itself.
    # We use a conservative SRE baseline for standard 'Two-Nines' HA.
    p_classical = 0.995 
    
    # 3. Divergence Ratio
    # The 'No-Cloning Gap' is the ratio of these probabilities.
    ratio = p_classical / p_quantum if p_quantum > 0 else float('inf')
    
    return {
        "p_classical": p_classical,
        "p_quantum": p_quantum,
        "ratio": ratio,
        "gap_magnitude": f"{ratio:,.0f}x"
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  SAGE AVAILABILITY GAP MODEL — RELIABILITY DIVERGENCE")
    print("="*60)
    
    # Analyze the 'Willow/Helios' baseline: 30-day MTBF
    results = calculate_survival_probability(30.0)
    
    print(f"\n  Baseline Hardware MTBF: 30.0 days")
    print(f"  Observation Window:    365.0 days")
    print(f"  " + "-"*40)
    print(f"  Classical Survival:    {results['p_classical']*100:.2f}% (HA Checkpointing)")
    print(f"  Quantum Survival:      {results['p_quantum']*100:.6f}% (No-Cloning)")
    print(f"\n  THE NO-CLONING GAP:    {results['gap_magnitude']}")
    print(f"  " + "="*40)
    print("  CONCLUSION: Mesh architecture is mandatory for availability.")
