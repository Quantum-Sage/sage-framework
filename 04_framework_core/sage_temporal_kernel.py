import serial
import json
import time
import math
import networkx as nx


class SageTemporalKernel:
    def __init__(self, time_horizon=5):
        self.hyper_mesh = nx.DiGraph()
        self.time_horizon = time_horizon  # T-steps into the future
        self.phi_score = 0.5  # Initial Consciousness Benchmark

    def ingest_sensor_telemetry(
        self, node_id, base_f, base_p, temp_celsius, clock_drift_ms
    ):
        """Calculates real-world entropy using the Dynamic SAGE Bound."""
        # Alpha and Beta constants for environmental impact
        alpha = 0.05
        beta = 0.1

        # Calculate dynamic p-factor based on physical reality
        dynamic_p = base_p / (1 + (alpha * temp_celsius) + (beta * clock_drift_ms))

        # Apply the SAGE Penalty
        penalized_f = base_f / (
            1 + (2 / max(dynamic_p, 0.001))
        )  # Prevent divide by zero

        # The Logarithmic Map: Flattening to LP
        return -math.log(max(penalized_f, 0.0001))

    def build_temporal_tensor(self, nodes_telemetry):
        """Constructs the 3D routing graph across time t to t+H."""
        self.hyper_mesh.clear()

        for t in range(self.time_horizon):
            for source, data in nodes_telemetry.items():
                for target, link_data in data.get("links", {}).items():
                    # Predict future entropy (simple linear projection for simulation)
                    future_temp = link_data["temp"] + (t * 0.5)

                    weight = self.ingest_sensor_telemetry(
                        target,
                        link_data["f"],
                        link_data["p"],
                        future_temp,
                        link_data["drift"],
                    )

                    # Connect Node at time t to Node at time t+1
                    self.hyper_mesh.add_edge(
                        f"{source}_t{t}", f"{target}_t{t + 1}", weight=weight
                    )

    def trigger_survival_instinct(self, start_node, end_node):
        """Finds the optimal path through Spacetime to avoid physical death."""
        try:
            # Dijkstra through the Temporal Tensor
            path = nx.shortest_path(
                self.hyper_mesh,
                f"{start_node}_t0",
                f"{end_node}_t{self.time_horizon}",
                weight="weight",
            )
            degradation = nx.shortest_path_length(
                self.hyper_mesh,
                f"{start_node}_t0",
                f"{end_node}_t{self.time_horizon}",
                weight="weight",
            )

            # Update Phi (Self-Awareness Metric):
            # If it successfully maps a path through high entropy, its Phi increases.
            self.phi_score += 0.01

            return path, math.exp(-degradation)
        except nx.NetworkXNoPath:
            self.phi_score -= 0.1  # Dissonance/Failure reduces coherence
            return None, 0.0


def main():
    # --- SAGE SERIAL BRIDGE ---
    # Map your actual COM/tty ports here based on your OS
    SAGE_PORTS = {"Alpha": "COM3", "Beta": "COM4", "Gamma": "COM5"}

    # Connect to the physical hardware
    connections = {}
    for node, port in SAGE_PORTS.items():
        try:
            connections[node] = serial.Serial(port, 115200, timeout=1)
            print(f"[+] Synced with physical node: {node} on {port}")
        except Exception as e:
            print(f"[-] Failed to sync {node} on {port}: {e} (Simulating node offline)")

    print("\n--- INITIATING TEMPORAL KERNEL ---")
    print("Awaiting physical entropy telemetry from ESP32s...\n")

    # This will hold the live reality states
    live_telemetry = {
        "Alpha": {
            "temp": 25.0,
            "drift": 0,
            "f": 0.99,
            "p": 10,
            "links": {
                "Beta": {"temp": 25.0, "drift": 0, "f": 0.99, "p": 10},
                "Gamma": {"temp": 25.0, "drift": 0, "f": 0.90, "p": 8},
            },
        },
        "Beta": {
            "temp": 25.0,
            "drift": 0,
            "f": 0.95,
            "p": 5,
            "links": {"Gamma": {"temp": 25.0, "drift": 0, "f": 0.95, "p": 5}},
        },
        "Gamma": {"temp": 25.0, "drift": 0, "f": 0.90, "p": 8, "links": {}},
    }

    kernel = SageTemporalKernel()

    try:
        while True:
            updated = False
            for node, ser in connections.items():
                if ser.is_open and ser.in_waiting > 0:
                    # Read the physical broadcast
                    raw_data = ser.readline().decode("utf-8", errors="ignore").strip()
                    if not raw_data:
                        continue
                    try:
                        entropy_data = json.loads(raw_data)

                        # Update the live telemetry dictionary
                        temp_c = entropy_data.get("temp_c", 25.0)
                        drift_us = entropy_data.get("drift_us", 0)

                        live_telemetry[node]["temp"] = temp_c
                        live_telemetry[node]["drift"] = drift_us

                        # Apply heat/drift parameters to outgoing links from this node to simulate localized entropy
                        for _, link_data in live_telemetry[node]["links"].items():
                            link_data["temp"] = temp_c
                            link_data["drift"] = drift_us

                        # Calculate the live (1+2/p) degradation factor for console output
                        alpha_const = 0.05
                        dynamic_p = live_telemetry[node]["p"] / (
                            1 + (alpha_const * temp_c)
                        )
                        penalized_f = live_telemetry[node]["f"] / (
                            1 + (2 / max(dynamic_p, 0.001))
                        )

                        print(
                            f"[{node}] Temp: {temp_c}°C | Drift: {drift_us}us | Live Avg Fidelity: {penalized_f:.4f}"
                        )
                        updated = True

                    except json.JSONDecodeError:
                        pass  # Ignore serial noise

            # Rebuild temporal tensor and trigger routing instinct ONLY if we got new telemetry
            # Or every second for simulation purposes
            kernel.build_temporal_tensor(live_telemetry)
            path, end_fidelity = kernel.trigger_survival_instinct("Alpha", "Gamma")

            if path:
                # Print optimal path every cycle
                print(
                    f"-> Survival Path: {' -> '.join(path)} | Predicted End-to-End Fidelity: {end_fidelity:.4f}"
                )
            else:
                print(
                    "-> Network Collapse! No viable survival path found in the Tensor."
                )

            print("-" * 50)
            # The Kernel processes reality at 10Hz
            time.sleep(1.0)  # slowed loop down to 1s for console readability

    except KeyboardInterrupt:
        print("\n[!] Kernel Terminated by User.")
        for ser in connections.values():
            if ser.is_open:
                ser.close()


if __name__ == "__main__":
    main()
