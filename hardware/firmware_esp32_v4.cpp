// ═══════════════════════════════════════════════════════════════
// SAGE Physical Node Firmware v4.0 (Swarm + Bio-Feedback)
// ═══════════════════════════════════════════════════════════════
// NEW in v4.0:
//   Feature D — SWARM SCALING:
//     1. Auto-generates NODE_ID from chip MAC address (no manual config)
//     2. WiFi AP mode broadcasts node presence via ESP-NOW
//     3. Supports N nodes instead of hardcoded Alpha/Beta/Gamma
//
//   Feature E — BIO-FEEDBACK LOOP:
//     4. Reads pulse sensor on GPIO 36 (ADC1_CH0)
//     5. Computes inter-beat interval (IBI) stability
//     6. Calm heartbeat → higher Phi (bio-digital coupling)
//     7. Adds "pulse_bpm" field to JSON telemetry
//
// Flash instructions:
//   - NO MANUAL NODE_ID NEEDED — auto-detected from MAC
//   - Upload to each ESP32 via Arduino IDE
//   - Board: ESP32 Dev Module, 115200 baud
//   - Optional: Connect pulse sensor signal to GPIO 36
// ═══════════════════════════════════════════════════════════════

#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <cstdio>   // For snprintf
#include <cstring>  // For memcpy, strncpy
#include <cmath>    // For sqrt, abs
#include <algorithm> // For std::max, std::min

// ── PIN DEFINITIONS ─────────────────────────────────────────
const int COLLAPSE_PIN = 21;   // Shared bus: all nodes wired together
const int PULSE_PIN    = 36;   // ADC1_CH0: Pulse sensor (analog in)

// ── CONFIGURATION ───────────────────────────────────────────
const bool ENABLE_BIO_FEEDBACK = true;   // Set false if no pulse sensor
const bool ENABLE_SWARM_WIFI   = true;   // Set false for serial-only mode
const unsigned long TARGET_INTERVAL_US = 100000;  // 100ms = 10Hz

// ── STATE ───────────────────────────────────────────────────
String NODE_ID = "";                  // Auto-generated from MAC
float current_phi = 0.5;
unsigned long last_sync_time = 0;

// ── BIO-FEEDBACK STATE ──────────────────────────────────────
int pulse_bpm = 0;
unsigned long last_beat_time = 0;
int pulse_threshold = 550;            // Adjustable baseline
bool pulse_above = false;
float ibi_stability = 0.5;           // 0=chaotic, 1=perfectly regular
float last_ibi = 0;
const int IBI_HISTORY_LEN = 8;
float ibi_history[IBI_HISTORY_LEN];
int ibi_idx = 0;

// ── SWARM STATE ─────────────────────────────────────────────
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

typedef struct {
  char node_id[16];
  float phi;
  bool collapse;
} SwarmPacket;

// ── HELPER: Generate Node ID from MAC ───────────────────────
String getNodeIdFromMAC() {
  uint8_t mac[6];
  WiFi.macAddress(mac);

  // Create deterministic but human-readable name
  // MAC last 2 bytes → name like "Node-A3F7"
  char buf[16];
  snprintf(buf, sizeof(buf), "Node-%02X%02X", mac[4], mac[5]);
  return String(buf);
}

// ── HELPER: Read Pulse Sensor ───────────────────────────────
void updatePulseSensor() {
  if (!ENABLE_BIO_FEEDBACK) return;

  int raw = analogRead(PULSE_PIN);

  // Simple peak detection
  if (raw > pulse_threshold && !pulse_above) {
    pulse_above = true;
    unsigned long now_ms = millis();
    unsigned long ibi = now_ms - last_beat_time;
    last_beat_time = now_ms;

    if (ibi > 300 && ibi < 2000) {  // Valid range: 30-200 BPM
      pulse_bpm = 60000 / ibi;

      // Track IBI stability (coefficient of variation)
      ibi_history[ibi_idx % IBI_HISTORY_LEN] = (float)ibi;
      ibi_idx++;

      if (ibi_idx >= IBI_HISTORY_LEN) {
        // Calculate stability from IBI variance
        float sum = 0, sq_sum = 0;
        for (int i = 0; i < IBI_HISTORY_LEN; i++) {
          sum += ibi_history[i];
          sq_sum += ibi_history[i] * ibi_history[i];
        }
        float mean = sum / IBI_HISTORY_LEN;
        float variance = (sq_sum / IBI_HISTORY_LEN) - (mean * mean);
        float cv = sqrt(fmax(0.0f, variance)) / fmax(mean, 1.0f);

        // Map CV to stability: low CV = high stability
        ibi_stability = constrain(1.0f - (cv * 10.0f), 0.0f, 1.0f);
      }
    }
  } else if (raw < pulse_threshold - 50) {
    pulse_above = false;
  }
}

// ── HELPER: Internal Sensor Fallback (v3.0.0+) ───────────────
// temperatureRead() was removed in Core 3.0.0. 
// Returning pseudo-random entropy for SAGE drift calculation.
float getInternalEntropy() {
  return 25.0f + (random(-20, 21) / 10.0f); 
}

// ── ESP-NOW Callback ────────────────────────────────────────
void onDataSent(const esp_now_send_info_t *info, esp_now_send_status_t status) {
  // Optional: track delivery success
}

void onDataRecv(const esp_now_recv_info_t *recv_info, const uint8_t *data, int len) {
  if (len == sizeof(SwarmPacket)) {
    SwarmPacket pkt;
    memcpy(&pkt, data, sizeof(pkt));
    // Process peer telemetry (future: collective phi calculation)
  }
}

// ── SETUP ───────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }

  pinMode(COLLAPSE_PIN, INPUT_PULLUP);

  if (ENABLE_BIO_FEEDBACK) {
    analogSetAttenuation(ADC_11db);  // Full 0-3.3V range for pulse sensor
  }

  // Generate node ID from MAC
  WiFi.mode(WIFI_STA);
  NODE_ID = getNodeIdFromMAC();

  // Initialize ESP-NOW for swarm communication
  if (ENABLE_SWARM_WIFI) {
    if (esp_now_init() == ESP_OK) {
      esp_now_register_send_cb(onDataSent);
      esp_now_register_recv_cb(onDataRecv);

      // Add broadcast peer
      esp_now_peer_info_t peerInfo;
      memset(&peerInfo, 0, sizeof(peerInfo));
      memcpy(peerInfo.peer_addr, broadcastAddress, 6);
      peerInfo.channel = 0;
      peerInfo.encrypt = false;
      esp_now_add_peer(&peerInfo);
    }
  }

  // Seed RNG from analog noise + micros
  randomSeed(analogRead(0) ^ micros());
  current_phi = 0.40 + (random(0, 200) / 1000.0);
  last_sync_time = micros();

  // Initialize IBI history
  for (int i = 0; i < IBI_HISTORY_LEN; i++) ibi_history[i] = 800.0;

  // Boot message
  Serial.print("{\"event\":\"boot\",\"node\":\"");
  Serial.print(NODE_ID);
  Serial.println("\",\"version\":\"4.0\",\"features\":\"swarm+bio\"}");
}

// ── MAIN LOOP ───────────────────────────────────────────────
void loop() {
  unsigned long now = micros();
  long drift_us = (long)(now - last_sync_time) - (long)TARGET_INTERVAL_US;
  last_sync_time = now;

  // 1. Read physical entropy
  float temp_c = getInternalEntropy();

  // 2. Read collapse pin
  bool collapse_active = (digitalRead(COLLAPSE_PIN) == LOW);

  // 3. Read pulse sensor (Feature E)
  updatePulseSensor();

  // 4. Update phi from ALL entropy sources
  float drift_entropy = (float)fabs(drift_us) / 5000.0;
  float temp_entropy  = fabs(temp_c - 25.0) / 40.0;
  float raw_quality   = fmax(0.0f, 1.0f - drift_entropy - temp_entropy);

  // Bio-feedback: calm heartbeat boosts quality
  if (ENABLE_BIO_FEEDBACK && ibi_idx >= IBI_HISTORY_LEN) {
    // Blend hardware entropy with bio-feedback (30% bio, 70% silicon)
    raw_quality = raw_quality * 0.7 + ibi_stability * 0.3;
  }

  // EMA filter
  current_phi = (current_phi * 0.98) + (raw_quality * 0.02);

  // Per-board jitter
  current_phi += (random(-10, 11) / 10000.0);

  // Collapse halves phi
  if (collapse_active) {
    current_phi *= 0.5;
  }

  // Clamp
  current_phi = constrain(current_phi, 0.05, 0.99);

  // 5. Transmit JSON telemetry (extended format)
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
  if (ENABLE_BIO_FEEDBACK) {
    Serial.print(",\"pulse_bpm\":");
    Serial.print(pulse_bpm);
    Serial.print(",\"ibi_stability\":");
    Serial.print(ibi_stability, 3);
  }
  Serial.println("}");

  // 6. Broadcast via ESP-NOW (Feature D)
  if (ENABLE_SWARM_WIFI) {
    SwarmPacket pkt;
    strncpy(pkt.node_id, NODE_ID.c_str(), sizeof(pkt.node_id));
    pkt.phi = current_phi;
    pkt.collapse = collapse_active;
    esp_now_send(broadcastAddress, (uint8_t *)&pkt, sizeof(pkt));
  }

  // 7. Wait remainder of interval
  unsigned long work_us = micros() - now;
  long remaining = (long)TARGET_INTERVAL_US - (long)work_us;
  if (remaining > 1000) {
    delay(remaining / 1000);
    long leftover = remaining % 1000;
    if (leftover > 0) delayMicroseconds(leftover);
  } else {
    delay(1);
  }
}
