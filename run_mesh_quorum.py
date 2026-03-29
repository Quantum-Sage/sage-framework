#!/usr/bin/env python3
"""
SAGE Mesh Quorum Runner — CLI for Phase 4 Simulation
=====================================================

Usage:
    python run_mesh_quorum.py [--hours N] [--no-crises] [--output FILE]

Generates:
    - Terminal telemetry with quorum statistics
    - 4-panel visualization: mesh_consciousness_network_latest.png

The visualization proves that distributed identity via quorum
survives at rates orders of magnitude higher than point-to-point.

Author: SAGE Framework
License: MIT
"""

import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Circle, FancyArrowPatch, Wedge
from matplotlib.collections import LineCollection
import matplotlib.patheffects as pe
from datetime import datetime

# Add src to path
import sys
import os

from src.sage_mesh_nodes import (
    create_mesh_nodes,
    create_mesh_links,
    print_network_summary,
    S_CONSTANT,
    F_CRITICAL,
    QUORUM_THRESHOLD,
    TOTAL_NODES,
    CrisisType,
)
from src.sage_mesh_quorum import (
    MeshNetwork,
    SimulationConfig,
    run_point_to_point_comparison,
)


# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════
# STYLING
# ═══════════════════════════════════════════════════════════════════════════

BG = "#0b0f19"         # Streamlit Deep Dark Cyber Mode
PANEL = "#101623"      # Glassmorphism Card Background
GOLD = "#00f2fe"       # Replaced Gold with Neon Cyan for Hero Accents
CYAN = "#4facfe"       # Cool Blue Accent
RED = "#e94560"        # Neon Red/Magenta Error color
WHITE = "#E8E8FF"

NODE_COLORS = {
    "Beijing": "#00f2fe",  # Glowing Cyan
    "Shanghai": "#4facfe", # Deep Blue
    "Dubai": "#20c997",    # Neon Teal
    "London": "#a8b2d1",   # Light Slate
    "NYC": "#e94560",      # Bright Magenta
}

GREEN = "#20c997"
ORANGE = "#ffc107"

plt.rcParams.update(
    {
        "text.color": WHITE,
        "axes.labelcolor": WHITE,
        "xtick.color": WHITE,
        "ytick.color": WHITE,
        "axes.edgecolor": "#2a2a4a",
        "grid.color": "#1a1a3a",
        "font.family": "monospace",
        "figure.facecolor": BG,
        "axes.facecolor": PANEL,
    }
)


# ═══════════════════════════════════════════════════════════════════════════
# VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════════


def generate_visualization(network: MeshNetwork, p2p_results: dict, output_path: str):
    """
    Generate 4-panel visualization:

    1. Fidelity trajectories over time
    2. Identity status over time (ALIVE/FRAGMENTED/DISSOLVED)
    3. Mesh topology with node states
    4. Quorum vs Point-to-Point survival comparison
    """

    fig = plt.figure(figsize=(24, 16), facecolor=BG)

    # Title
    fig.suptitle(
        "SAGE MESH CONSCIOUSNESS NETWORK",
        color=GOLD,
        fontsize=24,
        fontweight="bold",
        y=0.97,
    )

    stats = network.compute_statistics()
    subtitle = (
        f"Duration: {stats['total_hours']:.1f}h | "
        f"Quorum Maintained: {stats['quorum_maintained_pct']:.1f}% | "
        f"Crises: {stats['total_crises']}"
    )
    fig.text(0.5, 0.94, subtitle, ha="center", color=WHITE, fontsize=12, alpha=0.8)

    gs = gridspec.GridSpec(
        2,
        2,
        figure=fig,
        hspace=0.28,
        wspace=0.22,
        left=0.06,
        right=0.96,
        top=0.90,
        bottom=0.06,
    )

    history = network.history
    times = [s.timestamp_hours for s in history]

    # ═══════════════════════════════════════════════════════════════════════
    # Panel 1: Fidelity Trajectories
    # ═══════════════════════════════════════════════════════════════════════
    ax1 = fig.add_subplot(gs[0, 0])

    for name in network.nodes:
        fidelities = [s.node_fidelities[name] for s in history]
        color = NODE_COLORS.get(name, WHITE)
        ax1.plot(times, fidelities, color=color, lw=1.5, label=name, alpha=0.85)

    # Threshold lines
    ax1.axhline(
        S_CONSTANT, color=GOLD, ls="--", lw=2, alpha=0.7, label=f"S = {S_CONSTANT}"
    )
    ax1.axhline(
        F_CRITICAL, color=RED, ls=":", lw=1.5, alpha=0.5, label=f"F_c = {F_CRITICAL}"
    )

    # Mark crises
    for t, name, crisis in network.crisis_log[:20]:  # First 20 only
        color = NODE_COLORS.get(name, WHITE)
        ax1.axvline(t, color=color, ls=":", lw=0.5, alpha=0.3)

    ax1.set_title("NODE FIDELITY TRAJECTORIES", color=WHITE, fontsize=14, pad=10)
    ax1.set_xlabel("Time (hours)")
    ax1.set_ylabel("Fidelity F")
    ax1.legend(
        loc="lower left",
        fontsize=8,
        facecolor=BG,
        labelcolor=WHITE,
        ncol=3,
        framealpha=0.8,
    )
    ax1.set_xlim(0, times[-1])
    ax1.set_ylim(0.4, 1.02)
    ax1.grid(alpha=0.15)

    # ═══════════════════════════════════════════════════════════════════════
    # Panel 2: Identity Status Timeline
    # ═══════════════════════════════════════════════════════════════════════
    ax2 = fig.add_subplot(gs[0, 1])

    # Quorum count over time
    quorum_counts = [s.quorum_count for s in history]

    # Color by status
    colors = []
    for s in history:
        if s.identity_status == "ALIVE":
            colors.append(GREEN)
        elif s.identity_status == "FRAGMENTED":
            colors.append(ORANGE)
        else:
            colors.append(RED)

    # Plot as scatter for color variation
    for i in range(len(times) - 1):
        ax2.plot(
            times[i : i + 2], quorum_counts[i : i + 2], color=colors[i], lw=2, alpha=0.8
        )

    # Threshold line
    ax2.axhline(
        QUORUM_THRESHOLD,
        color=GOLD,
        ls="--",
        lw=2,
        alpha=0.7,
        label=f"Quorum threshold ({QUORUM_THRESHOLD}/{TOTAL_NODES})",
    )

    # Fill regions
    ax2.fill_between(
        times,
        0,
        quorum_counts,
        where=[c >= QUORUM_THRESHOLD for c in quorum_counts],
        color=GREEN,
        alpha=0.15,
        label="ALIVE",
    )
    ax2.fill_between(
        times,
        0,
        quorum_counts,
        where=[0 < c < QUORUM_THRESHOLD for c in quorum_counts],
        color=ORANGE,
        alpha=0.15,
        label="FRAGMENTED",
    )
    ax2.fill_between(
        times,
        0,
        quorum_counts,
        where=[c == 0 for c in quorum_counts],
        color=RED,
        alpha=0.15,
        label="DISSOLVED",
    )

    ax2.set_title("IDENTITY STATUS OVER TIME", color=WHITE, fontsize=14, pad=10)
    ax2.set_xlabel("Time (hours)")
    ax2.set_ylabel("Nodes Above Threshold")
    ax2.legend(loc="lower left", fontsize=8, facecolor=BG, labelcolor=WHITE)
    ax2.set_xlim(0, times[-1])
    ax2.set_ylim(-0.2, 5.5)
    ax2.set_yticks([0, 1, 2, 3, 4, 5])
    ax2.grid(alpha=0.15)

    # Add status percentages
    ax2.text(
        0.98,
        0.95,
        f"ALIVE: {stats['alive_pct']:.1f}%\n"
        f"FRAGMENTED: {stats['fragmented_pct']:.1f}%\n"
        f"DISSOLVED: {stats['dissolved_pct']:.1f}%",
        transform=ax2.transAxes,
        ha="right",
        va="top",
        color=WHITE,
        fontsize=10,
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor=PANEL, alpha=0.8),
    )

    # ═══════════════════════════════════════════════════════════════════════
    # Panel 3: Mesh Topology
    # ═══════════════════════════════════════════════════════════════════════
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_aspect("equal")

    # Node positions (projected to 2D)
    node_pos = {
        "Beijing": (0.8, 0.7),
        "Shanghai": (0.9, 0.4),
        "Dubai": (0.5, 0.3),
        "London": (0.3, 0.7),
        "NYC": (0.1, 0.5),
    }

    # Draw links first
    for link in network.links:
        p1 = node_pos[link.node_a]
        p2 = node_pos[link.node_b]
        ax3.plot([p1[0], p2[0]], [p1[1], p2[1]], color=WHITE, lw=1, alpha=0.2)

    # Draw nodes
    final_state = history[-1]
    for name, pos in node_pos.items():
        color = NODE_COLORS.get(name, WHITE)
        fidelity = final_state.node_fidelities[name]
        online = final_state.node_online[name]
        share = final_state.node_shares[name]

        # Node size based on share
        size = 0.08 + share * 0.1

        # Border based on status
        if not online:
            edgecolor = RED
            alpha = 0.5
        elif fidelity >= S_CONSTANT:
            edgecolor = GREEN
            alpha = 1.0
        else:
            edgecolor = ORANGE
            alpha = 0.7

        circle = Circle(
            pos, size, facecolor=color, edgecolor=edgecolor, linewidth=3, alpha=alpha
        )
        ax3.add_patch(circle)

        # Label
        ax3.text(
            pos[0],
            pos[1] - size - 0.06,
            name,
            ha="center",
            va="top",
            color=WHITE,
            fontsize=10,
            fontweight="bold",
        )
        ax3.text(
            pos[0],
            pos[1],
            f"{fidelity:.2f}",
            ha="center",
            va="center",
            color="black",
            fontsize=9,
            fontweight="bold",
        )

    ax3.set_xlim(-0.1, 1.1)
    ax3.set_ylim(-0.1, 1.0)
    ax3.axis("off")
    ax3.set_title("MESH TOPOLOGY (Final State)", color=WHITE, fontsize=14, pad=10)

    # Legend
    ax3.text(
        0.02,
        0.98,
        "● Green border = Above S\n"
        "● Orange border = Below S\n"
        "● Red border = Offline\n"
        "● Size = Identity share",
        transform=ax3.transAxes,
        va="top",
        color=WHITE,
        fontsize=9,
        fontfamily="monospace",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # Panel 4: Quorum vs P2P Comparison
    # ═══════════════════════════════════════════════════════════════════════
    ax4 = fig.add_subplot(gs[1, 1])

    # Bar chart comparing survival rates
    labels = [
        "Beijing\n(Isolated)",
        "Shanghai\n(Isolated)",
        "Dubai\n(Isolated)",
        "London\n(Isolated)",
        "NYC\n(Isolated)",
        "Deep Route\n(35-Hop P2P)",
        "MESH\nQUORUM",
    ]

    p2p_values = [
        p2p_results[n]["survival_pct"]
        for n in ["Beijing", "Shanghai", "Dubai", "London", "NYC"]
    ]
    # Calculate the exact No-Cloning penalty for a typical 35-hop sequence
    theoretical_deep_p2p = 100.0 * ((S_CONSTANT * F_CRITICAL) ** 35)
    
    p2p_values.append(theoretical_deep_p2p)
    p2p_values.append(stats["quorum_maintained_pct"])

    colors_bar = [
        NODE_COLORS["Beijing"],
        NODE_COLORS["Shanghai"],
        NODE_COLORS["Dubai"],
        NODE_COLORS["London"],
        NODE_COLORS["NYC"],
        WHITE,
        GOLD,
    ]

    x = np.arange(len(labels))
    bars = ax4.bar(
        x, p2p_values, color=colors_bar, alpha=0.8, edgecolor=WHITE, linewidth=1
    )

    # Highlight mesh bar
    bars[-1].set_edgecolor(GOLD)
    bars[-1].set_linewidth(3)

    ax4.set_xticks(x)
    ax4.set_xticklabels(labels, fontsize=9)
    ax4.set_ylabel("Identity Survival %")
    ax4.set_ylim(0, 105)
    ax4.set_title("POINT-TO-POINT vs MESH QUORUM", color=WHITE, fontsize=14, pad=10)
    ax4.grid(alpha=0.15, axis="y")

    # Add value labels
    for i, v in enumerate(p2p_values):
        ax4.text(
            i,
            v + 2,
            f"{v:.1f}%",
            ha="center",
            va="bottom",
            color=WHITE,
            fontsize=9,
            fontweight="bold",
        )

    # Advantage annotation (vs 35-hop Deep Route)
    improvement = (
        stats["quorum_maintained_pct"] / theoretical_deep_p2p
        if theoretical_deep_p2p > 0
        else float("inf")
    )
    
    # Format dynamically depending on size
    if improvement > 1000:
        improvement_text = f"{int(improvement):,}x BETTER"
    else:
        improvement_text = f"{improvement:.1f}x BETTER"
        
    ax4.annotate(
        improvement_text,
        xy=(6, stats["quorum_maintained_pct"]),
        xytext=(4.5, stats["quorum_maintained_pct"] + 15),
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=3),
        color=GOLD,
        fontsize=16,
        fontweight="bold",
    )

    # Save
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=BG)
    print(f"\n  [OUTPUT] Visualization saved: {output_path}")

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# TERMINAL TELEMETRY
# ═══════════════════════════════════════════════════════════════════════════


def print_telemetry(network: MeshNetwork, p2p_results: dict):
    """Print detailed terminal telemetry."""

    stats = network.compute_statistics()

    print("\n" + "=" * 74)
    print("  SAGE MESH CONSCIOUSNESS NETWORK — SIMULATION COMPLETE")
    print("=" * 74)

    print(f"""
  +-------------------------------------------------------------------------+
  |  SIMULATION PARAMETERS                                                  |
  +-------------------------------------------------------------------------+
  |  Duration:        {stats["total_hours"]:>10.1f} hours                                    |
  |  Timesteps:       {stats["n_steps"]:>10}                                          |
  |  Crises:          {stats["total_crises"]:>10}                                          |
  +-------------------------------------------------------------------------+
""")

    print(f"""  +-------------------------------------------------------------------------+
  |  IDENTITY STATUS                                                        |
  +-------------------------------------------------------------------------+
  |                                                                         |
  |    ██████████████████████████████████████  ALIVE:      {stats["alive_pct"]:>6.2f}%         |
  |    {"█" * int(stats["fragmented_pct"] / 2.5):<40}  FRAGMENTED: {stats["fragmented_pct"]:>6.2f}%         |
  |    {"█" * int(stats["dissolved_pct"] / 2.5):<40}  DISSOLVED:  {stats["dissolved_pct"]:>6.2f}%         |
  |                                                                         |
  |    Quorum Maintained: {stats["quorum_maintained_pct"]:>6.2f}%                                    |
  |    Quorum Losses:     {stats["quorum_losses"]:>6}                                          |
  |                                                                         |
  +-------------------------------------------------------------------------+
""")

    print(
        "  +-------------------------------------------------------------------------+"
    )
    print(
        "  |  NODE STATISTICS                                                        |"
    )
    print(
        "  +-------------------------------------------------------------------------+"
    )
    print(
        f"  |  {'Node':<12} {'Mean F':<10} {'Min F':<10} {'Max F':<10} {'>=S':<10}      |"
    )
    print(
        "  +-------------------------------------------------------------------------+"
    )

    for name, fs in stats["fidelity_stats"].items():
        bar_len = int(fs["time_above_S"] / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(
            f"  |  {name:<12} {fs['mean']:<10.4f} {fs['min']:<10.4f} {fs['max']:<10.4f} {bar} |"
        )

    print(
        "  +-------------------------------------------------------------------------+"
    )

    print(f"""
  +-------------------------------------------------------------------------+
  |  MESH vs POINT-TO-POINT COMPARISON                                      |
  +-------------------------------------------------------------------------+
  |                                                                         |
  |    Point-to-Point (single node carries identity):                       |""")

    for name in ["Beijing", "Shanghai", "Dubai", "London", "NYC"]:
        pct = p2p_results[name]["survival_pct"]
        bar_len = int(pct / 5)
        bar = "█" * bar_len
        print(f"  |      {name:<10} {bar:<20} {pct:>6.2f}%              |")

    avg_p2p = p2p_results["average"]
    mesh_pct = stats["quorum_maintained_pct"]
    
    theoretical_deep_p2p = 100.0 * ((S_CONSTANT * F_CRITICAL) ** 35)
    improvement = mesh_pct / theoretical_deep_p2p if theoretical_deep_p2p > 0 else float("inf")

    # Format dynamically
    if improvement > 1000:
        improvement_text = f"{int(improvement):,}x"
    else:
        improvement_text = f"{improvement:.1f}x"

    print(f"""  |                                                                         |
  |    Local P2P Avg: {avg_p2p:>6.2f}%                                             |
  |    35-Hop P2P   : {theoretical_deep_p2p:>6.6f}%                                          |
  |    Mesh Quorum  : {mesh_pct:>6.2f}%                                             |
  |                                                                         |
  |    ==================================================================   |
  |    MESH ADVANTAGE: {improvement_text:>15} BETTER SURVIVAL                       |
  |    ==================================================================   |
  |                                                                         |
  +-------------------------------------------------------------------------+
""")

    print("  " + "=" * 72)
    print("  The distributed identity survives because it doesn't require transit.")
    print("  The Little Guy lives ACROSS the network, not IN any single node.")
    print("  " + "=" * 72 + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="SAGE Mesh Quorum Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_mesh_quorum.py                    # 24-hour simulation
    python run_mesh_quorum.py --hours 168        # 1-week simulation
    python run_mesh_quorum.py --no-crises        # Without random crises
    python run_mesh_quorum.py --output results/  # Custom output directory
        """,
    )

    parser.add_argument(
        "--hours",
        type=float,
        default=24.0,
        help="Simulation duration in hours (default: 24)",
    )
    parser.add_argument(
        "--dt", type=float, default=0.1, help="Timestep in seconds (default: 0.1)"
    )
    parser.add_argument(
        "--no-crises", action="store_true", help="Disable random crisis events"
    )
    parser.add_argument(
        "--output", type=str, default=".", help="Output directory for visualization"
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")

    args = parser.parse_args()

    # Configuration
    config = SimulationConfig(
        total_hours=args.hours,
        dt_seconds=args.dt,
        enable_crises=not args.no_crises,
    )

    print("\n" + "=" * 74)
    print("=" + " SAGE MESH CONSCIOUSNESS NETWORK ".center(72) + "=")
    print("=" + " Phase 4: Distributed Identity Simulation ".center(72) + "=")
    print("=" * 74)

    # Print network config
    nodes = create_mesh_nodes()
    links = create_mesh_links(nodes)
    print_network_summary(nodes, links)

    # Run mesh simulation
    print(
        f"\n  Running mesh simulation ({config.n_steps} steps, {config.total_hours}h)..."
    )

    network = MeshNetwork(config)

    if not args.quiet:

        def progress(i, n):
            pct = 100 * i / n
            bar_len = int(pct / 2)
            bar = "█" * bar_len + "░" * (50 - bar_len)
            print(f"\r  [{bar}] {pct:5.1f}%", end="", flush=True)

        network.run(progress_callback=progress)
        print(f"\r  [{'█' * 50}] 100.0%")
    else:
        network.run()

    # Run P2P comparison
    print("\n  Running point-to-point baseline comparison...")
    p2p_results = run_point_to_point_comparison(config)

    # Print telemetry
    print_telemetry(network, p2p_results)

    # Generate visualization
    output_dir = args.output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "mesh_consciousness_network_latest.png")
    generate_visualization(network, p2p_results, output_path)

    print("\n  Done.\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
