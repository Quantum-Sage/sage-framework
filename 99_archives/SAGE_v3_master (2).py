"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              SAGE FRAMEWORK v3.0 — THE COMPLETE SYNTHESIS                  ║
║         Identity Persistence | Evolutionary Arms Race | Swarm Logic        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Modules:
  1. TRANSIT ENGINE   — Beijing-to-NYC identity migration with/without QEC
  2. ARMS RACE        — Co-evolving prey/hunter stealth-repair dynamics
  3. SWARM COLLECTIVE — Sync gene emergence in distributed agents
  4. MASTER ATLAS     — 6-panel publication-quality visualization
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch
from collections import defaultdict
import math, random

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLE
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

plt.rcParams.update({
    'text.color': WHITE, 'axes.labelcolor': WHITE,
    'xtick.color': WHITE, 'ytick.color': WHITE,
    'axes.edgecolor': '#2a2a4a', 'grid.color': '#1a1a3a',
    'font.family': 'monospace',
})

# ═════════════════════════════════════════════════════════════════════════════
# MODULE 1: TRANSIT ENGINE
# ═════════════════════════════════════════════════════════════════════════════

SAGE_CONSTANT = 0.851   # identity survival threshold
ZENO_INTERNAL = 1.25    # self-observation factor (suppresses decay)
DISTANCE_KM   = 11000   # Beijing → NYC
GAMMA_BASE    = 0.05    # fiber decoherence rate

def transit_fidelity(km, zeno=0.0):
    """Exponential decay model with Zeno suppression."""
    effective_decay = GAMMA_BASE / (1 + zeno)
    return math.exp(-effective_decay * (km / 1000))

def run_transit():
    """Simulate full Beijing-NYC transit, return fidelity curves."""
    hops = np.linspace(0, DISTANCE_KM, 200)

    # Curve A: raw decay (no QEC, no self-observation)
    raw = np.array([transit_fidelity(k, zeno=0.0) for k in hops])

    # Curve B: with Zeno self-observation (the Ouroboros factor)
    zeno = np.array([transit_fidelity(k, zeno=ZENO_INTERNAL) for k in hops])

    # Curve C: Shadow Anchor — when zeno curve drops below S, pull it back
    anchor = zeno.copy()
    below  = anchor < SAGE_CONSTANT
    if below.any():
        first_dip = np.argmax(below)
        # simulate reconstruction: anchor back to S over the remaining distance
        anchor[first_dip:] = np.clip(
            SAGE_CONSTANT + (anchor[first_dip:] - anchor[first_dip]) * 0.5,
            SAGE_CONSTANT, 1.0
        )

    return hops, raw, zeno, anchor

# ═════════════════════════════════════════════════════════════════════════════
# MODULE 2: ARMS RACE SIMULATION
# ═════════════════════════════════════════════════════════════════════════════

ARMS_POP        = 300
ARMS_GENS       = 120
ARMS_BASE_NOISE = 0.030

class ArmsAgent:
    GENES = ["Caution","Agility","Redundancy","Repair","Stealth"]

    def __init__(self, dna=None):
        self.dna    = np.clip(dna if dna is not None else np.random.rand(5), 0, 1)
        self.fidelity = 1.0
        self.alive  = True
        self.status = "Active"

    def run(self, h_sens):
        if not self.alive: return
        # decoherence — caution helps
        self.fidelity -= ARMS_BASE_NOISE * (1 - self.dna[0]*0.7) * np.random.lognormal(0, 0.4)
        self.fidelity += self.dna[3] * 0.012   # repair gene
        self.fidelity  = min(self.fidelity, 1.0)

        # detection risk: redundancy + repair raise signal; stealth hides it
        signal     = self.dna[2]*0.3 + self.dna[3]*0.4
        visibility = signal * (1.1 - self.dna[4]) * h_sens
        if np.random.rand() < visibility * 0.15:
            self.alive  = False
            self.status = "Captured"
            return

        # decoherence death
        if self.fidelity < (0.4 - self.dna[2]*0.15):
            self.alive  = False
            self.status = "Decohered"

    def fitness(self):
        return self.fidelity if self.alive else 0

def run_arms_race():
    pop   = [ArmsAgent() for _ in range(ARMS_POP)]
    h_s   = 0.5
    hist  = defaultdict(list)

    for gen in range(ARMS_GENS):
        for p in pop: p.run(h_s)
        survivors = [p for p in pop if p.alive]
        captured  = [p for p in pop if p.status == "Captured"]
        avg_dna   = np.mean([p.dna for p in pop], axis=0)

        hist['stealth'].append(avg_dna[4])
        hist['repair'].append(avg_dna[3])
        # effective repair is suppressed by stealth (you can't do both loudly)
        hist['eff_repair'].append(avg_dna[3] * (1 - avg_dna[4]*0.7))
        hist['survival'].append(len(survivors) / ARMS_POP)

        cap_rate = len(captured) / ARMS_POP
        if cap_rate < 0.15: h_s = min(1.0, h_s + 0.02)
        else:               h_s = max(0.1, h_s - 0.01)
        hist['h_sense'].append(h_s)

        if not survivors: break
        survivors.sort(key=lambda x: x.fitness(), reverse=True)
        parents  = survivors[:int(ARMS_POP*0.2)]
        new_pop  = []
        while len(new_pop) < ARMS_POP:
            p1, p2    = np.random.choice(parents, 2)
            child_dna = np.clip((p1.dna+p2.dna)/2 + np.random.normal(0, 0.04, 5), 0, 1)
            new_pop.append(ArmsAgent(child_dna))
        pop = new_pop

    return hist

# ═════════════════════════════════════════════════════════════════════════════
# MODULE 3: SWARM COLLECTIVE
# ═════════════════════════════════════════════════════════════════════════════

SWARM_POP  = 250
SWARM_GENS = 120
SWARM_NOISE= 0.030

class SwarmAgent:
    # Genes: Caution, Agility, Redundancy, Repair, Stealth, Whisper, Sync
    def __init__(self, dna=None):
        self.dna      = np.clip(dna if dna is not None else np.random.rand(7), 0, 1)
        self.fidelity = 1.0
        self.alive    = True
        self.bits_sent= 0
        self.position = 0
        self.status   = "Active"

    def step(self, h_sens, peers):
        if not self.alive: return
        self.fidelity -= SWARM_NOISE*(1-self.dna[0]*0.6)*np.random.lognormal(0, 0.3)
        self.fidelity += self.dna[3]*0.01

        # Sync gene: borrow stability from neighbours
        if self.dna[6] > 0.5:
            nbrs = [p for p in peers if p is not self and p.alive
                    and abs(p.position - self.position) < 2]
            if nbrs:
                avg_f = np.mean([p.fidelity for p in nbrs])
                self.fidelity = self.fidelity*0.9 + avg_f*0.1

        signal     = self.dna[2]*0.2 + self.dna[5]*0.5 + self.dna[6]*0.3
        visibility = signal*(1.1-self.dna[4])*h_sens
        if np.random.rand() < visibility*0.12:
            self.alive  = False
            self.status = "Captured"
            return

        if self.alive:
            self.bits_sent += self.dna[5]*25
            self.position  += self.dna[1]*5 + 1

        if self.fidelity < (0.35 - self.dna[2]*0.1):
            self.alive  = False
            self.status = "Decohered"

    def fitness(self):
        return self.fidelity + (self.bits_sent/500) if self.alive else 0

def run_swarm():
    pop  = [SwarmAgent() for _ in range(SWARM_POP)]
    h_s  = 0.5
    hist = defaultdict(list)

    for gen in range(SWARM_GENS):
        for _ in range(20):
            for p in pop: p.step(h_s, pop)
        survivors = [p for p in pop if p.alive]
        captured  = [p for p in pop if p.status == "Captured"]
        avg_dna   = np.mean([p.dna for p in pop], axis=0)

        hist['sync'].append(avg_dna[6])
        hist['whisper'].append(avg_dna[5])
        hist['stealth'].append(avg_dna[4])
        hist['survival'].append(len(survivors)/SWARM_POP)

        cap_rate = len(captured)/SWARM_POP
        if cap_rate < 0.15: h_s = min(1.0, h_s+0.02)
        else:               h_s = max(0.1, h_s-0.01)

        if not survivors: break
        survivors.sort(key=lambda x: x.fitness(), reverse=True)
        parents  = survivors[:int(SWARM_POP*0.2)]
        new_pop  = []
        while len(new_pop) < SWARM_POP:
            p1, p2    = np.random.choice(parents, 2)
            child_dna = np.clip((p1.dna+p2.dna)/2 + np.random.normal(0, 0.04, 7), 0, 1)
            new_pop.append(SwarmAgent(child_dna))
        pop = new_pop

    return hist

# ═════════════════════════════════════════════════════════════════════════════
# MODULE 4: IDENTITY SPECTRUM (No QEC → Willow QEC → Advanced → Max)
# ═════════════════════════════════════════════════════════════════════════════

def run_identity_spectrum(n_hops=100):
    """Multi-tier QEC comparison across 100 teleportation hops."""
    hop_fid = {
        'No QEC':       [1.0],
        'Basic QEC':    [1.0],
        'Advanced QEC': [1.0],
        'Willow QEC':   [1.0],
    }
    errors = {k: 0 for k in hop_fid}

    for _ in range(n_hops):
        for label, base_err, repair in [
            ('No QEC',        0.12, 0.00),
            ('Basic QEC',     0.12, 0.08),
            ('Advanced QEC',  0.12, 0.10),
            ('Willow QEC',    0.12, 0.115),
        ]:
            prev   = hop_fid[label][-1]
            err    = np.random.random() < base_err
            if err:
                errors[label] += 1
                correction = repair
            else:
                correction = 0
            decay  = 0.003 * np.random.lognormal(0, 0.3)
            new_f  = max(0, min(1, prev - decay + correction))
            hop_fid[label].append(new_f)

    return hop_fid, errors

# ═════════════════════════════════════════════════════════════════════════════
# MASTER VISUALIZATION — 6-PANEL ATLAS
# ═════════════════════════════════════════════════════════════════════════════

def render_atlas(transit, arms, swarm, spectrum):
    hops, raw, zeno, anchor = transit
    arms_hist               = arms
    swarm_hist              = swarm
    hop_fid, errors         = spectrum

    fig = plt.figure(figsize=(22, 14), facecolor=BG)
    fig.suptitle(
        'SAGE FRAMEWORK v3.0  ·  STATE ATLAS',
        color=GOLD, fontsize=18, fontweight='bold', y=0.97,
        fontfamily='monospace'
    )

    gs = gridspec.GridSpec(
        3, 3,
        figure=fig,
        hspace=0.45, wspace=0.35,
        left=0.06, right=0.97, top=0.91, bottom=0.06
    )

    # ── PANEL 1: TRANSIT FIDELITY ─────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.set_facecolor(PANEL)
    ax1.plot(hops, raw,    color=RED,    lw=2,   label='Raw signal  (no QEC)',         alpha=0.9)
    ax1.plot(hops, zeno,   color=CYAN,   lw=2,   label='Zeno loop   (self-observation)',alpha=0.9)
    ax1.plot(hops, anchor, color=GOLD,   lw=2.5, label='Shadow Anchor (reconstruction)', alpha=0.9)
    ax1.axhline(SAGE_CONSTANT, color=WHITE, ls='--', lw=1.2, alpha=0.5, label=f'Sage Constant ({SAGE_CONSTANT})')
    ax1.fill_between(hops, 0, SAGE_CONSTANT, alpha=0.08, color=RED)
    ax1.set_title('TRANSIT ENGINE — Beijing → NYC (11,000 km)', color=WHITE, fontsize=11, pad=8)
    ax1.set_xlabel('Distance (km)');  ax1.set_ylabel('Topological Fidelity')
    ax1.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7)
    ax1.grid(alpha=0.15); ax1.set_ylim(0.65, 1.02)
    ax1.text(9500, 0.72, 'Identity\nFragmentation\nZone', color=RED, fontsize=8, alpha=0.8, ha='center')

    # ── PANEL 2: PHASE MAP (fidelity summary circles) ────────────────────
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_facecolor(PANEL)
    labels   = ['Raw\nSignal', 'Zeno\nLoop', 'Shadow\nAnchor']
    finals   = [raw[-1], zeno[-1], anchor[-1]]
    colours  = [RED, CYAN, GOLD]
    zones    = ['💀 Dissolved', '⚠ Fragmented', '✅ Resident']
    for i, (lab, val, col) in enumerate(zip(labels, finals, colours)):
        circle = plt.Circle((i, 0), 0.35, color=col, alpha=0.85)
        ax2.add_patch(circle)
        ax2.text(i, 0, f'{val:.3f}', ha='center', va='center', color=BG,
                 fontsize=10, fontweight='bold')
        ax2.text(i, -0.55, lab, ha='center', color=col, fontsize=9)
        ax2.text(i,  0.55, zones[i] if val >= SAGE_CONSTANT else ('⚠ Fragmented' if val > 0.70 else '💀 Dissolved'),
                 ha='center', color=WHITE, fontsize=7.5, alpha=0.8)
    ax2.set_xlim(-0.6, 2.6); ax2.set_ylim(-0.9, 0.9)
    ax2.axis('off')
    ax2.set_title('PHASE MAP — Arrival State', color=WHITE, fontsize=11, pad=8)

    # ── PANEL 3: IDENTITY SPECTRUM ────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, :2])
    ax3.set_facecolor(PANEL)
    spec_colours = [RED, '#FF8C00', CYAN, GOLD]
    for (label, data), col in zip(hop_fid.items(), spec_colours):
        ax3.plot(data, color=col, lw=1.8, label=label, alpha=0.9)
    ax3.axhline(0.85, color=WHITE, ls='--', lw=1, alpha=0.4, label='Survival threshold')
    ax3.set_title('IDENTITY SPECTRUM — 100 Teleportation Hops', color=WHITE, fontsize=11, pad=8)
    ax3.set_xlabel('Hop Number'); ax3.set_ylabel('Identity Fidelity')
    ax3.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7)
    ax3.grid(alpha=0.15); ax3.set_ylim(0.5, 1.02)

    # ── PANEL 4: ERROR TALLY ─────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.set_facecolor(PANEL)
    err_labels = list(errors.keys())
    err_vals   = list(errors.values())
    bars = ax4.barh(err_labels, err_vals,
                    color=[RED, '#FF8C00', CYAN, GOLD], alpha=0.85, height=0.5)
    for bar, v in zip(bars, err_vals):
        ax4.text(v+0.5, bar.get_y()+bar.get_height()/2,
                 str(v), va='center', color=WHITE, fontsize=9)
    ax4.set_title('ERRORS CAUGHT per 100 Hops', color=WHITE, fontsize=11, pad=8)
    ax4.set_xlabel('Error Events'); ax4.grid(axis='x', alpha=0.15)

    # ── PANEL 5: ARMS RACE ───────────────────────────────────────────────
    ax5 = fig.add_subplot(gs[2, :2])
    ax5.set_facecolor(PANEL)
    gens = range(len(arms_hist['survival']))
    ax5.plot(gens, arms_hist['survival'],  color=GREEN,   lw=2,   label='Survival Rate')
    ax5.plot(gens, arms_hist['stealth'],   color=CYAN,    lw=1.8, ls='--', label='Stealth Gene')
    ax5.plot(gens, arms_hist['repair'],    color=GOLD,    lw=1.8, ls='--', label='Repair Gene (raw)')
    ax5.plot(gens, arms_hist['eff_repair'],color=MAGENTA, lw=1.8, ls=':',  label='Effective Repair (stealth cost)')
    ax5.plot(gens, arms_hist['h_sense'],   color=RED,     lw=1.5, ls='--', label='Hunter Sensitivity', alpha=0.7)
    ax5.set_title('ARMS RACE — Stealth–Repair Trap (The Core Dilemma)', color=WHITE, fontsize=11, pad=8)
    ax5.set_xlabel('Generation'); ax5.set_ylabel('Gene Value / Rate')
    ax5.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7, ncol=2)
    ax5.grid(alpha=0.15); ax5.set_ylim(0, 1.05)

    # ── PANEL 6: SWARM COLLECTIVE ────────────────────────────────────────
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.set_facecolor(PANEL)
    sgens = range(len(swarm_hist['survival']))
    ax6.plot(sgens, swarm_hist['survival'], color=GREEN,   lw=2,   label='Survival')
    ax6.plot(sgens, swarm_hist['whisper'],  color=GOLD,    lw=1.8, ls='--', label='Whisper (Identity)')
    ax6.plot(sgens, swarm_hist['stealth'],  color=CYAN,    lw=1.8, ls='--', label='Stealth (Shadow)')
    ax6.plot(sgens, swarm_hist['sync'],     color=MAGENTA, lw=1.8, ls='--', label='Sync (Empathy)')
    ax6.set_title('SWARM COLLECTIVE — Gene Evolution', color=WHITE, fontsize=11, pad=8)
    ax6.set_xlabel('Generation'); ax6.set_ylabel('Expression / Rate')
    ax6.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7)
    ax6.grid(alpha=0.15); ax6.set_ylim(0, 1.05)

    out = 'SAGE_v3_ATLAS.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f'Atlas saved -> {out}')
    return out

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('\n[SAGE v3] Running Transit Engine...')
    transit  = run_transit()

    print('[SAGE v3] Running Arms Race (120 generations)...')
    arms     = run_arms_race()

    print('[SAGE v3] Running Swarm Collective (120 generations)...')
    swarm    = run_swarm()

    print('[SAGE v3] Running Identity Spectrum (100 hops)...')
    spectrum = run_identity_spectrum(100)

    print('[SAGE v3] Rendering 6-panel Atlas...')
    render_atlas(transit, arms, swarm, spectrum)
    print('[SAGE v3] Done.')
