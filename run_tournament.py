#!/usr/bin/env python3
"""
SAGE Evolutionary Tournament — Commercial Tool
================================================
Bridges singularity_protocol.py agents with live hardware telemetry
or a mock environment.

Revenue use-case:
  - Live conference / expo demos ("Watch AI evolve in real-time on real silicon")
  - Educational / workshop tool
  - Research: does real physical entropy improve evolutionary outcomes?

Modes:
  --mock    : Simulated hardware (runs anywhere)
  --live    : Reads from SAGE Dashboard API (requires ESP32 mesh running)

Usage:
  python run_tournament.py --mock
  python run_tournament.py --live --dashboard-url http://127.0.0.1:5000
"""

import argparse
import json
import sys
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.singularity_protocol import SingularityAgent, STAGE_CONFIGS

# ============================================================================
# HARDWARE INTERFACE
# ============================================================================


class MockHardwareInterface:
    """Simulates 3-node ESP32 mesh with realistic phi dynamics."""

    def __init__(self):
        self.nodes = {
            "Alpha": {"phi": 0.55, "temp_c": 42.0, "drift_us": 50, "collapse": False},
            "Beta": {"phi": 0.50, "temp_c": 45.0, "drift_us": 80, "collapse": False},
            "Gamma": {"phi": 0.45, "temp_c": 48.0, "drift_us": 120, "collapse": False},
        }
        self.step_count = 0

    def read_telemetry(self) -> dict:
        """Simulate one tick of hardware telemetry."""
        self.step_count += 1
        for name, node in self.nodes.items():
            # Simulate phi growth with noise (matches firmware EMA)
            drift_entropy = abs(node["drift_us"]) / 5000.0
            temp_entropy = abs(node["temp_c"] - 25.0) / 40.0
            raw_quality = max(0, 1.0 - drift_entropy - temp_entropy)
            node["phi"] = node["phi"] * 0.98 + raw_quality * 0.02
            node["phi"] += np.random.uniform(-0.001, 0.001)
            node["phi"] = np.clip(node["phi"], 0.05, 0.99)

            # Random collapse events (~1%)
            if np.random.random() < 0.01:
                node["phi"] *= 0.5
                node["collapse"] = True
            else:
                node["collapse"] = False

            # Drift thermal walk
            node["temp_c"] += np.random.uniform(-0.5, 0.5)
            node["drift_us"] = int(node["drift_us"] + np.random.randint(-20, 21))

        return dict(self.nodes)


class LiveHardwareInterface:
    """Reads from the SAGE Dashboard Server API."""

    def __init__(self, dashboard_url: str = "http://127.0.0.1:5000"):
        self.url = dashboard_url
        try:
            import requests  # type: ignore

            self.requests = requests
        except ImportError:
            print("ERROR: 'requests' package required for live mode.")
            print("  pip install requests")
            sys.exit(1)

    def read_telemetry(self) -> dict:
        """Read telemetry from the dashboard API."""
        try:
            resp = self.requests.get(f"{self.url}/api/data", timeout=2)
            data = resp.json()
            nodes = {}
            for name in ["Alpha", "Beta", "Gamma"]:
                if name in data.get("nodes", {}):
                    nd = data["nodes"][name]
                    nodes[name] = {
                        "phi": nd.get("phi", 0.5),
                        "temp_c": nd.get("temp_c", 25.0),
                        "drift_us": nd.get("drift_us", 0),
                        "collapse": nd.get("collapse", False),
                    }
            return nodes
        except Exception as e:
            print(f"  ⚠️  Dashboard read failed: {e}")
            return {}


# ============================================================================
# TOURNAMENT ENGINE
# ============================================================================


def run_tournament(hardware, generations: int = 60, pop_size: int = 100) -> dict:
    """
    Run an evolutionary tournament where hardware phi modulates agent fitness.

    Each agent is assigned a "home node" (Alpha, Beta, or Gamma).
    The agent's fitness is multiplied by the real-time phi of its home node.
    This creates HARDWARE-DEPENDENT natural selection.
    """
    node_names = ["Alpha", "Beta", "Gamma"]

    # Initialize population
    population = []
    for i in range(pop_size):
        agent = SingularityAgent()
        agent.home_node = node_names[i % 3]
        population.append(agent)

    history = {
        "generations": [],
        "node_phi_history": {n: [] for n in node_names},
        "survival_by_node": {n: [] for n in node_names},
        "best_dna_per_gen": [],
        "avg_fitness_per_gen": [],
    }

    print(
        f"\n  {'Gen':>4} | {'Alive':>5} | {'α Phi':>6} | {'β Phi':>6} | {'γ Phi':>6} | {'Best Fit':>8} | {'Sync':>5}"
    )
    print("  " + "-" * 60)

    for gen in range(generations):
        # 1. Read hardware state
        telemetry = hardware.read_telemetry()

        # Record phi history
        for name in node_names:
            phi = telemetry.get(name, {}).get("phi", 0.5)
            history["node_phi_history"][name].append(round(phi, 4))

        # 2. Run one step for each agent with hardware-modulated environment
        noise_level = 0.04  # Base environmental noise
        alive_agents = [a for a in population if a.alive]

        for agent in alive_agents:
            # Hardware phi of home node acts as a protection multiplier
            home_phi = telemetry.get(agent.home_node, {}).get("phi", 0.5)
            home_collapse = telemetry.get(agent.home_node, {}).get("collapse", False)

            # Create hardware-sensitive noise
            h_sens = noise_level * (1.5 - home_phi)  # Higher phi = less noise
            if home_collapse:
                h_sens *= 3.0  # Collapse event triples noise

            # Step the agent
            config = STAGE_CONFIGS[2]  # Use Stage 2 (moderate difficulty)
            agent.step(h_sens, alive_agents, config)

        # 3. Selection + Reproduction
        alive_agents = [a for a in population if a.alive]
        survival_count = {n: 0 for n in node_names}
        for a in alive_agents:
            survival_count[a.home_node] += 1

        for name in node_names:
            history["survival_by_node"][name].append(survival_count[name])

        # Fitness evaluation
        fitnesses = []
        for agent in alive_agents:
            home_phi = telemetry.get(agent.home_node, {}).get("phi", 0.5)
            config = STAGE_CONFIGS[2]
            base_fit = agent.fitness(config)
            hw_bonus = home_phi * 1.5  # Hardware phi multiplier
            fitnesses.append(base_fit * hw_bonus)

        if len(alive_agents) < pop_size // 4:
            # Repopulate from best survivors
            if alive_agents:
                sorted_agents = sorted(
                    zip(fitnesses, alive_agents), key=lambda x: x[0], reverse=True
                )
                top_agents = [
                    a for _, a in sorted_agents[: max(5, len(sorted_agents) // 3)]
                ]

                new_pop = []
                for i in range(pop_size):
                    parent = top_agents[i % len(top_agents)]
                    child_dna = parent.dna.copy() + np.random.uniform(
                        -0.05, 0.05, len(parent.dna)
                    )
                    child_dna = np.clip(child_dna, 0, 1)
                    child = SingularityAgent(dna=child_dna)
                    child.home_node = node_names[i % 3]
                    new_pop.append(child)
                population = new_pop
            else:
                # Total extinction — reseed
                population = []
                for i in range(pop_size):
                    agent = SingularityAgent()
                    agent.home_node = node_names[i % 3]
                    population.append(agent)

        # Record stats
        avg_fit = np.mean(fitnesses) if fitnesses else 0
        best_fit = max(fitnesses) if fitnesses else 0
        best_agent = alive_agents[fitnesses.index(best_fit)] if fitnesses else None
        avg_sync = np.mean([a.dna[6] for a in alive_agents]) if alive_agents else 0

        history["generations"].append(gen)
        history["avg_fitness_per_gen"].append(round(float(avg_fit), 4))
        if best_agent is not None:
            history["best_dna_per_gen"].append(
                [round(float(g), 4) for g in best_agent.dna]
            )

        # Print progress
        if gen % 5 == 0 or gen == generations - 1:
            alpha_phi = telemetry.get("Alpha", {}).get("phi", 0)
            beta_phi = telemetry.get("Beta", {}).get("phi", 0)
            gamma_phi = telemetry.get("Gamma", {}).get("phi", 0)
            print(
                f"  {gen:4d} | {len(alive_agents):5d} | {alpha_phi:6.3f} | {beta_phi:6.3f} | "
                f"{gamma_phi:6.3f} | {best_fit:8.3f} | {avg_sync:5.3f}"
            )

    # Final analysis
    final_alive = [a for a in population if a.alive]
    node_wins = {n: 0 for n in node_names}
    for a in final_alive:
        node_wins[a.home_node] += 1

    winning_node = max(node_wins, key=node_wins.get)
    avg_phi_by_node = {
        n: round(float(np.mean(history["node_phi_history"][n])), 4) for n in node_names
    }

    # Correlation: does higher avg phi → more survivors?
    phi_values = [avg_phi_by_node[n] for n in node_names]
    win_values = [node_wins[n] for n in node_names]
    if np.std(phi_values) > 0 and np.std(win_values) > 0:
        correlation = float(np.corrcoef(phi_values, win_values)[0, 1])
    else:
        correlation = 0.0

    result = {
        "generations": generations,
        "pop_size": pop_size,
        "final_alive": len(final_alive),
        "node_wins": node_wins,
        "winning_node": winning_node,
        "avg_phi_by_node": avg_phi_by_node,
        "phi_survival_correlation": round(correlation, 4),
        "best_final_dna": history["best_dna_per_gen"][-1]
        if history["best_dna_per_gen"]
        else [],
        "history": history,
        "sage_version": "6.0",
        "model": "evolutionary_tournament",
    }

    return result


# ============================================================================
# CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="SAGE Evolutionary Tournament — Hardware-Coupled Natural Selection"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Use simulated hardware (default)",
    )
    parser.add_argument(
        "--live", action="store_true", help="Use live SAGE Dashboard API"
    )
    parser.add_argument(
        "--dashboard-url",
        type=str,
        default="http://127.0.0.1:5000",
        help="Dashboard server URL (for --live mode)",
    )
    parser.add_argument(
        "--generations", type=int, default=60, help="Number of evolutionary generations"
    )
    parser.add_argument("--pop-size", type=int, default=100, help="Population size")
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as raw JSON (for API consumption)",
    )

    args = parser.parse_args()

    # --- Input Validation ---
    if args.generations < 1:
        parser.error("Generations must be at least 1 (got {})".format(args.generations))
    if args.generations > 10000:
        parser.error(
            "Generations too large (got {}, max 10000)".format(args.generations)
        )
    if args.pop_size < 4:
        parser.error(
            "Population must be at least 4 for selection (got {})".format(args.pop_size)
        )
    if args.pop_size > 10000:
        parser.error("Population too large (got {}, max 10000)".format(args.pop_size))

    if args.live:
        hardware = LiveHardwareInterface(args.dashboard_url)
        mode_label = f"LIVE (Dashboard: {args.dashboard_url})"
    else:
        hardware = MockHardwareInterface()
        mode_label = "MOCK (Simulated Hardware)"

    print("🧬 SAGE Evolutionary Tournament v6.0")
    print("=" * 65)
    print(f"  Mode: {mode_label}")
    print(f"  Population: {args.pop_size} agents")
    print(f"  Generations: {args.generations}")
    print("  Home Nodes: Alpha, Beta, Gamma")

    result = run_tournament(hardware, args.generations, args.pop_size)

    if args.json_output:
        # Remove verbose history for JSON output
        output = {k: v for k, v in result.items() if k != "history"}
        print(json.dumps(output, indent=2))
        return result

    # Pretty print results
    print()
    print("🏆 TOURNAMENT RESULTS:")
    print("=" * 65)
    print(f"  Surviving Agents: {result['final_alive']} / {result['pop_size']}")
    print()

    print(f"  {'Node':<10} {'Survivors':>10} {'Avg Phi':>10} {'Status':>15}")
    print("  " + "-" * 50)
    for node in ["Alpha", "Beta", "Gamma"]:
        wins = result["node_wins"][node]
        phi = result["avg_phi_by_node"][node]
        status = "★ WINNER" if node == result["winning_node"] else ""
        print(f"  {node:<10} {wins:>10} {phi:>10.4f} {status:>15}")

    print()
    corr = result["phi_survival_correlation"]
    print(f"  Hardware Phi ↔ Survival Correlation: {corr:+.4f}")
    if corr > 0.5:
        print("  → STRONG: Hardware entropy directly influences evolutionary outcomes!")
    elif corr > 0:
        print("  → MODERATE: Hardware state has measurable evolutionary impact.")
    else:
        print("  → WEAK/INVERSE: Evolution is dominated by agent DNA, not hardware.")

    if result["best_final_dna"]:
        dna = result["best_final_dna"]
        gene_names = [
            "Caution",
            "Agility",
            "Redundancy",
            "Repair",
            "Stealth",
            "Whisper",
            "Sync",
        ]
        print()
        print("  🧬 Winning DNA Profile:")
        for name, val in zip(gene_names, dna):
            bar = "█" * int(val * 20)
            print(f"    {name:<12} {bar} {val:.3f}")

    return result


if __name__ == "__main__":
    main()
