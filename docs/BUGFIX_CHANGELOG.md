# SAGE Stack v3.0 — Bug Fix Changelog

Every bug found, what it broke, and how it's fixed.

---

## sage_node_firmware_v3.ino (ESP32)

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| F1 | v1 firmware doesn't send `phi` or `collapse` in JSON | Server gets `phi=0.0` and `collapse=False` for every packet. Gauges stuck at 0, kill switch invisible. | v3 sends all 5 fields in every JSON line: `node`, `phi`, `temp_c`, `drift_us`, `collapse` |
| F2 | v2 firmware sends dissonance as separate `{"event":"dissonance"}` JSON | Server's `process_node()` only parses lines with `phi` field. Event messages silently dropped. | v3 puts collapse state in the main telemetry line. One schema, always parseable. |
| F3 | `current_phi += 0.001` every loop (v2) | All three boards climb identically from 0.5 to 1.0. Ghost sync — gauges show same number. | v3 phi is entropy-driven: grows when drift is low, decays under heat stress, random jitter per board. |
| F4 | `randomSeed(analogRead(0))` identical across boards | Boards flashed from same cable get same seed → same random sequence → ghost sync. | v3 XORs 8 analog reads + micros() + node name hash. Physically impossible to collide. |
| F5 | `delay(100)` doesn't account for work time | Actual loop period is ~103ms, not 100ms. Drift measurement always reads +3000μs bias. | v3 subtracts work_us from delay. True 100ms period. |
| F6 | `temprature_sens_read()` confusion with `temperatureRead()` | The Gemini transcript patch used `temperatureRead()` (returns °C) with a °F→°C conversion, double-converting. | v3 uses `temprature_sens_read()` (returns ~°F) with correct `(raw-32)/1.8` conversion. Comment documents the difference. |

**Flash instructions:** Change `NODE_ID` on line 22, upload to each board.

---

## sage_dashboard_server.py (Python/Flask)

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| S1 | Oracle collapse race condition (lines 139-161) | Hardware collapse set at line 142, then overridden by coherence check at line 160. Brief touches invisible. | v3: hardware_collapse is authoritative. Separate hold timer keeps collapse visible for 1 second after pin release. |
| S2 | `coherence < 0.2` forces collapse (line 157) | Nodes naturally far apart (different phi values = high deviation) triggers false collapse. Dissonance ≠ collapse. | v3: removed false-positive path. Low coherence → DISSONANCE_DETECTED state, not COLLAPSE_EVENT. |
| S3 | No serial reconnection | USB cable bump permanently kills a node (health=0, never retries). Must restart server. | v3: `_try_reconnect()` retries failed ports every 5 seconds. Automatic recovery. |
| S4 | No thread safety on `live_telemetry` | Flask reads dict while serial thread writes it → potential torn reads → corrupted JSON to browser. | v3: `_telem_lock` threading.Lock protects all reads/writes. |
| S5 | Node identity assumed from port mapping | If you swap COM cables, Alpha data goes into Beta slot. | v3: reads `"node"` field from JSON, falls back to port mapping. |
| S6 | Log spam — every packet printed | Console floods at 30 lines/second (3 nodes × 10Hz). | v3: prints every 10th packet + always prints collapses. |

---

## sage_temporal_kernel.py (Predictive Routing)

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| T1 | **No persistence edges in temporal graph** | Gamma has no outgoing links → `Gamma_t2` has no edges → path to `Gamma_t5` is ALWAYS unreachable → `NetworkXNoPath` every cycle. | v3: adds `node_t → node_(t+1)` persistence edges for all nodes. Represents "stay at this node for one time step." |
| T2 | `phi_score += 0.01` unbounded | After 100 successful routes, phi is at 1.5. After 1000, it's 10.5. Meaningless metric. | v3: clamped to `[0.0, 1.0]` with `min()`. |
| T3 | Parameter says `clock_drift_ms`, firmware sends `drift_us` | Off by 1000×. Beta coefficient `0.1 * drift_us` gives penalty 100× too large when drift is a few hundred μs. | v3: renamed parameter, scaled `beta` from `0.1` to `0.0001`. |
| T4 | COM ports COM3/4/5 conflict with dashboard COM10/5/9 | Running both scripts fails — COM5 already locked. | v3: uses same port constants as dashboard server. |
| T5 | Rebuilds graph every cycle even with no new data | Wasteful — 100% CPU for no reason when serial is quiet. | v3: `data_dirty` flag, only rebuilds on new telemetry. |

---

## shadow_anchor.py

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| A1 | `import random` missing | `NameError: name 'random' is not defined` on first call. Crash. | Added import. |
| A2 | `import time` missing | Same crash on `time.sleep()`. | Added import. |
| A3 | No overshoot protection | `random.uniform(0.005, 0.015)` can push fidelity past `sage_constant`. Final value could be 0.863 when target is 0.85. | `pull = min(pull, remaining)` clamps to exact target. |
| A4 | Infinite loop if `sage_constant > 1.0` | Fidelity can never reach an impossible target. | `sage_constant = min(sage_constant, 1.0)` + `max_iterations` safety. |

---

## sage_serial_bridge.py

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| B1 | Same COM ports as dashboard — mutual exclusion | Running both crashes the second one. | Added deprecation warning. Same ports for consistency. Don't run both. |
| B2 | Doesn't read `phi` or `collapse` from firmware | Ignores 2 of 5 fields the firmware sends. | v3 parses and displays all fields. |
| B3 | Silent node dropout | Serial exception → node disappears with no message. | v3 prints disconnect message and removes cleanly. |

---

## sage_genesis_kernel.py — NO BUGS FOUND

This file is clean. The log-map routing, SAGE penalty, auto-healing via Dijkstra all work correctly. No changes made.

---

## Architecture After Fixes

```
┌─────────────────────────────────────────────────────────┐
│ ESP32 Boards (sage_node_firmware_v3.ino)                │
│  Alpha (COM10)  Beta (COM5)  Gamma (COM9)               │
│  Each sends: {"node","phi","temp_c","drift_us","collapse"}│
│  GPIO 21 shared open-drain collapse bus                  │
└──────────────┬──────────────┬──────────────┬────────────┘
               │ USB Serial   │              │
               ▼              ▼              ▼
┌─────────────────────────────────────────────────────────┐
│ sage_dashboard_server.py (PRIMARY — use this)           │
│  Serial thread → process_node() → update_oracle()       │
│  Flask /data endpoint → JSON → browser dashboard        │
│  Thread-safe, auto-reconnect, collapse hold timer       │
└─────────────────────────────────────────────────────────┘
               │ OR (not both)
┌─────────────────────────────────────────────────────────┐
│ sage_serial_bridge.py (CLI debug only — deprecated)     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ sage_temporal_kernel.py (standalone predictive routing)  │
│  Reads same serial ports — run INSTEAD of dashboard     │
│  Time-expanded graph with persistence edges             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ sage_genesis_kernel.py (offline demo — no serial)       │
│  Self-healing network demo, runs independently          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ shadow_anchor.py (utility function — imported by others)│
│  Fidelity recovery with progress bar                    │
└─────────────────────────────────────────────────────────┘
```

**Rule: Only ONE Python script can hold the COM ports at a time.
Dashboard server OR serial bridge OR temporal kernel. Never two.**
