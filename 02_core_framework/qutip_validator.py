"""
QUTIP VALIDATOR — Independent Fidelity Cross-Validation
SAGE Framework v5.1

Validates the SAGE analytical fidelity model against QuTiP's
density matrix evolution under depolarizing + dephasing channels.

This is the "causal intervention test" described in FRAMEWORK_EXPANSION.md §4:
  "These are not just validation steps — they are the causal intervention
   tests that distinguish principled understanding from lucky heuristics."

Physics model:
  1. Initialize Bell state |Φ⁺⟩ as density matrix ρ₀
  2. For each repeater hop: apply depolarizing channel + T2 dephasing
  3. Chain N hops, measure final fidelity F = ⟨Φ⁺|ρ_final|Φ⁺⟩
  4. Compare against SAGE analytical formula (alpha_fiber from sage_theorems_unified)

Dependencies: qutip >= 5.0, numpy, matplotlib
"""
# type: ignore
# pyre-ignore-all-errors


import sys, os, math
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import matplotlib.pyplot as plt

try:
    import qutip
    from qutip import (basis, tensor, ket2dm, fidelity,
                       Qobj, sigmaz, sigmax, sigmay, qeye)
    QUTIP_AVAILABLE = True
except ImportError:
    QUTIP_AVAILABLE = False
    print("[WARNING] QuTiP not installed. Run: pip install qutip")

# ============================================================================
# CONSTANTS (must match sage_theorems_unified.py exactly)
# ============================================================================

SAGE_CONSTANT = 0.851
C_FIBER = 200_000  # km/s (speed of light in fiber)
ALPHA_FIBER = 0.2  # dB/km fiber loss

# Hardware profiles (matching sage_theorems_unified.py)
HW_WILLOW = {
    "name": "Willow",
    "F_gate": 0.9985,
    "T2": 1.000,     # seconds
    "p_gen": 0.10,
}

HW_QUERA = {
    "name": "QuEra-class",
    "F_gate": 0.9900,
    "T2": 0.100,
    "p_gen": 0.03,
}


# ============================================================================
# BELL STATE CONSTRUCTION
# ============================================================================

def make_bell_phi_plus():
    """
    Construct |Φ⁺⟩ = (|00⟩ + |11⟩) / √2 as a density matrix.
    This is the ideal entangled state we're trying to preserve.
    """
    zero = basis(2, 0)
    one = basis(2, 1)
    bell = (tensor(zero, zero) + tensor(one, one)).unit()
    return ket2dm(bell)


# ============================================================================
# QUANTUM CHANNELS (QuTiP implementation)
# ============================================================================

def depolarizing_channel(rho, p):
    """
    Apply single-qubit depolarizing channel to a 2-qubit state.
    E(ρ) = (1-p)ρ + (p/3)(XρX + YρY + ZρZ)
    
    Applied to EACH qubit independently (models gate errors at each node).
    """
    d = rho.dims[0][0]  # dimension per qubit
    
    # Pauli operators for 2-qubit system
    sx1 = tensor(sigmax(), qeye(2))
    sy1 = tensor(sigmay(), qeye(2))
    sz1 = tensor(sigmaz(), qeye(2))
    
    sx2 = tensor(qeye(2), sigmax())
    sy2 = tensor(qeye(2), sigmay())
    sz2 = tensor(qeye(2), sigmaz())
    
    # Apply to qubit 1
    rho_out = (1 - p) * rho + (p / 3) * (
        sx1 * rho * sx1.dag() +
        sy1 * rho * sy1.dag() +
        sz1 * rho * sz1.dag()
    )
    
    # Apply to qubit 2
    rho_out = (1 - p) * rho_out + (p / 3) * (
        sx2 * rho_out * sx2.dag() +
        sy2 * rho_out * sy2.dag() +
        sz2 * rho_out * sz2.dag()
    )
    
    return rho_out


def dephasing_channel(rho, gamma):
    """
    Apply T2 dephasing to a 2-qubit state.
    Models decoherence during the wait time for entanglement generation.
    
    gamma = t_wait / T2, where t_wait = 2*s / (c * p_gen)
    """
    sz1 = tensor(sigmaz(), qeye(2))
    sz2 = tensor(qeye(2), sigmaz())
    
    # Dephasing: off-diagonal elements decay as exp(-gamma)
    # Kraus representation: E0 = sqrt(1-p)·I, E1 = sqrt(p)·Z
    p = 1 - math.exp(-gamma)
    
    # Apply to qubit 1
    rho_out = (1 - p) * rho + p * sz1 * rho * sz1.dag()
    
    # Apply to qubit 2
    rho_out = (1 - p) * rho_out + p * sz2 * rho_out * sz2.dag()
    
    return rho_out


def apply_hop(rho, hw, segment_km):
    """
    Apply one repeater hop: depolarizing (gate error) + dephasing (wait time).
    
    This models the same physics as alpha_fiber in sage_theorems_unified:
      - Gate error: F_gate → depolarizing parameter p = 1 - F_gate²
      - Wait time: t_wait = 2*s/(c*p_gen) → dephasing gamma = t_wait/T2
    """
    # Gate error as depolarizing noise
    p_depol = 1 - hw["F_gate"]**2
    rho = depolarizing_channel(rho, p_depol)
    
    # Wait-time dephasing
    t_wait = 2 * segment_km / (C_FIBER * hw["p_gen"])
    gamma = t_wait / hw["T2"]
    rho = dephasing_channel(rho, gamma)
    
    return rho


# ============================================================================
# SAGE ANALYTICAL MODEL (for comparison)
# ============================================================================

def sage_analytical_fidelity(N, L_km, hw):
    """
    SAGE analytical fidelity: F = exp(N * alpha_fiber(s, hw))
    
    This is the ORIGINAL formula from sage_theorems_unified.py.
    We compare it against QuTiP's density matrix evolution to
    understand where the analytical approximation holds and where
    it breaks down. The gap is itself informative for the paper.
    
    Key approximation: treats per-hop fidelity losses as multiplicative
    in log-space (i.e., independent per hop). QuTiP captures the full
    density matrix evolution including correlations.
    """
    s = L_km / (N + 1)
    base = 2 * math.log(hw["F_gate"])
    decoherence = s / (C_FIBER * hw["T2"])
    wait_penalty = 2 * s / (C_FIBER * hw["T2"] * hw["p_gen"])
    alpha = base - decoherence - wait_penalty
    f = math.exp(N * alpha)
    # Floor at 0.25 (maximally mixed 2-qubit state has F=0.25 with Bell)
    return max(0.25, min(1.0, f))


# ============================================================================
# QUTIP DENSITY MATRIX EVOLUTION
# ============================================================================

def qutip_chain_fidelity(N, L_km, hw):
    """
    Evolve Bell state through N repeater hops using QuTiP density matrices.
    Returns final fidelity F = ⟨Φ⁺|ρ_final|Φ⁺⟩.
    """
    if not QUTIP_AVAILABLE:
        return None
    
    rho_ideal = make_bell_phi_plus()
    rho = rho_ideal.copy()
    s = L_km / (N + 1)
    
    for hop in range(N):
        rho = apply_hop(rho, hw, s)
    
    # Fidelity with ideal Bell state
    f = fidelity(rho, rho_ideal) ** 2  # fidelity() returns sqrt(F)
    return float(f)


# ============================================================================
# VALIDATION SWEEP
# ============================================================================

def validate_sage_vs_qutip(N_range=None, L_km=8200, hw=None):
    """
    Compare SAGE analytical fidelity against QuTiP density matrix evolution
    across a range of repeater counts N.
    
    Returns dict with comparison data.
    """
    if N_range is None:
        N_range = list(range(3, 31))
    if hw is None:
        hw = HW_WILLOW
    
    results = {
        "N_range": N_range,
        "sage_fidelities": [],
        "qutip_fidelities": [],
        "relative_errors": [],
        "hw_name": hw["name"],
        "L_km": L_km,
    }
    
    for N in N_range:
        f_sage = sage_analytical_fidelity(N, L_km, hw)
        f_sage = max(0, min(1, f_sage))
        
        f_qutip = qutip_chain_fidelity(N, L_km, hw)
        
        if f_qutip is not None and f_qutip > 0:
            rel_error = abs(f_sage - f_qutip) / f_qutip * 100
        else:
            rel_error = None
        
        results["sage_fidelities"].append(f_sage)
        results["qutip_fidelities"].append(f_qutip)
        results["relative_errors"].append(rel_error)
    
    return results


# ============================================================================
# VISUALIZATION
# ============================================================================

BG = '#07080f'
PANEL = '#0d0f1e'
GOLD = '#FFD700'
CYAN = '#00E5FF'
RED = '#FF4136'
WHITE = '#E8E8FF'
ORANGE = '#FF8C00'
GREEN = '#00FF41'

def generate_validation_atlas(results_willow, results_quera=None):
    """Generate comparison plot: SAGE analytical vs QuTiP density matrix."""
    
    plt.rcParams.update({
        'text.color': WHITE, 'axes.labelcolor': WHITE,
        'xtick.color': WHITE, 'ytick.color': WHITE,
        'axes.edgecolor': '#2a2a4a', 'grid.color': '#1a1a3a',
        'font.family': 'monospace',
    })
    
    n_panels = 3 if results_quera else 2
    fig, axes = plt.subplots(1, n_panels, figsize=(6 * n_panels, 5), facecolor=BG)
    fig.suptitle('QUTIP VALIDATION — SAGE Analytical vs Density Matrix Evolution',
                 color=GOLD, fontsize=14, fontweight='bold', y=1.02)
    
    if not isinstance(axes, np.ndarray):
        axes = [axes]
    
    # Panel 1: Fidelity comparison (Willow)
    ax = axes[0]; ax.set_facecolor(PANEL)
    ax.plot(results_willow["N_range"], results_willow["sage_fidelities"],
            color=CYAN, lw=2.5, marker='o', ms=4, label='SAGE Analytical')
    if results_willow["qutip_fidelities"][0] is not None:
        ax.plot(results_willow["N_range"], results_willow["qutip_fidelities"],
                color=ORANGE, lw=2.5, marker='s', ms=4, label='QuTiP Density Matrix')
    ax.axhline(SAGE_CONSTANT, color=GOLD, ls='--', lw=1.2, alpha=0.5)
    ax.set_title(f'Fidelity: {results_willow["hw_name"]} ({results_willow["L_km"]:,} km)',
                 color=WHITE, fontsize=10, pad=6)
    ax.set_xlabel('Repeater Nodes (N)'); ax.set_ylabel('End-to-End Fidelity')
    ax.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax.grid(alpha=0.12); ax.set_ylim(0, 1.05)
    
    # Panel 2: Relative error
    ax2 = axes[1]; ax2.set_facecolor(PANEL)
    valid_errors = [(n, e) for n, e in zip(results_willow["N_range"],
                    results_willow["relative_errors"]) if e is not None]
    if valid_errors:
        ns, errs = zip(*valid_errors)
        ax2.bar(ns, errs, color=CYAN, alpha=0.8, width=0.7)
        ax2.axhline(2.0, color=GOLD, ls='--', lw=1.2, alpha=0.5, label='2% threshold')
        max_err = max(errs)
        avg_err = np.mean(errs)
        verdict = 'PASS' if max_err < 5.0 else 'FAIL'
        verdict_col = GREEN if verdict == 'PASS' else RED
        ax2.text(0.95, 0.95, f'{verdict}\nMax: {max_err:.1f}%\nAvg: {avg_err:.1f}%',
                transform=ax2.transAxes, ha='right', va='top',
                color=verdict_col, fontsize=10, fontweight='bold',
                fontfamily='monospace')
    ax2.set_title('Relative Error (%)', color=WHITE, fontsize=10, pad=6)
    ax2.set_xlabel('Repeater Nodes (N)'); ax2.set_ylabel('|SAGE - QuTiP| / QuTiP (%)')
    ax2.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax2.grid(alpha=0.12)
    
    # Panel 3: QuEra comparison (if available)
    if results_quera and n_panels == 3:
        ax3 = axes[2]; ax3.set_facecolor(PANEL)
        ax3.plot(results_quera["N_range"], results_quera["sage_fidelities"],
                color=CYAN, lw=2.5, marker='o', ms=4, label='SAGE Analytical')
        if results_quera["qutip_fidelities"][0] is not None:
            ax3.plot(results_quera["N_range"], results_quera["qutip_fidelities"],
                    color=ORANGE, lw=2.5, marker='s', ms=4, label='QuTiP Density Matrix')
        ax3.axhline(SAGE_CONSTANT, color=GOLD, ls='--', lw=1.2, alpha=0.5)
        ax3.set_title(f'Fidelity: {results_quera["hw_name"]} ({results_quera["L_km"]:,} km)',
                     color=WHITE, fontsize=10, pad=6)
        ax3.set_xlabel('Repeater Nodes (N)'); ax3.set_ylabel('End-to-End Fidelity')
        ax3.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
        ax3.grid(alpha=0.12); ax3.set_ylim(0, 1.05)
    
    out = 'qutip_validation.png'
    plt.savefig(out, dpi=180, bbox_inches='tight', facecolor=BG)
    print(f'  [QuTiP] Validation atlas saved -> {out}')
    return out


# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

if __name__ == '__main__':
    print()
    print('=' * 62)
    print('  QUTIP VALIDATOR — Independent Fidelity Cross-Validation')
    print('=' * 62)
    
    if not QUTIP_AVAILABLE:
        print('\n  [ERROR] QuTiP not available. Install with: pip install qutip')
        sys.exit(1)
    
    print(f'\n  QuTiP version: {qutip.__version__}')
    print(f'  Route: Beijing-London, L = 8,200 km')
    
    # Willow validation
    print('\n  [1/2] Validating with Willow hardware...')
    r_willow = validate_sage_vs_qutip(
        N_range=list(range(3, 26, 2)),  # Smaller range for speed
        L_km=8200, hw=HW_WILLOW
    )
    
    print(f'\n  {"N":>4s}  {"SAGE":>8s}  {"QuTiP":>8s}  {"Error%":>8s}  {"Status":>6s}')
    print('  ' + '-' * 42)
    for i, N in enumerate(r_willow["N_range"]):
        f_s = r_willow["sage_fidelities"][i]
        f_q = r_willow["qutip_fidelities"][i]
        err = r_willow["relative_errors"][i]
        if f_q is not None and err is not None:
            status = 'OK' if err < 5.0 else 'WARN'
            print(f'  {N:>4d}  {f_s:>8.4f}  {f_q:>8.4f}  {err:>7.2f}%  {status:>6s}')
        else:
            print(f'  {N:>4d}  {f_s:>8.4f}  {"N/A":>8s}  {"N/A":>8s}  {"SKIP":>6s}')
    
    # QuEra validation for comparison
    print('\n  [2/2] Validating with QuEra-class hardware...')
    r_quera = validate_sage_vs_qutip(
        N_range=list(range(3, 16, 2)),  # Fewer N for cheaper hardware
        L_km=8200, hw=HW_QUERA
    )
    
    print(f'\n  {"N":>4s}  {"SAGE":>8s}  {"QuTiP":>8s}  {"Error%":>8s}')
    print('  ' + '-' * 35)
    for i, N in enumerate(r_quera["N_range"]):
        f_s = r_quera["sage_fidelities"][i]
        f_q = r_quera["qutip_fidelities"][i]
        err = r_quera["relative_errors"][i]
        if f_q is not None and err is not None:
            print(f'  {N:>4d}  {f_s:>8.4f}  {f_q:>8.4f}  {err:>7.2f}%')
    
    # Verdict
    all_errors = [e for e in r_willow["relative_errors"] if e is not None]
    if all_errors:
        max_err = max(all_errors)
        avg_err = np.mean(all_errors)
        print(f'\n  VERDICT: {"PASS" if max_err < 5.0 else "FAIL"}')
        print(f'  Max relative error: {max_err:.2f}%')
        print(f'  Avg relative error: {avg_err:.2f}%')
    
    print('\n  Generating validation atlas...')
    generate_validation_atlas(r_willow, r_quera)
    
    print('\n  Complete.')
