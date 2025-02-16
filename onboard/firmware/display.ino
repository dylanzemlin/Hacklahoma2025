/***************************************************
  This is our GFX example for the Adafruit ILI9341 Breakout and Shield
  ----> http://www.adafruit.com/products/1651

  Check out the links above for our tutorials and wiring diagrams
  These displays use SPI to communicate, 4 or 5 pins are required to
  interface (RST is optional)
  Adafruit invests time and resources providing this open source code,
  please support Adafruit and open-source hardware by purchasing
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.
  MIT license, all text above must be included in any redistribution
 ****************************************************/

#include "SPI.h"
#include "Adafruit_GFX.h"
#include "Adafruit_ILI9341.h"

// For the Adafruit shield, these are the default.
#define TFT_DC 16
#define TFT_CS 5
#define TFT_MOSI 23
#define TFT_CLK 18
#define TFT_RST 17
#define TFT_MISO 19

#define BYTE_CONFIRMED_CHARACTER 0
#define BYTE_NEWLINE 1
#define BYTE_BACKSPACE 2
#define BYTE_PREDICTION 3
#define BYTE_FINALIZE 4

// Use hardware SPI (on Uno, #13, #12, #11) and the above for CS/DC
// Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC);
// If using the breakout, change pins as desired
Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_MOSI, TFT_CLK, TFT_RST, TFT_MISO);
#define BUFFER_SIZE 100

void setup()
{
    Serial.begin(9600);
    Serial.println("ILI9341 Test!");

    tft.begin();
    tft.setRotation(1);

    // read diagnostics (optional but can help debug problems)
    tft.fillScreen(ILI9341_WHITE);
    tft.setTextColor(ILI9341_RED);
    tft.setCursor(1, 1);
    tft.setTextSize(10);
}

void loop(void)
{
    while (Serial.available() > 0)
    {
        // Read the first incoming byte
        char incomingChar = Serial.read();

        // If the byte is a confirmed character, write the character to the screen
        if (incomingChar == BYTE_CONFIRMED_CHARACTER)
        {
            char character = Serial.read();
            tft.print(character);
        }

        // If the byte is a newline, move the cursor to the next line
        else if (incomingChar == BYTE_NEWLINE)
        {
            tft.println();
        }

        // If the byte is a backspace, move the cursor back one space
        // and clear the character at that position
        else if (incomingChar == BYTE_BACKSPACE)
        {
            tft.setCursor(tft.getCursorX() - 1, tft.getCursorY());
            tft.print(" ");
            tft.setCursor(tft.getCursorX() - 1, tft.getCursorY());
        }

        // If the byte is a prediction, print the prediction to the screen
        // in light gray instead of black
        else if (incomingChar == BYTE_PREDICTION)
        {
            tft.setTextColor(ILI9341_LIGHTGREY);
            char character = Serial.read();
            tft.print(character);
            tft.setTextColor(ILI9341_BLACK);
        }

        //  // Read incoming character
        // char incomingChar = Serial.read();

        // // If newline is received, process the message
        // if (incomingChar == '\n')
        // {
        //     messageBuffer[bufferIndex] = '\0'; // Null-terminate the string
        //     Serial.print("Received: ");
        //     tft.println(messageBuffer);
        //     bufferIndex = 0; // Reset buffer for the next message
        // }
        // else if (bufferIndex < BUFFER_SIZE - 1)
        // {
        //     messageBuffer[bufferIndex++] = incomingChar; // Store character in buffer
        // }
    }

    // TODO: Should probably reimplement this
    // if (tft.getCursorX() >= 235 || tft.getCursorY() >= 270)
    // {
    //     tft.fillScreen(ILI9341_WHITE);
    //     tft.setCursor(1, 1);
    //     tft.println(messageBuffer);

    //     delay(500);
    // }
}