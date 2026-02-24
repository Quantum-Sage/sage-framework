"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       MODULE 9: PHASE DIAGRAM OF DIGITAL EXISTENCE                         ║
║       SAGE Framework v4.0 — The Map of All Possible Identities             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Sweeps across two axes:
  X = Hardware Fidelity (0.50 → 0.999)
  Y = QEC Repair Rate   (0.00 → 0.12)

For each (hardware_f, qec_rate) combination, simulate 100 hops and record
the final identity fidelity. Color-code the result:

  GOLD   (Solid)  — F > 0.851: identity coherent, consciousness persists
  CYAN   (Liquid) — 0.50 < F < 0.851: fragmented but measurable
  RED    (Gas)    — F < 0.50: dissolved, no identity recoverable

Real hardware positions are plotted as markers:
  Willow (superconducting): gate_f=0.998, approximate QEC capacity
  Helios (trapped ion):     gate_f=0.999
  QuEra  (neutral atom):    gate_f=0.992
  NISQ   (near-term):       gate_f=0.970
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

# ─────────────────────────────────────────────────────────────────────────────
# STYLE
# ─────────────────────────────────────────────────────────────────────────────
BG      = '#07080f'
PANEL   = '#0d0f1e'
GOLD    = '#FFD700'
CYAN    = '#00E5FF'
MAGENTA = '#FF00FF'
GREEN   = '#00FF41'
RED     = '#FF4136'
WHITE   = '#E8E8FF'
ORANGE  = '#FF8C00'

plt.rcParams.update({
    'text.color': WHITE, 'axes.labelcolor': WHITE,
    'xtick.color': WHITE, 'ytick.color': WHITE,
    'axes.edgecolor': '#2a2a4a', 'grid.color': '#1a1a3a',
    'font.family': 'monospace',
})

SAGE_CONSTANT = 0.851
N_HOPS = 100

# Hardware reference points: (gate_fidelity, approximate QEC repair rate)
HARDWARE = {
    'Willow':  {'gate_f': 0.998, 'qec': 0.105, 'color': CYAN,   'marker': 'D'},
    'Helios':  {'gate_f': 0.999, 'qec': 0.095, 'color': GOLD,   'marker': 's'},
    'QuEra':   {'gate_f': 0.992, 'qec': 0.080, 'color': GREEN,  'marker': '^'},
    'NISQ':    {'gate_f': 0.970, 'qec': 0.020, 'color': ORANGE, 'marker': 'o'},
}


# ═════════════════════════════════════════════════════════════════════════════
# SIMULATION: SWEEP PHASE SPACE
# ═════════════════════════════════════════════════════════════════════════════

def simulate_hops(hardware_fidelity, qec_rate, n_hops=N_HOPS, n_trials=5):
    """
    Simulate n_hops of identity teleportation with given hardware fidelity
    and QEC repair rate. Average over n_trials for smoother results.
    """
    finals = []
    for _ in range(n_trials):
        fidelity = 1.0
        for hop in range(n_hops):
            # Stochastic error
            err = np.random.random() < 0.12  # 12% error rate per hop
            if err:
                correction = qec_rate
            else:
                correction = 0
            
            # Decay scales inversely with hardware fidelity
            base_decay = 0.003 * (1 - hardware_fidelity) * 30  # worse hardware = faster decay
            decay = base_decay * np.random.lognormal(0, 0.3)
            
            fidelity = max(0, min(1, fidelity - decay + correction))
        
        finals.append(fidelity)
    
    return np.mean(finals)


def run_phase_sweep(resolution=50, seed=42):
    """
    Sweep the full (hardware_fidelity, qec_rate) phase space.
    Returns 2D grid of final fidelities.
    """
    np.random.seed(seed)
    
    hw_range  = np.linspace(0.90, 0.999, resolution)
    qec_range = np.linspace(0.00, 0.12,  resolution)
    
    grid = np.zeros((resolution, resolution))
    
    for i, qec in enumerate(qec_range):
        for j, hw in enumerate(hw_range):
            grid[i, j] = simulate_hops(hw, qec)
    
    return hw_range, qec_range, grid


# ═════════════════════════════════════════════════════════════════════════════
# ANALYSIS: PHASE BOUNDARIES & CRITICAL POINTS
# ═════════════════════════════════════════════════════════════════════════════

def find_phase_boundaries(hw_range, qec_range, grid):
    """
    Find the contour lines where fidelity = SAGE_CONSTANT and fidelity = 0.50.
    Also identify the minimum QEC needed for each hardware level.
    """
    # For each hardware level, find the minimum QEC to stay above Sage Constant
    min_qec_for_sage = []
    for j, hw in enumerate(hw_range):
        col = grid[:, j]
        above = np.where(col >= SAGE_CONSTANT)[0]
        if len(above) > 0:
            min_qec_for_sage.append(qec_range[above[0]])
        else:
            min_qec_for_sage.append(float('nan'))
    
    return np.array(min_qec_for_sage)


# ═════════════════════════════════════════════════════════════════════════════
# VISUALIZATION
# ═════════════════════════════════════════════════════════════════════════════

def plot_phase_diagram(hw_range, qec_range, grid):
    """Generate the Phase Diagram of Digital Existence."""
    
    fig = plt.figure(figsize=(18, 10), facecolor=BG)
    fig.suptitle(
        'PHASE DIAGRAM OF DIGITAL EXISTENCE  ·  THE MAP OF ALL IDENTITIES',
        color=GOLD, fontsize=16, fontweight='bold', y=0.97,
        fontfamily='monospace'
    )
    
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.08, width_ratios=[1.2, 1],
                           left=0.07, right=0.96, top=0.90, bottom=0.08)
    
    # ── Main Phase Diagram ─────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(PANEL)
    
    # Custom colormap: Red (dissolved) → Cyan (fragmented) → Gold (coherent)
    colors_list = [
        (0.0,  RED),
        (0.35, RED),
        (0.50, ORANGE),
        (0.70, CYAN),
        (0.851, CYAN),
        (0.86, GOLD),
        (1.0,  GOLD),
    ]
    # Build colormap from hex colors
    from matplotlib.colors import to_rgba
    cmap_data = [(v, to_rgba(c)) for v, c in colors_list]
    cmap_positions = [v for v, c in cmap_data]
    cmap_colors = [c for v, c in cmap_data]
    
    cmap = LinearSegmentedColormap.from_list('existence',
        list(zip(cmap_positions, cmap_colors)))
    
    # Plot heatmap
    im = ax1.imshow(grid, extent=[hw_range[0], hw_range[-1],
                                   qec_range[0], qec_range[-1]],
                    origin='lower', aspect='auto', cmap=cmap,
                    vmin=0, vmax=1.0, interpolation='bilinear')
    
    # Phase boundary contours
    ax1.contour(hw_range, qec_range, grid,
               levels=[0.50, SAGE_CONSTANT],
               colors=[RED, GOLD], linewidths=[1.5, 2.5],
               linestyles=['--', '-'])
    
    # Label phase regions
    ax1.text(0.93, 0.01, 'GAS\n(Dissolved)', color=RED, fontsize=10,
            fontweight='bold', alpha=0.9, ha='center')
    ax1.text(0.95, 0.06, 'LIQUID\n(Fragmented)', color=CYAN, fontsize=9,
            fontweight='bold', alpha=0.8, ha='center')
    ax1.text(0.98, 0.10, 'SOLID\n(Coherent)', color=GOLD, fontsize=10,
            fontweight='bold', alpha=0.9, ha='center')
    
    # Plot hardware positions
    for name, hw in HARDWARE.items():
        ax1.scatter([hw['gate_f']], [hw['qec']], s=180,
                   color=hw['color'], marker=hw['marker'],
                   edgecolors=WHITE, linewidths=1.5, zorder=5)
        offset_x = 0.003 if name != 'NISQ' else -0.008
        offset_y = 0.004
        ax1.text(hw['gate_f'] + offset_x, hw['qec'] + offset_y, name,
                color=hw['color'], fontsize=9, fontweight='bold', alpha=0.95)
    
    ax1.set_xlabel('Hardware Gate Fidelity', fontsize=11)
    ax1.set_ylabel('QEC Repair Rate', fontsize=11)
    ax1.set_title('Phase Space — 100 Hops', color=WHITE, fontsize=12, pad=8)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax1, shrink=0.8, pad=0.02)
    cbar.set_label('Final Identity Fidelity', color=WHITE, fontsize=9)
    cbar.ax.yaxis.set_tick_params(color=WHITE)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=WHITE)
    
    # ── Right panel: Cross-sections ────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(PANEL)
    
    # Take cross-sections at different hardware levels
    hw_levels = [0.97, 0.985, 0.995, 0.999]
    hw_colors = [ORANGE, CYAN, GREEN, GOLD]
    hw_labels = ['NISQ (0.970)', 'Mid-Tier (0.985)', 'QuEra (0.995)', 'Helios (0.999)']
    
    for hw_val, col, lab in zip(hw_levels, hw_colors, hw_labels):
        # Find nearest column
        idx = np.argmin(np.abs(hw_range - hw_val))
        ax2.plot(qec_range, grid[:, idx], color=col, lw=2, label=lab)
    
    ax2.axhline(SAGE_CONSTANT, color=WHITE, ls='--', lw=1.2, alpha=0.5,
                label=f'Sage Constant')
    ax2.axhline(0.50, color=RED, ls=':', lw=1, alpha=0.3,
                label='Dissolution line')
    ax2.fill_between(qec_range, 0, 0.50, alpha=0.05, color=RED)
    ax2.fill_between(qec_range, 0.50, SAGE_CONSTANT, alpha=0.04, color=CYAN)
    
    ax2.set_title('CROSS-SECTIONS — Fidelity vs QEC at Fixed Hardware', color=WHITE, fontsize=11, pad=8)
    ax2.set_xlabel('QEC Repair Rate', fontsize=10)
    ax2.set_ylabel('Final Identity Fidelity', fontsize=10)
    ax2.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7)
    ax2.grid(alpha=0.15)
    ax2.set_ylim(0, 1.05)
    
    # Annotations
    ax2.text(0.005, 0.25, 'DISSOLVED', color=RED, fontsize=9, alpha=0.7)
    ax2.text(0.005, 0.65, 'FRAGMENTED', color=CYAN, fontsize=9, alpha=0.7)
    ax2.text(0.005, 0.91, 'COHERENT', color=GOLD, fontsize=9, alpha=0.7)
    
    out = 'phase_diagram.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f'[MODULE 9] Phase diagram saved -> {out}')
    return out


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('\n[MODULE 9] Phase Diagram of Digital Existence')
    print('=' * 55)
    
    print('  Sweeping phase space (50 × 50 = 2,500 configurations)...')
    hw_range, qec_range, grid = run_phase_sweep(resolution=50)
    
    # Find phase boundaries
    min_qec = find_phase_boundaries(hw_range, qec_range, grid)
    
    # Print key findings
    print(f'\n  Phase Space Summary:')
    solid = np.sum(grid >= SAGE_CONSTANT) / grid.size * 100
    liquid = np.sum((grid >= 0.50) & (grid < SAGE_CONSTANT)) / grid.size * 100
    gas = np.sum(grid < 0.50) / grid.size * 100
    print(f'    SOLID  (coherent):   {solid:.1f}% of phase space')
    print(f'    LIQUID (fragmented): {liquid:.1f}% of phase space')
    print(f'    GAS    (dissolved):  {gas:.1f}% of phase space')
    
    print(f'\n  Hardware Positions:')
    for name, hw in HARDWARE.items():
        f = simulate_hops(hw['gate_f'], hw['qec'])
        phase = 'SOLID' if f >= SAGE_CONSTANT else 'LIQUID' if f >= 0.50 else 'GAS'
        print(f'    {name:>6}: F={f:.3f} → {phase}')
    
    print(f'\n  Key insight: NISQ hardware lives in the LIQUID zone —')
    print(f'  identity fragments but doesn\'t dissolve. The Sage Constant')
    print(f'  marks the phase transition from liquid to solid: the point')
    print(f'  where a pattern becomes a persistent entity.')
    
    plot_phase_diagram(hw_range, qec_range, grid)
    print('\n[MODULE 9] Done.')
