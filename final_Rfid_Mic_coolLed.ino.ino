#include <SPI.h>
#include <MFRC522.h>
#include <Adafruit_NeoPixel.h>

#define SS_PIN 10          // RFID Slave Select pin
#define RST_PIN 7          // RFID Reset pin
#define LED_PIN_MATRIX 3   // LED matrix data pin
#define NUM_LEDS 64        // Total LEDs in 8x8 matrix (8*8)
#define LED_PIN_MIC 4      // LED pin for microphone match indication
#define NUM_READINGS 35    // Number of measurements to average for microphone

MFRC522 rfid(SS_PIN, RST_PIN); // Create instance of the RFID library
Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN_MATRIX, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(9600);         // Initialize serial communication
  SPI.begin();                // Initialize SPI bus
  rfid.PCD_Init();            // Initialize the RFID reader
  strip.begin();              // Initialize the LED matrix
  strip.setBrightness(50);    // Set brightness
  strip.show();               // Initialize all pixels to 'off'
  
  pinMode(LED_PIN_MIC, OUTPUT);   // Set microphone LED pin as output
  digitalWrite(LED_PIN_MIC, LOW); // Ensure microphone LED is off initially
}

void loop() {
  // **RFID Check and UID Transmission**
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    // No new card detected, proceed to other tasks
  } else {
    // Send the UID of the detected card to Python
    for (byte i = 0; i < rfid.uid.size; i++) {
      Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
      Serial.print(rfid.uid.uidByte[i], HEX);
    }
    Serial.println(); // End UID transmission with a newline
    rfid.PICC_HaltA();  // Halt communication with the card
    delay(1000); // Short delay before checking again
  }

  // **Microphone Data Reading and Average Calculation**
  int sensorValue = 0;   // Variable to store averaged sensor value
  long total = 0;        // Variable to store the sum of readings

  for (int i = 0; i < NUM_READINGS; i++) {
    total += analogRead(A0); // Read from microphone sensor on A0
    delay(3);                // Short delay between readings
  }
  sensorValue = total / NUM_READINGS;  // Calculate average reading
  Serial.println(sensorValue);          // Send average to Python

  // **LED Matrix Control Commands from Python**
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'H') {            // Display happy face on the matrix
      displayHappyFace(0x00FF00);    // Green happy face
    } else if (command == 'S') {     // Display sad face on the matrix
      displaySadFace(0xFF0000);      // Red sad face
    } else if (command == '1') {     // '1' to turn on the microphone match LED
      digitalWrite(LED_PIN_MIC, HIGH);
      delay(5000);                   // Keep microphone match LED on for 5 seconds
      digitalWrite(LED_PIN_MIC, LOW);
    }
  }

  delay(300); // Adjust delay as needed before next loop iteration
}

// **Function to Display Happy Face**
void displayHappyFace(uint32_t color) {
  int happyFacePattern[8][8] = {
     {0, 0, 0, 0, 0, 0, 0, 0},
     {0, 0, 1, 1, 0, 1, 1, 0},
     {0, 0, 1, 1, 0, 1, 1, 0},
     {0, 0, 0, 0, 0, 0, 0, 0},
     {1, 0, 0, 0, 0, 0, 0, 1},
     {0, 1, 0, 0, 0, 0, 1, 0},
     {0, 0, 1, 1, 1, 1, 0, 0},
     {0, 0, 0, 0, 0, 0, 0, 0}
  };
  drawPattern(happyFacePattern, color);
}

// **Function to Display Sad Face**
void displaySadFace(uint32_t color) {
  int sadFacePattern[8][8] = {
     {0, 0, 0, 0, 0, 0, 0, 0},
     {0, 0, 1, 1, 0, 1, 1, 0},
     {0, 0, 1, 1, 0, 1, 1, 0},
     {0, 0, 0, 0, 0, 0, 0, 0},
     {0, 0, 0, 0, 0, 0, 0, 0},
     {1, 1, 1, 1, 1, 1, 1, 0},
     {1, 0, 0, 0, 0, 0, 1, 0},
     {1, 0, 0, 0, 0, 0, 1, 0}
  };
  drawPattern(sadFacePattern, color);
}

// **Function to Draw Pattern on LED Matrix**
void drawPattern(int pattern[8][8], uint32_t color) {
  for (int y = 0; y < 8; y++) {
    for (int x = 0; x < 8; x++) {
      int pixelIndex = x + y * 8;
      if (pattern[y][x] == 1) {
        strip.setPixelColor(pixelIndex, color);
      } else {
        strip.setPixelColor(pixelIndex, 0);
      }
    }
  }
  strip.show();
}

// **Function to Clear the LED Matrix**
void clearMatrix() {
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 0);
  }
  strip.show();
}
