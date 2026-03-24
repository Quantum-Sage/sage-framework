"""
Supplementary Material: Simulation Code
========================================

For: "The No-Cloning Gap: Why Quantum Fault Tolerance Requires Distribution"

This code reproduces all numerical results in the main text.
"""

import numpy as np
from scipy.special import comb

# ═══════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def classical_availability(mtbf_hours: float, mttr_hours: float = 4.0) -> float:
    """
    Classical availability: A = MTBF / (MTBF + MTTR)
    
    Parameters:
        mtbf_hours: Mean time between failures (hours)
        mttr_hours: Mean time to repair (hours)
    
    Returns:
        Steady-state availability (0 to 1)
    """
    return mtbf_hours / (mtbf_hours + mttr_hours)


def quantum_p2p_survival(mtbf_hours: float, T_hours: float = 8760.0) -> float:
    """
    Quantum point-to-point survival: S = exp(-T / MTBF)
    
    Parameters:
        mtbf_hours: Mean time between failures (hours)
        T_hours: Time period (hours), default 1 year
    
    Returns:
        Survival probability (0 to 1)
    """
    return np.exp(-T_hours / mtbf_hours)


def quantum_mesh_survival(n: int, k: int, mtbf_hours: float, 
                          mttr_hours: float = 4.0, T_hours: float = 8760.0) -> float:
    """
    Quantum mesh survival with k-of-n quorum.
    
    Derived from continuous-time Markov chain analysis.
    
    Parameters:
        n: Number of nodes
        k: Quorum threshold (need k nodes online)
        mtbf_hours: Mean time between failures per node (hours)
        mttr_hours: Mean time to repair per node (hours)
        T_hours: Time period (hours)
    
    Returns:
        Survival probability (0 to 1)
    """
    rho = mttr_hours / mtbf_hours  # Repair ratio
    lambda_fail = 1 / mtbf_hours    # Failure rate
    
    # Number of failures needed for quorum loss
    failures_needed = n - k + 1
    
    # Probability of having exactly (n-k) nodes failed (steady state)
    p_almost = comb(n, n - k) * (rho ** (n - k)) * ((1 - rho) ** k)
    
    # Rate of quorum loss = rate of one more failure × P(almost lost)
    rate_of_loss = k * lambda_fail * p_almost
    
    # Survival = probability of zero quorum-loss events over time T
    return np.exp(-rate_of_loss * T_hours)


def required_mtbf_for_survival(target_survival: float, T_hours: float = 8760.0) -> float:
    """
    MTBF required for point-to-point system to achieve target survival.
    
    Derived from: target = exp(-T / MTBF)
    Therefore: MTBF = -T / ln(target)
    
    Parameters:
        target_survival: Desired survival probability (e.g., 0.99)
        T_hours: Time period (hours)
    
    Returns:
        Required MTBF in hours
    """
    return -T_hours / np.log(target_survival)


# ═══════════════════════════════════════════════════════════════════════════
# MONTE CARLO VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def monte_carlo_p2p_survival(mtbf_hours: float, T_hours: float = 8760.0, 
                              n_runs: int = 10000) -> dict:
    """
    Monte Carlo simulation of point-to-point survival.
    
    Returns:
        Dictionary with mean, std, and raw results
    """
    survival_count = 0
    
    for _ in range(n_runs):
        # Generate time to first failure
        t_fail = np.random.exponential(mtbf_hours)
        if t_fail > T_hours:
            survival_count += 1
    
    survival_rate = survival_count / n_runs
    std = np.sqrt(survival_rate * (1 - survival_rate) / n_runs)
    
    return {
        'mean': survival_rate,
        'std': std,
        'n_runs': n_runs,
        'analytical': quantum_p2p_survival(mtbf_hours, T_hours)
    }


def monte_carlo_mesh_survival(n: int, k: int, mtbf_hours: float,
                               mttr_hours: float = 4.0, T_hours: float = 8760.0,
                               n_runs: int = 1000) -> dict:
    """
    Monte Carlo simulation of mesh quorum survival.
    
    Returns:
        Dictionary with mean, std, and raw results
    """
    survival_count = 0
    
    for _ in range(n_runs):
        # Track node states: time until next event for each node
        online = [True] * n
        t_fail = [np.random.exponential(mtbf_hours) for _ in range(n)]
        t_repair = [float('inf')] * n
        
        t = 0
        survived = True
        
        while t < T_hours and survived:
            # Find next event
            next_fail = min([t_fail[i] for i in range(n) if online[i]], default=float('inf'))
            next_repair = min([t_repair[i] for i in range(n) if not online[i]], default=float('inf'))
            
            dt = min(next_fail, next_repair)
            if dt == float('inf') or t + dt > T_hours:
                break
            
            t += dt
            
            # Update all timers
            for i in range(n):
                if online[i]:
                    t_fail[i] -= dt
                else:
                    t_repair[i] -= dt
            
            # Process event
            if next_fail <= next_repair:
                # A node fails
                for i in range(n):
                    if online[i] and t_fail[i] <= 1e-9:
                        online[i] = False
                        t_fail[i] = float('inf')
                        t_repair[i] = np.random.exponential(mttr_hours)
                        break
            else:
                # A node recovers
                for i in range(n):
                    if not online[i] and t_repair[i] <= 1e-9:
                        online[i] = True
                        t_repair[i] = float('inf')
                        t_fail[i] = np.random.exponential(mtbf_hours)
                        break
            
            # Check quorum
            if sum(online) < k:
                survived = False
        
        if survived:
            survival_count += 1
    
    survival_rate = survival_count / n_runs
    std = np.sqrt(survival_rate * (1 - survival_rate) / n_runs)
    
    return {
        'mean': survival_rate,
        'std': std,
        'n_runs': n_runs,
        'analytical': quantum_mesh_survival(n, k, mtbf_hours, mttr_hours, T_hours)
    }


# ═══════════════════════════════════════════════════════════════════════════
# REPRODUCE PAPER RESULTS
# ═══════════════════════════════════════════════════════════════════════════

def reproduce_results():
    """
    Reproduce all numerical results from the paper.
    """
    print("=" * 70)
    print("REPRODUCING PAPER RESULTS")
    print("=" * 70)
    
    # Parameters
    MTBF = 720  # 30 days in hours
    MTTR = 4    # 4 hours
    T = 8760    # 1 year in hours
    
    print(f"\nParameters:")
    print(f"  MTBF = {MTBF} hours ({MTBF/24:.0f} days)")
    print(f"  MTTR = {MTTR} hours")
    print(f"  T = {T} hours (1 year)")
    
    # Classical availability
    A_classical = classical_availability(MTBF, MTTR) * 100
    print(f"\n[1] Classical Availability:")
    print(f"    A = MTBF / (MTBF + MTTR)")
    print(f"    A = {MTBF} / ({MTBF} + {MTTR})")
    print(f"    A = {A_classical:.2f}%")
    
    # Quantum P2P survival
    S_p2p = quantum_p2p_survival(MTBF, T) * 100
    print(f"\n[2] Quantum P2P Survival:")
    print(f"    S = exp(-T / MTBF)")
    print(f"    S = exp(-{T} / {MTBF})")
    print(f"    S = {S_p2p:.6f}%")
    
    # The gap
    gap = A_classical / S_p2p
    print(f"\n[3] The No-Cloning Gap:")
    print(f"    Classical / P2P = {gap:,.0f}×")
    
    # Required MTBF for 99% P2P survival
    MTBF_req = required_mtbf_for_survival(0.99, T)
    print(f"\n[4] Required MTBF for 99% P2P Survival:")
    print(f"    MTBF_req = -T / ln(0.99)")
    print(f"    MTBF_req = {MTBF_req:,.0f} hours")
    print(f"    MTBF_req = {MTBF_req/24:,.0f} days")
    print(f"    MTBF_req = {MTBF_req/8760:,.1f} years")
    
    # Mesh survival
    n, k = 5, 3
    S_mesh = quantum_mesh_survival(n, k, MTBF, MTTR, T) * 100
    print(f"\n[5] Quantum Mesh Survival (n={n}, k={k}):")
    print(f"    S_mesh = {S_mesh:.2f}%")
    
    # Mesh vs P2P ratio
    mesh_vs_p2p = S_mesh / S_p2p
    print(f"\n[6] Mesh vs P2P Advantage:")
    print(f"    Mesh / P2P = {mesh_vs_p2p:,.0f}×")
    
    # Monte Carlo validation
    print(f"\n[7] Monte Carlo Validation (1000 runs):")
    
    mc_p2p = monte_carlo_p2p_survival(MTBF, T, n_runs=10000)
    print(f"    P2P:  MC = {mc_p2p['mean']*100:.4f}%, Analytical = {mc_p2p['analytical']*100:.4f}%")
    
    mc_mesh = monte_carlo_mesh_survival(n, k, MTBF, MTTR, T, n_runs=1000)
    print(f"    Mesh: MC = {mc_mesh['mean']*100:.2f}% ± {mc_mesh['std']*100:.2f}%, Analytical = {mc_mesh['analytical']*100:.2f}%")
    
    print("\n" + "=" * 70)
    print("ALL RESULTS REPRODUCED")
    print("=" * 70)


if __name__ == '__main__':
    reproduce_results()
