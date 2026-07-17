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
const char* ssid = "NIAT_TAKEOVER_2026";
const char* password = "Takeover@2026";

// ─── Server Configuration ───
const String SERVER_IP = "10.10.17.49:5000";
const int SERVER_PORT = 5000;
String ESP32_CAM_IP = "0.0.0.0";
const String pollUrl = "http://" + SERVER_IP + ":5000/api/controller/poll";
const String eventUrl = "http://" + SERVER_IP + ":5000/api/controller/event";

// ─── Pin Definitions ───
#define GREEN_LED 14
#define RED_LED   15
#define BUZZER    2
#define RELAY_PIN 4

// ─── Push Button Pins (4 Buttons) ───
#define BTN_PREVIEW   13  // Button 1: Toggle live camera preview on OLED
#define BTN_STATS     27  // Button 2: Show stored data / stats on OLED
#define BTN_DOWNLOAD  32  // Button 3: Download PDF report on website
#define BTN_RECOG     12  // Button 4: Start Face Recognition

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

// ─── Button Configuration & Debounce ───
const int buttonPins[4] = {BTN_PREVIEW, BTN_STATS, BTN_DOWNLOAD, BTN_RECOG};
unsigned long lastBtnTime[4] = {0, 0, 0, 0};
const unsigned long debounceDelay = 250; // ms
unsigned long tempDisplayUntil = 0;      // Non-blocking timer to preserve status screens

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
void checkButtons();
void handleButtonPress(int btn);

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  Serial.begin(115200);
  pinMode(GREEN_LED, OUTPUT); pinMode(RED_LED, OUTPUT); pinMode(BUZZER, OUTPUT); pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(GREEN_LED, 0); digitalWrite(RED_LED, 0); digitalWrite(RELAY_PIN, 0);

  for (int i = 0; i < 4; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }

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
  checkButtons();

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
        String details = getSDName(id);
        String displayName = details;
        String displayId = "ID: " + String(id);
        int sepIndex = details.indexOf('|');
        if (sepIndex != -1) {
          displayName = details.substring(0, sepIndex);
          displayId = "ID: " + details.substring(sepIndex + 1);
        }
        updateOLED("ACCESS GRANTED", displayName, displayId);
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

  // 4. Screensaver / Idle (Screensaver disabled, ssActive remains false)
  if (!action) {
    if (isLocked) {
      static unsigned long lastU = 0;
      if (now - lastU > 500 && now >= tempDisplayUntil) { lastU = now; updateOLED(o1, o2, o3); }
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
  
  // 1. Draw Corner HUD brackets
  display.drawLine(0, 0, 8, 0, WHITE); display.drawLine(0, 0, 0, 8, WHITE);
  display.drawLine(127, 0, 119, 0, WHITE); display.drawLine(127, 0, 127, 8, WHITE);
  display.drawLine(0, 63, 8, 63, WHITE); display.drawLine(0, 63, 0, 55, WHITE);
  display.drawLine(127, 63, 119, 63, WHITE); display.drawLine(127, 63, 127, 55, WHITE);
  
  // 2. Draw Sleek Top Bar
  display.fillRoundRect(22, 2, 84, 11, 2, WHITE);
  display.setTextColor(BLACK);
  display.setCursor(26, 4);
  display.print(isLocked ? "SECURED MODE" : "UNLOCKED MODE");
  display.setTextColor(WHITE);
  
  // 3. Draw Wi-Fi indicator
  display.fillRect(114, 10, 2, 2, WHITE);
  display.fillRect(118, 8, 2, 4, WHITE);
  display.fillRect(122, 6, 2, 6, WHITE);

  // 4. Draw Divider line
  display.drawLine(4, 15, 124, 15, WHITE); 
  display.drawLine(34, 18, 34, 60, WHITE);
  
  // 5. Draw Left Side Graphic
  if (l1 == "DOOR LOCKED" || l1 == "SYSTEM IDLE" || l1 == "SYSTEM READY") {
    // Padlock body
    display.fillRoundRect(8, 32, 20, 20, 2, WHITE);
    if (isLocked) {
      // Padlock shackle (closed)
      display.drawCircle(18, 32, 6, WHITE);
      display.fillRect(12, 32, 13, 6, BLACK);
    } else {
      // Padlock shackle (open)
      display.drawCircle(13, 26, 6, WHITE);
      display.fillRect(13, 26, 7, 7, BLACK);
    }
    // Keyhole
    display.fillCircle(18, 40, 2, BLACK);
    display.drawLine(18, 42, 18, 48, BLACK);

    // Right Side Info
    display.fillRoundRect(38, 18, 86, 11, 2, WHITE); 
    display.setTextColor(BLACK); 
    display.setCursor(42, 20); 
    display.print("E2C ACTIVE");
    display.setTextColor(WHITE);
    drawMargin("Scan Bio", 38, 34);
    drawMargin("System Ready", 38, 48);
  } else {
    // Draw animated scanner box
    display.drawRect(8, 24, 20, 28, WHITE);
    display.drawCircle(18, 38, 4, WHITE);
    display.drawCircle(18, 38, 8, WHITE);
    int lineY = 26 + ((millis() / 150) % 24);
    display.drawLine(9, lineY, 26, lineY, WHITE);
    
    // Right Side Info
    drawMargin(l1, 38, 18); 
    drawMargin(l2, 38, 32); 
    drawMargin(l3, 38, 48); 
  }
  
  display.display();
}

int drawMargin(String t, int x, int y) {
  display.setCursor(x, y); int cpL = (128 - x) / 6;
  if (t.length() <= cpL) { display.print(t); return y + 10; }
  else { display.print(t.substring(0, cpL)); display.setCursor(x, y + 9); display.print(t.substring(cpL, cpL * 2)); return y + 19; }
}

String getSDName(int id) {
  // 1. Try querying Python server directly first (contains latest DB)
  HTTPClient h; 
  h.begin("http://" + SERVER_IP + ":5000/api/controller/student_details?slot=" + String(id));
  h.setTimeout(2000);
  int code = h.GET();
  if (code == 200) {
    JsonDocument d;
    if (!deserializeJson(d, h.getString())) {
      const char* name = d["name"];
      const char* studId = d["id"];
      if (name && studId) {
        h.end();
        return String(name) + "|" + String(studId);
      }
    }
  }
  h.end();

  // 2. Fallback to ESP32-CAM if server is not accessible
  if (ESP32_CAM_IP != "0.0.0.0") {
    h.begin("http://" + ESP32_CAM_IP + ":81/sd/read?path=/students.json");
    h.setTimeout(2000);
    if (h.GET() == 200) {
      JsonDocument d;
      if (!deserializeJson(d, h.getString())) {
        JsonArray arr = d.as<JsonArray>();
        for (JsonObject o : arr) {
          int s = o["slot"] | o["fp_id"] | 0;
          if (s == id) {
            const char* name = o["name"];
            const char* studId = o["id"];
            h.end();
            if (name) {
              return String(name) + "|" + (studId ? String(studId) : String(id));
            }
          }
        }
      }
    }
    h.end();
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

void checkButtons() {
  unsigned long now = millis();
  for (int i = 0; i < 4; i++) {
    int state = digitalRead(buttonPins[i]);
    if (state == LOW) { // Active Low (button pressed pulls to GND)
      if (now - lastBtnTime[i] > debounceDelay) {
        lastBtnTime[i] = now;
        handleButtonPress(i + 1); // 1-indexed button number
      }
    }
  }
}

void handleButtonPress(int btn) {
  Serial.print("[Physical Button] pressed: "); Serial.println(btn);
  
  // Make a short feedback beep
  toneShort(BUZZER, 1200, 80);
  
  // Send the button press event to the server
  sendEvent("button_press", btn, "Pressed", 0);
  
  switch(btn) {
    case 1:
      // Cam Toggle Button
      previewActive = !previewActive;
      ssActive = false;
      lastAction = millis();
      updateOLED("CAMERA MODE", previewActive ? "Toggled ON" : "Toggled OFF", "Local control");
      tempDisplayUntil = millis() + 2500; // Keep message visible for 2.5s
      break;
      
    case 2:
      // OLED Stats Button
      // The server calculates stats and feeds them via polling.
      // We display a brief loading state immediately.
      ssActive = false;
      lastAction = millis();
      updateOLED("FETCHING STATS", "Accessing server...", "Please wait");
      tempDisplayUntil = millis() + 8000; // Let poll data display for 8 seconds
      break;
      
    case 3:
      // Download PDF Button
      // The server generates the PDF and sets the download trigger for web client.
      ssActive = false;
      lastAction = millis();
      updateOLED("DOWNLOADING PDF", "Triggering report", "on web client");
      tempDisplayUntil = millis() + 3000; // Keep message visible for 3s
      break;
      
    case 4:
      // Face Recognition Button
      ssActive = false;
      lastAction = millis();
      updateOLED("FACE RECOG", "Toggling...", "Face attendance");
      tempDisplayUntil = millis() + 3000; // Keep message visible for 3s
      break;
  }
}
