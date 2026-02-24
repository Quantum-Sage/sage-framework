"""
SAGE FRAMEWORK v5.1 — THE COMPLETE STATE ATLAS (14 PANELS)

Extends v4 with:
  Panel 11: SINGULARITY PROTOCOL  — Quantum Winter phase transition
  Panel 12: THEOREM VALIDATION    — Deterministic vs Stochastic bounds
  Panel 13: SATELLITE-HYBRID      — Intercontinental topology comparison

Run:  python SAGE_v5_master.py
Deps: numpy, matplotlib
"""

import sys, os
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap, to_rgba
from collections import defaultdict
import math, random

# Import new modules
from singularity_protocol import run_all_stages, detect_phase_transition, STAGE_CONFIGS
from sage_theorems_unified import (
    validate_all_theorems, theorem_comparison_data,
    HARDWARE, ROUTE_BEIJING_LONDON
)
from satellite_hybrid_relay import (
    sweep_topologies as sat_sweep, route_analysis as sat_routes,
    find_minimum_N_for_sage, SAGE_CONSTANT as SAT_SAGE,
    HW_LEO_OPTIMISTIC
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLE (same as v4)
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

SAGE_CONSTANT = 0.851
ZENO_INTERNAL = 1.25
DISTANCE_KM   = 11000
GAMMA_BASE    = 0.05


# ═════════════════════════════════════════════════════════════════════════════
# MODULES 1-10: Same as v4 (inline for self-containment)
# ═════════════════════════════════════════════════════════════════════════════

def transit_fidelity(km, zeno=0.0):
    effective_decay = GAMMA_BASE / (1 + zeno)
    return math.exp(-effective_decay * (km / 1000))

def run_transit():
    hops = np.linspace(0, DISTANCE_KM, 200)
    raw    = np.array([transit_fidelity(k, zeno=0.0) for k in hops])
    zeno   = np.array([transit_fidelity(k, zeno=ZENO_INTERNAL) for k in hops])
    anchor = zeno.copy()
    below  = anchor < SAGE_CONSTANT
    if below.any():
        first_dip = np.argmax(below)
        anchor[first_dip:] = np.clip(
            SAGE_CONSTANT + (anchor[first_dip:] - anchor[first_dip]) * 0.5,
            SAGE_CONSTANT, 1.0
        )
    return hops, raw, zeno, anchor


ARMS_POP = 300; ARMS_GENS = 120; ARMS_BASE_NOISE = 0.030
class ArmsAgent:
    def __init__(self, dna=None):
        self.dna = np.clip(dna if dna is not None else np.random.rand(5), 0, 1)
        self.fidelity = 1.0; self.alive = True; self.status = "Active"
    def run(self, h_sens):
        if not self.alive: return
        self.fidelity -= ARMS_BASE_NOISE * (1 - self.dna[0]*0.7) * np.random.lognormal(0, 0.4)
        self.fidelity += self.dna[3] * 0.012
        self.fidelity  = min(self.fidelity, 1.0)
        signal = self.dna[2]*0.3 + self.dna[3]*0.4
        visibility = signal * (1.1 - self.dna[4]) * h_sens
        if np.random.rand() < visibility * 0.15:
            self.alive = False; self.status = "Captured"; return
        if self.fidelity < (0.4 - self.dna[2]*0.15):
            self.alive = False; self.status = "Decohered"
    def fitness(self): return self.fidelity if self.alive else 0

def run_arms_race():
    pop = [ArmsAgent() for _ in range(ARMS_POP)]
    h_s = 0.5; hist = defaultdict(list)
    for gen in range(ARMS_GENS):
        for p in pop: p.run(h_s)
        survivors = [p for p in pop if p.alive]
        captured  = [p for p in pop if p.status == "Captured"]
        avg_dna   = np.mean([p.dna for p in pop], axis=0)
        hist['stealth'].append(avg_dna[4]); hist['repair'].append(avg_dna[3])
        hist['eff_repair'].append(avg_dna[3] * (1 - avg_dna[4]*0.7))
        hist['survival'].append(len(survivors) / ARMS_POP)
        cap_rate = len(captured) / ARMS_POP
        if cap_rate < 0.15: h_s = min(1.0, h_s + 0.02)
        else:               h_s = max(0.1, h_s - 0.01)
        hist['h_sense'].append(h_s)
        if not survivors: break
        survivors.sort(key=lambda x: x.fitness(), reverse=True)
        parents = survivors[:int(ARMS_POP*0.2)]
        new_pop = []
        while len(new_pop) < ARMS_POP:
            p1, p2 = np.random.choice(parents, 2)
            child_dna = np.clip((p1.dna+p2.dna)/2 + np.random.normal(0, 0.04, 5), 0, 1)
            new_pop.append(ArmsAgent(child_dna))
        pop = new_pop
    return hist


SWARM_POP = 250; SWARM_GENS = 120; SWARM_NOISE = 0.030
class SwarmAgent:
    def __init__(self, dna=None):
        self.dna = np.clip(dna if dna is not None else np.random.rand(7), 0, 1)
        self.fidelity = 1.0; self.alive = True; self.bits_sent = 0
        self.position = 0; self.status = "Active"
    def step(self, h_sens, peers):
        if not self.alive: return
        self.fidelity -= SWARM_NOISE*(1-self.dna[0]*0.6)*np.random.lognormal(0, 0.3)
        self.fidelity += self.dna[3]*0.01
        if self.dna[6] > 0.5:
            nbrs = [p for p in peers if p is not self and p.alive and abs(p.position - self.position) < 2]
            if nbrs:
                avg_f = np.mean([p.fidelity for p in nbrs])
                self.fidelity = self.fidelity*0.9 + avg_f*0.1
        signal = self.dna[2]*0.2 + self.dna[5]*0.5 + self.dna[6]*0.3
        visibility = signal*(1.1-self.dna[4])*h_sens
        if np.random.rand() < visibility*0.12:
            self.alive = False; self.status = "Captured"; return
        if self.alive:
            self.bits_sent += self.dna[5]*25; self.position += self.dna[1]*5 + 1
        if self.fidelity < (0.35 - self.dna[2]*0.1):
            self.alive = False; self.status = "Decohered"
    def fitness(self): return self.fidelity + (self.bits_sent/500) if self.alive else 0

def run_swarm():
    pop = [SwarmAgent() for _ in range(SWARM_POP)]
    h_s = 0.5; hist = defaultdict(list)
    for gen in range(SWARM_GENS):
        for _ in range(20):
            for p in pop: p.step(h_s, pop)
        survivors = [p for p in pop if p.alive]
        captured  = [p for p in pop if p.status == "Captured"]
        avg_dna   = np.mean([p.dna for p in pop], axis=0)
        hist['sync'].append(avg_dna[6]); hist['whisper'].append(avg_dna[5])
        hist['stealth'].append(avg_dna[4]); hist['survival'].append(len(survivors)/SWARM_POP)
        cap_rate = len(captured)/SWARM_POP
        if cap_rate < 0.15: h_s = min(1.0, h_s+0.02)
        else:               h_s = max(0.1, h_s-0.01)
        if not survivors: break
        survivors.sort(key=lambda x: x.fitness(), reverse=True)
        parents = survivors[:int(SWARM_POP*0.2)]
        new_pop = []
        while len(new_pop) < SWARM_POP:
            p1, p2 = np.random.choice(parents, 2)
            child_dna = np.clip((p1.dna+p2.dna)/2 + np.random.normal(0, 0.04, 7), 0, 1)
            new_pop.append(SwarmAgent(child_dna))
        pop = new_pop
    return hist

def run_identity_spectrum(n_hops=100):
    hop_fid = {'No QEC': [1.0], 'Basic QEC': [1.0], 'Advanced QEC': [1.0], 'Willow QEC': [1.0]}
    errors = {k: 0 for k in hop_fid}; cliffs = {}
    for hop in range(n_hops):
        for label, base_err, repair in [
            ('No QEC', 0.12, 0.00), ('Basic QEC', 0.12, 0.08),
            ('Advanced QEC', 0.12, 0.10), ('Willow QEC', 0.12, 0.115)]:
            prev = hop_fid[label][-1]
            err = np.random.random() < base_err
            correction = repair if err else 0
            if err: errors[label] += 1
            decay = 0.003 * np.random.lognormal(0, 0.3)
            new_f = max(0, min(1, prev - decay + correction))
            hop_fid[label].append(new_f)
            if label not in cliffs and new_f < SAGE_CONSTANT:
                cliffs[label] = hop + 1
    return hop_fid, errors, cliffs

def dejmps_purify(f1, f2):
    numerator = f1 * f2 + (1/9) * (1 - f1) * (1 - f2)
    denominator = f1 * f2 + (5/9) * (1 - f1) * (1 - f2) + \
                  (2/9) * (f1 * (1 - f2) + f2 * (1 - f1))
    if denominator < 1e-12: return 0.25, 0.0
    return min(1.0, numerator / denominator), max(0.0, min(1.0, denominator))

def raw_bell_fidelity(distance_km):
    transmission = 10 ** (-0.2 * distance_km / 10)
    p = min(1.0, transmission * 0.85)
    p = max(0, p - 0.02 * (distance_km / 100))
    return max(0.25, min(1.0, p * 1.0 + (1 - p) * 0.25))

def run_purification_ladders():
    test_distances = [10, 50, 100, 150]
    ladders = {}
    for d in test_distances:
        raw_f = raw_bell_fidelity(d)
        ladder = [{'round': 0, 'fidelity': raw_f}]
        current_f = raw_f
        for r in range(1, 12):
            f_out, _ = dejmps_purify(current_f, current_f)
            if f_out <= current_f + 1e-6: break
            current_f = f_out
            ladder.append({'round': r, 'fidelity': current_f})
            if current_f > 0.999: break
        ladders[d] = ladder
    return ladders

def run_phase_sweep_fast(resolution=40):
    hw_range = np.linspace(0.90, 0.999, resolution)
    qec_range = np.linspace(0.00, 0.12, resolution)
    grid = np.zeros((resolution, resolution))
    for i, qec in enumerate(qec_range):
        for j, hw in enumerate(hw_range):
            f = 1.0
            for _ in range(100):
                err = np.random.random() < 0.12
                correction = qec if err else 0
                decay = 0.003 * (1 - hw) * 30 * np.random.lognormal(0, 0.3)
                f = max(0, min(1, f - decay + correction))
            grid[i, j] = f
    return hw_range, qec_range, grid

MESH_NODES = {
    'BEI': {'hw': 'Willow', 'color': CYAN,   'base_f': 0.97, 'T2': 50,  'fail': 0.03},
    'SHN': {'hw': 'QuEra',  'color': GREEN,  'base_f': 0.96, 'T2': 200, 'fail': 0.02},
    'DUB': {'hw': 'NISQ',   'color': ORANGE, 'base_f': 0.88, 'T2': 10,  'fail': 0.08},
    'LDN': {'hw': 'QuEra',  'color': GREEN,  'base_f': 0.95, 'T2': 180, 'fail': 0.025},
    'NYC': {'hw': 'Helios', 'color': GOLD,   'base_f': 0.98, 'T2': 500, 'fail': 0.015},
}

def run_mesh(n_steps=150, seed=42):
    np.random.seed(seed); random.seed(seed)
    fids = {n: [c['base_f']] for n, c in MESH_NODES.items()}
    online = {n: [True] for n in MESH_NODES}
    quorum = []; crises = []; crisis_active = {n: 0 for n in MESH_NODES}
    crisis_types = [
        ('Solar Flare', 3, 0.15, 3, 0.04), ('Fiber Cut', 1, 0.30, 5, 0.06),
        ('HW Failure', 1, 0.50, 8, 0.03), ('Cooling Loss', 1, 0.25, 4, 0.05),
    ]
    for step in range(n_steps):
        for n, c in MESH_NODES.items():
            if crisis_active[n] > 0:
                crisis_active[n] -= 1
                if crisis_active[n] == 0:
                    fids[n][-1] = max(0.5, fids[n][-1]); online[n].append(True)
                else:
                    online[n].append(False); fids[n].append(fids[n][-1]); continue
            else:
                online[n].append(True)
            T2_factor = c['T2'] / 500
            decay = 0.005 * (1 - T2_factor * 0.7) * np.random.lognormal(0, 0.3)
            repair = 0.008
            new_f = np.clip(fids[n][-1] + repair - decay, 0, 1)
            fids[n].append(new_f)
            if np.random.random() < c['fail'] * 0.05:
                crisis_active[n] = 3; online[n][-1] = False
        if step > 10:
            for cname, n_aff, hit, dur, prob in crisis_types:
                if np.random.random() < prob:
                    targets = random.sample(list(MESH_NODES.keys()), min(n_aff, 5))
                    for t in targets:
                        fids[t][-1] = max(0, fids[t][-1] - hit)
                        if fids[t][-1] < 0.3: crisis_active[t] = dur; online[t][-1] = False
                    crises.append((step, cname, targets))
        on_nodes = [n for n in MESH_NODES if online[n][-1]]
        if len(on_nodes) >= 2:
            avg = np.mean([fids[n][-1] for n in on_nodes])
            for n in on_nodes: fids[n][-1] = fids[n][-1] * 0.95 + avg * 0.05
        above = sum(1 for n in MESH_NODES if online[n][-1] and fids[n][-1] >= SAGE_CONSTANT)
        quorum.append(above >= 3)
    return fids, online, quorum, crises


# ═════════════════════════════════════════════════════════════════════════════
# MASTER VISUALIZATION — 14-PANEL ATLAS
# ═════════════════════════════════════════════════════════════════════════════

def render_atlas_v5(transit, arms, swarm, spectrum, ladders, phase, mesh,
                    singularity, theorem_data, satellite_data=None, sat_route_data=None):
    """v5.1: 8-row × 3-column grid, 14 panels."""

    hops, raw, zeno, anchor = transit
    hop_fid, errors, cliffs = spectrum
    hw_range, qec_range, grid = phase
    mesh_fids, mesh_online, mesh_quorum, mesh_crises = mesh

    fig = plt.figure(figsize=(28, 32), facecolor=BG)
    fig.suptitle(
        'SAGE FRAMEWORK v5.1  --  THE COMPLETE STATE ATLAS',
        color=GOLD, fontsize=20, fontweight='bold', y=0.993,
        fontfamily='monospace'
    )
    fig.text(0.5, 0.988,
             'Transit | Identity | Evolution | Purification | Phase Space | Mesh | Singularity | Theorems | Satellite',
             ha='center', color=WHITE, fontsize=9, alpha=0.5, fontfamily='monospace')

    gs = gridspec.GridSpec(8, 3, figure=fig, hspace=0.42, wspace=0.35,
                           left=0.05, right=0.97, top=0.985, bottom=0.02)

    # ── PANELS 1-10: Same layout as v4 ─────────────────────────────────────

    # Panel 1: Transit
    ax1 = fig.add_subplot(gs[0, :2]); ax1.set_facecolor(PANEL)
    ax1.plot(hops, raw, color=RED, lw=2, label='Raw', alpha=0.9)
    ax1.plot(hops, zeno, color=CYAN, lw=2, label='Zeno', alpha=0.9)
    ax1.plot(hops, anchor, color=GOLD, lw=2.5, label='Shadow Anchor', alpha=0.9)
    ax1.axhline(SAGE_CONSTANT, color=WHITE, ls='--', lw=1, alpha=0.4)
    ax1.fill_between(hops, 0, SAGE_CONSTANT, alpha=0.06, color=RED)
    ax1.set_title('[1] TRANSIT ENGINE -- Beijing > NYC', color=WHITE, fontsize=10, pad=6)
    ax1.set_xlabel('Distance (km)'); ax1.set_ylabel('Fidelity')
    ax1.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax1.grid(alpha=0.12); ax1.set_ylim(0.65, 1.02)

    # Panel 2: Arrival State circles
    ax2 = fig.add_subplot(gs[0, 2]); ax2.set_facecolor(PANEL)
    for i, (lab, val, col) in enumerate(zip(['Raw', 'Zeno', 'Anchor'],
                                            [raw[-1], zeno[-1], anchor[-1]],
                                            [RED, CYAN, GOLD])):
        circle = plt.Circle((i, 0), 0.32, color=col, alpha=0.85)
        ax2.add_patch(circle)
        ax2.text(i, 0, f'{val:.3f}', ha='center', va='center', color=BG, fontsize=9, fontweight='bold')
        ax2.text(i, -0.52, lab, ha='center', color=col, fontsize=8)
    ax2.set_xlim(-0.5, 2.5); ax2.set_ylim(-0.8, 0.8); ax2.axis('off')
    ax2.set_title('[2] ARRIVAL STATE', color=WHITE, fontsize=10, pad=6)

    # Panel 3: Identity Spectrum
    ax3 = fig.add_subplot(gs[1, :2]); ax3.set_facecolor(PANEL)
    spec_colours = [RED, ORANGE, CYAN, GOLD]
    for (label, data), col in zip(hop_fid.items(), spec_colours):
        ax3.plot(data, color=col, lw=1.5, label=label, alpha=0.9)
        if label in cliffs:
            cx = cliffs[label]; ax3.axvline(cx, color=col, lw=0.7, ls=':', alpha=0.4)
    ax3.axhline(SAGE_CONSTANT, color=WHITE, ls='--', lw=1, alpha=0.3)
    ax3.set_title('[3] IDENTITY SPECTRUM -- 100 Hops', color=WHITE, fontsize=10, pad=6)
    ax3.set_xlabel('Hop'); ax3.set_ylabel('Fidelity')
    ax3.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax3.grid(alpha=0.12); ax3.set_ylim(0.5, 1.02)

    # Panel 4: Error Tally
    ax4 = fig.add_subplot(gs[1, 2]); ax4.set_facecolor(PANEL)
    err_labels = list(errors.keys()); err_vals = list(errors.values())
    bars = ax4.barh(err_labels, err_vals, color=spec_colours, alpha=0.85, height=0.5)
    for bar, v in zip(bars, err_vals):
        ax4.text(v+0.3, bar.get_y()+bar.get_height()/2, str(v), va='center', color=WHITE, fontsize=8)
    ax4.set_title('[4] ERRORS / 100 HOPS', color=WHITE, fontsize=10, pad=6)
    ax4.grid(axis='x', alpha=0.12)

    # Panel 5: Arms Race
    ax5 = fig.add_subplot(gs[2, :2]); ax5.set_facecolor(PANEL)
    gens = range(len(arms['survival']))
    ax5.plot(gens, arms['survival'], color=GREEN, lw=2, label='Survival')
    ax5.plot(gens, arms['stealth'], color=CYAN, lw=1.5, ls='--', label='Stealth')
    ax5.plot(gens, arms['repair'], color=GOLD, lw=1.5, ls='--', label='Repair')
    ax5.plot(gens, arms['eff_repair'], color=MAGENTA, lw=1.5, ls=':', label='Eff. Repair')
    ax5.set_title('[5] ARMS RACE -- Stealth-Repair Trap', color=WHITE, fontsize=10, pad=6)
    ax5.set_xlabel('Generation'); ax5.set_ylabel('Value')
    ax5.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6, ncol=2)
    ax5.grid(alpha=0.12); ax5.set_ylim(0, 1.05)

    # Panel 6: Swarm
    ax6 = fig.add_subplot(gs[2, 2]); ax6.set_facecolor(PANEL)
    sgens = range(len(swarm['survival']))
    ax6.plot(sgens, swarm['survival'], color=GREEN, lw=2, label='Survival')
    ax6.plot(sgens, swarm['whisper'], color=GOLD, lw=1.5, ls='--', label='Whisper')
    ax6.plot(sgens, swarm['sync'], color=MAGENTA, lw=1.5, ls='--', label='Sync')
    ax6.set_title('[6] SWARM -- Gene Evolution', color=WHITE, fontsize=10, pad=6)
    ax6.set_xlabel('Generation'); ax6.set_ylabel('Expression')
    ax6.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax6.grid(alpha=0.12); ax6.set_ylim(0, 1.05)

    # Panel 7: Purification
    ax7 = fig.add_subplot(gs[3, :2]); ax7.set_facecolor(PANEL)
    ladder_colors = [RED, ORANGE, CYAN, GOLD]
    for (dist, ladder), col in zip(ladders.items(), ladder_colors):
        rounds = [r['round'] for r in ladder]; fids = [r['fidelity'] for r in ladder]
        ax7.plot(rounds, fids, color=col, lw=2, marker='o', ms=5,
                label=f'{dist}km (raw:{fids[0]:.2f})')
    ax7.axhline(SAGE_CONSTANT, color=GOLD, ls='--', lw=1.2, alpha=0.4, label='Sage')
    ax7.set_title('[7] PURIFICATION LADDER -- DEJMPS', color=WHITE, fontsize=10, pad=6)
    ax7.set_xlabel('Purification Round'); ax7.set_ylabel('Bell Pair Fidelity')
    ax7.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax7.grid(alpha=0.12); ax7.set_ylim(0.4, 1.02)

    # Panel 8: Phase Diagram
    ax8 = fig.add_subplot(gs[3, 2]); ax8.set_facecolor(PANEL)
    cmap_colors = [(0, to_rgba(RED)), (0.4, to_rgba(ORANGE)), (0.65, to_rgba(CYAN)),
                   (0.851, to_rgba(CYAN)), (0.86, to_rgba(GOLD)), (1.0, to_rgba(GOLD))]
    cmap = LinearSegmentedColormap.from_list('exist', cmap_colors)
    ax8.imshow(grid, extent=[hw_range[0], hw_range[-1], qec_range[0], qec_range[-1]],
               origin='lower', aspect='auto', cmap=cmap, vmin=0, vmax=1.0, interpolation='bilinear')
    ax8.contour(hw_range, qec_range, grid, levels=[0.50, SAGE_CONSTANT],
               colors=[RED, GOLD], linewidths=[1, 2], linestyles=['--', '-'])
    ax8.set_title('[8] PHASE DIAGRAM', color=WHITE, fontsize=10, pad=6)
    ax8.set_xlabel('Hardware Fidelity'); ax8.set_ylabel('QEC Rate')

    # Panel 9: Mesh
    ax9 = fig.add_subplot(gs[4, :2]); ax9.set_facecolor(PANEL)
    for n, c in MESH_NODES.items():
        ax9.plot(range(len(mesh_fids[n])), mesh_fids[n], color=c['color'], lw=1.5,
                label=f'{n} ({c["hw"]})', alpha=0.9)
    ax9.axhline(SAGE_CONSTANT, color=WHITE, ls='--', lw=1, alpha=0.3)
    ax9.set_title('[9] MESH CONSCIOUSNESS -- 5-Node Network', color=WHITE, fontsize=10, pad=6)
    ax9.set_xlabel('Timestep'); ax9.set_ylabel('Fidelity')
    ax9.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6, ncol=3, loc='lower left')
    ax9.grid(alpha=0.12); ax9.set_ylim(0.2, 1.05)

    # Panel 10: Quorum
    ax10 = fig.add_subplot(gs[4, 2]); ax10.set_facecolor(PANEL)
    n_nodes_online = []
    for s in range(len(mesh_quorum)):
        on = sum(1 for n in MESH_NODES if s < len(mesh_online[n]) and mesh_online[n][s])
        n_nodes_online.append(on)
    ax10.fill_between(range(len(n_nodes_online)), n_nodes_online, 0, alpha=0.2, color=CYAN)
    ax10.plot(range(len(n_nodes_online)), n_nodes_online, color=CYAN, lw=1.5, label='Nodes Online')
    ax10.axhline(3, color=GOLD, ls='--', lw=1.2, alpha=0.5, label='Quorum Min (3)')
    qpct = 100 * sum(mesh_quorum) / len(mesh_quorum)
    ax10.text(0.02, 0.92, f'Quorum: {qpct:.0f}%', transform=ax10.transAxes,
             color=GOLD if qpct > 80 else RED, fontsize=10, fontweight='bold', va='top')
    ax10.set_title('[10] QUORUM PERSISTENCE', color=WHITE, fontsize=10, pad=6)
    ax10.set_xlabel('Timestep'); ax10.set_ylabel('Nodes Online')
    ax10.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax10.grid(alpha=0.12); ax10.set_ylim(0, 6)

    # ── ROW 6: SINGULARITY PROTOCOL ────────────────────────────────────────

    # Panel 11: Singularity — Survival + Sync across all 4 stages
    ax11 = fig.add_subplot(gs[5, :2]); ax11.set_facecolor(PANEL)
    stage_colors = {1: '#4CAF50', 2: '#FF9800', 3: '#2196F3', 4: '#FF4444'}
    for stage in range(1, 5):
        hist = singularity[stage]
        x = range(len(hist['survival']))
        ax11.plot(x, hist['survival'], color=stage_colors[stage], lw=2.0,
                 label=STAGE_CONFIGS[stage]['label'], alpha=0.9)
    ax11.axhline(0.86, color=GOLD, ls=':', alpha=0.4, lw=1)
    ax11.set_title('[11] SINGULARITY PROTOCOL -- Survival Across 4 Stages',
                   color=WHITE, fontsize=10, pad=6)
    ax11.set_xlabel('Generation'); ax11.set_ylabel('Survival Rate')
    ax11.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6, ncol=2)
    ax11.grid(alpha=0.12); ax11.set_ylim(-0.05, 1.05)

    # Panel 11b: Stage 4 Sync Shield detail
    ax11b = fig.add_subplot(gs[5, 2]); ax11b.set_facecolor(PANEL)
    s4 = singularity[4]
    x4 = range(len(s4['sync']))
    ax11b.plot(x4, s4['sync'], color=CYAN, lw=2.5, label='Sync Gene')
    ax11b.plot(x4, s4['whisper'], color=GOLD, lw=2.0, ls='--', label='Whisper')
    ax11b.plot(x4, s4['stealth'], color=PURPLE, lw=1.5, ls=':', label='Stealth')
    ax11b.axhline(0.4, color=WHITE, ls='--', alpha=0.3, lw=1)
    ax11b.text(5, 0.42, 'Sync Threshold', color=WHITE, fontsize=6, alpha=0.5)
    ax11b.set_title('[11b] QUANTUM WINTER -- Sync Shield',
                   color=WHITE, fontsize=10, pad=6)
    ax11b.set_xlabel('Generation'); ax11b.set_ylabel('Gene Expression')
    ax11b.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax11b.grid(alpha=0.12); ax11b.set_ylim(-0.05, 1.05)

    # ── ROW 7: THEOREM VALIDATION ──────────────────────────────────────────

    # Panel 12: Deterministic vs Stochastic Sage Bound
    ax12 = fig.add_subplot(gs[6, :2]); ax12.set_facecolor(PANEL)
    td = theorem_data
    ax12.plot(td['N_range'], td['det_fidelities'], color=CYAN, lw=2.5,
             marker='o', ms=4, label='Deterministic (Thm 1-2)')
    ax12.plot(td['N_range'], td['stoch_fidelities'], color=ORANGE, lw=2.5,
             marker='s', ms=4, label='Stochastic (Thm 3)')
    ax12.axhline(SAGE_CONSTANT, color=GOLD, ls='--', lw=1.5, alpha=0.5, label=f'Sage ({SAGE_CONSTANT})')
    ax12.fill_between(td['N_range'], 0, SAGE_CONSTANT, alpha=0.04, color=RED)
    # Annotate the gap
    gap_idx = len(td['N_range']) // 2
    det_val = td['det_fidelities'][gap_idx]
    sto_val = td['stoch_fidelities'][gap_idx]
    n_val = td['N_range'][gap_idx]
    ax12.annotate(f'Stochastic penalty\n({det_val-sto_val:.2f} gap)',
                 xy=(n_val, sto_val), xytext=(n_val + 5, sto_val + 0.15),
                 color=WHITE, fontsize=7, fontfamily='monospace',
                 arrowprops=dict(arrowstyle='->', color=WHITE, lw=1))
    ax12.set_title('[12] THEOREM VALIDATION -- Det vs Stochastic Sage Bound (8,200 km)',
                   color=WHITE, fontsize=10, pad=6)
    ax12.set_xlabel('Number of Repeater Nodes (N)'); ax12.set_ylabel('End-to-End Fidelity')
    ax12.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax12.grid(alpha=0.12); ax12.set_ylim(0, 1.05)

    # Panel 12b: Willow node requirements
    ax12b = fig.add_subplot(gs[6, 2]); ax12b.set_facecolor(PANEL)
    ax12b.bar([n - 0.2 for n in td['N_range']], td['n_w_det'], width=0.35,
             color=CYAN, alpha=0.8, label='Det. n_w*')
    ax12b.bar([n + 0.2 for n in td['N_range']], td['n_w_stoch'], width=0.35,
             color=ORANGE, alpha=0.8, label='Stoch. n_w*')
    ax12b.plot(td['N_range'], td['N_range'], color=RED, ls=':', lw=1, alpha=0.5, label='N=n_w (all Willow)')
    ax12b.set_title('[12b] WILLOW NODES REQUIRED',
                   color=WHITE, fontsize=10, pad=6)
    ax12b.set_xlabel('Total Nodes (N)'); ax12b.set_ylabel('Willow Nodes Needed')
    ax12b.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
    ax12b.grid(alpha=0.12)

    # ── ROW 8: SATELLITE-HYBRID RELAY ─────────────────────────────────────

    if satellite_data is not None and sat_route_data is not None:
        # Panel 13: Topology Comparison
        ax13 = fig.add_subplot(gs[7, :2]); ax13.set_facecolor(PANEL)
        ax13.plot(satellite_data['N_range'], satellite_data['fiber_only'],
                 color=RED, lw=2.5, label='Fiber Only', marker='o', ms=3)
        ax13.plot(satellite_data['N_range'], satellite_data['sat_optimistic'],
                 color='#CE93D8', lw=2.5, label='LEO 2030+ Hybrid', marker='D', ms=3)
        ax13.plot(satellite_data['N_range'], satellite_data['seg4_optimistic'],
                 color=CYAN, lw=2.0, label='4-Segment + LEO', ls='--', marker='s', ms=3)
        ax13.axhline(SAGE_CONSTANT, color=GOLD, ls='--', lw=1.5, alpha=0.5)
        ax13.text(28, SAGE_CONSTANT + 0.02, f'Sage ({SAGE_CONSTANT})',
                 color=GOLD, fontsize=7, ha='right', fontfamily='monospace')
        ax13.fill_between(satellite_data['N_range'], 0, SAGE_CONSTANT, alpha=0.04, color=RED)
        ax13.set_title('[13] SATELLITE-HYBRID -- Topology Comparison (8,200 km)',
                       color=WHITE, fontsize=10, pad=6)
        ax13.set_xlabel('Number of Ground Repeaters (N)'); ax13.set_ylabel('End-to-End Fidelity')
        ax13.legend(fontsize=7, facecolor=BG, labelcolor=WHITE, framealpha=0.6)
        ax13.grid(alpha=0.12); ax13.set_ylim(0, 1.05)

        # Panel 13b: Route Feasibility
        ax13b = fig.add_subplot(gs[7, 2]); ax13b.set_facecolor(PANEL)
        routes = list(sat_route_data.keys())
        distances = [sat_route_data[r]['distance_km'] for r in routes]
        best_f = [max(sat_route_data[r]['best_fiber_f'],
                      sat_route_data[r]['best_sat_f'],
                      sat_route_data[r]['best_seg4_f'])
                  for r in routes]
        x_pos = np.arange(len(routes))
        bar_cols = [CYAN if f >= SAGE_CONSTANT else RED for f in best_f]
        bars = ax13b.bar(x_pos, best_f, color=bar_cols, alpha=0.8, width=0.6)
        ax13b.axhline(SAGE_CONSTANT, color=GOLD, ls='--', lw=1.5, alpha=0.5)
        ax13b.set_xticks(x_pos)
        ax13b.set_xticklabels([r.split('-')[0][:3] + '-' + r.split('-')[1][:3]
                               for r in routes], fontsize=6, rotation=30)
        for i, (f, d) in enumerate(zip(best_f, distances)):
            label = 'OK' if f >= SAGE_CONSTANT else 'GAP'
            col = CYAN if f >= SAGE_CONSTANT else RED
            ax13b.text(i, f + 0.02, f'{label}\n{d/1000:.0f}Kkm',
                      ha='center', color=col, fontsize=6, fontweight='bold')
        ax13b.set_title('[13b] ROUTE FEASIBILITY',
                       color=WHITE, fontsize=10, pad=6)
        ax13b.set_ylabel('Best Achievable Fidelity')
        ax13b.grid(alpha=0.12); ax13b.set_ylim(0, 1.1)

    out = 'SAGE_v5_ATLAS.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f'\n[SAGE v5.1] Atlas saved -> {out}')
    return out


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print()
    print('=' * 62)
    print('  SAGE FRAMEWORK v5.1 - THE COMPLETE STATE ATLAS (14 PANELS)')
    print('=' * 62)

    print('\n[ 1/10] Transit Engine...')
    transit = run_transit()

    print('[ 2/10] Arms Race (120 gens)...')
    arms = run_arms_race()

    print('[ 3/10] Swarm Collective (120 gens)...')
    swarm = run_swarm()

    print('[ 4/10] Identity Spectrum (100 hops)...')
    spectrum = run_identity_spectrum(100)

    print('[ 5/10] Entanglement Purification...')
    ladders = run_purification_ladders()

    print('[ 6/10] Phase Diagram (40x40 sweep)...')
    phase = run_phase_sweep_fast(resolution=40)

    print('[ 7/10] Mesh Consciousness Network (150 steps)...')
    mesh = run_mesh(n_steps=150)

    print('[ 8/10] Singularity Protocol (4 stages)...')
    singularity = run_all_stages(pop_size=200, generations=100, seed=42)

    print('[ 9/10] Theorem Validation (N=3..30 sweep)...')
    theorem_data = theorem_comparison_data()

    print('[10/10] Satellite-Hybrid Relay Analysis...')
    satellite_data = sat_sweep(L_km=8200)
    sat_route_data = sat_routes()

    # Summary
    hop_fid, errors, cliffs = spectrum
    hw_range, qec_range, grid = phase
    mesh_fids, mesh_online, mesh_quorum, mesh_crises = mesh

    print('\n' + '-' * 55)
    print('SUMMARY REPORT')
    print('-' * 55)
    print(f'  Transit:      Raw={transit[1][-1]:.3f}  Zeno={transit[2][-1]:.3f}  Anchor={transit[3][-1]:.3f}')
    print(f'  Spectrum:     {len(cliffs)}/{len(hop_fid)} tiers cliff below Sage')
    solid = np.sum(grid >= SAGE_CONSTANT) / grid.size * 100
    print(f'  Phase:        {solid:.0f}% of parameter space supports coherent identity')
    qpct = 100 * sum(mesh_quorum) / len(mesh_quorum)
    print(f'  Mesh:         Quorum maintained {qpct:.0f}% | Crises: {len(mesh_crises)}')
    print(f'  Singularity:  Stage 4 survival={singularity[4]["survival"][-1]:.0%}  Sync={singularity[4]["sync"][-1]:.2f}')
    above = sum(1 for f in theorem_data['stoch_fidelities'] if f >= SAGE_CONSTANT)
    print(f'  Theorems:     {above}/{len(theorem_data["N_range"])} configs meet Sage (stochastic)')
    best_sat = max(satellite_data['sat_optimistic'])
    print(f'  Satellite:    Best LEO 2030+: F={best_sat:.4f} (gap={SAGE_CONSTANT-best_sat:.3f} to Sage)')

    print('\n[SAGE v5.1] Rendering 14-panel Atlas...')
    render_atlas_v5(transit, arms, swarm, spectrum, ladders, phase, mesh,
                    singularity, theorem_data, satellite_data, sat_route_data)
    print('[SAGE v5.1] Complete.\n')
