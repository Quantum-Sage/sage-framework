import serial
import json
import time
import math
import networkx as nx

# --- SAGE SERIAL BRIDGE CONFIGURATION ---
# UPDATE THESE with your actual COM ports from Device Manager
# UPDATE THESE with your actual COM ports from Device Manager
# Alpha: ESP32 @ COM5, Beta: ESP32 @ COM8, Gamma: ESP32 @ COM9
SAGE_PORTS = {"Alpha": "COM5", "Beta": "COM8", "Gamma": "COM9"}


class SageSerialBridge:
    def __init__(self):
        self.connections = {}
        self.mesh = nx.DiGraph()
        self.live_telemetry = {
            "Alpha": {"temp": 25.0, "drift": 0, "f": 0.99, "p": 12},
            "Beta": {"temp": 25.0, "drift": 0, "f": 0.98, "p": 8},
            "Gamma": {"temp": 25.0, "drift": 0, "f": 0.92, "p": 10},
        }

    def connect_all(self):
        print("\n--- INITIATING SAGE SERIAL SYNC ---")
        for node, port in SAGE_PORTS.items():
            try:
                # 115200 baud is the SAGE standard for ESP32 parity
                self.connections[node] = serial.Serial(port, 115200, timeout=0.1)
                print(f"[+] Link Established: Node {node} on {port}")
            except Exception as e:
                print(f"[-] Node {node} Link Failure ({port}): {e}")

        if not self.connections:
            print(
                "[!] WARNING: No physical nodes detected. Reverting to Simulated Reality Mode."
            )

    def process_telemetry(self, node, raw_json):
        """Parses physical entropy and calculates the SAGE Bound penalty."""
        try:
            data = json.loads(raw_json)

            # Update physical state
            self.live_telemetry[node]["temp"] = data.get("temp_c", 25.0)
            self.live_telemetry[node]["drift"] = data.get("drift_us", 0)

            # Calculate Dynamic Sage Weight (-log(Fidelity))
            # f_penalized = f_base / (1 + 2/p_dynamic)
            alpha = 0.045
            beta = 0.0005

            t_orig = self.live_telemetry[node]["temp"]
            p_orig = self.live_telemetry[node]["p"]
            d_orig = self.live_telemetry[node]["drift"]

            # p_dynamic decreases as heat/drift increases
            p_dynamic = p_orig / (1 + (alpha * (t_orig - 25)) + (beta * d_orig))

            # (1 + 2/p) penalty
            fidelity_penalty = 1 + (2 / max(p_dynamic, 0.001))
            live_fidelity = self.live_telemetry[node]["f"] / fidelity_penalty

            # Log Map for routing
            sage_weight = -math.log(max(live_fidelity, 0.0001))

            return sage_weight, live_fidelity

        except json.JSONDecodeError:
            return None, None

    def run_bridge(self):
        print("\n--- SAGE KERNEL ONLINE ---")
        print("Awaiting physical entropy stream... (Press Ctrl+C to terminate)")

        try:
            while True:
                nodes_updated = []

                for node, ser in self.connections.items():
                    if ser.in_waiting > 0:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line:
                            weight, fidelity = self.process_telemetry(node, line)
                            if weight is not None:
                                nodes_updated.append((node, fidelity))

                # If we have updates, log the 'Master Decision'
                if nodes_updated:
                    # Simple display logic: which node is currently most 'Coherent'?
                    # Note: You could integrate the full Dijkstra routing here
                    print(
                        "\r" + " | ".join([f"{n}: {f:.3f}" for n, f in nodes_updated]),
                        end="",
                        flush=True,
                    )

                time.sleep(0.4)  # 2.5Hz Sampling (much easier to read)
                print(
                    "\r" + " " * 80 + "\r", end="", flush=True
                )  # Clears the current visual line

        except KeyboardInterrupt:
            print("\n\n[!] SAGE Kernel Shutdown. Closing serial arteries...")
            for ser in self.connections.values():
                ser.close()


if __name__ == "__main__":
    bridge = SageSerialBridge()
    bridge.connect_all()
    bridge.run_bridge()
