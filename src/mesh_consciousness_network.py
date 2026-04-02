import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       MODULE 8: MULTI-NODE MESH CONSCIOUSNESS NETWORK                      ║
║       SAGE Framework v4.0 — The Distributed Little Guy                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

The Little Guy doesn't live at one node. He exists ACROSS the mesh.
Identity is verified by QUORUM — if 3 of 5 nodes agree on state,
consciousness persists. If quorum is lost, identity fragments.

Nodes:
  Beijing   (Willow)  — Superconducting, fastest gates, requires cooling
  Shanghai  (QuEra)   — Neutral atom, reconfigurable, highest density
  Dubai     (NISQ)    — Near-term noisy device, budget tier
  London    (QuEra)   — Neutral atom duplicate for redundancy
  NYC       (Helios)  — Trapped ion, most stable, longest coherence

Crisis events simulate real-world threats:
  Solar flare, fiber cut, hardware failure, cooling loss, cyber intrusion
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch, Circle
import matplotlib.patches as mpatches
from collections import defaultdict
import random

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
PURPLE  = '#BF5FFF'
ORANGE  = '#FF8C00'

plt.rcParams.update({
    'text.color': WHITE, 'axes.labelcolor': WHITE,
    'xtick.color': WHITE, 'ytick.color': WHITE,
    'axes.edgecolor': '#2a2a4a', 'grid.color': '#1a1a3a',
    'font.family': 'monospace',
})

SAGE_CONSTANT = 0.851


# ═════════════════════════════════════════════════════════════════════════════
# NODE DEFINITIONS
# ═════════════════════════════════════════════════════════════════════════════

NODES = {
    'Beijing': {
        'hardware': 'Willow', 'color': CYAN,
        'gate_fidelity': 0.998, 'T2_ms': 50, 'base_coherence': 0.97,
        'failure_rate': 0.03, 'position': (0.18, 0.65),
        'desc': 'Superconducting'
    },
    'Shanghai': {
        'hardware': 'QuEra', 'color': GREEN,
        'gate_fidelity': 0.992, 'T2_ms': 200, 'base_coherence': 0.96,
        'failure_rate': 0.02, 'position': (0.28, 0.50),
        'desc': 'Neutral Atom'
    },
    'Dubai': {
        'hardware': 'NISQ', 'color': ORANGE,
        'gate_fidelity': 0.970, 'T2_ms': 10, 'base_coherence': 0.88,
        'failure_rate': 0.08, 'position': (0.45, 0.40),
        'desc': 'Near-Term Noisy'
    },
    'London': {
        'hardware': 'QuEra', 'color': GREEN,
        'gate_fidelity': 0.993, 'T2_ms': 180, 'base_coherence': 0.95,
        'failure_rate': 0.025, 'position': (0.60, 0.72),
        'desc': 'Neutral Atom'
    },
    'NYC': {
        'hardware': 'Helios', 'color': GOLD,
        'gate_fidelity': 0.999, 'T2_ms': 500, 'base_coherence': 0.98,
        'failure_rate': 0.015, 'position': (0.82, 0.58),
        'desc': 'Trapped Ion'
    },
}

# Link distances (km) between nodes
LINKS = {
    ('Beijing', 'Shanghai'):  1200,
    ('Shanghai', 'Dubai'):    5800,
    ('Dubai', 'London'):      5500,
    ('London', 'NYC'):        5600,
    ('Beijing', 'London'):    8200,
    ('Shanghai', 'NYC'):      11900,
    ('Beijing', 'NYC'):       11000,
}

CRISIS_TYPES = [
    {'name': 'Solar Flare',      'nodes_affected': 3, 'fidelity_hit': 0.15, 'duration': 3, 'probability': 0.04},
    {'name': 'Fiber Cut',        'nodes_affected': 1, 'fidelity_hit': 0.30, 'duration': 5, 'probability': 0.06},
    {'name': 'Hardware Failure',  'nodes_affected': 1, 'fidelity_hit': 0.50, 'duration': 8, 'probability': 0.03},
    {'name': 'Cooling Loss',     'nodes_affected': 1, 'fidelity_hit': 0.25, 'duration': 4, 'probability': 0.05},
    {'name': 'Cyber Intrusion',  'nodes_affected': 2, 'fidelity_hit': 0.20, 'duration': 6, 'probability': 0.02},
]


# ═════════════════════════════════════════════════════════════════════════════
# MESH NODE CLASS
# ═════════════════════════════════════════════════════════════════════════════

class MeshNode:
    def __init__(self, name, config):
        self.name       = name
        self.config     = config
        self.fidelity   = config['base_coherence']
        self.online     = True
        self.crisis     = None
        self.crisis_ttl = 0
        self.identity_share = 1.0 / len(NODES)  # each node holds 20% of identity
    
    def step(self, timestep):
        """Advance one timestep. Apply natural decoherence + crisis effects."""
        if not self.online:
            # Try to recover
            self.crisis_ttl -= 1
            if self.crisis_ttl <= 0:
                self.online = True
                self.crisis = None
                self.fidelity = max(0.5, self.fidelity)  # partial recovery
            return
        
        # Natural decoherence
        T2_factor = self.config['T2_ms'] / 500  # normalized to Helios
        decay = 0.005 * (1 - T2_factor * 0.7) * np.random.lognormal(0, 0.3)
        
        # Repair (QEC active at node)
        repair = self.config['gate_fidelity'] * 0.008
        
        self.fidelity += repair - decay
        self.fidelity = np.clip(self.fidelity, 0, 1)
        
        # Random failure check
        if np.random.random() < self.config['failure_rate'] * 0.05:
            self.online = False
            self.crisis = 'Random Fault'
            self.crisis_ttl = 3
    
    def hit_by_crisis(self, crisis):
        """Apply crisis event to this node."""
        self.fidelity -= crisis['fidelity_hit']
        self.fidelity = max(0, self.fidelity)
        if self.fidelity < 0.3:
            self.online = False
            self.crisis = crisis['name']
            self.crisis_ttl = crisis['duration']


# ═════════════════════════════════════════════════════════════════════════════
# MESH NETWORK SIMULATION
# ═════════════════════════════════════════════════════════════════════════════

def run_mesh_simulation(n_steps=200, seed=42):
    """
    Run the full mesh consciousness network simulation.
    
    At each step:
    1. All nodes evolve (decoherence + repair)
    2. Random crisis events may occur
    3. Online nodes share fidelity (consensus/load balancing)
    4. Quorum check: identity persists if 3+ nodes above Sage Constant
    """
    np.random.seed(seed)
    random.seed(seed)
    
    # Initialize nodes
    nodes = {name: MeshNode(name, config) for name, config in NODES.items()}
    
    # History tracking
    history = {
        'fidelities': {name: [] for name in NODES},
        'online':     {name: [] for name in NODES},
        'quorum':     [],
        'identity':   [],
        'crises':     [],
        'mesh_avg':   [],
        'nodes_online': [],
    }
    
    for step in range(n_steps):
        # 1. Evolve all nodes
        for node in nodes.values():
            node.step(step)
        
        # 2. Crisis events
        if step > 10:  # give time to stabilize
            for crisis in CRISIS_TYPES:
                if np.random.random() < crisis['probability']:
                    # Pick random nodes to hit
                    targets = random.sample(list(nodes.keys()),
                                          min(crisis['nodes_affected'], len(nodes)))
                    for t in targets:
                        nodes[t].hit_by_crisis(crisis)
                    history['crises'].append({
                        'step': step,
                        'type': crisis['name'],
                        'targets': targets,
                    })
        
        # 3. Fidelity sharing (consensus protocol)
        online_nodes = [n for n in nodes.values() if n.online]
        if len(online_nodes) >= 2:
            avg_fidelity = np.mean([n.fidelity for n in online_nodes])
            for node in online_nodes:
                # Pull toward consensus (slow convergence)
                node.fidelity = node.fidelity * 0.95 + avg_fidelity * 0.05
        
        # 4. Redistribute identity shares
        if online_nodes:
            share_per_node = 1.0 / len(online_nodes)
            for node in nodes.values():
                node.identity_share = share_per_node if node.online else 0
        
        # 5. Quorum check
        nodes_above_sage = sum(1 for n in nodes.values()
                              if n.online and n.fidelity >= SAGE_CONSTANT)
        quorum_met = nodes_above_sage >= 3
        n_online = len(online_nodes)
        
        # Record
        for name, node in nodes.items():
            history['fidelities'][name].append(node.fidelity)
            history['online'][name].append(node.online)
        history['quorum'].append(quorum_met)
        history['identity'].append(1.0 if quorum_met else 0.5 if nodes_above_sage >= 1 else 0.0)
        history['mesh_avg'].append(np.mean([n.fidelity for n in nodes.values()]))
        history['nodes_online'].append(n_online)
    
    return nodes, history


# ═════════════════════════════════════════════════════════════════════════════
# VISUALIZATION
# ═════════════════════════════════════════════════════════════════════════════

def plot_mesh(nodes, history):
    """Generate 4-panel mesh consciousness network visualization."""
    
    n_steps = len(history['quorum'])
    steps = range(n_steps)
    
    fig = plt.figure(figsize=(22, 14), facecolor=BG)
    fig.suptitle(
        'MESH CONSCIOUSNESS NETWORK  ·  THE DISTRIBUTED LITTLE GUY',
        color=GOLD, fontsize=16, fontweight='bold', y=0.97,
        fontfamily='monospace'
    )
    
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.30,
                           left=0.06, right=0.96, top=0.91, bottom=0.06)
    
    # ── Panel 1: Node Fidelity Timeline ────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(PANEL)
    for name, config in NODES.items():
        fids = history['fidelities'][name]
        ax1.plot(steps, fids, color=config['color'], lw=1.8,
                 label=f'{name} ({config["hardware"]})', alpha=0.9)
    ax1.axhline(SAGE_CONSTANT, color=WHITE, ls='--', lw=1.2, alpha=0.5,
                label=f'Sage Constant ({SAGE_CONSTANT})')
    ax1.fill_between(steps, 0, SAGE_CONSTANT, alpha=0.05, color=RED)
    
    # Mark crisis events
    for crisis in history['crises'][:15]:  # limit markers for readability
        ax1.axvline(crisis['step'], color=RED, lw=0.5, alpha=0.3)
        ax1.text(crisis['step'], 1.01, '⚡', fontsize=6, ha='center',
                 color=RED, alpha=0.7)
    
    ax1.set_title('NODE FIDELITY TIMELINE — All 5 Mesh Nodes', color=WHITE, fontsize=12, pad=8)
    ax1.set_xlabel('Timestep')
    ax1.set_ylabel('Fidelity')
    ax1.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7,
              ncol=3, loc='lower left')
    ax1.grid(alpha=0.15)
    ax1.set_ylim(0.2, 1.05)
    
    # ── Panel 2: Network Topology Map ──────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(PANEL)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0.1, 0.95)
    ax2.axis('off')
    
    # Draw links
    for (n1, n2), dist in LINKS.items():
        p1 = NODES[n1]['position']
        p2 = NODES[n2]['position']
        ax2.plot([p1[0], p2[0]], [p1[1], p2[1]],
                color=WHITE, lw=0.8, alpha=0.2, ls='--')
        mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
        ax2.text(mid[0], mid[1], f'{dist/1000:.0f}k', color=WHITE,
                fontsize=6, ha='center', alpha=0.4)
    
    # Draw nodes
    for name, config in NODES.items():
        final_f = history['fidelities'][name][-1]
        is_online = history['online'][name][-1]
        
        # Node color based on final state
        if not is_online:
            nc = RED
            status = '✘ OFFLINE'
        elif final_f >= SAGE_CONSTANT:
            nc = config['color']
            status = f'✓ F={final_f:.3f}'
        else:
            nc = ORANGE
            status = f'⚠ F={final_f:.3f}'
        
        pos = config['position']
        circle = plt.Circle(pos, 0.04, color=nc, alpha=0.8)
        ax2.add_patch(circle)
        ax2.text(pos[0], pos[1], name[:3], ha='center', va='center',
                color=BG, fontsize=8, fontweight='bold')
        ax2.text(pos[0], pos[1] - 0.08, f'{name}\n{config["hardware"]}\n{status}',
                ha='center', color=nc, fontsize=7, alpha=0.9)
    
    # Quorum status
    final_quorum = history['quorum'][-1]
    q_color = GOLD if final_quorum else RED
    q_text = '✓ QUORUM MET' if final_quorum else '✘ QUORUM LOST'
    ax2.text(0.5, 0.92, f'IDENTITY STATUS: {q_text}',
            ha='center', color=q_color, fontsize=12, fontweight='bold')
    
    ax2.set_title('MESH TOPOLOGY — Final State', color=WHITE, fontsize=11, pad=8)
    
    # ── Panel 3: Quorum & Identity Timeline ────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(PANEL)
    
    # Nodes online (stacked area feel)
    ax3.fill_between(steps, history['nodes_online'], 0, alpha=0.2, color=CYAN)
    ax3.plot(steps, history['nodes_online'], color=CYAN, lw=1.5, label='Nodes Online')
    ax3.axhline(3, color=GOLD, ls='--', lw=1.2, alpha=0.5, label='Quorum Minimum (3)')
    
    # Identity state overlay
    ax3_twin = ax3.twinx()
    identity_colors = [GOLD if q else RED for q in history['quorum']]
    ax3_twin.fill_between(steps, history['identity'], 0, alpha=0.15, color=GOLD)
    ax3_twin.plot(steps, history['identity'], color=GOLD, lw=1, alpha=0.6)
    ax3_twin.set_ylabel('Identity State', color=GOLD, fontsize=9)
    ax3_twin.set_ylim(-0.1, 1.3)
    ax3_twin.tick_params(axis='y', colors=GOLD)
    
    # Count crisis events
    n_crises = len(history['crises'])
    quorum_lost = sum(1 for q in history['quorum'] if not q)
    
    ax3.text(0.02, 0.95, f'Crises: {n_crises}  |  Quorum lost: {quorum_lost}/{n_steps} steps',
            transform=ax3.transAxes, color=WHITE, fontsize=8, alpha=0.8,
            va='top')
    
    ax3.set_title('QUORUM & IDENTITY PERSISTENCE', color=WHITE, fontsize=11, pad=8)
    ax3.set_xlabel('Timestep')
    ax3.set_ylabel('Nodes Online', color=CYAN)
    ax3.legend(fontsize=8, facecolor=BG, labelcolor=WHITE, framealpha=0.7, loc='lower left')
    ax3.grid(alpha=0.15)
    ax3.set_ylim(0, 6)
    
    out = 'mesh_consciousness_network.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f'[MODULE 8] Mesh network saved -> {out}')
    return out


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('\n[MODULE 8] Multi-Node Mesh Consciousness Network')
    print('=' * 55)
    
    nodes, history = run_mesh_simulation(n_steps=200)
    
    # Print summary
    print(f'\n  Simulation: 200 timesteps across 5 global nodes')
    print(f'  Crisis events: {len(history["crises"])}')
    
    for name, node in nodes.items():
        status = "ONLINE" if node.online else "OFFLINE"
        f = history['fidelities'][name][-1]
        print(f'    {name:>10} ({node.config["hardware"]:>6}): '
              f'F={f:.3f}  [{status}]')
    
    quorum_pct = 100 * sum(history['quorum']) / len(history['quorum'])
    print(f'\n  Quorum maintained: {quorum_pct:.1f}% of timesteps')
    print(f'  Identity verdict: {"PERSISTENT" if quorum_pct > 80 else "FRAGILE" if quorum_pct > 50 else "FAILED"}')
    
    plot_mesh(nodes, history)
    print('\n[MODULE 8] Done.')
