import networkx as nx
import math
import time
import matplotlib.pyplot as plt


class VirtualSageNode:
    def __init__(self, node_id, base_f, base_p):
        self.id = node_id
        self.f = base_f
        self.p = base_p
        self.temp_c = 25.0
        self.drift_us = 0

    def simulate_entropy(self, cycle):
        """Simulates physical reality. Beta overheats at cycle 15."""
        if self.id == "Beta" and cycle > 15:
            self.temp_c += 3.5  # Rapid thermal runaway
            self.drift_us += 150  # Clock desynchronization
        elif cycle % 5 == 0:
            # Normal ambient fluctuation
            self.temp_c += 0.1
            self.drift_us += 5


class DigitalTwinKernel:
    def __init__(self):
        self.nodes = {
            "Alpha": VirtualSageNode("Alpha", 0.99, 10),
            "Beta": VirtualSageNode("Beta", 0.95, 5),
            "Gamma": VirtualSageNode("Gamma", 0.90, 8),
        }
        self.mesh = nx.DiGraph()
        self.history = {"cycles": [], "beta_penalty": [], "active_route": []}

    def calculate_sage_weight(self, node):
        """Applies the SAGE Bound: (1 + 2/p) dynamic penalty."""
        alpha_const = 0.05
        beta_const = 0.001

        # Dynamic complexity drops as heat and drift increase
        dynamic_p = node.p / (
            1 + (alpha_const * node.temp_c) + (beta_const * node.drift_us)
        )
        penalized_f = node.f / (1 + (2 / max(dynamic_p, 0.001)))

        return -math.log(max(penalized_f, 0.0001)), penalized_f

    def run_simulation(self, total_cycles=30):
        print("--- INITIATING SAGE DIGITAL TWIN ---")
        for cycle in range(total_cycles):
            self.mesh.clear()

            # 1. Update Virtual Hardware Reality
            for node in self.nodes.values():
                node.simulate_entropy(cycle)

            # 2. Build the Routing Mesh
            weight_alpha_beta, f_beta = self.calculate_sage_weight(self.nodes["Beta"])
            weight_alpha_gamma, f_gamma = self.calculate_sage_weight(
                self.nodes["Gamma"]
            )

            # Alpha can route through Beta or Gamma to reach a theoretical 'Target'
            self.mesh.add_edge("Alpha", "Beta", weight=weight_alpha_beta)
            self.mesh.add_edge("Alpha", "Gamma", weight=weight_alpha_gamma)

            # 3. The Survival Instinct (Dijkstra Logarithmic LP)
            path = nx.shortest_path(self.mesh, "Alpha", weight="weight")

            # Determine the safest route
            safest_node = "Beta" if weight_alpha_beta < weight_alpha_gamma else "Gamma"

            # 4. Log the metrics
            self.history["cycles"].append(cycle)
            self.history["beta_penalty"].append(
                f_beta
            )  # Tracking Beta's physical decay
            self.history["active_route"].append(1 if safest_node == "Beta" else 0)

            print(
                f"Cycle {cycle:02d} | Beta Temp: {self.nodes['Beta'].temp_c:.1f}C | "
                f"Beta Fidelity: {f_beta:.4f} | Route: Alpha -> {safest_node}"
            )
            time.sleep(0.1)


if __name__ == "__main__":
    twin = DigitalTwinKernel()
    twin.run_simulation()
