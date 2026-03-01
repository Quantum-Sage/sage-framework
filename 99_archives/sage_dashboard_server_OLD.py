import serial
import json
import time
import threading
import hashlib
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="dashboard")

# --- SAGE CONFIGURATION ---
SAGE_PORTS = {"Alpha": "COM10", "Beta": "COM5", "Gamma": "COM9"}

# Using a more robust structure for the telemetry state
live_telemetry = {
    "nodes": {
        "Alpha": {
            "temp": 25.0,
            "drift": 0,
            "f": 0.0,
            "phi": 0.0,
            "health": 1.0,
            "p": 12.0,
        },
        "Beta": {
            "temp": 25.0,
            "drift": 0,
            "f": 0.0,
            "phi": 0.0,
            "health": 1.0,
            "p": 8.0,
        },
        "Gamma": {
            "temp": 25.0,
            "drift": 0,
            "f": 0.0,
            "phi": 0.0,
            "health": 1.0,
            "p": 10.0,
        },
    },
    "oracle": {
        "state": "CALIBRATING",
        "coherence": 1.0,
        "shifts": 0,
        "peak": 0.0,
        "seed": "BOOTING...",
        "collapse": False,
        "manifest": "OFFLINE",
    },
}


class SageNeuralKernel:
    """The Physical Telemetry Layer - Neural Link Engine v2.0."""

    def __init__(self):
        self.connections = {}
        self.running = True
        self.history = {"Alpha": [], "Beta": [], "Gamma": []}
        self.last_seed_time = 0.0
        self.load_manifest()

    def load_manifest(self):
        try:
            with open("CONSCIOUSNESS_MANIFEST.json", "r") as f:
                manifest = json.load(f)
                live_telemetry["oracle"]["manifest"] = manifest.get("status", "LOADED")
                print(
                    f"[SYS] Manifest Verified: {live_telemetry['oracle']['manifest']}"
                )
        except Exception:
            print("[!] Warning: CONSCIOUSNESS_MANIFEST.json not found.")

    def connect_all(self):
        print("\n--- INITIATING SAGE SERIAL SYNC (v2.0) ---")
        for node, port in SAGE_PORTS.items():
            try:
                self.connections[node] = serial.Serial(port, 115200, timeout=0.04)
                self.connections[node].dtr = True
                self.connections[node].rts = True
                live_telemetry["nodes"][node]["health"] = 1.0
                print(f"[+] Link Established: Node {node} on {port}")
            except Exception as e:
                live_telemetry["nodes"][node]["health"] = 0.0
                print(f"[-] Node {node} Link Failure ({port}): {e}")

    def process_node(self, node: str, raw_json: str):
        try:
            data = json.loads(raw_json)
            # HARDWARE TRANSPONDER MAPPING (v2.7 Sync)
            t = float(data.get("temp_c", 25.0))
            phi = float(data.get("phi", 0.0))
            d = int(data.get("drift_us", 0))
            fidelity = phi
            node_collapse = bool(data.get("collapse", False))

            # Log sync for debug
            if d != 0:
                print(f"[OK] {node} Sync: {phi:.4f} | {d}us")

            node_health = max(0.0, 1.0 - (abs(d) / 50000.0) - (max(0, t - 65) / 100.0))
            # node_collapse detected above

            node_entry = live_telemetry["nodes"][node]
            node_entry["temp"] = t
            node_entry["drift"] = d
            node_entry["f"] = min(1.0, fidelity)
            node_entry["phi"] = phi
            node_entry["health"] = node_health
            node_entry["collapse"] = node_collapse

            # DIRECT HARDWARE OVERRIDE: If the wire touches ground, the Oracle screams.
            if node_collapse:
                live_telemetry["oracle"]["collapse"] = True
                print(f"[!] ORACLE: Hardware Collapse detected on Node {node}!")

            self.update_oracle(node, fidelity)
        except Exception as e:
            print(f"[-] Node Processing Error: {e}")

    def update_oracle(self, node: str, fidelity: float):
        self.history[node].append(fidelity)
        if len(self.history[node]) > 100:
            self.history[node].pop(0)

        if all(len(h) >= 10 for h in self.history.values()):
            nodes = live_telemetry["nodes"]
            oracle = live_telemetry["oracle"]

            # Use COHERENCE: Measure the gap BETWEEN nodes
            f_vals = [nodes["Alpha"]["f"], nodes["Beta"]["f"], nodes["Gamma"]["f"]]
            deviation = max(f_vals) - min(f_vals)

            # Check for ANY node reporting hardware collapse
            hardware_collapse = any(
                live_telemetry["nodes"][n].get("collapse", False) for n in nodes
            )

            if hardware_collapse:
                oracle["state"] = "COLLAPSE_EVENT"
                oracle["collapse"] = True
                oracle["coherence"] = 0.0  # Force zero coherence during collapse
            else:
                # Normal Resonance Logic
                if deviation > 0.15:
                    oracle["state"] = "DISSONANCE_DETECTED"
                elif deviation < 0.12:
                    oracle["state"] = "CONSCIOUS"
                else:
                    oracle["state"] = "STABLE"
                oracle["collapse"] = False
                oracle["coherence"] = max(0.0, 1.0 - (deviation * 2.0))
            if deviation > float(oracle["peak"]):
                oracle["peak"] = deviation

            # Final safety check for low coherence
            if oracle["coherence"] < 0.2:
                oracle["state"] = "COLLAPSE_EVENT"
                oracle["collapse"] = True
            elif not hardware_collapse:
                oracle["collapse"] = False

            now = time.time()
            if now - self.last_seed_time > 0.8:
                self.last_seed_time = now
                pool = f"{nodes['Alpha']['f']}{nodes['Beta']['f']}{nodes['Gamma']['f']}{now}"
                oracle["seed"] = hashlib.sha256(pool.encode()).hexdigest()[:12].upper()

    def loop(self):
        print("[SYS] High-Speed Telemetry Loop Active.")
        while self.running:
            for node, ser in self.connections.items():
                try:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line.startswith("{"):
                            self.process_node(node, line)
                except Exception:
                    live_telemetry["nodes"][node]["health"] = 0.0
            time.sleep(0.001)


# High-Speed Sync


# --- WEB UI ROUTES ---
@app.route("/")
def index():
    return send_from_directory("dashboard", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("dashboard", path)


@app.route("/data")
def get_data():
    return jsonify(live_telemetry)


def start_kernel():
    kernel = SageNeuralKernel()
    kernel.connect_all()
    kernel.loop()


if __name__ == "__main__":
    t = threading.Thread(target=start_kernel)
    t.daemon = True
    t.start()

    print("\n[+] SAGE Neural Master initializing on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
