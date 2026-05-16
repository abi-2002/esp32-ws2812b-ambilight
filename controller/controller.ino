#define FASTLED_ALLOW_INTERRUPTS 0
#include <FastLED.h>

#define NUM_LEDS 92
#define DATA_PIN 8
#define FRAME_START 255

#define MODE_AMBILIGHT 0
#define MODE_STATIC    1

CRGB leds[NUM_LEDS];

byte buffer[NUM_LEDS * 2];
int index = 0;
bool receiving = false;

uint8_t brightness = 30;
uint8_t mode = MODE_AMBILIGHT;

void setup() {
  Serial.begin(115200);

  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(brightness);

  Serial.println("READY");
}

void loop() {

  while (Serial.available()) {

    byte incoming = Serial.read();

    // Data format - [FRAME_START][Brightness][Mode][Data...]
    // Mode - 0: Ambilight (packed RGB565), 1: Custom Color (RGB888)

    if (!receiving) {
      if (incoming == FRAME_START) {
        receiving = true;
        index = -2;   // indicates we're expecting Brightness next
      }
      continue;
    }

    // brightness
    if (index == -2) {
      brightness = incoming;
      FastLED.setBrightness(brightness);
      index = -1; // indicates we're expecting Mode next
      continue;
    }

    // mode
    if (index == -1) {
      mode = incoming;
      index = 0;
      continue;
    }

    // -------------------------
    // MODE: AMBILIGHT (packed)
    // -------------------------
    if (mode == MODE_AMBILIGHT) {

      buffer[index++] = incoming;

      // Each LED is sent as 2 bytes (RGB565 packed format)
      // Once we have received data for all LEDs, we can update the strip
      if (index >= NUM_LEDS * 2) {

        for (int i = 0; i < NUM_LEDS; i++) {

          uint16_t packed =
              ((uint16_t)buffer[i * 2] << 8) |
               (uint16_t)buffer[i * 2 + 1];

          uint8_t r5 = (packed >> 10) & 0x1F;
          uint8_t g5 = (packed >> 5)  & 0x1F;
          uint8_t b5 =  packed        & 0x1F;

          uint8_t r = (r5 << 3) | (r5 >> 2);
          uint8_t g = (g5 << 3) | (g5 >> 2);
          uint8_t b = (b5 << 3) | (b5 >> 2);

          leds[i].setRGB(r, g, b);
        }

        FastLED.show();
        receiving = false;
      }
    }

    // -------------------------
    // MODE: CUSTOM COLOR
    // -------------------------
    else if (mode == MODE_STATIC) {

      buffer[index++] = incoming;

      // For static mode, we expect 3 bytes (R, G, B) for the entire strip
      if (index >= 3) {

        uint8_t r = buffer[0];
        uint8_t g = buffer[1];
        uint8_t b = buffer[2];

        for (int i = 0; i < NUM_LEDS; i++) {
          leds[i].setRGB(r, g, b);
        }

        FastLED.show();
        receiving = false;
      }
    }
  }
}