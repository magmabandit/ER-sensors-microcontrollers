// ReadyToDriveSound Driver
// Andre Chabra, 3/2/25
//
// Drives the speakers to play the ready-to-drive-sound when the Cascadia
// motorcontroller first enters the Motor Running State (VSM_State=6)
// This program makes use of the playsimple sample code for the Adafruit Music
// Maker and all credit for that goes to Adafruit which is commented below

/*************************************************** 
  This is an example for the Adafruit VS1053 Codec Breakout

  Designed specifically to work with the Adafruit VS1053 Codec Breakout 
  ----> https://www.adafruit.com/products/1381

  Adafruit invests time and resources providing this open source code, 
  please support Adafruit and open-source hardware by purchasing 
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.  
  BSD license, all text above must be included in any redistribution
 ****************************************************/

// include SPI, MP3 and SD libraries
#include <SPI.h>
#include <Adafruit_VS1053.h>
#include <SD.h>

// define the pins used
//#define CLK 13       // SPI Clock, shared with SD card
//#define MISO 12      // Input data, from VS1053/SD card
//#define MOSI 11      // Output data, to VS1053/SD card
// Connect CLK, MISO and MOSI to hardware SPI pins. 
// See http://arduino.cc/en/Reference/SPI "Connections"

// These are the pins used for the breakout example
#define BREAKOUT_RESET  9      // VS1053 reset pin (output)
#define BREAKOUT_CS     10     // VS1053 chip select pin (output)
#define BREAKOUT_DCS    8      // VS1053 Data/command select pin (output)
// These are the pins used for the music maker shield
#define SHIELD_RESET  -1      // VS1053 reset pin (unused!)
#define SHIELD_CS     7      // VS1053 chip select pin (output)
#define SHIELD_DCS    6      // VS1053 Data/command select pin (output)

// These are common pins between breakout and shield
#define CARDCS 4     // Card chip select pin
// DREQ should be an Int pin, see http://arduino.cc/en/Reference/attachInterrupt
#define DREQ 3       // VS1053 Data request, ideally an Interrupt pin 

Adafruit_VS1053_FilePlayer musicPlayer = 
    // create breakout-example object!
    //Adafruit_VS1053_FilePlayer(BREAKOUT_RESET, BREAKOUT_CS, BREAKOUT_DCS, DREQ, CARDCS);
    // create shield-example object!
    Adafruit_VS1053_FilePlayer(SHIELD_RESET, SHIELD_CS, SHIELD_DCS, DREQ, CARDCS);

union FloatUnion {
  byte bytes[4];
  float value;
};

void setup() {
  Serial.begin(19200);

  if (!musicPlayer.begin()) { // initialise the music player
    Serial.println(F("Couldn't find VS1053, do you have the right pins defined?"));
    while (1);
  }
  
  if (!SD.begin(CARDCS)) {
    Serial.println(F("SD failed, or not present"));
    while (1);  // don't do anything more
  }

  // list files
  // printDirectory(SD.open("/"), 0);
  
  // Set volume for left, right channels. lower numbers == louder volume!
  musicPlayer.setVolume(1,1);

  // Timer interrupts are not suggested, better to use DREQ interrupt!
  //musicPlayer.useInterrupt(VS1053_FILEPLAYER_TIMER0_INT); // timer int

  // If DREQ is on an interrupt pin (on uno, #2 or #3) we can do background
  // audio playing
  musicPlayer.useInterrupt(VS1053_FILEPLAYER_PIN_INT);  // DREQ int
}

void loop() {
  static bool receiving = false;
  static bool played = false;
  static byte buffer[4];
  int byteIndex = 0;
  int numFloats = 0;

  // get sensor readings from aggregator
  while (Serial.available()) {

    byte incomingByte = Serial.read();

    if (!receiving) {
        if (incomingByte == 0xFF) {  // Start marker detected
            receiving = true;
        }
        
    } else {
      if (incomingByte == 1) {
        FloatUnion reading1; // reads in the VSM state from the motor controller in bytes
        for (int j = 0; j < 4; j++) {
          while (!Serial.available());
          reading1.bytes[j] = Serial.read();
        }

        // plays the ready-to-drive sound when the the motor controller enters
        // the motor running state for the first time
        if (reading1.value == 6.0 && !played) {
          musicPlayer.playFullFile("/track003.mp3");
          played = true;
          // delay(100);
        }

        // if (reading1.value != 6.0) {
        //   played = false;
        // }
      }

      receiving = false; // Try to receive a new message
    }
  }
}


/// File listing helper
void printDirectory(File dir, int numTabs) {
   while(true) {
     
     File entry =  dir.openNextFile();
     if (! entry) {
       // no more files
       //Serial.println("**nomorefiles**");
       break;
     }
     for (uint8_t i=0; i<numTabs; i++) {
       Serial.print('\t');
     }
     Serial.print(entry.name());
     if (entry.isDirectory()) {
       Serial.println("/");
       printDirectory(entry, numTabs+1);
     } else {
       // files have sizes, directories do not
       Serial.print("\t\t");
       Serial.println(entry.size(), DEC);
     }
     entry.close();
   }
}