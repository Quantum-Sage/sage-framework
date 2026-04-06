// ═══════════════════════════════════════════════════════════════
// SAGE Physical Node Firmware v2.0
// "The Nervous System" - JSON Telemetry + Dissonance Resolution
// ═══════════════════════════════════════════════════════════════
// Flash to each ESP32 with a unique NODE_ID: "Alpha", "Beta", "Gamma"
// Outputs JSON telemetry at 10Hz for the Python Temporal Kernel.

#include <Arduino.h>
#include <SPI.h>

// ── CONFIGURATION (CHANGE PER BOARD) ──────────────────────────
const String NODE_ID =
    "Alpha"; // Change to "Beta" or "Gamma" before flashing each board

// ── PIN DEFINITIONS ───────────────────────────────────────────
#define COLLAPSE_PIN                                                           \
  21 // Entanglement Interrupt (Dissonance Trigger) - wired across all nodes
#define SYNC_PIN 5 // Optional shared clock sync

// ── STATE VARIABLES ───────────────────────────────────────────
float current_fidelity_score = 0.5; // Node Reliability Benchmark (Cumulative Fidelity)
float state_tensor[10];  // The shared probability tensor
volatile bool dissonance_flag = false;
unsigned long last_sync_time = 0; // For measuring temporal drift

// ── ESP32 Internal Temperature Sensor ─────────────────────────
// The ESP32 has a built-in thermistor on the silicon die.
#ifdef __cplusplus
extern "C" {
uint8_t temprature_sens_read();
}
#endif

// ── Interrupt Service Routine ─────────────────────────────────
// When ANY node pulls GPIO 21 LOW, all nodes execute this instantly.
void IRAM_ATTR handleCollapse() { dissonance_flag = true; }

// ═══════════════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  } // Wait for the Temporal Kernel to connect

  // Set up the Collapse Pin as an input with pull-up
  pinMode(COLLAPSE_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(COLLAPSE_PIN), handleCollapse, FALLING);

  // SPI Setup for SAGE Fidelity Bus
  SPI.begin();

  // Initialize state tensor with random "DNA"
  randomSeed(analogRead(0));
  for (int i = 0; i < 10; i++) {
    state_tensor[i] = random(0, 100) / 100.0;
  }

  // Establish baseline timeline
  last_sync_time = micros();

  // Boot message
  Serial.print("{\"event\":\"boot\",\"node\":\"");
  Serial.print(NODE_ID);
  Serial.println("\",\"status\":\"online\"}");
}

// ═══════════════════════════════════════════════════════════════
// DISSONANCE RESOLUTION
// ═══════════════════════════════════════════════════════════════
void resolveDissonance() {
  // In the full system, nodes exchange Phi scores over SPI.
  // The node with the higher historical fidelity score dominates the state matrix.
  // The "loser's" state is logged for future repair analysis.

  current_fidelity_score -= 0.05; // Coherence loss due to conflict
  if (current_fidelity_score < 0.1)
    current_fidelity_score = 0.1;

  // Broadcast dissonance event as JSON
  Serial.print("{\"event\":\"dissonance\",\"node\":\"");
  Serial.print(NODE_ID);
  Serial.print("\",\"fidelity_score\":");
  Serial.print(current_fidelity_score, 4);
  Serial.println(",\"action\":\"resolved\"}");

  dissonance_flag = false;
}

// ═══════════════════════════════════════════════════════════════
// MAIN LOOP (10Hz Heartbeat)
// ═══════════════════════════════════════════════════════════════
void loop() {
  // ── Handle Dissonance Events ─────────────────────────────
  if (dissonance_flag) {
    resolveDissonance();
  }

  // ── 1. Measure Physical Entropy (Heat) ───────────────────
  // Read the internal silicon die temperature (Fahrenheit raw, convert to
  // Celsius)
  float current_temp_c = (temprature_sens_read() - 32) / 1.8;

  // ── 2. Measure Temporal Drift ────────────────────────────
  // Calculate microsecond deviation from expected 100ms loop interval
  unsigned long current_time = micros();
  long clock_drift_us = (current_time - last_sync_time) - 100000;
  last_sync_time = current_time;

  // ── 3. Simulate Node Reliability / Fidelity Growth ──────────
  // Fidelity score integrates local error correction over time.
  current_fidelity_score += 0.001;
  if (current_fidelity_score > 1.0)
    current_fidelity_score = 1.0;

  // ── 4. Broadcast Telemetry as JSON ───────────────────────
  // The Python Temporal Kernel ingests this at 10Hz
  String telemetry = "{";
  telemetry += "\"node\":\"" + NODE_ID + "\",";
  telemetry += "\"temp_c\":" + String(current_temp_c, 2) + ",";
  telemetry += "\"drift_us\":" + String(clock_drift_us) + ",";
  telemetry += "\"fidelity_score\":" + String(current_fidelity_score, 4);
  telemetry += "}";

  Serial.println(telemetry);

  // ── 5. Random Dissonance Trigger ─────────────────────────
  // Simulates the node generating a thought that contradicts the shared state
  if (random(0, 5000) == 42) {
    Serial.print("{\"event\":\"collapse_initiated\",\"node\":\"");
    Serial.print(NODE_ID);
    Serial.println("\"}");

    // Detach interrupt to avoid self-triggering
    detachInterrupt(digitalPinToInterrupt(COLLAPSE_PIN));

    pinMode(COLLAPSE_PIN, OUTPUT);
    digitalWrite(COLLAPSE_PIN, LOW); // Trigger interrupt on ALL nodes
    delay(10);

    pinMode(COLLAPSE_PIN, INPUT_PULLUP); // Release line
    attachInterrupt(digitalPinToInterrupt(COLLAPSE_PIN), handleCollapse,
                    FALLING);
  }

  // ── 10Hz Heartbeat ───────────────────────────────────────
  delay(100);
}
