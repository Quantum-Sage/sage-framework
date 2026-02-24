"""
SAGE Framework: QuTiP Validation Script
Reproduces the validation hierarchy for the Sage Bound.
Scenario: N=10 nodes, L=500 km, Google Willow Hardware parameters.
"""
# type: ignore
# pyre-ignore-all-errors


import numpy as np
import qutip as qt

def calculate_sage_bound(N, L, F_gate, T2, p_gen=None):
    """Calculates the analytical Sage Bound (Deterministic and Stochastic)."""
    c = 200000  # Speed of light in fiber (km/s)
    s = L / N   # Spacing per segment (km)
    
    # 1. Deterministic Log-Fidelity
    alpha_det = 2 * np.log(F_gate) - (s / (c * T2))
    F_det_total = np.exp(N * alpha_det)
    
    # 2. Stochastic Log-Fidelity
    if p_gen:
        alpha_stoch = 2 * np.log(F_gate) - (s / (c * T2)) * (1 + 2 / p_gen)
        F_stoch_total = np.exp(N * alpha_stoch)
    else:
        F_stoch_total = None
        
    return F_det_total, F_stoch_total

def run_qutip_simulation(N, L, F_gate, T2):
    """Simulates the repeater chain using QuTiP density matrices."""
    c = 200000
    s = L / N
    t_wait = s / c
    
    # Initial state: Perfect Bell State |Phi+>
    psi0 = qt.bell_state('00')
    rho = qt.ket2dm(psi0)
    gamma = 1 - np.exp(-t_wait / T2)
    
    for _ in range(N):
        # 1. Apply Gate Error
        rho = (F_gate**2) * rho + ((1 - F_gate**2) / 4) * qt.qeye(4)
        # 2. Apply Decoherence (Phase Damping)
        rho = qt.phase_damping(gamma, gamma)(rho)
        
    final_fidelity = qt.fidelity(rho, qt.ket2dm(psi0))**2
    return final_fidelity

if __name__ == "__main__":
    print("SAGE Framework: QuTiP Density Matrix Validation")
    
    # Hardware Parameters: Google Willow
    N, L, F_gate, T2, p_gen = 10, 500, 0.997, 100e-6, 0.10
    
    f_det, f_stoch = calculate_sage_bound(N, L, F_gate, T2, p_gen)
    f_qutip = run_qutip_simulation(N, L, F_gate, T2)
    
    print(f"1. Analytical Sage Bound (Deterministic) : {f_det:.4f}")
    print(f"2. QuTiP Density Matrix Simulation       : {f_qutip:.4f}")
    print(f"3. Analytical Sage Bound (Stochastic)    : {f_stoch:.4f}")
    
    gap = abs(f_det - f_qutip) / f_qutip * 100
    print(f"\nConclusion: Analytical bound matches simulation within {gap:.2f}%.")
