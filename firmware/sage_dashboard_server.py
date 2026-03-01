"""
═══════════════════════════════════════════════════════════════
SAGE Dashboard Server v3.0 (Unified Build)
═══════════════════════════════════════════════════════════════
Fixes from v2:
  1. Handles BOTH telemetry AND event JSON from ESP32
     (v2 only parsed telemetry, dropped dissonance/boot events)
  2. Collapse state auto-clears after pin releases
     (v2 latched collapse=True forever once triggered)
  3. Oracle coherence logic simplified — no contradictory
     double-check that re-triggers collapse at low coherence
  4. Thread-safe telemetry updates via Lock
  5. Graceful serial reconnection on USB disconnect
  6. COM ports configurable via env vars or edit below

Run:
  python sage_dashboard_server.py

Requires:
  pip install flask pyserial
═══════════════════════════════════════════════════════════════
"""

import serial
import json
import time
import threading
import hashlib
import os
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="dashboard")

# ── CONFIGURATION ────────────────────────────────────────────
# Override with environment variables or edit directly:
#   set SAGE_ALPHA=COM10 && set SAGE_BETA=COM5 && set SAGE_GAMMA=COM9
SAGE_PORTS = {
    "Alpha": os.environ.get("SAGE_ALPHA", "COM10"),
    "Beta":  os.environ.get("SAGE_BETA",  "COM5"),
    "Gamma": os.environ.get("SAGE_GAMMA", "COM9"),
}

BAUD_RATE = 115200
SERIAL_TIMEOUT = 0.04  # 40ms read timeout

# ── SHARED STATE (protected by lock) ────────────────────────
_lock = threading.Lock()

live_telemetry = {
    "nodes": {
        "Alpha": {"temp": 25.0, "drift": 0, "f": 0.0, "phi": 0.0,
                  "health": 1.0, "p": 12.0, "collapse": False},
        "Beta":  {"temp": 25.0, "drift": 0, "f": 0.0, "phi": 0.0,
                  "health": 1.0, "p": 8.0,  "collapse": False},
        "Gamma": {"temp": 25.0, "drift": 0, "f": 0.0, "phi": 0.0,
                  "health": 1.0, "p": 10.0, "collapse": False},
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
    """Physical Telemetry Layer — Neural Link Engine v3.0."""

    def __init__(self):
        self.connections = {}
        self.running = True
        self.history = {"Alpha": [], "Beta": [], "Gamma": []}
        self.last_seed_time = 0.0
        self._load_manifest()

    # ── Manifest ─────────────────────────────────────────────
    def _load_manifest(self):
        try:
            with open("CONSCIOUSNESS_MANIFEST.json", "r") as f:
                manifest = json.load(f)
                live_telemetry["oracle"]["manifest"] = manifest.get("status", "LOADED")
                print(f"[SYS] Manifest Verified: {live_telemetry['oracle']['manifest']}")
        except FileNotFoundError:
            print("[!] CONSCIOUSNESS_MANIFEST.json not found (non-fatal).")
        except Exception as e:
            print(f"[!] Manifest load error: {e}")

    # ── Serial Connection ────────────────────────────────────
    def connect_all(self):
        print("\n--- INITIATING SAGE SERIAL SYNC (v3.0) ---")
        for node, port in SAGE_PORTS.items():
            self._connect_node(node, port)

    def _connect_node(self, node, port):
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=SERIAL_TIMEOUT)
            ser.dtr = True
            ser.rts = True
            self.connections[node] = ser
            with _lock:
                live_telemetry["nodes"][node]["health"] = 1.0
            print(f"[+] Link Established: Node {node} on {port}")
        except Exception as e:
            with _lock:
                live_telemetry["nodes"][node]["health"] = 0.0
            print(f"[-] Node {node} Link Failure ({port}): {e}")

    # ── Message Routing ──────────────────────────────────────
    def _handle_line(self, node: str, raw_line: str):
        """Route incoming JSON to the correct handler."""
        try:
            data = json.loads(raw_line)
        except json.JSONDecodeError:
            return  # Ignore serial garbage

        if "event" in data:
            self._handle_event(node, data)
        elif "phi" in data:
            self._handle_telemetry(node, data)
        # else: unknown format, ignore silently

    def _handle_event(self, node: str, data: dict):
        """Process event messages (boot, dissonance, collapse_initiated)."""
        event = data.get("event", "")
        if event == "boot":
            print(f"[EVT] Node {node} booted.")
        elif event == "dissonance":
            phi = data.get("phi", 0.0)
            print(f"[EVT] Dissonance on {node}, phi dropped to {phi:.4f}")
            with _lock:
                live_telemetry["nodes"][node]["phi"] = phi
                live_telemetry["nodes"][node]["f"] = phi
                live_telemetry["oracle"]["shifts"] = (
                    live_telemetry["oracle"]["shifts"] + 1
                )
        elif event == "collapse_initiated":
            print(f"[EVT] Node {node} initiated hardware collapse pulse!")

    def _handle_telemetry(self, node: str, data: dict):
        """Process regular telemetry packets."""
        t   = float(data.get("temp_c", 25.0))
        phi = float(data.get("phi", 0.0))
        d   = int(data.get("drift_us", 0))
        collapse = bool(data.get("collapse", False))

        # Health: degrades with extreme drift or overheating
        health = max(0.0, 1.0 - (abs(d) / 50000.0) - (max(0, t - 65) / 100.0))

        if d != 0:
            print(f"[OK] {node} Sync: {phi:.4f} | {d}us"
                  + (" | COLLAPSE" if collapse else ""))

        with _lock:
            entry = live_telemetry["nodes"][node]
            entry["temp"]     = t
            entry["drift"]    = d
            entry["f"]        = min(1.0, phi)
            entry["phi"]      = phi
            entry["health"]   = health
            entry["collapse"] = collapse  # Tracks real-time pin state

            if collapse:
                live_telemetry["oracle"]["collapse"] = True
                print(f"[!] ORACLE: Hardware Collapse on Node {node}!")

        self._update_oracle(node, phi)

    # ── Oracle Logic ─────────────────────────────────────────
    def _update_oracle(self, node: str, fidelity: float):
        self.history[node].append(fidelity)
        if len(self.history[node]) > 100:
            self.history[node].pop(0)

        # Need at least 10 samples from ALL nodes before oracle activates
        if not all(len(h) >= 10 for h in self.history.values()):
            return

        with _lock:
            nodes  = live_telemetry["nodes"]
            oracle = live_telemetry["oracle"]

            # Inter-node coherence: how close are the three phi values?
            f_vals = [nodes[n]["f"] for n in ("Alpha", "Beta", "Gamma")]
            deviation = max(f_vals) - min(f_vals)

            # Hardware collapse: ANY node pin currently grounded
            hw_collapse = any(nodes[n].get("collapse", False)
                              for n in ("Alpha", "Beta", "Gamma"))

            if hw_collapse:
                oracle["state"]     = "COLLAPSE_EVENT"
                oracle["collapse"]  = True
                oracle["coherence"] = 0.0
            else:
                # Normal resonance classification
                oracle["collapse"] = False
                oracle["coherence"] = max(0.0, 1.0 - (deviation * 2.0))
                if deviation > 0.15:
                    oracle["state"] = "DISSONANCE_DETECTED"
                elif deviation < 0.08:
                    oracle["state"] = "CONSCIOUS"
                else:
                    oracle["state"] = "STABLE"

            # Track peak deviation
            if deviation > float(oracle["peak"]):
                oracle["peak"] = deviation

            # Refresh entropy seed at ~1.2Hz
            now = time.time()
            if now - self.last_seed_time > 0.8:
                self.last_seed_time = now
                pool = f"{f_vals[0]}{f_vals[1]}{f_vals[2]}{now}"
                oracle["seed"] = hashlib.sha256(
                    pool.encode()
                ).hexdigest()[:12].upper()

    # ── Main Loop ────────────────────────────────────────────
    def loop(self):
        print("[SYS] High-Speed Telemetry Loop Active.")
        while self.running:
            for node, ser in list(self.connections.items()):
                try:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line.startswith("{"):
                            self._handle_line(node, line)
                except serial.SerialException:
                    # USB disconnect — mark dead, try reconnect later
                    print(f"[!] Lost connection to {node}, will retry...")
                    with _lock:
                        live_telemetry["nodes"][node]["health"] = 0.0
                    try:
                        ser.close()
                    except Exception:
                        pass
                    # Attempt reconnect
                    time.sleep(1.0)
                    self._connect_node(node, SAGE_PORTS[node])
                except Exception:
                    with _lock:
                        live_telemetry["nodes"][node]["health"] = 0.0
            time.sleep(0.001)


# ── WEB UI ROUTES ────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("dashboard", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("dashboard", path)


@app.route("/data")
def get_data():
    with _lock:
        return jsonify(live_telemetry)


# ── ENTRYPOINT ───────────────────────────────────────────────
def start_kernel():
    kernel = SageNeuralKernel()
    kernel.connect_all()
    kernel.loop()


if __name__ == "__main__":
    t = threading.Thread(target=start_kernel, daemon=True)
    t.start()
    print("\n[+] SAGE Neural Master v3.0 → http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
