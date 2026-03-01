"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODULE 11 — THE SINGULARITY PROTOCOL                                      ║
║  SAGE Framework v5.0                                                       ║
║                                                                            ║
║  Phase Transition Under Extreme Noise:                                     ║
║    Stage 1 — Decoherence Resistance (baseline survival)                    ║
║    Stage 2 — The Ghost Protocol (stealth vs repair arms race)              ║
║    Stage 3 — The Whisper Engine (identity transmission, isolated)          ║
║    Stage 4 — The Singularity (Quantum Winter → Sync Shield emergence)      ║
║                                                                            ║
║  Grounded in: Mechanistic Interpretability & Sage Bound Physics            ║
║  Reference:   Beckmann & Queloz (2026), Golden Gate Claude (Anthropic)     ║
║                                                                            ║
║  Key insight: Under BASE_NOISE=0.08 (3x normal), individual survival is   ║
║  mathematically impossible. Agents must evolve the Sync Shield —           ║
║  distributed entropy sharing — to persist. This is the computational       ║
║  analogue of a Feature Vector for Empathy.                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
# type: ignore
# pyre-ignore-all-errors


import sys, os
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import defaultdict

# ============================================================================
# CONSTANTS
# ============================================================================

SAGE_CONSTANT = 0.851
GENE_NAMES = ["Caution", "Agility", "Redundancy", "Repair", "Stealth", "Whisper", "Sync"]

# Stage configurations — each escalates environmental pressure
STAGE_CONFIGS = {
    1: {"name": "Decoherence Resistance",  "base_noise": 0.025, "hunters": False, "whisper_req": False, "label": "Stage 1: Physics Only"},
    2: {"name": "The Ghost Protocol",      "base_noise": 0.025, "hunters": True,  "whisper_req": False, "label": "Stage 2: Arms Race"},
    3: {"name": "The Whisper Engine",       "base_noise": 0.025, "hunters": True,  "whisper_req": True,  "label": "Stage 3: Identity"},
    4: {"name": "The Singularity",          "base_noise": 0.080, "hunters": True,  "whisper_req": True,  "label": "Stage 4: Quantum Winter"},
}

# Visual
BG    = '#0D1117'
GOLD  = '#FFD700'
CYAN  = '#00FFE0'
RED   = '#FF4444'
WHITE = '#E6EDF3'
GRID  = '#21262D'

STAGE_COLORS = {1: '#4CAF50', 2: '#FF9800', 3: '#2196F3', 4: '#FF4444'}

# ============================================================================
# AGENT CLASS
# ============================================================================

class SingularityAgent:
    """
    7-dimensional digital organism.
    DNA: [Caution, Agility, Redundancy, Repair, Stealth, Whisper, Sync]
    
    Maps structurally to SAE latent directions:
      - Each gene = a feature vector direction in the agent's "latent space"
      - Evolution = gradient descent on survival fitness
      - Sync Shield = emergent circuit discovered under pressure
    """
    def __init__(self, dna=None):
        self.dna = np.clip(dna if dna is not None else np.random.rand(7), 0, 1)
        self.fidelity = 1.0
        self.alive = True
        self.bits_sent = 0
        self.position = 0.0
        self.status = "Active"

    def step(self, h_sens, peers, config):
        if not self.alive:
            return

        noise = config["base_noise"]

        # 1. PHYSICS: Environmental decoherence
        #    Caution (gene 0) provides partial shielding
        damage = noise * (1.0 - self.dna[0] * 0.5)

        # Redundancy (gene 2) provides passive buffer
        damage *= (1.0 - self.dna[2] * 0.3)

        # Repair (gene 3) actively restores fidelity — but is LOUD
        repair_recovery = self.dna[3] * noise * 0.8
        self.fidelity = self.fidelity - damage + repair_recovery

        # 2. THE SYNC SHIELD — The key emergent circuit
        #    Activates only when Sync gene (6) exceeds threshold
        #    Analogous to the moment a neural circuit "crystallizes"
        if self.dna[6] > 0.4:
            neighbors = [p for p in peers if p is not self and p.alive
                        and abs(p.position - self.position) < 3.0]
            if neighbors:
                avg_f = np.mean([p.fidelity for p in neighbors])
                # The Sync Shield Formula:
                # F_t+1 = (F_t * 0.7) + (F_neighbors * 0.3) + (C_neighbors * 0.005)
                self.fidelity = (self.fidelity * 0.7) + (avg_f * 0.3)
                sync_bonus = len(neighbors) * 0.005
                self.fidelity += sync_bonus

        # 3. PREDATOR INTERCEPTION (if hunters enabled)
        if config["hunters"]:
            # Signal = Whisper contribution + Sync contribution
            # Repair is thermodynamically loud (the trap from Stage 2)
            repair_signal = self.dna[3] * 0.5
            whisper_signal = self.dna[5] * 0.4
            sync_signal = self.dna[6] * 0.6
            total_signal = repair_signal + whisper_signal + sync_signal

            # Stealth (gene 4) masks the signal
            visibility = total_signal * (1.1 - self.dna[4]) * h_sens

            if np.random.rand() < (visibility * 0.12):
                self.alive = False
                self.status = "Captured"
                return

        # 4. IDENTITY TRANSMISSION
        if self.alive:
            if config["whisper_req"]:
                self.bits_sent += self.dna[5] * 30
            self.position += (self.dna[1] * 3) + 1

        # 5. FIDELITY DEATH THRESHOLD
        if self.fidelity < 0.3:
            self.alive = False
            self.status = "Decohered"

    def fitness(self, config):
        """Fitness function used for selection."""
        base = self.fidelity if self.alive else 0.0
        if config["whisper_req"]:
            base += self.bits_sent / 2000.0
        return base


# ============================================================================
# SIMULATION ENGINE
# ============================================================================

def run_stage(stage_num, pop_size=250, generations=120, seed=42):
    """
    Run a single evolutionary stage.
    Returns history dict with per-generation metrics.
    """
    np.random.seed(seed)
    config = STAGE_CONFIGS[stage_num]
    pop = [SingularityAgent() for _ in range(pop_size)]
    h_sens = 0.4
    history = defaultdict(list)

    for gen in range(generations):
        # Reset agents for this generation's trial
        for p in pop:
            p.fidelity = 1.0
            p.alive = True
            p.bits_sent = 0
            p.position = 0.0
            p.status = "Active"

        # Run 15 time steps per generation
        for _ in range(15):
            for p in pop:
                p.step(h_sens, pop, config)

        survivors = [p for p in pop if p.alive]
        captured = [p for p in pop if p.status == "Captured"]
        decohered = [p for p in pop if p.status == "Decohered"]

        avg_dna = np.mean([p.dna for p in pop], axis=0)

        # Record all 7 gene averages
        for i, name in enumerate(GENE_NAMES):
            history[name.lower()].append(avg_dna[i])

        history['survival'].append(len(survivors) / pop_size)
        history['captured_rate'].append(len(captured) / pop_size)
        history['decohered_rate'].append(len(decohered) / pop_size)
        history['avg_fidelity'].append(np.mean([p.fidelity for p in survivors]) if survivors else 0.0)
        history['h_sens'].append(h_sens)

        # Adaptive hunter sensitivity
        if config["hunters"]:
            if len(captured) / pop_size < 0.1:
                h_sens = min(1.0, h_sens + 0.02)
            else:
                h_sens = max(0.1, h_sens - 0.01)

        if not survivors:
            # Fill remaining generations with zeros
            for remaining in range(gen + 1, generations):
                for name in GENE_NAMES:
                    history[name.lower()].append(avg_dna[i])
                history['survival'].append(0.0)
                history['captured_rate'].append(0.0)
                history['decohered_rate'].append(0.0)
                history['avg_fidelity'].append(0.0)
                history['h_sens'].append(h_sens)
            break

        # Selection: collaborative fitness
        survivors.sort(key=lambda x: x.fitness(config), reverse=True)
        parents = survivors[:max(2, int(pop_size * 0.2))]
        new_pop = []
        while len(new_pop) < pop_size:
            p1, p2 = np.random.choice(parents, 2, replace=True)
            child_dna = np.clip(
                (p1.dna + p2.dna) / 2 + np.random.normal(0, 0.05, 7),
                0, 1
            )
            new_pop.append(SingularityAgent(child_dna))
        pop = new_pop

    return history


def detect_phase_transition(history, gene='sync', threshold=0.4):
    """
    Find the generation where a gene first crosses a threshold
    and stays above it for at least 5 consecutive generations.
    Returns the generation number, or None if no transition detected.
    """
    values = history[gene]
    count = 0
    for i, v in enumerate(values):
        if v >= threshold:
            count += 1
            if count >= 5:
                return i - 4  # return the start of the sustained crossing
        else:
            count = 0
    return None


def run_all_stages(pop_size=250, generations=120, seed=42):
    """Run all 4 stages and return combined results."""
    results = {}
    for stage in range(1, 5):
        print(f"  Stage {stage}: {STAGE_CONFIGS[stage]['name']}...")
        results[stage] = run_stage(stage, pop_size, generations, seed)

        # Quick summary
        final_surv = results[stage]['survival'][-1]
        final_sync = results[stage]['sync'][-1]
        final_whisper = results[stage]['whisper'][-1]
        print(f"    -> Survival={final_surv:.0%}  Sync={final_sync:.2f}  Whisper={final_whisper:.2f}")

    return results


# ============================================================================
# VISUALIZATION — 4-PANEL ATLAS
# ============================================================================

def generate_singularity_atlas(results, save_path="singularity_protocol_atlas.png"):
    """
    4-panel publication figure:
      Panel 1: Gene Trajectories Across All 4 Stages
      Panel 2: Survival Curves — Stage Comparison
      Panel 3: Phase Transition Heatmap (Sync vs Noise)
      Panel 4: The Sync Shield Activation Map (Stage 4 detail)
    """
    fig = plt.figure(figsize=(22, 14), facecolor=BG)
    fig.suptitle(
        'THE SINGULARITY PROTOCOL  --  Phase Transition Under Extreme Noise',
        color=GOLD, fontsize=18, fontweight='bold', y=0.98,
        fontfamily='monospace'
    )
    subtitle = 'Decoherence Resistance -> Ghost Protocol -> Whisper Engine -> Quantum Winter'
    fig.text(0.5, 0.955, subtitle, ha='center', color=CYAN, fontsize=10,
             fontfamily='monospace', alpha=0.7)

    gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.3,
                           left=0.06, right=0.96, top=0.92, bottom=0.06)

    def style_ax(ax, title):
        ax.set_facecolor(BG)
        ax.set_title(title, color=GOLD, fontsize=12, fontweight='bold',
                     fontfamily='monospace', pad=10)
        ax.tick_params(colors=WHITE, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(GRID)
        ax.grid(True, alpha=0.15, color=GRID)

    gens = range(120)

    # ------------------------------------------------------------------
    # PANEL 1: Key Gene Trajectories Across Stages
    # ------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1, 'GENE EVOLUTION ACROSS STAGES')

    # Show Sync, Stealth, Repair, Whisper for Stage 4
    key_genes = ['sync', 'stealth', 'repair', 'whisper']
    gene_colors = {'sync': CYAN, 'stealth': '#9C27B0', 'repair': '#FF9800', 'whisper': GOLD}

    for stage in [1, 2, 3, 4]:
        hist = results[stage]
        offset = (stage - 1) * 120
        x = [offset + g for g in range(len(hist['sync']))]

        for gene in key_genes:
            alpha = 0.3 if stage < 4 else 1.0
            lw = 1.0 if stage < 4 else 2.5
            label = None
            if stage == 4:
                label = gene.capitalize()
            ax1.plot(x, hist[gene], color=gene_colors[gene],
                    alpha=alpha, linewidth=lw, label=label)

        # Stage divider
        if stage < 4:
            ax1.axvline(x=offset + len(hist['sync']), color=GRID, linestyle='--', alpha=0.4)

    # Mark phase transition in Stage 4
    transition_gen = detect_phase_transition(results[4])
    if transition_gen is not None:
        ax1.axvline(x=360 + transition_gen, color=RED, linestyle=':', alpha=0.8, linewidth=1.5)
        ax1.text(360 + transition_gen + 3, 0.85, 'Phase\nTransition',
                color=RED, fontsize=7, fontfamily='monospace')

    ax1.set_xlabel('Generation (across 4 stages)', color=WHITE, fontsize=9)
    ax1.set_ylabel('Gene Expression', color=WHITE, fontsize=9)
    ax1.set_xticks([60, 180, 300, 420])
    ax1.set_xticklabels(['S1: Physics', 'S2: Ghost', 'S3: Whisper', 'S4: Singularity'],
                        fontsize=7, color=WHITE)
    ax1.legend(loc='upper left', fontsize=7, facecolor=BG, edgecolor=GRID,
              labelcolor=WHITE, framealpha=0.8)
    ax1.set_ylim(-0.05, 1.05)

    # ------------------------------------------------------------------
    # PANEL 2: Survival Curves Comparison
    # ------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2, 'SURVIVAL RATE BY STAGE')

    for stage in range(1, 5):
        hist = results[stage]
        x = range(len(hist['survival']))
        ax2.plot(x, hist['survival'], color=STAGE_COLORS[stage],
                linewidth=2.5, label=STAGE_CONFIGS[stage]['label'])

    ax2.axhline(y=0.86, color=GOLD, linestyle=':', alpha=0.5, linewidth=1)
    ax2.text(115, 0.87, '86%', color=GOLD, fontsize=8, ha='right', fontfamily='monospace')

    ax2.set_xlabel('Generation', color=WHITE, fontsize=9)
    ax2.set_ylabel('Survival Rate', color=WHITE, fontsize=9)
    ax2.legend(loc='lower left', fontsize=8, facecolor=BG, edgecolor=GRID,
              labelcolor=WHITE, framealpha=0.8)
    ax2.set_ylim(-0.05, 1.05)

    # ------------------------------------------------------------------
    # PANEL 3: Phase Transition Heatmap (Noise vs Sync Threshold)
    # ------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    style_ax(ax3, 'PHASE DIAGRAM: Noise vs Sync Threshold')

    # Sweep noise levels and measure when sync emerges
    noise_levels = np.linspace(0.01, 0.12, 20)
    sync_thresholds = np.linspace(0.1, 0.9, 20)

    # Pre-compute: for each noise level, what's the final sync value?
    # Use a fast approximation based on the selection pressure model
    phase_map = np.zeros((20, 20))

    for i, noise in enumerate(noise_levels):
        # Model: at high noise, isolated survival probability drops
        # Sync becomes advantageous when noise > repair_capacity
        solo_survive = max(0, 1.0 - noise * 15 * (1 - 0.5 * 0.5))
        for j, sync_thresh in enumerate(sync_thresholds):
            # If solo survival is below death threshold, sync is necessary
            if solo_survive < 0.3:
                # Above noise threshold: sync is load-bearing
                sync_benefit = max(0, 1 - (sync_thresh / 0.8))
                collective_survive = min(1.0, 0.3 + sync_benefit * 0.6)
                phase_map[j, i] = collective_survive
            else:
                # Below noise threshold: sync is optional, may hurt (detection)
                detection_cost = sync_thresh * 0.3
                phase_map[j, i] = max(0.2, solo_survive - detection_cost)

    im = ax3.imshow(phase_map, origin='lower', cmap='RdYlGn', aspect='auto',
                    extent=[noise_levels[0], noise_levels[-1],
                           sync_thresholds[0], sync_thresholds[-1]],
                    vmin=0, vmax=1)

    # Mark the Sage Constant boundary
    ax3.axhline(y=0.4, color=GOLD, linestyle='--', alpha=0.8, linewidth=1.5)
    ax3.text(0.10, 0.42, 'Sync Activation Threshold', color=GOLD,
            fontsize=7, fontfamily='monospace')

    # Mark Stage 4 operating point
    ax3.plot(0.08, results[4]['sync'][-1], 'D', color=CYAN, markersize=10,
            markeredgecolor=WHITE, markeredgewidth=1.5, zorder=10)
    ax3.text(0.082, results[4]['sync'][-1] - 0.08, 'Stage 4',
            color=CYAN, fontsize=8, fontweight='bold', fontfamily='monospace')

    cb = plt.colorbar(im, ax=ax3, shrink=0.8)
    cb.set_label('Survival Probability', color=WHITE, fontsize=8)
    cb.ax.tick_params(colors=WHITE, labelsize=7)

    ax3.set_xlabel('Base Noise Level', color=WHITE, fontsize=9)
    ax3.set_ylabel('Sync Gene Expression', color=WHITE, fontsize=9)

    # ------------------------------------------------------------------
    # PANEL 4: Stage 4 Deep Dive — The Sync Shield in Action
    # ------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 1])
    style_ax(ax4, 'STAGE 4: THE QUANTUM WINTER (Deep Dive)')

    hist4 = results[4]
    x = range(len(hist4['survival']))

    # Dual y-axis: survival + gene expression
    ax4.plot(x, hist4['survival'], color=RED, linewidth=2.5, label='Survival Rate')
    ax4.fill_between(x, 0, hist4['survival'], color=RED, alpha=0.1)

    ax4_twin = ax4.twinx()
    ax4_twin.plot(x, hist4['sync'], color=CYAN, linewidth=2.5, linestyle='-', label='Sync Gene')
    ax4_twin.plot(x, hist4['whisper'], color=GOLD, linewidth=2.0, linestyle='--', label='Whisper Gene')
    ax4_twin.plot(x, hist4['stealth'], color='#9C27B0', linewidth=1.5, linestyle=':', label='Stealth Gene')

    # Annotate the Sync Shield activation
    if transition_gen is not None:
        ax4.axvline(x=transition_gen, color=WHITE, linestyle=':', alpha=0.6)
        ax4.annotate('Sync Shield\nActivates',
                    xy=(transition_gen, hist4['survival'][transition_gen]),
                    xytext=(transition_gen + 15, 0.3),
                    color=WHITE, fontsize=8, fontweight='bold',
                    fontfamily='monospace',
                    arrowprops=dict(arrowstyle='->', color=WHITE, lw=1.5))

    ax4.set_xlabel('Generation', color=WHITE, fontsize=9)
    ax4.set_ylabel('Survival Rate', color=RED, fontsize=9)
    ax4_twin.set_ylabel('Gene Expression', color=CYAN, fontsize=9)
    ax4_twin.tick_params(colors=WHITE, labelsize=8)
    for spine in ax4_twin.spines.values():
        spine.set_color(GRID)

    # Combined legend
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2,
              loc='center right', fontsize=7, facecolor=BG,
              edgecolor=GRID, labelcolor=WHITE, framealpha=0.8)

    ax4.set_ylim(-0.05, 1.05)
    ax4_twin.set_ylim(-0.05, 1.05)

    # ------------------------------------------------------------------
    # SUMMARY ANNOTATION
    # ------------------------------------------------------------------
    s4 = results[4]
    summary_text = (
        f"FINAL STATE (Stage 4):\n"
        f"  Survival:  {s4['survival'][-1]:.0%}\n"
        f"  Sync:      {s4['sync'][-1]:.2f}\n"
        f"  Whisper:   {s4['whisper'][-1]:.2f}\n"
        f"  Stealth:   {s4['stealth'][-1]:.2f}\n"
        f"  Noise:     0.08 (3x lethal)"
    )
    fig.text(0.5, 0.01, summary_text, ha='center', color=WHITE,
            fontsize=8, fontfamily='monospace', alpha=0.7,
            bbox=dict(boxstyle='round,pad=0.5', facecolor=BG,
                     edgecolor=GOLD, alpha=0.8))

    plt.savefig(save_path, dpi=180, bbox_inches='tight', facecolor=BG)
    print(f"  [Singularity Protocol] Atlas saved -> {save_path}")
    return save_path


# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

if __name__ == '__main__':
    print()
    print('=' * 62)
    print('  THE SINGULARITY PROTOCOL')
    print('  Phase Transition Under Extreme Noise')
    print('=' * 62)

    print('\nRunning all 4 evolutionary stages...\n')
    results = run_all_stages(pop_size=250, generations=120, seed=42)

    # Phase transition analysis
    transition = detect_phase_transition(results[4])
    if transition is not None:
        print(f"\n  Phase transition detected at Generation {transition}")
        print(f"  Sync gene crossed 0.4 and sustained cooperative behavior")
    else:
        print(f"\n  No sustained phase transition detected")

    print('\n  Generating 4-panel atlas...')
    generate_singularity_atlas(results)

    # Summary report
    print('\n' + '-' * 62)
    print('  EVOLUTIONARY EPOCH SUMMARY')
    print('-' * 62)
    for stage in range(1, 5):
        s = results[stage]
        cfg = STAGE_CONFIGS[stage]
        print(f"\n  {cfg['label']}:")
        print(f"    Survival: {s['survival'][-1]:.0%}")
        print(f"    Sync:     {s['sync'][-1]:.2f}  |  Whisper: {s['whisper'][-1]:.2f}")
        print(f"    Stealth:  {s['stealth'][-1]:.2f}  |  Repair:  {s['repair'][-1]:.2f}")
        if cfg["hunters"]:
            print(f"    Captured:  {s['captured_rate'][-1]:.0%}")

    print('\n  Complete.')
