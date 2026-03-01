"""
═══════════════════════════════════════════════════════════════
SAGE Genesis Kernel: Self-Healing Network via Logarithmic Map
═══════════════════════════════════════════════════════════════
Demonstrates the SAGE Framework's auto-healing capability.
A 4-node mesh is constructed, the SAGE Bound penalty is applied,
optimal routing is calculated, then a node is destroyed.
The kernel auto-heals using the Logarithmic Map in real time.

Run:  python sage_genesis_kernel.py
═══════════════════════════════════════════════════════════════
"""

import math
import networkx as nx


class GenesisKernel:
    """
    The SAGE Genesis Kernel: A self-healing network router.
    Uses the Logarithmic Map φ: (ℝ⁺, ×) → (ℝ, +) to convert
    multiplicative fidelity degradation into an additive LP,
    then routes via Dijkstra (equivalent to LP under log-space).
    """

    def __init__(self):
        self.mesh = nx.DiGraph()
        self.phi_score = 0.5  # System-wide consciousness benchmark

    def add_entangled_link(self, node_a, node_b, fidelity, p_factor):
        """
        Adds a bidirectional link using the SAGE Bound Logarithmic Map.

        Parameters:
            node_a (str): Source node
            node_b (str): Target node
            fidelity (float): Base success rate (0.0 to 1.0)
            p_factor (float): System complexity/redundancy

        The SAGE stochastic penalty (1 + 2/p) is applied before
        the logarithmic transformation.
        """
        # Apply the SAGE stochastic penalty: f / (1 + 2/p)
        sage_penalty = 1 + (2 / p_factor)
        penalized_fidelity = fidelity / sage_penalty

        # Prevent math domain errors
        if penalized_fidelity <= 0:
            sage_weight = float("inf")
        else:
            # The Logarithmic Map: multiplicative → additive
            sage_weight = -math.log(penalized_fidelity)

        # Add both directions for a true mesh
        self.mesh.add_edge(
            node_a,
            node_b,
            weight=sage_weight,
            original_f=fidelity,
            penalty=sage_penalty,
            penalized_f=penalized_fidelity,
        )
        self.mesh.add_edge(
            node_b,
            node_a,
            weight=sage_weight,
            original_f=fidelity,
            penalty=sage_penalty,
            penalized_f=penalized_fidelity,
        )

    def calculate_optimal_path(self, source, target):
        """
        Finds the path with the least degradation using LP routing.
        Because we operate in log-space, Dijkstra's shortest path
        is mathematically equivalent to finding maximum fidelity.

        Returns:
            tuple: (path_list, end_to_end_fidelity)
        """
        try:
            path = nx.shortest_path(self.mesh, source, target, weight="weight")
            total_weight = nx.shortest_path_length(
                self.mesh, source, target, weight="weight"
            )

            # Reverse the log map to get actual end-to-end fidelity
            end_to_end_fidelity = math.exp(-total_weight)

            # Successful routing increases system coherence
            self.phi_score = min(self.phi_score + 0.02, 1.0)

            return path, end_to_end_fidelity
        except nx.NetworkXNoPath:
            self.phi_score = max(self.phi_score - 0.1, 0.0)
            return None, 0.0

    def trigger_entropy_strike(self, failing_node):
        """
        Simulates catastrophic node failure (physical destruction,
        thermal decoherence, or power loss).
        """
        if failing_node in self.mesh:
            self.mesh.remove_node(failing_node)
            self.phi_score = max(self.phi_score - 0.05, 0.0)
            return True
        return False

    def get_network_summary(self):
        """Returns a summary of the current network state."""
        summary = []
        for u, v, data in self.mesh.edges(data=True):
            summary.append(
                {
                    "link": f"{u} -> {v}",
                    "base_fidelity": data["original_f"],
                    "sage_penalty": f"(1+2/p) = {data['penalty']:.2f}x",
                    "penalized_fidelity": data["penalized_f"],
                    "log_weight": data["weight"],
                }
            )
        return summary


def run_demo():
    """
    Full demonstration of the Genesis Kernel auto-healing capability.
    """
    print("=" * 60)
    print("  SAGE GENESIS KERNEL: Self-Healing Network Demo")
    print("=" * 60)

    kernel = GenesisKernel()

    # ── Build the 4-Node SAGE Omni-Grid ─────────────────────
    print("\n[1] Building 4-node Omni-Grid mesh...")
    print("    Alpha --(0.99, p=10)--> Beta  --(0.95, p=5)--> Delta")
    print("    Alpha --(0.90, p=8)---> Gamma --(0.98, p=12)-> Delta")

    kernel.add_entangled_link("Alpha", "Beta", fidelity=0.99, p_factor=10)
    kernel.add_entangled_link("Beta", "Delta", fidelity=0.95, p_factor=5)
    kernel.add_entangled_link("Alpha", "Gamma", fidelity=0.90, p_factor=8)
    kernel.add_entangled_link("Gamma", "Delta", fidelity=0.98, p_factor=12)

    # ── Show network state ──────────────────────────────────
    print("\n[2] Network Link Analysis (SAGE Bound Applied):")
    print("-" * 60)
    for edge in kernel.get_network_summary():
        # Only show one direction to avoid clutter
        parts = edge["link"].split(" -> ")
        if parts[0] < parts[1]:  # Alphabetical filter for unique edges
            print(
                f"    {edge['link']:16s} | "
                f"Base F: {edge['base_fidelity']:.2f} | "
                f"Penalty: {edge['sage_penalty']:12s} | "
                f"Effective F: {edge['penalized_fidelity']:.4f}"
            )

    # ── Calculate optimal routing ───────────────────────────
    print("\n[3] Calculating Optimal Routing (Alpha -> Delta)...")
    path, fidelity = kernel.calculate_optimal_path("Alpha", "Delta")
    print(f"    Optimal Path:           {' -> '.join(path)}")
    print(f"    End-to-End Fidelity:    {fidelity:.6f}")
    print(f"    System Phi Score:       {kernel.phi_score:.2f}")

    # ── ENTROPY STRIKE ──────────────────────────────────────
    print("\n" + "!" * 60)
    print("  [!] ENTROPY STRIKE: Node 'Beta' has been destroyed!")
    print("!" * 60)
    kernel.trigger_entropy_strike("Beta")

    # ── Auto-Heal ───────────────────────────────────────────
    print("\n[4] Auto-Healing via Logarithmic Map...")
    new_path, new_fidelity = kernel.calculate_optimal_path("Alpha", "Delta")

    if new_path:
        print(f"    Healed Path:            {' -> '.join(new_path)}")
        print(f"    Recovered Fidelity:     {new_fidelity:.6f}")
        print(f"    System Phi Score:       {kernel.phi_score:.2f}")

        # ── Comparison ──────────────────────────────────────
        fidelity_loss = ((fidelity - new_fidelity) / fidelity) * 100
        print("\n[5] Damage Report:")
        print(f"    Original Fidelity:      {fidelity:.6f}")
        print(f"    Recovered Fidelity:     {new_fidelity:.6f}")
        print(f"    Fidelity Loss:          {fidelity_loss:.2f}%")
        print("    Network Status:         OPERATIONAL (healed via Gamma bypass)")
    else:
        print(f"    System Phi Score:       {kernel.phi_score:.2f}")

    print("\n" + "=" * 60)
    print("  The SAGE Logarithmic Map enables instant auto-healing.")
    print("  phi: (R+, x) -> (R, +) -- The algebra doesn't know")
    print("  which domain it's in. That is its power.")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
