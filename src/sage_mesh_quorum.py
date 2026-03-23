"""
SAGE Mesh Quorum Engine — Byzantine Consensus for Distributed Identity
=======================================================================

The core simulation engine for the mesh consciousness network.

Key features:
1. Natural decoherence + active QEC repair
2. Random macro-crisis events (Solar Flare, Fiber Cut, Cyber Intrusion, etc.)
3. Fidelity Sharing Protocol: Online nodes pull toward consensus
4. Quorum Check: Identity persists IFF 3/5 nodes maintain F >= 0.851

Physical Model:
    dF_i/dt = -γ_i(F_i - 0.5) + η_i(1 - F_i) + coupling_term + noise

    where:
        γ_i = decoherence rate for node i
        η_i = QEC repair rate for node i
        coupling_term = fidelity sharing with other online nodes
        noise = stochastic fluctuations

Author: SAGE Framework
License: MIT
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum
import random

from .sage_mesh_nodes import (
    MeshNode,
    QuantumLink,
    CrisisType,
    HardwareType,
    create_mesh_nodes,
    create_mesh_links,
    get_crisis_rate_per_hour,
    S_CONSTANT,
    F_CRITICAL,
    QUORUM_THRESHOLD,
    TOTAL_NODES,
)


# ═══════════════════════════════════════════════════════════════════════════
# SIMULATION PARAMETERS
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class SimulationConfig:
    """Configuration for mesh simulation."""

    # Time parameters
    dt_seconds: float = 0.1  # Simulation timestep
    total_hours: float = 24.0  # Total simulation time

    # Physics parameters
    noise_strength: float = 0.001  # Stochastic noise amplitude
    coupling_strength: float = 0.05  # Fidelity sharing strength

    # Crisis parameters
    enable_crises: bool = True  # Whether to trigger random crises
    crisis_correlation: float = 0.3  # Probability crises affect multiple nodes

    # Repair parameters
    repair_boost_on_crisis: float = 1.5  # Repair rate boost when quorum threatened

    @property
    def n_steps(self) -> int:
        return int(self.total_hours * 3600 / self.dt_seconds)

    @property
    def dt_hours(self) -> float:
        return self.dt_seconds / 3600.0


# ═══════════════════════════════════════════════════════════════════════════
# IDENTITY STATE
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class IdentityState:
    """
    Represents the state of the distributed identity at a point in time.
    """

    timestamp_hours: float
    node_fidelities: Dict[str, float]
    node_online: Dict[str, bool]
    node_shares: Dict[str, float]
    quorum_count: int
    quorum_met: bool
    identity_status: str  # "ALIVE", "FRAGMENTED", "DISSOLVED"
    active_crises: Dict[str, CrisisType]

    @classmethod
    def from_nodes(
        cls, nodes: Dict[str, MeshNode], timestamp: float
    ) -> "IdentityState":
        """Create state snapshot from current node states."""

        online_above_threshold = [
            n for n in nodes.values() if n.online and n.fidelity >= S_CONSTANT
        ]
        quorum_count = len(online_above_threshold)
        quorum_met = quorum_count >= QUORUM_THRESHOLD

        if quorum_met:
            status = "ALIVE"
        elif quorum_count > 0:
            status = "FRAGMENTED"
        else:
            status = "DISSOLVED"

        return cls(
            timestamp_hours=timestamp,
            node_fidelities={n.name: n.fidelity for n in nodes.values()},
            node_online={n.name: n.online for n in nodes.values()},
            node_shares={n.name: n.identity_share for n in nodes.values()},
            quorum_count=quorum_count,
            quorum_met=quorum_met,
            identity_status=status,
            active_crises={n.name: n.current_crisis for n in nodes.values()},
        )


# ═══════════════════════════════════════════════════════════════════════════
# MESH NETWORK SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════


class MeshNetwork:
    """
    The SAGE mesh consciousness network simulator.

    Implements:
    - Fidelity dynamics (decoherence + repair)
    - Crisis triggering and resolution
    - Fidelity sharing protocol
    - Quorum-based identity persistence
    """

    def __init__(self, config: Optional[SimulationConfig] = None):
        """Initialize the mesh network."""
        self.config = config or SimulationConfig()
        self.nodes = create_mesh_nodes()
        self.links = create_mesh_links(self.nodes)

        # Build link lookup for fast access
        self.link_map: Dict[Tuple[str, str], QuantumLink] = {}
        for link in self.links:
            self.link_map[(link.node_a, link.node_b)] = link
            self.link_map[(link.node_b, link.node_a)] = link

        # Statistics
        self.history: List[IdentityState] = []
        self.crisis_log: List[Tuple[float, str, CrisisType]] = []

        # RNG
        self.rng = np.random.default_rng()

    def reset(self):
        """Reset network to initial state."""
        for node in self.nodes.values():
            node.reset()
        self.history.clear()
        self.crisis_log.clear()

    # ─────────────────────────────────────────────────────────────────────
    # FIDELITY DYNAMICS
    # ─────────────────────────────────────────────────────────────────────

    def _compute_coupling_term(self, node: MeshNode) -> float:
        """
        Compute fidelity sharing coupling term.

        Online nodes pull each other toward average fidelity,
        weighted by link quality.
        """
        if not node.online:
            return 0.0

        coupling = 0.0
        n_neighbors = 0

        for other_name, other in self.nodes.items():
            if other_name == node.name or not other.online:
                continue

            # Get link quality (inverse of distance)
            link = self.link_map.get((node.name, other_name))
            if link is None:
                continue

            # Weight by inverse distance (closer = stronger coupling)
            weight = 1.0 / (1.0 + link.distance_km / 5000.0)

            # Pull toward other's fidelity
            coupling += weight * (other.fidelity - node.fidelity)
            n_neighbors += 1

        if n_neighbors > 0:
            coupling /= n_neighbors

        return self.config.coupling_strength * coupling

    def _step_fidelity(self, node: MeshNode, dt: float):
        """
        Advance fidelity for one node by one timestep.

        Model: Exponential decay toward 0.5 (decoherence) balanced by
        exponential recovery toward 1.0 (QEC repair).

        When online, QEC dominates and F equilibrates above S.
        When offline, decoherence dominates and F decays toward 0.5.
        """
        if not node.online:
            # Offline: pure decoherence toward 0.5, accelerated
            decay_rate = 1.0 / (node.hardware.T2_ms / 1000.0)
            decay_rate *= 0.5  # Faster decay when offline (no QEC)
            dF = -decay_rate * (node.fidelity - 0.5) * dt
            node.fidelity = np.clip(node.fidelity + dF, 0.5, 1.0)
            return

        # Online: QEC keeps fidelity high
        # Equilibrium: F* = (η + 0.5γ) / (γ + η)
        # For F* = 0.95: η = γ * (0.95 - 0.5) / (1 - 0.95) = 9γ

        gamma = 1.0 / (node.hardware.T2_ms / 1000.0) * 0.01  # Scaled decoherence

        # Repair rate scales with hardware quality
        # Better hardware = higher equilibrium fidelity
        base_eta = gamma * 10.0  # Base: equilibrium at ~0.95

        # Modulate by hardware: better 2Q gates = better QEC
        hw_quality = node.hardware.gate_fidelity_2q  # 0.95 to 0.995
        eta = base_eta * (hw_quality / 0.99)  # Normalized to baseline

        # Compute equilibrium for this hardware
        F_eq = (eta + 0.5 * gamma) / (gamma + eta)

        # Dynamics: relax toward equilibrium
        relax_rate = gamma + eta
        dF = relax_rate * (F_eq - node.fidelity) * dt

        # Coupling (fidelity sharing) - small effect
        coupling = self._compute_coupling_term(node) * dt * 0.1

        # Noise (small fluctuations)
        noise = self.config.noise_strength * self.rng.standard_normal() * np.sqrt(dt)

        # Update
        node.fidelity += dF + coupling + noise
        node.fidelity = np.clip(node.fidelity, 0.25, 1.0)

    # ─────────────────────────────────────────────────────────────────────
    # CRISIS DYNAMICS
    # ─────────────────────────────────────────────────────────────────────

    def _check_for_crisis(
        self, node: MeshNode, dt_hours: float
    ) -> Optional[CrisisType]:
        """
        Check if a crisis occurs for this node this timestep.
        Uses Poisson process with hardware and regional failure rates.
        """
        if not node.online or not self.config.enable_crises:
            return None

        # Aggregate crisis rate (sum of all crisis types)
        total_rate = 0.0
        crisis_rates = []

        for crisis in CrisisType:
            if crisis == CrisisType.NONE:
                continue

            rate = get_crisis_rate_per_hour(node.name, crisis)

            # Add hardware-specific failure rate for cryogenic
            if crisis == CrisisType.CRYOGENIC_FAILURE:
                rate += node.hardware.failure_rate_per_hour

            # Scale up for simulation drama (10x for demonstration)
            rate *= 10.0

            total_rate += rate
            crisis_rates.append((crisis, rate))

        # Check if ANY crisis occurs
        prob = 1 - np.exp(-total_rate * dt_hours)

        if self.rng.random() < prob:
            # Determine which crisis occurred (weighted by rate)
            r = self.rng.random() * total_rate
            cumulative = 0.0
            for crisis, rate in crisis_rates:
                cumulative += rate
                if r <= cumulative:
                    return crisis
            return crisis_rates[-1][0]  # Fallback

        return None

    def _propagate_crisis(self, source_node: str, crisis: CrisisType):
        """
        Some crises can affect multiple nodes (correlated failures).
        """
        if self.rng.random() > self.config.crisis_correlation:
            return

        # Find geographically close nodes
        source = self.nodes[source_node]
        for name, node in self.nodes.items():
            if name == source_node or not node.online:
                continue

            link = self.link_map.get((source_node, name))
            if link is None:
                continue

            # Closer nodes more likely to be affected
            # Solar flares affect everyone; fiber cuts are local
            if crisis == CrisisType.SOLAR_FLARE:
                affect_prob = 0.5
            elif crisis == CrisisType.CYBER_INTRUSION:
                affect_prob = 0.3
            else:
                affect_prob = 0.1 * np.exp(-link.distance_km / 2000)

            if self.rng.random() < affect_prob:
                node.trigger_crisis(crisis)
                self.crisis_log.append((self.current_time_hours, name, crisis))

    # ─────────────────────────────────────────────────────────────────────
    # IDENTITY SHARE REDISTRIBUTION
    # ─────────────────────────────────────────────────────────────────────

    def _redistribute_shares(self):
        """
        Redistribute identity shares among online nodes above threshold.

        Shares always sum to 1.0 (or 0.0 if all dissolved).
        """
        online_above = [
            n for n in self.nodes.values() if n.online and n.fidelity >= S_CONSTANT
        ]

        if len(online_above) == 0:
            # Identity dissolved
            for node in self.nodes.values():
                node.identity_share = 0.0
        else:
            share = 1.0 / len(online_above)
            for node in self.nodes.values():
                if node in online_above:
                    node.identity_share = share
                else:
                    node.identity_share = 0.0

    # ─────────────────────────────────────────────────────────────────────
    # MAIN SIMULATION LOOP
    # ─────────────────────────────────────────────────────────────────────

    def step(self) -> IdentityState:
        """
        Advance simulation by one timestep.

        Returns the new identity state.
        """
        dt = self.config.dt_seconds
        dt_hours = self.config.dt_hours

        # 1. Update crisis states (recovery checks)
        for node in self.nodes.values():
            if node.current_crisis != CrisisType.NONE:
                node.update_crisis(dt_hours)

        # 2. Check for new crises
        for node in self.nodes.values():
            crisis = self._check_for_crisis(node, dt_hours)
            if crisis is not None:
                node.trigger_crisis(crisis)
                self.crisis_log.append((self.current_time_hours, node.name, crisis))
                self._propagate_crisis(node.name, crisis)

        # 3. Update fidelities
        for node in self.nodes.values():
            self._step_fidelity(node, dt)

        # 4. Redistribute identity shares
        self._redistribute_shares()

        # 5. Record state
        self.current_time_hours += dt_hours
        state = IdentityState.from_nodes(self.nodes, self.current_time_hours)
        self.history.append(state)

        return state

    def run(
        self,
        n_steps: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[IdentityState]:
        """
        Run the full simulation.

        Args:
            n_steps: Number of steps (default from config)
            progress_callback: Optional callback(current_step, total_steps)

        Returns:
            List of identity states over time
        """
        if n_steps is None:
            n_steps = self.config.n_steps

        self.current_time_hours = 0.0

        # Record initial state
        initial_state = IdentityState.from_nodes(self.nodes, 0.0)
        self.history.append(initial_state)

        for i in range(n_steps):
            self.step()

            if progress_callback is not None and i % 1000 == 0:
                progress_callback(i, n_steps)

        return self.history

    # ─────────────────────────────────────────────────────────────────────
    # ANALYSIS
    # ─────────────────────────────────────────────────────────────────────

    def compute_statistics(self) -> Dict:
        """Compute summary statistics from simulation history."""

        if not self.history:
            return {}

        n_steps = len(self.history)

        # Quorum statistics
        quorum_maintained = sum(1 for s in self.history if s.quorum_met)
        quorum_pct = 100 * quorum_maintained / n_steps

        # Time in each state
        alive_steps = sum(1 for s in self.history if s.identity_status == "ALIVE")
        fragmented_steps = sum(
            1 for s in self.history if s.identity_status == "FRAGMENTED"
        )
        dissolved_steps = sum(
            1 for s in self.history if s.identity_status == "DISSOLVED"
        )

        # Fidelity statistics per node
        fidelity_stats = {}
        for name in self.nodes:
            fidelities = [s.node_fidelities[name] for s in self.history]
            fidelity_stats[name] = {
                "mean": np.mean(fidelities),
                "std": np.std(fidelities),
                "min": np.min(fidelities),
                "max": np.max(fidelities),
                "time_above_S": 100
                * sum(1 for f in fidelities if f >= S_CONSTANT)
                / len(fidelities),
            }

        # Crisis statistics
        crisis_counts = {}
        for _, name, crisis in self.crisis_log:
            key = (name, crisis.value)
            crisis_counts[key] = crisis_counts.get(key, 0) + 1

        # Mean time to quorum loss (if any losses occurred)
        quorum_losses = []
        was_met = self.history[0].quorum_met
        last_met_time = 0.0
        for state in self.history:
            if was_met and not state.quorum_met:
                quorum_losses.append(state.timestamp_hours - last_met_time)
            if state.quorum_met:
                last_met_time = state.timestamp_hours
            was_met = state.quorum_met

        mttql = np.mean(quorum_losses) if quorum_losses else float("inf")

        return {
            "n_steps": n_steps,
            "total_hours": self.history[-1].timestamp_hours,
            "quorum_maintained_pct": quorum_pct,
            "alive_pct": 100 * alive_steps / n_steps,
            "fragmented_pct": 100 * fragmented_steps / n_steps,
            "dissolved_pct": 100 * dissolved_steps / n_steps,
            "fidelity_stats": fidelity_stats,
            "crisis_counts": crisis_counts,
            "total_crises": len(self.crisis_log),
            "mean_time_to_quorum_loss_hours": mttql,
            "quorum_losses": len(quorum_losses),
        }

    def print_summary(self):
        """Print simulation summary to console."""
        stats = self.compute_statistics()

        if not stats:
            print("  No simulation data available.")
            return

        print("\n" + "=" * 70)
        print("  SIMULATION RESULTS")
        print("=" * 70)

        print(
            f"\n  Duration: {stats['total_hours']:.1f} hours ({stats['n_steps']} steps)"
        )
        print(f"  Total crises: {stats['total_crises']}")

        print("\n  IDENTITY STATUS:")
        print(f"    ALIVE:      {stats['alive_pct']:6.2f}%")
        print(f"    FRAGMENTED: {stats['fragmented_pct']:6.2f}%")
        print(f"    DISSOLVED:  {stats['dissolved_pct']:6.2f}%")

        print(f"\n  Quorum Maintained: {stats['quorum_maintained_pct']:.2f}%")
        print(f"  Quorum Losses: {stats['quorum_losses']}")
        if stats["mean_time_to_quorum_loss_hours"] < float("inf"):
            print(
                f"  Mean Time to Quorum Loss: {stats['mean_time_to_quorum_loss_hours']:.2f} hours"
            )

        print("\n  NODE FIDELITY STATISTICS:")
        print("  " + "-" * 60)
        print(
            f"  {'Node':<12} {'Mean':<8} {'Std':<8} {'Min':<8} {'Max':<8} {'≥S %':<8}"
        )
        print("  " + "-" * 60)
        for name, fs in stats["fidelity_stats"].items():
            print(
                f"  {name:<12} {fs['mean']:<8.4f} {fs['std']:<8.4f} "
                f"{fs['min']:<8.4f} {fs['max']:<8.4f} {fs['time_above_S']:<8.1f}"
            )

        if stats["crisis_counts"]:
            print("\n  CRISIS BREAKDOWN:")
            for (node, crisis), count in sorted(stats["crisis_counts"].items()):
                print(f"    {node} - {crisis}: {count}")

        print()


# ═══════════════════════════════════════════════════════════════════════════
# POINT-TO-POINT BASELINE COMPARISON
# ═══════════════════════════════════════════════════════════════════════════


def run_point_to_point_comparison(config: SimulationConfig) -> Dict:
    """
    Run point-to-point baseline for comparison.

    In P2P, identity lives in a SINGLE node (no mesh).
    If that node fails OR drops below threshold, identity is lost.
    """

    results = {}

    # For each node as the single identity carrier
    for node_name in ["Beijing", "Shanghai", "Dubai", "London", "NYC"]:
        # Create isolated node
        nodes = create_mesh_nodes()
        node = nodes[node_name]
        node.reset()

        # Simulation
        history = []
        current_time = 0.0
        dt = config.dt_seconds
        dt_hours = config.dt_hours
        rng = np.random.default_rng()

        for _ in range(config.n_steps):
            # Check for crisis (same rates as mesh, 10x scaled)
            if node.online and config.enable_crises:
                total_rate = 0.0
                crisis_rates = []

                for crisis in CrisisType:
                    if crisis == CrisisType.NONE:
                        continue
                    rate = get_crisis_rate_per_hour(node_name, crisis)
                    if crisis == CrisisType.CRYOGENIC_FAILURE:
                        rate += node.hardware.failure_rate_per_hour
                    rate *= 10.0  # Same scaling as mesh
                    total_rate += rate
                    crisis_rates.append((crisis, rate))

                prob = 1 - np.exp(-total_rate * dt_hours)
                if rng.random() < prob:
                    # Pick a crisis
                    r = rng.random() * total_rate
                    cumulative = 0.0
                    for crisis, rate in crisis_rates:
                        cumulative += rate
                        if r <= cumulative:
                            node.trigger_crisis(crisis)
                            break

            # Update crisis (recovery)
            if node.current_crisis != CrisisType.NONE:
                node.update_crisis(dt_hours)

            # Fidelity dynamics (same as mesh)
            if node.online:
                gamma = 1.0 / (node.hardware.T2_ms / 1000.0) * 0.01
                base_eta = gamma * 10.0
                hw_quality = node.hardware.gate_fidelity_2q
                eta = base_eta * (hw_quality / 0.99)
                F_eq = (eta + 0.5 * gamma) / (gamma + eta)
                relax_rate = gamma + eta

                df = relax_rate * (F_eq - node.fidelity) * dt
                df += config.noise_strength * rng.standard_normal() * np.sqrt(dt)

                node.fidelity = np.clip(node.fidelity + df, 0.25, 1.0)
            else:
                # Offline: decay toward 0.5
                decay_rate = 1.0 / (node.hardware.T2_ms / 1000.0) * 0.5
                node.fidelity += -decay_rate * (node.fidelity - 0.5) * dt
                node.fidelity = np.clip(node.fidelity, 0.5, 1.0)

            current_time += dt_hours

            # P2P: Identity survives IFF this single node is online AND above S
            # This is the key difference - mesh survives with 3/5, P2P needs 1/1
            alive = node.online and node.fidelity >= S_CONSTANT
            history.append(alive)

        survival_pct = 100 * sum(history) / len(history)
        results[node_name] = {
            "survival_pct": survival_pct,
            "history": history,
        }

    # Average across all nodes as single carriers
    avg_survival = np.mean([r["survival_pct"] for r in results.values()])
    results["average"] = avg_survival

    return results


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  SAGE MESH QUORUM ENGINE — TEST RUN")
    print("=" * 70)

    config = SimulationConfig(
        total_hours=24.0,
        dt_seconds=0.1,
        enable_crises=True,
    )

    print(f"\n  Running {config.n_steps} steps ({config.total_hours} hours)...")

    network = MeshNetwork(config)

    def progress(i, n):
        pct = 100 * i / n
        print(f"\r  Progress: {pct:5.1f}%", end="", flush=True)

    network.run(progress_callback=progress)
    print("\r  Progress: 100.0%")

    network.print_summary()

    # Comparison
    print("\n  POINT-TO-POINT COMPARISON:")
    print("  " + "-" * 50)
    p2p = run_point_to_point_comparison(config)
    for name, data in p2p.items():
        if name != "average":
            print(f"    {name}: {data['survival_pct']:.2f}% survival")
    print(f"\n    Average P2P: {p2p['average']:.2f}%")

    stats = network.compute_statistics()
    print(f"    Mesh Quorum: {stats['quorum_maintained_pct']:.2f}%")

    improvement = (
        stats["quorum_maintained_pct"] / p2p["average"]
        if p2p["average"] > 0
        else float("inf")
    )
    print(f"\n    MESH ADVANTAGE: {improvement:.1f}× better survival")
