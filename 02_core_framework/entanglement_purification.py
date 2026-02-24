"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       MODULE 7: ENTANGLEMENT PURIFICATION PROTOCOL                         ║
║       SAGE Framework v4.0 — The Missing Physics                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Every real quantum repeater must PURIFY noisy Bell pairs before use.
Raw entanglement from fiber is never perfect — photon loss, phase noise,
and dark counts contaminate the state.

This module models:
  1. Raw Bell pair generation (noisy channel output)
  2. DEJMPS purification (2 noisy pairs → 1 better pair, probabilistically)
  3. Resource overhead tracking (pairs consumed per successful purification)
  4. Comparison: no purification vs single-round vs iterative
  5. Integration with Sage Constant — how many rounds to cross threshold?

Physics reference:
  Deutsch, Ekert, Jozsa, Macchiavello, Popescu & Sanpera (1996)
  "Quantum privacy amplification and the security of quantum cryptography
   over noisy channels." Physical Review Letters 77(13), 2818–2821.
"""
# type: ignore
# pyre-ignore-all-errors


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ─────────────────────────────────────────────────────────────────────────────
# STYLE (matches SAGE v3 atlas)
# ─────────────────────────────────────────────────────────────────────────────
BG      = '#07080f'
PANEL   = '#0d0f1e'
GOLD    = '#FFD700'
CYAN    = '#00E5FF'
MAGENTA = '#FF00FF'
GREEN   = '#00FF41'
RED     = '#FF4136'
WHITE   = '#E8E8FF'
PURPLE  = '#BF5FFF'
ORANGE  = '#FF8C00'

plt.rcParams.update({
    'text.color': WHITE, 'axes.labelcolor': WHITE,
    'xtick.color': WHITE, 'ytick.color': WHITE,
    'axes.edgecolor': '#2a2a4a', 'grid.color': '#1a1a3a',
    'font.family': 'monospace',
})

SAGE_CONSTANT = 0.851   # identity survival threshold

# ═════════════════════════════════════════════════════════════════════════════
# CORE PHYSICS: BELL PAIR GENERATION & PURIFICATION
# ═════════════════════════════════════════════════════════════════════════════

def raw_bell_fidelity(distance_km, fiber_loss_db_per_km=0.2, detector_eff=0.85):
    """
    Model raw Bell pair fidelity from a fiber channel.
    
    Real-world sources of noise:
    - Fiber attenuation (exponential with distance)
    - Detector dark counts and inefficiency
    - Phase noise from fiber birefringence
    
    Returns fidelity of the raw entangled pair (0.25 to ~0.95)
    F = 0.25 is maximally mixed (no entanglement), F = 1.0 is perfect Bell state.
    """
    # Transmission probability through fiber
    transmission = 10 ** (-fiber_loss_db_per_km * distance_km / 10)
    
    # Effective fidelity: starts high, degrades with distance
    # Werner state model: F = p * 1.0 + (1-p) * 0.25, where p = transmission * detector_eff
    p = min(1.0, transmission * detector_eff)
    
    # Add phase noise contribution (worsens with distance)
    phase_noise = 0.02 * (distance_km / 100)  # 2% per 100km
    p = max(0, p - phase_noise)
    
    fidelity = p * 1.0 + (1 - p) * 0.25
    return max(0.25, min(1.0, fidelity))


def dejmps_purify(f1, f2):
    """
    DEJMPS entanglement purification protocol.
    
    Takes two Bell pairs with fidelities f1 and f2.
    Performs bilateral CNOT + measurement.
    If measurement succeeds (probability p_success), output pair has higher fidelity.
    If it fails, both pairs are lost.
    
    Returns: (output_fidelity, success_probability)
    """
    # DEJMPS formula for Werner states
    numerator = f1 * f2 + (1/9) * (1 - f1) * (1 - f2)
    denominator = f1 * f2 + (5/9) * (1 - f1) * (1 - f2) + \
                  (2/9) * (f1 * (1 - f2) + f2 * (1 - f1))
    
    if denominator < 1e-12:
        return 0.25, 0.0
    
    f_out = numerator / denominator
    p_success = denominator + (2/9) * (f1 * (1 - f2) + f2 * (1 - f1))
    
    return min(1.0, f_out), max(0.0, min(1.0, p_success))


def iterative_purification(initial_fidelity, max_rounds=10):
    """
    Run iterative DEJMPS purification starting from raw Bell pairs.
    Each round: take 2 pairs at current fidelity → produce 1 better pair.
    
    Returns: list of dicts with per-round stats
    """
    results = [{
        'round': 0,
        'fidelity': initial_fidelity,
        'pairs_consumed': 1,
        'cumulative_pairs': 1,
        'success_prob': 1.0,
        'above_sage': initial_fidelity >= SAGE_CONSTANT,
    }]
    
    current_f = initial_fidelity
    cumulative_pairs = 1
    
    for r in range(1, max_rounds + 1):
        # Each round consumes 2 pairs to produce 1
        f_out, p_success = dejmps_purify(current_f, current_f)
        
        # If purification doesn't improve, stop
        if f_out <= current_f + 1e-6:
            break
        
        # Resource cost: 2 pairs consumed, success probability reduces yield
        pairs_this_round = 2
        effective_cost = pairs_this_round / max(p_success, 0.01)
        cumulative_pairs *= effective_cost
        
        current_f = f_out
        results.append({
            'round': r,
            'fidelity': current_f,
            'pairs_consumed': effective_cost,
            'cumulative_pairs': cumulative_pairs,
            'success_prob': p_success,
            'above_sage': current_f >= SAGE_CONSTANT,
        })
        
        # If we've reached near-unity, stop
        if current_f > 0.999:
            break
    
    return results


# ═════════════════════════════════════════════════════════════════════════════
# SIMULATION: FULL PURIFICATION ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════

def run_purification_analysis():
    """
    Run full entanglement purification analysis:
    1. Raw fidelity vs distance
    2. Purification ladders for different starting fidelities
    3. Resource cost analysis
    4. Distance at which purification becomes essential
    """
    
    # ── 1. Raw Bell pair fidelity vs distance ──
    distances = np.linspace(1, 200, 200)
    raw_fidelities = [raw_bell_fidelity(d) for d in distances]
    
    # ── 2. Purification ladders for key distances ──
    test_distances = [10, 50, 100, 150]  # km
    ladders = {}
    for d in test_distances:
        raw_f = raw_bell_fidelity(d)
        ladders[d] = iterative_purification(raw_f, max_rounds=12)
    
    # ── 3. Strategy comparison: no purification vs 1 round vs iterative ──
    strategy_distances = np.linspace(5, 180, 50)
    strategies = {
        'No Purification': [],
        'Single Round': [],
        'Iterative (to threshold)': [],
    }
    resource_costs = {
        'No Purification': [],
        'Single Round': [],
        'Iterative (to threshold)': [],
    }
    
    for d in strategy_distances:
        raw_f = raw_bell_fidelity(d)
        
        # Strategy 1: No purification
        strategies['No Purification'].append(raw_f)
        resource_costs['No Purification'].append(1)
        
        # Strategy 2: Single round DEJMPS
        f_out, p_succ = dejmps_purify(raw_f, raw_f)
        strategies['Single Round'].append(f_out)
        resource_costs['Single Round'].append(2 / max(p_succ, 0.01))
        
        # Strategy 3: Iterative until above Sage Constant or converged
        ladder = iterative_purification(raw_f, max_rounds=12)
        final = ladder[-1]
        strategies['Iterative (to threshold)'].append(final['fidelity'])
        resource_costs['Iterative (to threshold)'].append(final['cumulative_pairs'])
    
    # ── 4. Find critical distance: where raw fidelity drops below Sage Constant ──
    critical_dist = None
    for d, f in zip(distances, raw_fidelities):
        if f < SAGE_CONSTANT:
            critical_dist = d
            break
    
    # ── 5. Rounds needed to reach Sage Constant vs starting fidelity ──
    starting_fids = np.linspace(0.30, 0.95, 50)
    rounds_needed = []
    for sf in starting_fids:
        ladder = iterative_purification(sf, max_rounds=20)
        # Find first round where we cross threshold
        crossed = [r for r in ladder if r['above_sage']]
        if crossed:
            rounds_needed.append(crossed[0]['round'])
        else:
            rounds_needed.append(float('nan'))
    
    return {
        'distances': distances,
        'raw_fidelities': raw_fidelities,
        'ladders': ladders,
        'test_distances': test_distances,
        'strategy_distances': strategy_distances,
        'strategies': strategies,
        'resource_costs': resource_costs,
        'critical_dist': critical_dist,
        'starting_fids': starting_fids,
        'rounds_needed': rounds_needed,
    }


# ═════════════════════════════════════════════════════════════════════════════
# VISUALIZATION
# ═════════════════════════════════════════════════════════════════════════════

def plot_purification(results):
    """Generate 4-panel purification analysis visualization."""
    
    fig = plt.figure(figsize=(20, 12), facecolor=BG)
    fig.suptitle(
        'ENTANGLEMENT PURIFICATION PROTOCOL  ·  THE MISSING PHYSICS',
        color=GOLD, fontsize=16, fontweight='bold', y=0.97,
        fontfamily='monospace'
    )
    
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.30,
                           left=0.07, right=0.96, top=0.91, bottom=0.07)
    
    # ── Panel 1: Raw Fidelity vs Distance ──────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(PANEL)
    ax1.plot(results['distances'], results['raw_fidelities'],
             color=RED, lw=2.5, label='Raw Bell Pair Fidelity')
    ax1.axhline(SAGE_CONSTANT, color=GOLD, ls='--', lw=1.5, alpha=0.7,
                label=f'Sage Constant ({SAGE_CONSTANT})')
    ax1.axhline(0.25, color=WHITE, ls=':', lw=1, alpha=0.3,
                label='Maximally Mixed (no entanglement)')
    if results['critical_dist']:
        ax1.axvline(results['critical_dist'], color=CYAN, ls=':', lw=1.2, alpha=0.6)
        ax1.text(results['critical_dist'] + 2, 0.88,
                 f'Critical:\n{results["critical_dist"]:.0f} km',
                 color=CYAN, fontsize=9, alpha=0.9)
    ax1.fill_between(results['distances'], 0, SAGE_CONSTANT, alpha=0.06, color=RED)
    ax1.set_title('RAW BELL PAIR FIDELITY vs DISTANCE', color=WHITE, fontsize=11, pad=8)
    ax1.set_xlabel('Fiber Distance (km)')
    ax1.set_ylabel('Fidelity')
    ax1.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7)
    ax1.grid(alpha=0.15)
    ax1.set_ylim(0.2, 1.02)
    
    # ── Panel 2: Purification Ladder ───────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(PANEL)
    colors = [RED, ORANGE, CYAN, GOLD]
    for (dist, ladder), col in zip(results['ladders'].items(), colors):
        rounds = [r['round'] for r in ladder]
        fids   = [r['fidelity'] for r in ladder]
        ax2.plot(rounds, fids, color=col, lw=2, marker='o', markersize=5,
                 label=f'{dist} km (raw: {fids[0]:.3f})')
        # Mark where it crosses Sage Constant
        for r in ladder:
            if r['above_sage'] and r['round'] > 0:
                ax2.scatter([r['round']], [r['fidelity']], color=col,
                           s=120, zorder=5, marker='*', edgecolors=WHITE, linewidths=0.5)
                break
    ax2.axhline(SAGE_CONSTANT, color=GOLD, ls='--', lw=1.5, alpha=0.5,
                label=f'Sage Constant')
    ax2.set_title('PURIFICATION LADDER — Fidelity per Round', color=WHITE, fontsize=11, pad=8)
    ax2.set_xlabel('Purification Round')
    ax2.set_ylabel('Output Fidelity')
    ax2.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7)
    ax2.grid(alpha=0.15)
    ax2.set_ylim(0.4, 1.02)
    
    # ── Panel 3: Strategy Comparison ───────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor(PANEL)
    strat_colors = [RED, CYAN, GOLD]
    for (name, vals), col in zip(results['strategies'].items(), strat_colors):
        ax3.plot(results['strategy_distances'], vals, color=col, lw=2, label=name)
    ax3.axhline(SAGE_CONSTANT, color=WHITE, ls='--', lw=1, alpha=0.4)
    ax3.fill_between(results['strategy_distances'], 0, SAGE_CONSTANT, alpha=0.06, color=RED)
    ax3.set_title('STRATEGY COMPARISON — Achieved Fidelity by Distance', color=WHITE, fontsize=11, pad=8)
    ax3.set_xlabel('Segment Distance (km)')
    ax3.set_ylabel('Achieved Fidelity')
    ax3.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7)
    ax3.grid(alpha=0.15)
    ax3.set_ylim(0.2, 1.02)
    
    # ── Panel 4: Resource Cost ─────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(PANEL)
    for (name, costs), col in zip(results['resource_costs'].items(), strat_colors):
        ax4.semilogy(results['strategy_distances'], costs, color=col, lw=2, label=name)
    ax4.set_title('RESOURCE COST — Bell Pairs Consumed per Usable Pair', color=WHITE, fontsize=11, pad=8)
    ax4.set_xlabel('Segment Distance (km)')
    ax4.set_ylabel('Pairs Consumed (log scale)')
    ax4.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7)
    ax4.grid(alpha=0.15)
    
    out = 'entanglement_purification.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f'[MODULE 7] Purification analysis saved -> {out}')
    return out


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('\n[MODULE 7] Entanglement Purification Protocol')
    print('=' * 55)
    
    results = run_purification_analysis()
    
    # Print key findings
    print(f'\n  Critical distance (raw F < Sage): {results["critical_dist"]:.0f} km')
    print(f'\n  Purification Ladders:')
    for dist, ladder in results['ladders'].items():
        final = ladder[-1]
        print(f'    {dist:>4} km: raw {ladder[0]["fidelity"]:.3f} → '
              f'purified {final["fidelity"]:.3f} in {final["round"]} rounds '
              f'(cost: {final["cumulative_pairs"]:.1f} pairs)')
    
    print(f'\n  Key insight: Purification is ESSENTIAL beyond '
          f'{results["critical_dist"]:.0f} km.')
    print(f'  Without it, raw Bell pairs drop below identity survival.')
    print(f'  The cost: exponential pair consumption with distance.')
    
    plot_purification(results)
    print('\n[MODULE 7] Done.')
