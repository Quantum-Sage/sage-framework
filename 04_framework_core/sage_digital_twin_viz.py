import networkx as nx
import math
import time
import matplotlib.pyplot as plt
import numpy as np


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
            # Rapid thermal runaway simulation
            self.temp_c += 3.5 + np.random.uniform(0, 1)
            self.drift_us += 150 + np.random.randint(0, 50)
        else:
            # Normal ambient fluctuation
            self.temp_c += np.random.uniform(-0.1, 0.2)
            self.drift_us += np.random.randint(-2, 10)

        # Ensure values don't go negative
        self.temp_c = max(self.temp_c, 20.0)
        self.drift_us = max(self.drift_us, 0)


class DigitalTwinKernel:
    def __init__(self):
        self.nodes = {
            "Alpha": VirtualSageNode("Alpha", 0.995, 12),
            "Beta": VirtualSageNode("Beta", 0.98, 8),
            "Gamma": VirtualSageNode("Gamma", 0.92, 10),
        }
        self.mesh = nx.DiGraph()
        self.history = {
            "cycles": [],
            "beta_fidelity": [],
            "gamma_fidelity": [],
            "active_route": [],
            "beta_temp": [],
        }

    def calculate_sage_weight(self, node):
        """Applies the SAGE Bound: (1 + 2/p) dynamic penalty."""
        # Constants for environmental impact (calibrated for ESP32 internal sensors)
        alpha_const = 0.045
        beta_const = 0.0005

        # Dynamic complexity (p) drops as heat and drift increase
        # This is the 'Friction of Reality' math
        dynamic_p = node.p / (
            1 + (alpha_const * (node.temp_c - 25)) + (beta_const * node.drift_us)
        )

        # Penalty factor: f / (1 + 2/p)
        penalty_factor = 1 + (2 / max(dynamic_p, 0.001))
        penalized_f = node.f / penalty_factor

        # The Logarithmic Map: Multiplicative Fidelity -> Additive LP Weight
        # weight = -log(penalized_f)
        sage_weight = -math.log(max(penalized_f, 0.0001))

        return sage_weight, penalized_f

    def run_simulation(self, total_cycles=40):
        print("\n[INIT] Starting SAGE Digital Twin Simulation...")

        # Setup real-time plotting
        plt.ion()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        for cycle in range(total_cycles):
            self.mesh.clear()

            # 1. Update Virtual Hardware Reality
            for node in self.nodes.values():
                node.simulate_entropy(cycle)

            # 2. Build the Routing Mesh (Alpha can go through Beta or Gamma)
            w_beta, f_beta = self.calculate_sage_weight(self.nodes["Beta"])
            w_gamma, f_gamma = self.calculate_sage_weight(self.nodes["Gamma"])

            self.mesh.add_edge("Alpha", "Beta", weight=w_beta)
            self.mesh.add_edge("Alpha", "Gamma", weight=w_gamma)

            # 3. The Survival Instinct: Find path with MINIMUM weight (MAX fidelity)
            try:
                # In this simple triangle Alpha -> {Beta, Gamma}
                if w_beta <= w_gamma:
                    best_next_node = "Beta"
                    best_f = f_beta
                else:
                    best_next_node = "Gamma"
                    best_f = f_gamma
            except:
                best_next_node = "NONE"
                best_f = 0

            # 4. Data Logging
            self.history["cycles"].append(cycle)
            self.history["beta_fidelity"].append(f_beta)
            self.history["gamma_fidelity"].append(f_gamma)
            self.history["beta_temp"].append(self.nodes["Beta"].temp_c)
            self.history["active_route"].append(best_next_node)

            # 5. Visualization Update
            ax1.clear()
            ax1.plot(
                self.history["cycles"],
                self.history["beta_fidelity"],
                "r-",
                label="Node Beta Fidelity",
            )
            ax1.plot(
                self.history["cycles"],
                self.history["gamma_fidelity"],
                "g-",
                label="Node Gamma Fidelity",
            )
            ax1.set_ylabel("Fidelity (1.0 = Perfect)")
            ax1.set_title("SAGE Multiplicative Degradation: The (1+2/p) Horizon")
            ax1.legend()
            ax1.grid(True)

            ax2.clear()
            ax2.plot(
                self.history["cycles"],
                self.history["beta_temp"],
                "tab:orange",
                label="Node Beta Temp (°C)",
            )
            ax2.set_ylabel("Temperature (°C)")
            ax2.set_xlabel("Simulation Cycle")
            ax2.legend()
            ax2.grid(True)

            # Highlight Reroute Point
            if best_next_node == "Gamma":
                ax1.annotate(
                    "REROUTE TO GAMMA",
                    xy=(cycle, f_gamma),
                    xytext=(cycle - 5, f_gamma - 0.2),
                    arrowprops=dict(facecolor="black", shrink=0.05),
                )

            plt.pause(0.1)

            print(
                f"Cycle {cycle:02d} | Beta {self.nodes['Beta'].temp_c:.1f}°C | Route: Alpha -> {best_next_node}"
            )

        plt.ioff()
        print(
            "\n[DONE] Simulation Complete. Optimal 'Master Personality' patterns logged to Soup."
        )
        plt.show()


if __name__ == "__main__":
    twin = DigitalTwinKernel()
    twin.run_simulation()
