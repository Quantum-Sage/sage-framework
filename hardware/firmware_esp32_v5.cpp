// ═══════════════════════════════════════════════════════════════
// SAGE Classical Logic Sandbox v5.0 (Algorithmic Mirror Daemon)
// ═══════════════════════════════════════════════════════════════
// !!! SCIENTIFIC DISCLAIMER !!!
// This code is a CLASSICAL LOGIC DEMONSTRATION. It does NOT possess
// quantum hardware and does NOT perform Quantum Error Correction.
// The "Mirror Daemon" implemented here is a classical PID/Feedback
// loop designed to visualize the CONTROL LOGIC described in SAGE
// Paper #3. It serves as a physical proxy for dashboard telemetry.
//
// current_phi represents a CLASSICAL PROBABILITY ANALOG.
// ═══════════════════════════════════════════════════════════════

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiType.h>
#include <HardwareSerial.h>
#include <esp_now.h>
#include <cstdio>
#include <cstring>
#include <cmath>
#include <algorithm>

// ── PIN DEFINITIONS ─────────────────────────────────────────
const int COLLAPSE_PIN    = 21;   // Shared bus
const int PULSE_PIN       = 36;   // Pulse sensor
const int SYNC_SHIELD_LED = 2;    // Onboard LED (indicates daemon activity)

// ── CONFIGURATION ───────────────────────────────────────────
const bool ENABLE_BIO_FEEDBACK = true;
const bool ENABLE_SWARM_WIFI   = true;
const bool ENABLE_MIRROR_DAEMON = true; // NEW: Feature F
const unsigned long TARGET_INTERVAL_US = 100000; // 10Hz

// ── DAEMON PARAMETERS (From Handover Paradox Analysis) ──────
const float REFERENCE_PHI    = 0.950f;
const float BASE_THRESHOLD   = 0.600f; // Crossing F=0.5 is death; 0.6 is the safety margin
const float INJECTION_ALPHA  = 0.050f; // Proportional blend strength

// ── STATE ───────────────────────────────────────────────────
String NODE_ID = "";
float current_phi = 0.50;
unsigned long last_sync_time = 0;
unsigned long injection_count = 0;
bool sync_shield_active = false;

// ── BIO-FEEDBACK STATE ──────────────────────────────────────
int pulse_bpm = 0;
unsigned long last_beat_time = 0;
int pulse_threshold = 550;
bool pulse_above = false;
float ibi_stability = 0.5;
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
  bool injection_active;
} SwarmPacket;

// ── HELPERS ─────────────────────────────────────────────────

String getNodeIdFromMAC() {
  uint8_t mac[6];
  WiFi.macAddress(mac);
  char buf[16];
  snprintf(buf, sizeof(buf), "Node-%02X%02X", mac[4], mac[5]);
  return String(buf);
}

void updatePulseSensor() {
  if (!ENABLE_BIO_FEEDBACK) return;
  int raw = analogRead(PULSE_PIN);
  if (raw > pulse_threshold && !pulse_above) {
    pulse_above = true;
    unsigned long now_ms = millis();
    unsigned long ibi = now_ms - last_beat_time;
    last_beat_time = now_ms;
    if (ibi > 300 && ibi < 2000) {
      pulse_bpm = 60000 / ibi;
      ibi_history[ibi_idx % IBI_HISTORY_LEN] = (float)ibi;
      ibi_idx++;
      if (ibi_idx >= IBI_HISTORY_LEN) {
        float sum = 0, sq_sum = 0;
        for (int i = 0; i < IBI_HISTORY_LEN; i++) {
          sum += ibi_history[i];
          sq_sum += ibi_history[i] * ibi_history[i];
        }
        float mean = sum / IBI_HISTORY_LEN;
        float variance = (sq_sum / IBI_HISTORY_LEN) - (mean * mean);
        float cv = sqrt(fmax(0.0f, variance)) / fmax(mean, 1.0f);
        ibi_stability = constrain(1.0f - (cv * 10.0f), 0.0f, 1.0f);
      }
    }
  } else if (raw < pulse_threshold - 50) {
    pulse_above = false;
  }
}

float getInternalEntropy() {
  return 25.0f + (random(-20, 21) / 10.0f); 
}

// ── ESP-NOW CALLBACKS ───────────────────────────────────────
void onDataSent(const esp_now_send_info_t *info, esp_now_send_status_t status) {}
void onDataRecv(const esp_now_recv_info_t *recv_info, const uint8_t *data, int len) {
  if (len == sizeof(SwarmPacket)) {
    SwarmPacket pkt;
    memcpy(&pkt, data, sizeof(pkt));
  }
}

// ── SETUP ───────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  pinMode(COLLAPSE_PIN, INPUT_PULLUP);
  pinMode(SYNC_SHIELD_LED, OUTPUT);
  digitalWrite(SYNC_SHIELD_LED, LOW);

  if (ENABLE_BIO_FEEDBACK) analogSetAttenuation(ADC_ATTEN_DB_12);

  WiFi.mode(WIFI_STA);
  NODE_ID = getNodeIdFromMAC();

  if (ENABLE_SWARM_WIFI) {
    if (esp_now_init() == ESP_OK) {
      esp_now_register_send_cb(onDataSent);
      esp_now_register_recv_cb(onDataRecv);
      esp_now_peer_info_t peerInfo;
      memset(&peerInfo, 0, sizeof(peerInfo));
      memcpy(peerInfo.peer_addr, broadcastAddress, 6);
      peerInfo.channel = 0;
      peerInfo.encrypt = false;
      esp_now_add_peer(&peerInfo);
    }
  }

  randomSeed(analogRead(0) ^ micros());
  current_phi = 0.50;
  last_sync_time = micros();
  for (int i = 0; i < IBI_HISTORY_LEN; i++) ibi_history[i] = 800.0;

  Serial.print("{\"event\":\"boot\",\"node\":\"");
  Serial.print(NODE_ID.c_str());
  Serial.println("\",\"version\":\"5.0\",\"features\":\"swarm+bio+daemon\"}");
}

// ── MAIN LOOP ───────────────────────────────────────────────
void loop() {
  unsigned long now = micros();
  long drift_us = (long)(now - last_sync_time) - (long)TARGET_INTERVAL_US;
  last_sync_time = now;

  float temp_c = getInternalEntropy();
  bool collapse_active = (digitalRead(COLLAPSE_PIN) == LOW);
  updatePulseSensor();

  // 1. Compute Operational Quality (Noise/Drift)
  float drift_entropy = (float)fabs(drift_us) / 5000.0;
  float temp_entropy  = fabs(temp_c - 25.0) / 40.0;
  float operational_quality = fmax(0.0f, 1.0f - drift_entropy - temp_entropy);

  if (ENABLE_BIO_FEEDBACK && ibi_idx >= IBI_HISTORY_LEN) {
    operational_quality = operational_quality * 0.7 + ibi_stability * 0.3;
  }

  // 2. Adaptive Threshold Calculation
  // In v5.0, threshold is higher when noise is higher (escalating fatigue)
  float noise_rate = drift_entropy + temp_entropy;
  float threshold_current = BASE_THRESHOLD + (noise_rate * 0.1f);
  threshold_current = constrain(threshold_current, BASE_THRESHOLD, 0.85);

  // 3. Mirror Daemon Injection Logic (Feature F)
  sync_shield_active = false;
  if (ENABLE_MIRROR_DAEMON) {
    if (current_phi < threshold_current) {
      // Calculate dynamic strength based on how far we've fallen
      float strength = INJECTION_ALPHA * (1.1f - (current_phi / threshold_current));
      strength = constrain(strength, 0.01f, 0.20f);
      
      // Inject Reference Phi (Self-Regeneration)
      current_phi = (current_phi * (1.0f - strength)) + (REFERENCE_PHI * strength);
      injection_count++;
      sync_shield_active = true;
    }
  }

  // 4. Standard Environmental Decay (The entropic baseline)
  // Phi decays toward operational_quality without daemon intervention
  current_phi = (current_phi * 0.985) + (operational_quality * 0.015);

  // 5. Hard Penalties
  if (collapse_active) current_phi *= 0.5;

  // Clamp
  current_phi = constrain(current_phi, 0.05, 0.99);

  // 6. Sync Shield LED (Visual Feedback)
  if (sync_shield_active) {
    digitalWrite(SYNC_SHIELD_LED, HIGH);
  } else {
    // Faint "breathing" if inactive but alive
    int brightness = (int)(current_phi * 50);
    analogWrite(SYNC_SHIELD_LED, brightness);
  }

  // 7. Transmit JSON Telemetry
  Serial.print("{\"node\":\"");
  Serial.print(NODE_ID.c_str());
  Serial.print("\",\"phi\":");
  Serial.print((double)current_phi, 4);
  Serial.print(",\"threshold\":");
  Serial.print(threshold_current, 3);
  Serial.print(",\"injections\":");
  Serial.print(injection_count);
  Serial.print(",\"daemon_active\":");
  Serial.print(sync_shield_active ? "true" : "false");
  Serial.print(",\"pulse_bpm\":");
  Serial.print(pulse_bpm);
  Serial.println("}");

  // 8. Swarm Broadcast
  if (ENABLE_SWARM_WIFI) {
    SwarmPacket pkt;
    strncpy(pkt.node_id, NODE_ID.c_str(), sizeof(pkt.node_id));
    pkt.phi = current_phi;
    pkt.collapse = collapse_active;
    pkt.injection_active = sync_shield_active;
    esp_now_send(broadcastAddress, (uint8_t *)&pkt, sizeof(pkt));
  }

  // 9. Interval Wait
  unsigned long work_us = micros() - now;
  long remaining = (long)TARGET_INTERVAL_US - (long)work_us;
  if (remaining > 1000) delay(remaining / 1000);
  else delay(1);
}
