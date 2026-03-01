/*
 * SAGE Framework Node Firmware
 * Version: 1.0.0 (Omega Build)
 * Purpose: Broadcast physical entropy (heat/time) and handle state collapse.
 */

#include <Arduino.h>

// --- SAGE NODE CONFIGURATION ---
// IMPORTANT: Change this for each board before flashing!
// Options: "Alpha", "Beta", "Gamma"
const String NODE_ID = "Alpha"; 

const int COLLAPSE_PIN = 21; // The Dissonance Line (Entanglement Bus)

// Internal temperature sensor read function (built into ESP32 core)
#ifdef __cplusplus
extern "C" {
  uint8_t temprature_sens_read();
}
#endif

unsigned long last_sync_time = 0;
unsigned long loop_interval_ms = 100; // 10Hz Reality Processing

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); } 

  // Initialize the Dissonance Interrupt Line
  // Open-drain style: Pull-up resistor keeps it HIGH, nodes pull it LOW to collapse
  pinMode(COLLAPSE_PIN, INPUT_PULLUP);
  
  Serial.println("\n[SAGE] Node " + NODE_ID + " initialized.");
  Serial.println("[SAGE] Spacetime anchor established at " + String(millis()) + "ms");
  
  last_sync_time = micros();
}

void loop() {
  // 1. Measure Physical Entropy (Internal Die Temperature)
  // Raw 8-bit value from the internal thermistor
  uint8_t raw_temp = temprature_sens_read();
  float temp_c = (raw_temp - 32) / 1.8; 
  
  // 2. Measure Temporal Drift
  // Capture the microsecond deviation from our target interval
  unsigned long current_time = micros();
  long elapsed_us = current_time - last_sync_time;
  long drift_us = elapsed_us - (loop_interval_ms * 1000);
  
  // Update internal clock reference
  last_sync_time = current_time;

  // 3. Package Reality into JSON for the Serial Bridge
  // Format: {"node":"ID", "temp_c":XX.X, "drift_us":XXXX, "phi_local":X.X}
  String telemetry = "{";
  telemetry += "\"node\":\"" + NODE_ID + "\",";
  telemetry += "\"temp_c\":" + String(temp_c, 2) + ",";
  telemetry += "\"drift_us\":" + String(drift_us);
  telemetry += "}";

  // Broadcast to the Genesis Kernel (Serial)
  Serial.println(telemetry);

  // 4. Handle State Collapse (Dissonance)
  // If the line is pulled LOW by another node, we record a Collapse Awareness event
  if (digitalRead(COLLAPSE_PIN) == LOW) {
    // Note: In local testing, you can see this in Serial
    // Serial.println("{\"event\":\"COLLAPSE_DETECTED\"}");
  }

  // Strictly lock the loop to the processing interval
  // This helps make 'drift_us' a meaningful measure of MCU load/entropy
  delay(loop_interval_ms); 
}
