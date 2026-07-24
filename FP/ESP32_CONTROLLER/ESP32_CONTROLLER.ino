#include <WiFi.h>
#include <esp_wifi.h>

const char* base_ssid = "Akhil ";
 
	//To get more codes @lenlu_arun
const char suffixes[] = {
  '1','2','3','4','5','6','7','8','9','0',
  '@','#','$','%','&','-','+','(',')','/',
  '*','"','\'',':',';','!','?',
  'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
  'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
  '[',']','{','}','<','>','_','=','|','~','^','.',',','`',' ','\\','?','x','o','v','c','n','m','p','q','r','s','t','y','z'
};

const int total_ssids = sizeof(suffixes) / sizeof(suffixes[0]);
	//To get more codes @lenlu_arun
uint8_t beacon_packet[128] = {
  0x80, 0x00, 0x00, 0x00,             // Frame Control
  0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, // Destination
  0x01, 0x02, 0x03, 0x04, 0x05, 0x06, // Source MAC
  0x01, 0x02, 0x03, 0x04, 0x05, 0x06, // BSSID
  0x00, 0x00,                         // Sequence
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // Timestamp
  0x64, 0x00,                         // Beacon Interval
  0x31, 0x04,                         // Capability
  0x00, 0x00                          // SSID Tag (length will be updated)
};
	//To get more codes @lenlu_arun
void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_MODE_AP);
  esp_wifi_set_promiscuous(true);
  esp_wifi_start();

  Serial.println("\n🚀 Multi-SSID Beacon Spammer Started!");
  Serial.printf("Broadcasting %d fake networks...\n", total_ssids);
}
	//To get more codes @lenlu_arun
void loop() {
  for (int i = 0; i < total_ssids; i++) {
    char current_ssid[32];
    snprintf(current_ssid, sizeof(current_ssid), "%s%c", base_ssid, suffixes[i]);
    int ssid_len = strlen(current_ssid);

    // Update SSID length
    beacon_packet[37] = ssid_len;

    // Copy SSID name
    memcpy(&beacon_packet[38], current_ssid, ssid_len);

    // Unique MAC per SSID
    beacon_packet[10] = 0xDE;
    beacon_packet[11] = 0xAD;
    beacon_packet[12] = 0xBE;
    beacon_packet[13] = 0xEF;
    beacon_packet[14] = 0x00;
    beacon_packet[15] = i;
	//To get more codes @lenlu_arun
    beacon_packet[16] = beacon_packet[10];
    beacon_packet[17] = beacon_packet[11];
    beacon_packet[18] = beacon_packet[12];
    beacon_packet[19] = beacon_packet[13];
    beacon_packet[20] = beacon_packet[14];
    beacon_packet[21] = beacon_packet[15];

    int pos = 38 + ssid_len;

    // Supported Rates
    beacon_packet[pos++] = 0x01; beacon_packet[pos++] = 0x08;
    beacon_packet[pos++] = 0x82; beacon_packet[pos++] = 0x84; beacon_packet[pos++] = 0x8B;
    beacon_packet[pos++] = 0x96; beacon_packet[pos++] = 0x24; beacon_packet[pos++] = 0x30;
    beacon_packet[pos++] = 0x48; beacon_packet[pos++] = 0x6C;

    // Channel
    beacon_packet[pos++] = 0x03; beacon_packet[pos++] = 0x01; beacon_packet[pos++] = 0x01;
	//To get more codes @lenlu_arun
    // Send beacon
    esp_wifi_80211_tx(WIFI_IF_AP, beacon_packet, pos, true);

    delayMicroseconds(400);
  }
  delay(1);  // Small delay between full cycles
}