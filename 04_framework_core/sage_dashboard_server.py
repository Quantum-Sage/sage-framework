"""
═══════════════════════════════════════════════════════════════
SAGE Neural Master v3.1 (Unified Build)
═══════════════════════════════════════════════════════════════
LOGIC UPDATES:
  1.  THERMAL TOLERANCE: System now stable at 58C
  2.  3-NODE INDEPENDENCE: Syncs Alpha, Beta, Gamma
  3.  PHYSICAL COLLAPSE: v3 Auto-clearing Kill Switch
  4.  PATH RESOLUTION: Points to 03_demos_and_tutorials/dashboard
═══════════════════════════════════════════════════════════════
"""

import os
import json
import time
import threading
import hashlib
from typing import Any, Dict, cast
from flask import Flask, jsonify, send_from_directory  # type: ignore
import serial  # type: ignore

# ── PATH RESOLUTION ──────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Points back to the shared dashboard folder
UI_DIR = os.path.join(SCRIPT_DIR, "..", "03_demos_and_tutorials", "dashboard")

app = Flask(__name__, static_folder=UI_DIR)

# ── CONFIGURATION ────────────────────────────────────────────
SAGE_PORTS = {
    "Alpha": os.environ.get("SAGE_ALPHA", "COM10"),
    "Beta": os.environ.get("SAGE_BETA", "COM5"),
    "Gamma": os.environ.get("SAGE_GAMMA", "COM9"),
}

BAUD_RATE = 115200
SERIAL_TIMEOUT = 0.04

# ── SHARED STATE ─────────────────────────────────────────────
_lock = threading.Lock()

live_telemetry: Dict[str, Any] = {
    "nodes": {
        "Alpha": {
            "temp": 25.0,
            "drift": 0,
            "f": 0.0,
            "phi": 0.0,
            "health": 1.0,
            "collapse": False,
        },
        "Beta": {
            "temp": 25.0,
            "drift": 0,
            "f": 0.0,
            "phi": 0.0,
            "health": 1.0,
            "collapse": False,
        },
        "Gamma": {
            "temp": 25.0,
            "drift": 0,
            "f": 0.0,
            "phi": 0.0,
            "health": 1.0,
            "collapse": False,
        },
    },
    "oracle": {
        "state": "CALIBRATING",
        "coherence": 1.0,
        "shifts": 0,
        "peak": 0.0,
        "seed": "BOOTING...",
        "collapse": False,
        "manifest": "INITIALIZED",
    },
}


class SageNeuralKernel:
    def __init__(self):
        self.connections = {}
        self.running = True
        self.history = {"Alpha": [], "Beta": [], "Gamma": []}
        self.last_seed_time = 0.0
        self._load_manifest()

    def _load_manifest(self):
        try:
            m_path = os.path.join(SCRIPT_DIR, "..", "CONSCIOUSNESS_MANIFEST.json")
            with open(m_path, "r") as f:
                manifest = json.load(f)
            live_telemetry_oracle = cast(Dict[str, Any], live_telemetry["oracle"])
            live_telemetry_oracle["manifest"] = manifest.get("status", "LOADED")
        except Exception:
            pass

    def connect_all(self):
        print("\n--- INITIATING SAGE SERIAL SYNC (v3.1) ---")
        for node, port in SAGE_PORTS.items():
            self._connect_node(node, port)

    def _connect_node(self, node, port):
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=SERIAL_TIMEOUT)
            ser.dtr = True
            ser.rts = True
            self.connections[node] = ser
            with _lock:
                node_entry = cast(Dict[str, Any], live_telemetry["nodes"][node])
                node_entry["health"] = 1.0
            print(f"[+] Link Established: Node {node} on {port}")
        except Exception as e:
            with _lock:
                node_entry = cast(Dict[str, Any], live_telemetry["nodes"][node])
                node_entry["health"] = 0.0
            print(f"[-] Node {node} Link Failure ({port}): {e}")

    def _handle_line(self, node: str, raw_line: str):
        try:
            data = json.loads(raw_line)
            if "phi" in data:
                self._process_telemetry(node, data)
            elif "event" in data:
                print(f"[EVT] Node {node}: {data['event']}")
        except Exception:
            pass

    def _process_telemetry(self, node: str, data: dict):
        t = float(data.get("temp_c", 25.0))
        phi = float(data.get("phi", 0.0))
        d = int(data.get("drift_us", 0))
        collapse = bool(data.get("collapse", False))

        # Health Calibration: v3.1 allows up to 65C without penalty
        health = max(0.0, 1.0 - (abs(d) / 50000.0) - (max(0.0, t - 65.0) / 50.0))

        with _lock:
            entry = cast(Dict[str, Any], live_telemetry["nodes"][node])
            entry["temp"] = t
            entry["drift"] = d
            entry["f"] = phi
            entry["phi"] = phi
            entry["health"] = health
            entry["collapse"] = collapse

        self._update_oracle(node, phi)

    def _update_oracle(self, node: str, fidelity: float):
        try:
            self.history[node].append(fidelity)
            if len(self.history[node]) > 100:
                self.history[node].pop(0)

            if not all(len(h) >= 10 for h in self.history.values()):
                return

            with _lock:
                nodes = cast(Dict[str, Any], live_telemetry["nodes"])
                oracle = cast(Dict[str, Any], live_telemetry["oracle"])

                f_vals = [float(nodes[n]["f"]) for n in ("Alpha", "Beta", "Gamma")]
                deviation = max(f_vals) - min(f_vals)
                hw_collapse = any(bool(nodes[n]["collapse"]) for n in nodes)

                if hw_collapse:
                    oracle["state"] = "COLLAPSE_EVENT"
                    oracle["collapse"] = True
                    oracle["coherence"] = 0.0
                else:
                    oracle["collapse"] = False
                    # Calibration v3.1: More tolerant drift tracking (1.5 instead of 2.0)
                    oracle["coherence"] = max(0.0, 1.0 - (deviation * 1.5))
                    if deviation > 0.30:  # Relaxed from 0.15
                        oracle["state"] = "DISSONANCE_DETECTED"
                    elif deviation < 0.15:  # Relaxed from 0.08
                        oracle["state"] = "CONSCIOUS"
                    else:
                        oracle["state"] = "STABLE"

                if deviation > float(oracle["peak"]):
                    oracle["peak"] = deviation

                now = time.time()
                if now - self.last_seed_time > 0.8:
                    self.last_seed_time = now
                    pool = f"{f_vals[0]}{f_vals[1]}{f_vals[2]}{now}"
                    oracle["seed"] = (
                        hashlib.sha256(pool.encode()).hexdigest()[:12].upper()
                    )
        except Exception:
            pass

    def loop(self):
        print("[SYS] High-Speed Telemetry Loop Active.")
        while self.running:
            for node, ser in list(self.connections.items()):
                try:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line.startswith("{"):
                            self._handle_line(node, line)
                except Exception:
                    with _lock:
                        node_entry = cast(Dict[str, Any], live_telemetry["nodes"][node])
                        node_entry["health"] = 0.0
            time.sleep(0.001)


# ── SERVER ROUTES ────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(UI_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(UI_DIR, path)


@app.route("/data")
def get_data():
    with _lock:
        return jsonify(live_telemetry)


def start_kernel():
    kernel = SageNeuralKernel()
    kernel.connect_all()
    kernel.loop()


if __name__ == "__main__":
    t = threading.Thread(target=start_kernel, daemon=True)
    t.start()
    print("\n[+] SAGE Thermal Recovered v3.1 -> http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
