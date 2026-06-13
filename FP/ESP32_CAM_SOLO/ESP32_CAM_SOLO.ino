#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "esp_camera.h"
#include "esp_http_server.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "FS.h"
#include "SD_MMC.h"
#include <vector>

// ─── WiFi Configuration (UPDATE THESE FOR YOUR NETWORK) ───
const char* ssid = "Arunesh";
const char* password = "00000000";

// ─── Server Configuration (Computer IPv4: 10.83.201.98) ───
const String SERVER_IP = "10.83.201.98";  // Your Computer's IPv4 Address
const int SERVER_PORT = 5000;
const String cameraPollEndpoint = "http://" + SERVER_IP + ":5000/api/camera/poll";

// ─── Pin Definitions (ESP32-CAM) ───
#define FLASH_LED 4         // Camera flash

// ─── Camera Model Select ───
#define CAMERA_MODEL_AI_THINKER

#if defined(CAMERA_MODEL_AI_THINKER)
  #define PWDN_GPIO_NUM     32
  #define RESET_GPIO_NUM    -1
  #define XCLK_GPIO_NUM      0
  #define SIOD_GPIO_NUM     26
  #define SIOC_GPIO_NUM     27
  #define Y9_GPIO_NUM       35
  #define Y8_GPIO_NUM       34
  #define Y7_GPIO_NUM       39
  #define Y6_GPIO_NUM       36
  #define Y5_GPIO_NUM       21
  #define Y4_GPIO_NUM       19
  #define Y3_GPIO_NUM       18
  #define Y2_GPIO_NUM        5
  #define VSYNC_GPIO_NUM    25
  #define HREF_GPIO_NUM     23
  #define PCLK_GPIO_NUM     22
#endif

// ─── System State ───
bool cameraReady = false;
bool sdAvailable = false;
unsigned long lastCommandPollTime = 0;
const unsigned long pollInterval = 3000;  // Poll every 3 seconds

httpd_handle_t camera_httpd = NULL;

// Reusable HTTP client for speed
HTTPClient httpClient;

// Forward declarations
void initCamera();
void startCameraServer();
void fetchServerCommands();

void setup() {
  // Disable brownout detector early
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  Serial.begin(115200);
  delay(500);
  
  Serial.println("\n╔════════════════════════════════════════╗");
  Serial.println("║    E2C BiometricHub — Camera Server    ║");
  Serial.println("║         (ESP32-CAM Dedicated)          ║");
  Serial.println("╚════════════════════════════════════════╝\n");
  
  pinMode(FLASH_LED, OUTPUT);
  digitalWrite(FLASH_LED, LOW);
  
  // ─── Camera Initialization ───
  initCamera();

  // ─── WiFi Connection ───
  Serial.print("[WiFi] Connecting to: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempts++;
    if (attempts > 60) ESP.restart(); // Restart if no connection after 30s
  }
  
  // ─── SD Card Initialization (Retry logic for better stability) ───
  Serial.println("[SD] Mounting SD Card (1-bit mode)...");
  int sd_retries = 0;
  while (sd_retries < 3) {
    if (SD_MMC.begin("/sdcard", true)) {
      sdAvailable = true;
      Serial.println("[SD] ✅ SD Card mounted successfully!");
      
      uint8_t cardType = SD_MMC.cardType();
      if(cardType == CARD_NONE){
          Serial.println("[SD] ⚠️ No SD card attached but mount succeeded?");
          sdAvailable = false;
      } else {
          Serial.print("[SD] Card Type: ");
          if(cardType == CARD_MMC) Serial.println("MMC");
          else if(cardType == CARD_SD) Serial.println("SDSC");
          else if(cardType == CARD_SDHC) Serial.println("SDHC");
          else Serial.println("UNKNOWN");
          
          uint64_t cardSize = SD_MMC.cardSize() / (1024 * 1024);
          Serial.printf("[SD] Card Size: %lluMB\n", cardSize);
          break;
      }
    } else {
      sdAvailable = false;
      sd_retries++;
      Serial.printf("[SD] ❌ Mount failed (Attempt %d/3). Retrying in 1s...\n", sd_retries);
      delay(1000);
    }
  }

  if (!sdAvailable) {
    Serial.println("[SD] 🛑 CRITICAL: SD Card could not be mounted. Attendance logging to SD will be disabled.");
    Serial.println("[SD] Note: Ensure card is FAT32 formatted and fully inserted.");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] ✅ Connected successfully!");
    Serial.print("[WiFi] IP Address: ");
    Serial.println(WiFi.localIP());
    
    httpClient.setReuse(true);
    
    // Start camera stream server
    if (cameraReady) {
      startCameraServer();
    }
  } else {
    Serial.println("\n[WiFi] ❌ Failed to connect.");
  }
}

void loop() {
  // ─── Server Command Polling (Flash Control) ───
  if (millis() - lastCommandPollTime >= pollInterval) {
    lastCommandPollTime = millis();
    if (WiFi.status() == WL_CONNECTED) {
      fetchServerCommands();
    } else {
      Serial.println("[WiFi] Connection lost. Reconnecting...");
      WiFi.disconnect();
      WiFi.reconnect();
    }
  }
  delay(100);
}

void initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  #ifdef CAMERA_GRAB_LATEST
  config.grab_mode = CAMERA_GRAB_LATEST;
  #endif
  #ifdef CAMERA_FB_IN_PSRAM
  config.fb_location = CAMERA_FB_IN_PSRAM;
  #endif
  
  if(psramFound()){
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QVGA;  // Use QVGA (320x240) to fit in internal SRAM when PSRAM is absent
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[Camera] Camera init failed: 0x%x\n", err);
    cameraReady = false;
    return;
  }
  
  sensor_t * s = esp_camera_sensor_get();
  if (s) {
    s->set_brightness(s, 0);
    s->set_contrast(s, 0);
    s->set_saturation(s, 0);
  }

  cameraReady = true;
  Serial.println("[Camera] ✅ Camera initialized successfully!");
}

esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t * _jpg_buf = NULL;
  char * part_buf[64];

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=123456789000000000000987654321");
  if(res != ESP_OK){
    return res;
  }

  while(true){
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("[Camera] Capture failed");
      res = ESP_FAIL;
    } else {
      if(fb->format != PIXFORMAT_JPEG){
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if(!jpeg_converted){
          Serial.println("[Camera] JPEG conversion failed");
          res = ESP_FAIL;
        }
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }
    if(res == ESP_OK){
      size_t hlen = snprintf((char *)part_buf, 64, "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", _jpg_buf_len);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if(res == ESP_OK){
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if(res == ESP_OK){
      res = httpd_resp_send_chunk(req, "\r\n--123456789000000000000987654321\r\n", 36);
    }
    if(fb){
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if(_jpg_buf){
      free(_jpg_buf);
      _jpg_buf = NULL;
    }
    if(res != ESP_OK){
      break;
    }
    delay(50);
  }
  return res;
}

esp_err_t capture_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;

  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[Camera] Capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
  res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return res;
}

// ─────────────────────────────────────────────────────────────────
// SD CARD ENDPOINTS
// ─────────────────────────────────────────────────────────────────
String urlDecode(String str) {
  String decoded = "";
  char temp[] = "0x00";
  for (int i = 0; i < str.length(); i++) {
    if (str[i] == '%') {
      if (i + 2 < str.length()) {
        temp[2] = str[i + 1];
        temp[3] = str[i + 2];
        decoded += (char)strtol(temp, NULL, 16);
        i += 2;
      }
    } else if (str[i] == '+') {
      decoded += ' ';
    } else {
      decoded += str[i];
    }
  }
  return decoded;
}

esp_err_t sd_list_handler(httpd_req_t *req) {
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  if (!sdAvailable) {
    httpd_resp_set_type(req, "application/json");
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "{\"error\": \"SD Card not mounted\"}");
    return ESP_FAIL;
  }
  
  File root = SD_MMC.open("/");
  if (!root || !root.isDirectory()) {
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Failed to open root");
    return ESP_FAIL;
  }

  DynamicJsonDocument doc(4096);
  JsonArray arr = doc.to<JsonArray>();
  
  File file = root.openNextFile();
  while (file) {
    JsonObject obj = arr.createNestedObject();
    obj["name"] = String(file.name());
    obj["size"] = file.size();
    obj["dir"] = file.isDirectory();
    file = root.openNextFile();
  }
  
  String response;
  serializeJson(doc, response);
  httpd_resp_set_type(req, "application/json");
  httpd_resp_send(req, response.c_str(), response.length());
  return ESP_OK;
}

esp_err_t sd_read_handler(httpd_req_t *req) {
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  if (!sdAvailable) {
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "SD Card not mounted");
    return ESP_FAIL;
  }
  
  char buf[256];
  if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) != ESP_OK) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Missing query string");
    return ESP_FAIL;
  }
  
  char filepath[128] = {0};
  if (httpd_query_key_value(buf, "path", filepath, sizeof(filepath)) != ESP_OK) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Missing 'path' parameter");
    return ESP_FAIL;
  }
  
  String path = urlDecode(String(filepath));
  if (!path.startsWith("/")) {
    path = "/" + path;
  }
  
  File file = SD_MMC.open(path, FILE_READ);
  if (!file) {
    httpd_resp_send_err(req, HTTPD_404_NOT_FOUND, "File not found");
    return ESP_FAIL;
  }
  
  if (path.endsWith(".json")) {
    httpd_resp_set_type(req, "application/json");
  } else if (path.endsWith(".csv")) {
    httpd_resp_set_type(req, "text/csv");
  } else if (path.endsWith(".txt") || path.endsWith(".log")) {
    httpd_resp_set_type(req, "text/plain");
  } else if (path.endsWith(".jpg")) {
    httpd_resp_set_type(req, "image/jpeg");
  } else {
    httpd_resp_set_type(req, "application/octet-stream");
  }
  
  char chunk[512];
  int readBytes = 0;
  while ((readBytes = file.read((uint8_t*)chunk, sizeof(chunk))) > 0) {
    if (httpd_resp_send_chunk(req, chunk, readBytes) != ESP_OK) {
      file.close();
      return ESP_FAIL;
    }
  }
  httpd_resp_send_chunk(req, NULL, 0);
  file.close();
  return ESP_OK;
}

esp_err_t sd_save_handler(httpd_req_t *req) {
  if (!sdAvailable) {
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "SD Card not mounted");
    return ESP_FAIL;
  }
  
  char query[256];
  if (httpd_req_get_url_query_str(req, query, sizeof(query)) != ESP_OK) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Missing query string");
    return ESP_FAIL;
  }
  
  char filepath[128] = {0};
  if (httpd_query_key_value(query, "path", filepath, sizeof(filepath)) != ESP_OK) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Missing 'path' parameter");
    return ESP_FAIL;
  }
  
  String path = urlDecode(String(filepath));
  if (!path.startsWith("/")) {
    path = "/" + path;
  }
  
  // Ensure parent directories exist
  int lastSlash = path.lastIndexOf('/');
  if (lastSlash > 0) {
    String dir = path.substring(0, lastSlash);
    if (!SD_MMC.exists(dir)) {
      // Simple recursive mkdir
      String currentDir = "";
      int start = 0;
      int end = dir.indexOf('/', start + 1);
      while (end != -1) {
        currentDir = dir.substring(0, end);
        if (!SD_MMC.exists(currentDir)) {
          SD_MMC.mkdir(currentDir);
        }
        start = end;
        end = dir.indexOf('/', start + 1);
      }
      if (!SD_MMC.exists(dir)) {
        SD_MMC.mkdir(dir);
      }
    }
  }

  char appendVal[16] = {0};
  bool appendMode = false;
  if (httpd_query_key_value(query, "append", appendVal, sizeof(appendVal)) == ESP_OK) {
    if (strcmp(appendVal, "1") == 0) {
      appendMode = true;
    }
  }

  File file = SD_MMC.open(path, appendMode ? FILE_APPEND : FILE_WRITE);
  if (!file) {
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Failed to open file for writing");
    return ESP_FAIL;
  }
  
  char buf[512];
  int ret = 0;
  int remaining = req->content_len;
  
  while (remaining > 0) {
    int toRead = remaining < sizeof(buf) ? remaining : sizeof(buf);
    if ((ret = httpd_req_recv(req, buf, toRead)) <= 0) {
      if (ret == HTTPD_SOCK_ERR_TIMEOUT) {
        continue;
      }
      file.close();
      httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Socket error");
      return ESP_FAIL;
    }
    file.write((uint8_t*)buf, ret);
    remaining -= ret;
  }
  
  file.close();
  httpd_resp_send(req, "{\"status\":\"success\"}", 20);
  return ESP_OK;
}

esp_err_t sd_delete_handler(httpd_req_t *req) {
  if (!sdAvailable) {
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "SD Card not mounted");
    return ESP_FAIL;
  }
  
  char query[256];
  if (httpd_req_get_url_query_str(req, query, sizeof(query)) != ESP_OK) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Missing query string");
    return ESP_FAIL;
  }
  
  char filepath[128] = {0};
  if (httpd_query_key_value(query, "path", filepath, sizeof(filepath)) != ESP_OK) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Missing 'path' parameter");
    return ESP_FAIL;
  }
  
  String path = urlDecode(String(filepath));
  if (!path.startsWith("/")) {
    path = "/" + path;
  }
  
  if (SD_MMC.exists(path)) {
    if (SD_MMC.remove(path)) {
      httpd_resp_send(req, "{\"status\":\"success\"}", 20);
      return ESP_OK;
    } else {
      httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Failed to delete file");
      return ESP_FAIL;
    }
  } else {
    httpd_resp_send_err(req, HTTPD_404_NOT_FOUND, "File not found");
    return ESP_FAIL;
  }
}

void wipeDirectory(String path) {
  File root = SD_MMC.open(path);
  if (!root || !root.isDirectory()) return;
  
  std::vector<String> filesToDelete;
  std::vector<String> dirsToDelete;
  
  File file = root.openNextFile();
  while (file) {
    String name = String(file.name());
    
    // Skip system folders/files that cannot be deleted
    if (name.indexOf("System Volume Information") == -1 && name != "." && name != "..") {
      String fullPath = path;
      if (!fullPath.endsWith("/")) fullPath += "/";
      if (name.startsWith("/")) {
        fullPath = name;
      } else {
        fullPath += name;
      }
      
      if (file.isDirectory()) {
        dirsToDelete.push_back(fullPath);
      } else {
        filesToDelete.push_back(fullPath);
      }
    }
    file.close();
    file = root.openNextFile();
  }
  root.close();
  
  // 1. Delete all files collected in this directory
  for (size_t i = 0; i < filesToDelete.size(); i++) {
    SD_MMC.remove(filesToDelete[i].c_str());
  }
  
  // 2. Recursively wipe and delete subdirectories collected
  for (size_t i = 0; i < dirsToDelete.size(); i++) {
    wipeDirectory(dirsToDelete[i]);
    SD_MMC.rmdir(dirsToDelete[i].c_str());
  }
}

esp_err_t sd_format_handler(httpd_req_t *req) {
  if (!sdAvailable) {
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "SD Card not mounted");
    return ESP_FAIL;
  }
  
  Serial.println("[SD] Formatting/wiping SD card...");
  wipeDirectory("/");
  Serial.println("[SD] ✅ SD card wiped successfully!");
  httpd_resp_send(req, "{\"status\":\"success\"}", 20);
  return ESP_OK;
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 81;
  config.ctrl_port = 32769;
 
  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };
 
  httpd_uri_t capture_uri = {
    .uri       = "/capture",
    .method    = HTTP_GET,
    .handler   = capture_handler,
    .user_ctx  = NULL
  };
 
  httpd_uri_t sd_list_uri = {
    .uri       = "/sd/list",
    .method    = HTTP_GET,
    .handler   = sd_list_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t sd_read_uri = {
    .uri       = "/sd/read",
    .method    = HTTP_GET,
    .handler   = sd_read_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t sd_save_uri = {
    .uri       = "/sd/save",
    .method    = HTTP_POST,
    .handler   = sd_save_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t sd_delete_uri = {
    .uri       = "/sd/delete",
    .method    = HTTP_POST,
    .handler   = sd_delete_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t sd_format_uri = {
    .uri       = "/sd/format",
    .method    = HTTP_POST,
    .handler   = sd_format_handler,
    .user_ctx  = NULL
  };

  if (httpd_start(&camera_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &stream_uri);
    httpd_register_uri_handler(camera_httpd, &capture_uri);
    httpd_register_uri_handler(camera_httpd, &sd_list_uri);
    httpd_register_uri_handler(camera_httpd, &sd_read_uri);
    httpd_register_uri_handler(camera_httpd, &sd_save_uri);
    httpd_register_uri_handler(camera_httpd, &sd_delete_uri);
    httpd_register_uri_handler(camera_httpd, &sd_format_uri);
    Serial.println("[Camera] Server started on port 81");
  } else {
    Serial.println("[Camera] Failed to start server");
  }
}

void fetchServerCommands() {
  String url = cameraPollEndpoint + "?camera_ready=" + String(cameraReady ? "1" : "0") + "&sd_ready=" + String(sdAvailable ? "1" : "0");
  httpClient.begin(url);
  
  int httpResponseCode = httpClient.GET();
  if (httpResponseCode == 200) {
    String responseBody = httpClient.getString();
    StaticJsonDocument<128> doc;
    DeserializationError error = deserializeJson(doc, responseBody);
    if (!error) {
      bool flashOn = doc["flash"] | false;
      digitalWrite(FLASH_LED, flashOn ? HIGH : LOW);
    }
  }
}
