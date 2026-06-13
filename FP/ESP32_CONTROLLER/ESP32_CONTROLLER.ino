#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_Fingerprint.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// ─── WiFi Configuration ───
const char* ssid = "Arunesh";
const char* password = "00000000";

// ─── Server Configuration ───
const String SERVER_IP = "10.83.201.98"; 
const int SERVER_PORT = 5000;
String ESP32_CAM_IP = "0.0.0.0";
const String pollUrl = "http://" + SERVER_IP + ":5000/api/controller/poll";
const String eventUrl = "http://" + SERVER_IP + ":5000/api/controller/event";

// ─── Pin Definitions ───
#define GREEN_LED 14
#define RED_LED   15
#define BUZZER    2
#define RELAY_PIN 4

// ─── OLED Configuration ───
Adafruit_SSD1306 display(128, 64, &Wire, -1);

// ─── Fingerprint Sensor ───
HardwareSerial mySerial(2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

// ─── System State ───
bool sensorReady = false;
bool oledReady = false;
unsigned long lastPoll = 0;
const unsigned long pollInterval = 1000; 
unsigned long lastAction = 0;
unsigned long lastCamFetch = 0;
const unsigned long camInterval = 150; 
bool ssActive = false;
bool previewActive = false;
int enrollSlot = 0;
unsigned long lockTime = 0;
bool isLocked = true;
String o1 = "SYSTEM IDLE", o2 = "Ready", o3 = "";
bool hazardOn = false;
int hzStep = -1;
int ssX = 0, ssY = 0, ssDX = 1, ssDY = 1;

// Reusable HTTP client for speed
HTTPClient httpClient;

// Forward declarations
void updateOLED(String l1, String l2, String l3);
int drawMargin(String t, int x, int y);
uint8_t doEnroll(int id);
void sendEvent(String a, int s, String m, int c = 0);
void pollServer();
void toneShort(uint8_t p, int f, int d);
void unlock(int d);
void updateLock();
void updateHazard();
bool drawCam();
String getSDName(int id);
void bootAnimation();
uint8_t identifyFinger(uint16_t &id, uint16_t &conf);

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  Serial.begin(115200);
  pinMode(GREEN_LED, OUTPUT); pinMode(RED_LED, OUTPUT); pinMode(BUZZER, OUTPUT); pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(GREEN_LED, 0); digitalWrite(RED_LED, 0); digitalWrite(RELAY_PIN, 0);

  Wire.begin(21, 22);
  Wire.setClock(400000); // Fast I2C
  
  if (display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    oledReady = true;
    bootAnimation();
  }

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  WiFi.begin(ssid, password);
  int att = 0; 
  while (WiFi.status() != WL_CONNECTED) { 
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 10);
    display.print("WiFi Connecting...");
    display.drawRect(10, 30, 108, 10, WHITE);
    display.fillRect(12, 32, (att % 22) * 5, 6, WHITE);
    display.display();
    delay(500); 
    att++; 
    if (att > 60) ESP.restart(); // Restart if no connection after 30s
  }
  
  mySerial.begin(57600, SERIAL_8N1, 25, 26); delay(500); 
  if (finger.verifyPassword()) sensorReady = true;
  else { 
    mySerial.begin(115200, SERIAL_8N1, 25, 26); delay(500); 
    if (finger.verifyPassword()) sensorReady = true; 
  }
  
  if (sensorReady) {
    toneShort(BUZZER, 1000, 200);
    finger.getParameters(); 
  }
  lastAction = millis();
  httpClient.setReuse(true);
}

void bootAnimation() {
  display.clearDisplay();
  for (int i = 0; i < 64; i += 4) {
    display.drawRect(64 - i, 32 - i / 2, i * 2, i, WHITE);
    display.display();
    delay(20);
  }
  delay(200);
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(20, 25);
  display.print("E2C HUB");
  display.display();
  toneShort(BUZZER, 800, 100);
  toneShort(BUZZER, 1200, 150);
  delay(1000);
}

void drawSS() {
  static unsigned long lastSS = 0;
  if (millis() - lastSS < 50) return; 
  lastSS = millis();
  
  display.clearDisplay(); display.setTextSize(2); display.setTextColor(WHITE);
  display.setCursor(ssX, ssY); display.print("E2C");
  ssX += ssDX; ssY += ssDY;
  if (ssX <= 0 || ssX >= 92) ssDX = -ssDX;
  if (ssY <= 0 || ssY >= 48) ssDY = -ssDY;
  for(int i=0; i<4; i++) display.drawPixel(random(128), random(64), WHITE);
  display.display();
}

void loop() {
  unsigned long now = millis();
  bool action = false;

  updateLock();
  updateHazard();

  if (now - lastPoll >= pollInterval) {
    lastPoll = now;
    if (WiFi.status() == WL_CONNECTED) pollServer();
  }

  // 1. Enrollment Priority
  if (sensorReady && enrollSlot > 0) {
    action = true; lastAction = now; ssActive = false;
    doEnroll(enrollSlot);
    enrollSlot = 0; 
    return;
  }

  // 2. Camera Preview / Recognition
  if (previewActive) {
    action = true; lastAction = now; ssActive = false;
    if (now - lastCamFetch >= camInterval) {
      lastCamFetch = now;
      if (!drawCam()) {
        updateOLED("CAMERA ACTIVE", "Initializing...", "Please wait");
      }
    }
  }

  // 3. Fingerprint Recognition (Only if not in preview and no action yet)
  if (!action && sensorReady && !previewActive) {
    static uint16_t lastIdentify = 0;
    if (now - lastIdentify > 100) { 
      lastIdentify = now;
      uint16_t id = 0, conf = 0;
      uint8_t p = identifyFinger(id, conf);
      
      if (p == FINGERPRINT_OK) {
        action = true; lastAction = now; ssActive = false;
        digitalWrite(GREEN_LED, 1); toneShort(BUZZER, 1000, 150);
        String name = getSDName(id);
        updateOLED("ACCESS GRANTED", name, "ID: " + String(id));
        unlock(5); sendEvent("match", id, "Success", conf);
        delay(2000); digitalWrite(GREEN_LED, 0);
      } else if (p == FINGERPRINT_NOTFOUND) {
        action = true; lastAction = now; ssActive = false;
        digitalWrite(RED_LED, 1); toneShort(BUZZER, 400, 800);
        updateOLED("ACCESS DENIED", "Unknown User", "Try again");
        sendEvent("match", 0, "Denied", 0);
        delay(1500); digitalWrite(RED_LED, 0);
      } else if (p != FINGERPRINT_NOFINGER) {
        // Detailed error reporting with HEX code for debugging
        action = true; lastAction = now; ssActive = false;
        digitalWrite(RED_LED, 1); toneShort(BUZZER, 200, 100);
        
        String errDesc = "Bad scan";
        if (p == FINGERPRINT_IMAGEMESS) errDesc = "Image messy";
        else if (p == FINGERPRINT_PACKETRECIEVEERR) errDesc = "Comm error";
        else if (p == FINGERPRINT_IMAGEFAIL) errDesc = "Imaging error";
        else if (p == FINGERPRINT_FEATUREFAIL) errDesc = "Feature fail";
        else if (p == FINGERPRINT_INVALIDIMAGE) errDesc = "Invalid image";
        else if (p == FINGERPRINT_TIMEOUT) errDesc = "Timeout";
        
        Serial.print("[Fingerprint] Error: "); Serial.print(errDesc); 
        Serial.print(" (0x"); Serial.print(p, HEX); Serial.println(")");
        
        // Show hex code on OLED and lock it for 3 seconds
        updateOLED("READ ERROR", errDesc, "Code: 0x" + String(p, HEX));
        sendEvent("error", 0, "FP_READ_ERROR: " + errDesc + " (0x" + String(p, HEX) + ")", p);
        delay(3000); // Lock display for 3 seconds so user can read it
        digitalWrite(RED_LED, 0);
        lastAction = millis(); // Refresh last action to prevent immediate screensaver
      }
    }
  }

  // 4. Screensaver / Idle
  if (!action) {
    if (now - lastAction > 15000) { 
      ssActive = true; drawSS();
    } else if (isLocked) {
      static unsigned long lastU = 0;
      if (now - lastU > 500) { lastU = now; updateOLED(o1, o2, o3); }
    }
  }
  delay(1);
}

void pollServer() {
  httpClient.begin(pollUrl + "?sensor_ready=" + String(sensorReady ? "1" : "0"));
  int code = httpClient.GET();
  if (code == 200) {
    JsonDocument d;
    if (!deserializeJson(d, httpClient.getString())) {
      String l1 = d["oled_line1"] | "";
      if (l1.length() > 0) { o1 = l1; o2 = d["oled_line2"].as<String>(); o3 = d["oled_line3"].as<String>(); }
      int en = d["enroll_slot"] | 0;
      if (en > 0) { enrollSlot = en; lastAction = millis(); ssActive = false; }
      bool pa = d["preview_active"] | false;
      if (pa) { previewActive = true; lastAction = millis(); ssActive = false; } else { previewActive = false; }
      hazardOn = d["hazard"] | false;
      int un = d["unlock_duration"] | 0; if (un > 0) unlock(un);
      const char* ip = d["esp32_cam_ip"]; if (ip) ESP32_CAM_IP = String(ip);
      bool resetDB = d["empty_sensor_db"] | false;
      if (resetDB && sensorReady) {
        if (finger.emptyDatabase() == FINGERPRINT_OK) {
          updateOLED("DATABASE WIPED", "All prints", "deleted");
          toneShort(BUZZER, 500, 1000);
          sendEvent("system", 0, "DB_WIPED");
          delay(2000);
        }
      }
    }
  } else { previewActive = false; }
}

bool drawCam() {
  httpClient.begin("http://" + SERVER_IP + ":5000/api/controller/live_face");
  int code = httpClient.GET();

  if (code == 200 && httpClient.getSize() == 1024) {
    uint8_t b[1024];
    WiFiClient* s = httpClient.getStreamPtr();

    int r = 0;
    unsigned long start = millis();
    while (r < 1024 && (millis() - start < 500)) { 
      if (s->available()) b[r++] = s->read();
    }

    if (r == 1024) {
      display.clearDisplay();
      display.drawBitmap(0, 0, b, 128, 64, WHITE);
      display.fillRect(0, 0, 52, 9, BLACK);
      display.setCursor(2, 1);
      display.setTextColor(WHITE);
      display.setTextSize(1);
      display.print("LIVE CAM");
      display.display();
      return true;
    }
  }
  return false;
}

void updateOLED(String l1, String l2, String l3) {
  if (!oledReady || ssActive) return;
  display.clearDisplay(); display.setTextSize(1); display.setTextColor(WHITE);
  display.drawRect(0, 0, 128, 64, WHITE);
  display.setCursor(6, 4); display.print(isLocked ? "[SECURE] E2C" : "[UNLOCK] E2C");
  display.drawLine(4, 13, 124, 13, WHITE); display.drawLine(36, 17, 36, 60, WHITE);
  if (l1 == "DOOR LOCKED" || l1 == "SYSTEM IDLE") {
    display.drawRect(6, 22, 24, 26, WHITE); display.drawCircle(18, 30, 6, WHITE); display.drawLine(18, 36, 18, 42, WHITE);
    display.fillRoundRect(40, 18, 66, 11, 2, WHITE); display.setTextColor(BLACK); display.setCursor(43, 20); display.print("STATION");
    display.setTextColor(WHITE); drawMargin("READY", 40, 33); drawMargin("Scan to start", 40, 46);
  } else { drawMargin(l1, 40, 18); drawMargin(l2, 40, 32); drawMargin(l3, 40, 48); }
  display.display();
}

int drawMargin(String t, int x, int y) {
  display.setCursor(x, y); int cpL = (128 - x) / 6;
  if (t.length() <= cpL) { display.print(t); return y + 10; }
  else { display.print(t.substring(0, cpL)); display.setCursor(x, y + 9); display.print(t.substring(cpL, cpL * 2)); return y + 19; }
}

String getSDName(int id) {
  if (ESP32_CAM_IP == "0.0.0.0") return "ID:" + String(id);
  
  HTTPClient h; h.begin("http://" + ESP32_CAM_IP + ":81/sd/read?path=/students.json");
  h.setTimeout(2000);
  if (h.GET() == 200) {
    JsonDocument d;
    if (!deserializeJson(d, h.getString())) {
      JsonArray arr = d.as<JsonArray>();
      for (JsonObject o : arr) {
        int s = o["slot"] | o["fp_id"] | 0;
        if (s == id) {
          const char* name = o["name"];
          return name ? String(name) : "ID:" + String(id);
        }
      }
    }
  }
  return "ID:" + String(id);
}

void sendEvent(String a, int s, String m, int c) {
  HTTPClient h; h.begin(eventUrl); h.addHeader("Content-Type", "application/json");
  h.setTimeout(3000);
  JsonDocument d; d["action"]=a; d["slot"]=s; d["status"]=m; d["confidence"]=c;
  String j; serializeJson(d, j); h.POST(j); h.end();
}

void toneShort(uint8_t p, int f, int d) {
  unsigned long s = millis(); while (millis()-s < d) { digitalWrite(p,1); delayMicroseconds(500000/f); digitalWrite(p,0); delayMicroseconds(500000/f); }
}

void unlock(int d) { isLocked = false; lockTime = millis()+(d*1000); digitalWrite(RELAY_PIN, 1); }
void updateLock() { if (!isLocked && millis()>=lockTime) { isLocked=true; digitalWrite(RELAY_PIN, 0); o1="SYSTEM IDLE"; } }
void updateHazard() {
  if (!hazardOn) { digitalWrite(GREEN_LED,0); digitalWrite(RED_LED,0); hzStep=-1; return; }
  static unsigned long l; if (millis()-l>=100) { l=millis(); hzStep=(hzStep+1)%4; digitalWrite(GREEN_LED,hzStep==0); digitalWrite(RED_LED,hzStep==2); }
}

uint8_t identifyFinger(uint16_t &id, uint16_t &conf) {
  uint8_t p = finger.getImage();
  if (p == FINGERPRINT_NOFINGER) return p;
  
  // Finger detected! 
  unsigned long start = millis();
  while (millis() - start < 2000) {
    p = finger.getImage();
    if (p == FINGERPRINT_OK) {
      delay(100); // Settle
      p = finger.image2Tz(1);
      if (p == FINGERPRINT_OK) break; // Success!
      
      if (p == 0x07) {
        updateOLED("SCANNING", "Center finger", "Keep still");
        Serial.println("[Fingerprint] Feature fail (0x07), retrying capture...");
      }
    }
    if (p == FINGERPRINT_NOFINGER) return p;
    delay(100);
  }
  
  if (p != FINGERPRINT_OK) return p;
  
  p = finger.fingerFastSearch();
  if (p == FINGERPRINT_OK) {
    id = finger.fingerID;
    conf = finger.confidence;
  }
  return p;
}

uint8_t doEnroll(int id) {
  updateOLED("ENROLL MODE", "Place finger", "Slot #" + String(id));
  uint8_t p = FINGERPRINT_NOFINGER;
  unsigned long start = millis();
  
  // 1. Capture first scan with retry for 0x07
  while (millis() - start < 15000) {
    p = finger.getImage();
    if (p == FINGERPRINT_OK) {
      p = finger.image2Tz(1);
      if (p == FINGERPRINT_OK) break;
      if (p == 0x07) updateOLED("ENROLLING", "Center finger", "Try again");
    }
    delay(100);
  }
  
  if (p != FINGERPRINT_OK) {
    sendEvent("enroll_fail", id, "Tz1 Error", p);
    updateOLED("READ ERROR", "Bad scan", "Code: 0x" + String(p, HEX));
    delay(3000); return 0xFF;
  }
  
  updateOLED("ENROLL MODE", "Remove finger", "");
  toneShort(BUZZER, 1200, 100);
  delay(1000); while (finger.getImage() != FINGERPRINT_NOFINGER) delay(50);
  
  updateOLED("ENROLL MODE", "Place same", "finger again");
  start = millis();
  
  // 2. Capture second scan with retry for 0x07
  while (millis() - start < 15000) {
    p = finger.getImage();
    if (p == FINGERPRINT_OK) {
      p = finger.image2Tz(2);
      if (p == FINGERPRINT_OK) break;
      if (p == 0x07) updateOLED("ENROLLING", "Center finger", "Try again");
    }
    delay(100);
  }
  
  if (p != FINGERPRINT_OK) {
    sendEvent("enroll_fail", id, "Tz2 Error", p);
    updateOLED("READ ERROR", "Bad scan", "Code: 0x" + String(p, HEX));
    delay(3000); return 0xFF;
  }
  
  p = finger.createModel();
  if (p != FINGERPRINT_OK) {
    String msg = (p == FINGERPRINT_ENROLLMISMATCH) ? "Prints mismatch" : "Model error";
    updateOLED("ENROLL FAIL", msg, "Retry");
    sendEvent("enroll_fail", id, msg, p);
    delay(2000); return 0xFF;
  }
  
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
    updateOLED("SUCCESS", "Enrolled", "Slot #" + String(id));
    sendEvent("enroll_success", id, "Stored"); toneShort(BUZZER, 1500, 300);
    delay(2000); return FINGERPRINT_OK;
  }
  
  updateOLED("FAILED", "Store error", ""); 
  sendEvent("enroll_fail", id, "Store error", p);
  delay(1500); return 0xFF;
}
