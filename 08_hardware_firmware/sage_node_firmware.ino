// ═══════════════════════════════════════════════════════════════
// SAGE Physical Node Firmware v3.1 (THERMAL CALIBRATION)
// ═══════════════════════════════════════════════════════════════
// Fixes from v3.0:
//   1. THERMAL BASELINE: Shifted from 25°C to 58°C for real-world OPS.
//   2. COHERENCE RECOVERY: Faster integration (0.08) for live sync.
//   3. LOOP TIMING: Locked at 100ms for stable drift telemetry.
// ═══════════════════════════════════════════════════════════════

#include <Arduino.h>

// ── CONFIGURATION (CHANGE PER BOARD) ────────────────────────
const String NODE_ID = "Alpha";  // <<< CHANGE: "Alpha", "Beta", "Gamma"
const int COLLAPSE_PIN = 21; 

// ── STATE ───────────────────────────────────────────────────
float current_phi = 0.5;
unsigned long last_sync_time = 0;
const unsigned long TARGET_INTERVAL_US = 100000; 

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }

  pinMode(COLLAPSE_PIN, INPUT_PULLUP);
  randomSeed(analogRead(0) ^ micros());
  current_phi = 0.40 + (random(0, 200) / 1000.0);
  last_sync_time = micros();

  Serial.println("{\"event\":\"boot\",\"node\":\"" + NODE_ID + "\"}");
}

void loop() {
  unsigned long now = micros();
  long drift_us = (long)(now - last_sync_time) - (long)TARGET_INTERVAL_US;
  last_sync_time = now;

  float temp_c = temperatureRead();
  bool collapse_active = (digitalRead(COLLAPSE_PIN) == LOW);

  // ─ REPAIR: THERMAL CALIBRATION (v3.1) ─────────────────────
  // Baseline set to 58°C which is your observed operating temp.
  float temp_entropy  = abs(temp_c - 58.0) / 40.0; 
  float drift_entropy = (float)abs(drift_us) / 5000.0;
  float raw_quality   = max(0.0f, 1.0f - drift_entropy - temp_entropy);

  // Sync recovery speed increase
  current_phi = (current_phi * 0.92) + (raw_quality * 0.08);
  current_phi += (random(-10, 11) / 10000.0);

  if (collapse_active) {
    current_phi *= 0.5;
  }

  current_phi = constrain(current_phi, 0.05, 0.99);

  // Transmit JSON (v3.1 Sync Protocol)
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

  unsigned long work_us = micros() - now;
  long remaining = (long)TARGET_INTERVAL_US - (long)work_us;
  if (remaining > 1000) {
    delay(remaining / 1000);
  } else {
    delay(1);
  }
}
