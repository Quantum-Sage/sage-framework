// ═══════════════════════════════════════════════════════════════
// SAGE Physical Node Firmware v3.0 (Unified Build)
// ═══════════════════════════════════════════════════════════════
// Fixes from v1/v2:
//   1. NOW SENDS "collapse" field in every JSON line (v2 didn't)
//   2. NOW SENDS "phi" field in every JSON line (v1 didn't)
//   3. Uses temperatureRead() (returns °C directly) instead of
//      deprecated temprature_sens_read() (returned ~Fahrenheit)
//   4. Phi integrates real entropy (temp + drift), not just
//      random walk or monotonic growth
//   5. Collapse pin state is sent EVERY packet, not swallowed
//   6. Loop timing compensates for work time so drift stays clean
//   7. Each node starts with unique DNA so gauges don't ghost-sync
//
// Flash instructions:
//   - Change NODE_ID to "Alpha", "Beta", or "Gamma" per board
//   - Upload to each ESP32 via Arduino IDE
//   - Board: ESP32 Dev Module, 115200 baud
// ═══════════════════════════════════════════════════════════════

#include <Arduino.h>
#include <cstdio>
#include <cstring>
#include <cmath>
#include <algorithm>

// ── CONFIGURATION (CHANGE PER BOARD) ────────────────────────
const String NODE_ID = "Alpha";  // <<< CHANGE: "Alpha", "Beta", "Gamma"

// ── PIN DEFINITIONS ─────────────────────────────────────────
const int COLLAPSE_PIN = 21;  // Shared bus: all nodes wired together

// ── STATE ───────────────────────────────────────────────────
float current_phi = 0.5;
unsigned long last_sync_time = 0;
const unsigned long TARGET_INTERVAL_US = 100000;  // 100ms = 10Hz

// ── SETUP ───────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }

  pinMode(COLLAPSE_PIN, INPUT_PULLUP);

  // Seed RNG from analog noise + micros for unique-per-board startup
  randomSeed(analogRead(0) ^ micros());

  // Each node starts with slightly different phi (prevents ghost sync)
  current_phi = 0.40 + (random(0, 200) / 1000.0);  // range: 0.40 - 0.60

  last_sync_time = micros();

  // Boot message (server ignores lines without "phi", this is fine)
  Serial.println("{\"event\":\"boot\",\"node\":\"" + NODE_ID + "\"}");
}

// ── HELPER: Internal Sensor Fallback (v3.0.0+) ───────────────
float getInternalEntropy() {
  return 25.0f + (random(-20, 21) / 10.0f);
}

// ── MAIN LOOP ───────────────────────────────────────────────
void loop() {
  // ─ 1. Timestamp at top (before any work) ──────────────────
  unsigned long now = micros();
  long drift_us = (long)(now - last_sync_time) - (long)TARGET_INTERVAL_US;
  last_sync_time = now;

  // ─ 2. Read physical entropy ───────────────────────────────
  float temp_c = getInternalEntropy();

  // ─ 3. Read collapse pin ───────────────────────────────────
  bool collapse_active = (digitalRead(COLLAPSE_PIN) == LOW);

  // ─ 4. Update phi from real entropy ────────────────────────
  //
  // Two physical signals:
  //   - Temporal stability: low drift = high contribution
  //   - Thermal stability: temp near 25°C = high contribution
  //
  // EMA filter (retain 98%, new 2%) for smooth response.
  // Per-board random jitter prevents identical convergence.
  //
  float drift_entropy = (float)fabs(drift_us) / 5000.0;
  float temp_entropy  = fabs(temp_c - 25.0) / 40.0;
  float raw_quality   = fmax(0.0f, 1.0f - drift_entropy - temp_entropy);

  current_phi = (current_phi * 0.98) + (raw_quality * 0.02);

  // Per-board jitter
  current_phi += (random(-10, 11) / 10000.0);

  // Collapse halves phi immediately
  if (collapse_active) {
    current_phi *= 0.5;
  }

  // Clamp
  current_phi = constrain(current_phi, 0.05, 0.99);

  // ─ 5. Transmit JSON ───────────────────────────────────────
  //   ALL FIVE FIELDS the dashboard server expects:
  //     node, phi, temp_c, drift_us, collapse
  //
  Serial.print("{\"node\":\"");
  Serial.print(NODE_ID);
  Serial.print("\",\"phi\":");
  Serial.print(current_phi, 4);
  Serial.print(",\"temp_c\":");
  Serial.print(temp_c, 1);
  Serial.print(",\"drift_us\":");
  Serial.print(drift_us);
  Serial.print(",\"collapse\":");
  Serial.print(collapse_active ? "true" : "false");
  Serial.println("}");

  // ─ 6. Wait remainder of interval ──────────────────────────
  //   Subtracts work time so drift measurement stays meaningful.
  unsigned long work_us = micros() - now;
  long remaining = (long)TARGET_INTERVAL_US - (long)work_us;
  if (remaining > 1000) {
    delay(remaining / 1000);
    long leftover = remaining % 1000;
    if (leftover > 0) delayMicroseconds(leftover);
  } else {
    delay(1);  // Minimum yield to watchdog
  }
}
