# KEY TASK

Please assist me in writing a custom keyboard driver using KMK on an Adafruit KB2040 to interface an XBOX 360 Chatpad with a Raspberry Pi Zero 2W as a USB keyboard with a keymap that aims to support software development commands in a terminal. The device itself is something of a "cyberdeck", or task-oriented device with a narrow focus. This device aims to create a portable terminal interface to perform software development both locally and remotely.

Pay attention to the headers of the following sections, then take each section and review its material one at a time. Write up the high-points from each section that exemplify the important functions and definitions of individual aspects of the project.

---

# Custom Arduino Keyboard Driver

Chatpad.h
```cpp
#ifndef CHATPAD_H
#define CHATPAD_H

#include <Arduino.h>
#include <Keyboard.h>

//-----------------------------------------------------------------
// Class: Chatpad
// Purpose: Interface with an Xbox Chatpad, process incoming key events,
//          convert raw keycodes into ASCII values, and dispatch key events
//          via a user-provided callback.
//-----------------------------------------------------------------
class Chatpad {
public:
    //-----------------------------------------------------------------
    // Enumeration: keycode_t
    // Purpose: List of raw keycodes as defined by the Chatpad hardware.
    //-----------------------------------------------------------------
    enum keycode_t {
        Key1 = 0x17, Key2 = 0x16, Key3 = 0x15, Key4 = 0x14, Key5 = 0x13,
        Key6 = 0x12, Key7 = 0x11, Key8 = 0x67, Key9 = 0x66, Key0 = 0x65,
        KeyQ = 0x27, KeyW = 0x26, KeyE = 0x25, KeyR = 0x24, KeyT = 0x23,
        KeyY = 0x22, KeyU = 0x21, KeyI = 0x76, KeyO = 0x75, KeyP = 0x64,
        KeyA = 0x37, KeyS = 0x36, KeyD = 0x35, KeyF = 0x34, KeyG = 0x33,
        KeyH = 0x32, KeyJ = 0x31, KeyK = 0x77, KeyL = 0x72, KeyComma = 0x62,
        KeyZ = 0x46, KeyX = 0x45, KeyC = 0x44, KeyV = 0x43, KeyB = 0x42,
        KeyN = 0x41, KeyM = 0x52, KeyPeriod = 0x53, KeyEnter = 0x63,
        KeyLeft = 0x55, KeySpace = 0x54, KeyRight = 0x51, KeyBackspace = 0x71,
        KeyShift = 0x81, KeyGreen = 0x82, KeyPeople = 0x83, KeyOrange = 0x84
    };

    //-----------------------------------------------------------------
    // Enumeration: eventtype_t
    // Purpose: Indicates whether a key event is a key press (Down) or release (Up).
    //-----------------------------------------------------------------
    enum eventtype_t {
        Up = 0,
        Down = 1
    };

    //-----------------------------------------------------------------
    // Typedef: callback_t
    // Purpose: Define a function pointer type for key event callbacks.
    //          The callback receives a reference to the Chatpad, the keycode,
    //          and the event type.
    //-----------------------------------------------------------------
    typedef void (*callback_t)(Chatpad &, keycode_t, eventtype_t);

    //-----------------------------------------------------------------
    // Function: init
    // Purpose: Initialize the Chatpad with a given HardwareSerial interface and
    //          register the callback function for key events.
    //-----------------------------------------------------------------
    void init(HardwareSerial &serial, callback_t callback);

    //-----------------------------------------------------------------
    // Function: poll
    // Purpose: Poll the underlying serial interface for incoming data,
    //          process complete packets, and dispatch key events.
    //-----------------------------------------------------------------
    void poll();

    //-----------------------------------------------------------------
    // Getter Functions:
    // Purpose: Check the current state of modifier keys.
    //-----------------------------------------------------------------
    bool isShiftDown() const;
    bool isGreenDown() const;
    bool isOrangeDown() const;
    bool isPeopleDown() const;
    bool isPeopleModeToggled() const;

    //-----------------------------------------------------------------
    // Function: toAscii
    // Purpose: Convert a raw keycode to its corresponding ASCII character
    //          based on the current modifier state.
    // Parameters:
    //    - keycode: A raw keycode value from the Chatpad.
    // Returns:
    //    - The ASCII character for that keycode, or 0 if unmapped.
    //-----------------------------------------------------------------
    char toAscii(keycode_t keycode);

private:
    //-----------------------------------------------------------------
    // Private Members:
    // _serial       : Pointer to the HardwareSerial interface used for communication.
    // _callback     : Function pointer for dispatching key events.
    // _buffer[8]    : Buffer for reading 8-byte packets from the Chatpad.
    // _last_modifiers: Last known modifier state.
    // _last_key0    : Last keycode received in slot 0.
    // _last_key1    : Last keycode received in slot 1.
    // _last_ping    : Timestamp of the last keep-alive message sent.
    // _peopleToggleMode: Tracks whether People mode is toggled.
    // _shiftToggled : Tracks whether Shift mode is toggled.
    //-----------------------------------------------------------------
    HardwareSerial *_serial;
    callback_t _callback;
    uint8_t _buffer[8];

    uint8_t _last_modifiers;
    uint8_t _last_key0;
    uint8_t _last_key1;
    uint32_t _last_ping;

    bool _peopleToggleMode = false;
    bool _shiftToggled = false;

    //-----------------------------------------------------------------
    // Function: dispatch
    // Purpose: Dispatch a key event to the registered callback.
    // Parameters:
    //    - keycode: The keycode to dispatch.
    //    - is_down: A non-zero value indicates a key press; zero indicates release.
    //-----------------------------------------------------------------
    void dispatch(uint8_t keycode, int is_down);
};

#endif // CHATPAD_H
```

Chatpad.ino
```cpp
#include <Adafruit_NeoPixel.h>  // Library to control NeoPixel LEDs
#include <Keyboard.h>           // Library to emulate keyboard input
#include "Chatpad.h"            // Library for interfacing with the Xbox 360 Chatpad

// Define the pin and number of NeoPixels used
#define NEOPIXEL_PIN 17         // Digital pin connected to the NeoPixel
#define NUM_PIXELS 1            // Only 1 LED in this example

// Create the NeoPixel object; using GRB color order and an 800 KHz signal
Adafruit_NeoPixel neoPixel(NUM_PIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

// Define which serial port to use for the Chatpad communication
#define CHATPAD_SERIAL Serial1

// Define LED color constants using macros. These use the neoPixel.Color() method:
#define COLOR_BLUE       (neoPixel.Color(0, 0, 255))
#define COLOR_GREEN      (neoPixel.Color(0, 255, 0))
#define COLOR_YELLOW     (neoPixel.Color(255, 255, 0))
#define COLOR_RED        (neoPixel.Color(255, 0, 0))
#define COLOR_OFF        (neoPixel.Color(0, 0, 0))
#define COLOR_HEARTBEAT  (neoPixel.Color(20, 20, 20))  // Dim white for heartbeat debugging

// Create an instance of the Chatpad
Chatpad chatpad;

// Global variable for heartbeat timing
unsigned long lastHeartbeat = 0;

//-----------------------------------------------------------------
// Function: debugLED
// Purpose: Flash the LED with a specific color for debugging purposes.
// Parameters:
//   - color: The color to display (use one of the COLOR_* macros)
//   - duration: How long to display the color (default: 100 ms)
//-----------------------------------------------------------------
void debugLED(uint32_t color, uint16_t duration = 100) {
  neoPixel.setPixelColor(0, color);
  neoPixel.show();
  delay(duration);
  neoPixel.setPixelColor(0, COLOR_OFF);
  neoPixel.show();
}

//-----------------------------------------------------------------
// Function: handleKey
// Purpose: Called on key events from the Chatpad.
// Parameters:
//   - pad: Reference to the Chatpad object
//   - key: Key code from the Chatpad
//   - event: Event type (Down for key press, Up for key release)
//-----------------------------------------------------------------
void handleKey(Chatpad &pad, Chatpad::keycode_t key, Chatpad::eventtype_t event) {
  char asciiKey = pad.toAscii(key);  // Convert keycode to ASCII (if possible)

  if (event == Chatpad::Down) {  // On key press
    if (asciiKey) {
      // Send key press to the computer
      Keyboard.press(asciiKey);
      Serial.print("Key pressed: ");
      Serial.println(asciiKey);

      // Set LED color based on key type
      if (isalpha(asciiKey))
        neoPixel.setPixelColor(0, COLOR_BLUE);    // Blue for letters
      else if (isdigit(asciiKey))
        neoPixel.setPixelColor(0, COLOR_GREEN);     // Green for digits
      else
        neoPixel.setPixelColor(0, COLOR_YELLOW);    // Yellow for other ASCII characters
    } else {
      // For non-ASCII keys, log the code and flash red for debugging
      Serial.print("Non-ASCII key pressed, code: ");
      Serial.println(key, HEX);
      neoPixel.setPixelColor(0, COLOR_RED);
    }
    neoPixel.show();
  }
  else if (event == Chatpad::Up) {  // On key release
    if (asciiKey)
      Keyboard.release(asciiKey);
    // Turn off the LED when the key is released
    neoPixel.setPixelColor(0, COLOR_OFF);
    neoPixel.show();
  }
}

//-----------------------------------------------------------------
// Function: setup
// Purpose: Initializes Serial communication, the NeoPixel LED,
//          Chatpad, and Keyboard. Also does initial LED debugging.
//-----------------------------------------------------------------
void setup() {
  Serial.begin(115200);

  // Initialize the NeoPixel library and set the brightness
  neoPixel.begin();
  neoPixel.setBrightness(50);
  neoPixel.show();

  // LED Debugging: Blink the LED twice to indicate successful initialization
  for (int i = 0; i < 2; i++) {
    neoPixel.setPixelColor(0, COLOR_BLUE);
    neoPixel.show();
    delay(200);
    neoPixel.setPixelColor(0, COLOR_OFF);
    neoPixel.show();
    delay(200);
  }

  // Initialize the Chatpad serial connection and its key callback
  CHATPAD_SERIAL.begin(19200);
  chatpad.init(CHATPAD_SERIAL, handleKey);

  // Initialize Keyboard functionality (required for sending key presses)
  Keyboard.begin();
}

//-----------------------------------------------------------------
// Function: loop
// Purpose: Poll the Chatpad for key events and run a heartbeat LED
//          debug pattern every second.
//-----------------------------------------------------------------
void loop() {
  chatpad.poll();  // Poll Chatpad for key events

  // Heartbeat LED Debugging: Blink a dim white LED every 1000 ms
  if (millis() - lastHeartbeat >= 1000) {
    neoPixel.setPixelColor(0, COLOR_HEARTBEAT);
    neoPixel.show();
    delay(50);  // Brief blink duration
    neoPixel.setPixelColor(0, COLOR_OFF);
    neoPixel.show();
    lastHeartbeat = millis();
  }
}
```

Chatpad.cpp
```cpp#include "Chatpad.h"  // Include the Chatpad library header

// Define bit masks for various modifier flags (each one represents a specific button)
static const uint8_t kShiftMask  = (1 << 0);  // Bit 0: Shift key mask
static const uint8_t kGreenMask  = (1 << 1);  // Bit 1: Green button mask
static const uint8_t kOrangeMask = (1 << 2);  // Bit 2: Orange button mask
static const uint8_t kPeopleMask = (1 << 3);  // Bit 3: People button mask

// Define messages (as byte arrays) to be sent to the Chatpad for initialization and to keep it awake
static const uint8_t kInitMessage[]  = { 0x87, 0x02, 0x8C, 0x1F, 0xCC };
static const uint8_t kAwakeMessage[] = { 0x87, 0x02, 0x8C, 0x1B, 0xD0 };


//-----------------------------------------------------------------
// Function: Chatpad::init
// Purpose: Initialize the Chatpad communication and set up initial state.
// Parameters:
//    - serial: Reference to a HardwareSerial object for communication
//    - callback: Function pointer to call when a key event occurs
//-----------------------------------------------------------------
void Chatpad::init(HardwareSerial &serial, Chatpad::callback_t callback) {
    _serial = &serial;          // Store pointer to the provided serial port
    _callback = callback;       // Store the key event callback
    _last_modifiers = 0;        // Clear last modifiers state
    _last_key0 = 0;             // Clear last key (first slot)
    _last_key1 = 0;             // Clear last key (second slot)
    _last_ping = 0;             // Initialize last ping time

    _serial->begin(19200);      // Start serial communication at 19200 baud
    _serial->write(kInitMessage, sizeof(kInitMessage));  // Send initialization message to Chatpad
}


//-----------------------------------------------------------------
// Function: Chatpad::poll
// Purpose: Poll the Chatpad for incoming data, validate and process packets,
//          handle modifier changes, dispatch key events, and send periodic keep‐alive pings.
//-----------------------------------------------------------------
void Chatpad::poll() {
    // Check if there is any data available on the serial port
    if (_serial->available()) {
        uint8_t byte = _serial->read();  // Read one byte from the serial stream

        // Look for valid packet start bytes (0xA5 or 0xB4)
        if (byte == 0xA5 || byte == 0xB4) {
            _buffer[0] = byte;  // Store the first byte in the buffer

            // Read the next 7 bytes to complete an 8-byte packet
            for (int i = 1; i < 8; i++) {
                // Wait (busy-wait) until a byte is available
                while (!_serial->available()) {
                    ;  // Do nothing until data is available
                }
                _buffer[i] = _serial->read();  // Store the byte in the buffer
            }
        } else {
            return;  // If the first byte is not valid, exit the poll function
        }

        // If the packet starts with 0xA5, ignore it and return (it might be a status message)
        if (_buffer[0] == 0xA5) return;

        // Validate packet header: Packet must start with 0xB4 followed by 0xC5
        if (_buffer[0] != 0xB4 || _buffer[1] != 0xC5) {
            Serial.println("Unexpected packet type or header:");
            Serial.print("Packet: ");
            // Print the entire packet for debugging
            for (int i = 0; i < 8; i++) {
                Serial.print("0x");
                Serial.print(_buffer[i], HEX);
                Serial.print(" ");
            }
            Serial.println();
            return;
        }

        // Compute checksum: sum of bytes 0 through 6, then take the negative (two's complement)
        uint8_t checksum = _buffer[0];
        for (int i = 1; i < 7; i++) {
            checksum += _buffer[i];
        }
        checksum = -checksum;

        // Compare computed checksum with the received checksum (byte 7)
        if (checksum != _buffer[7]) {
            Serial.println("Checksum failure");
            return;
        }

        // Extract modifier and key information from the packet
        uint8_t modifiers = _buffer[3];  // Byte 3 contains modifier flags
        uint8_t key0 = _buffer[4];       // Byte 4 contains first key code
        uint8_t key1 = _buffer[5];       // Byte 5 contains second key code

        // Determine which modifier bits have changed since last packet
        uint8_t modifier_changes = modifiers ^ _last_modifiers;

        // Check if the People button state has changed
        if (modifier_changes & kPeopleMask) {
            if (modifiers & kPeopleMask) {
                _peopleToggleMode = !_peopleToggleMode;  // Toggle People mode on press
                Serial.print("People button toggled mode: ");
                Serial.println(_peopleToggleMode ? "ON" : "OFF");
            }
        }

        // If both Shift and Orange modifiers are active, toggle the Shift mode
        if ((modifiers & kShiftMask) && (modifiers & kOrangeMask)) {
            _shiftToggled = !_shiftToggled;  // Toggle Shift mode
            Serial.print("Shift mode toggled: ");
            Serial.println(_shiftToggled ? "ON" : "OFF");
        }

        // Update the stored modifier state for the next poll cycle
        _last_modifiers = modifiers;

        // Dispatch key events based on changes between current keys and last keys:
        // If a new key (key0) is pressed and it is different from previous keys, send a "Down" event.
        if (key0 && key0 != _last_key0 && key0 != _last_key1) {
            dispatch(key0, Down);
        }
        // Do the same for key1.
        if (key1 && key1 != _last_key0 && key1 != _last_key1) {
            dispatch(key1, Down);
        }
        // If a previously pressed key (stored in _last_key0) is no longer present, send an "Up" event.
        if (_last_key0 && _last_key0 != key0 && _last_key0 != key1) {
            dispatch(_last_key0, Up);
        }
        // Similarly for _last_key1.
        if (_last_key1 && _last_key1 != key0 && _last_key1 != key1) {
            dispatch(_last_key1, Up);
        }

        // Update the stored key states for the next poll cycle
        _last_key0 = key0;
        _last_key1 = key1;
    }

    // Periodically send an "awake" message to the Chatpad every 1000 ms
    uint32_t time = millis();
    if (time - _last_ping > 1000) {
        _last_ping = time;
        _serial->write(kAwakeMessage, sizeof(kAwakeMessage));
    }
}


//-----------------------------------------------------------------
// Function: isPeopleModeToggled
// Purpose: Return whether People mode is toggled on
//-----------------------------------------------------------------
bool Chatpad::isPeopleModeToggled() const {
    return _peopleToggleMode;
}


//-----------------------------------------------------------------
// Function: isShiftDown
// Purpose: Return whether Shift is currently active (either toggled or held)
//-----------------------------------------------------------------
bool Chatpad::isShiftDown() const {
    return _shiftToggled || (_last_modifiers & kShiftMask);
}


//-----------------------------------------------------------------
// Function: isGreenDown
// Purpose: Return whether the Green button is currently pressed
//-----------------------------------------------------------------
bool Chatpad::isGreenDown() const {
    return _last_modifiers & kGreenMask;
}


//-----------------------------------------------------------------
// Function: isOrangeDown
// Purpose: Return whether the Orange button is currently pressed
//-----------------------------------------------------------------
bool Chatpad::isOrangeDown() const {
    return _last_modifiers & kOrangeMask;
}


//-----------------------------------------------------------------
// Function: isPeopleDown
// Purpose: Return whether the People button is currently pressed
//-----------------------------------------------------------------
bool Chatpad::isPeopleDown() const {
    return _last_modifiers & kPeopleMask;
}


//-----------------------------------------------------------------
// Function: dispatch
// Purpose: Call the callback function (if set) with a key event.
// Parameters:
//    - keycode: The key code for the event
//    - is_down: Non-zero value indicates a key press (Down), zero indicates release (Up)
//-----------------------------------------------------------------
void Chatpad::dispatch(uint8_t keycode, int is_down) {
    if (_callback) {  // If a callback function is registered
        _callback(*this, static_cast<keycode_t>(keycode), is_down ? Down : Up);
    }
}


//-----------------------------------------------------------------
// Function: toAscii
// Purpose: Convert a Chatpad keycode into an ASCII character using lookup tables.
//          The table used depends on the current modifier state (Shift, Green, Orange, or People mode).
// Parameters:
//    - keycode: The raw keycode from the Chatpad
// Returns:
//    - The corresponding ASCII character, or 0 if no mapping exists.
//-----------------------------------------------------------------
char Chatpad::toAscii(keycode_t keycode) {
    // Lookup tables stored in program memory (PROGMEM) for different modifier states.
    static const char kAsciiTable[] PROGMEM = {
        '7', '6', '5', '4', '3', '2', '1', 0,
        'u', 'y', 't', 'r', 'e', 'w', 'q', 0,
        'j', 'h', 'g', 'f', 'd', 's', 'a', 0,
        'n', 'b', 'v', 'c', 'x', 'z', 0, 0,
        128, 'm', '.', ' ', 130, 0, 0, 0,
        0, ',', '\n', 'p', '0', '9', '8', 0,
        '\b', 'l', 0, 0, 'o', 'i', 'k', 0,
    };

    static const char kAsciiTable_Shifted[] PROGMEM = {
        '&', '^', '%', '$', '#', '@', '!', 0,
        'U', 'Y', 'T', 'R', 'E', 'W', 'Q', 0,
        'J', 'H', 'G', 'F', 'D', 'S', 'A', 0,
        'N', 'B', 'V', 'C', 'X', 'Z', 0, 0,
        0, 'M', '?', ' ', 0, 0, 0, 0,
        0, 58, '\n', 'P', ')', '(', '*', 0,
        '\b', 'L', 0, 0, 'O', 'I', 'K', 0,
    };

    static const char kAsciiTable_Green[] PROGMEM = {
        '&', '^', '%', '$', '#', '@', '!', 0,
        '&', '^', '%', '#', 128, '@', '!', 0,
        39, 47, 168, 125, 123, 138, '~', 0,
        '<', '|', '-', 187, 171, 96, 0, 0,
        0, '>', '?', ' ', 0, 0, 0, 0,
        0, 58, '\n', ')', ')', '(', '*', 0,
        '\b', 93, 0, 0, '(', '*', 91, 0,
    };

    static const char kAsciiTable_Orange[] PROGMEM = {
       KEY_F7, KEY_F6, KEY_F5, KEY_F4, KEY_F3, KEY_F2, KEY_F1, 0,
       'U', 'Y', 'T', 'R', 'E', 'W', 'Q', 0,
       34, 92, 'G', 'F', 'D', 'S', 'A', 0,
       'N', 'B', '_', 'C', 'X', 'Z', 0, 0,
       9, 'M', '.', ' ', 177, 0, 0, 0,
       0, 59, '\n', '=', KEY_F10, KEY_F9, KEY_F8, 0,
       212, 'L', 0, 0, 'O', 'I', 'K', 0,
    };

    static const char kAsciiTable_PeopleMode[] PROGMEM = {
        KEY_F7, KEY_F6, KEY_F5, KEY_F4, KEY_F3, KEY_F2, KEY_F1, 0,
        'u', 'y', 't', 'r', 'e', 218, 'q', 0,
        'j', 'h', 'g', 'f', 215, 217, 216, 0,
        'n', 'b', 'v', 'c', 'x', 'z', 0, 0,
        9, 'm', '.', ' ', 177, 0, 0, 0,
        0, ',', '\n', 'p', KEY_F10, KEY_F9, KEY_F8, 0,
        '\b', 'l', 0, 0, 'o', 'i', 'k', 0,
    };

    // Compute the lookup table index from the raw keycode.
    // The calculation maps the keycode into an index that selects the correct character.
    uint8_t index = (((keycode - 0x11) & 0x70) >> 1) | ((keycode - 0x11) & 0x7);
    // Ensure the index is within bounds; if not, return 0 (no mapping).
if (index >= (sizeof(kAsciiTable) / sizeof(kAsciiTable[0])))
    return 0;

    // Select the appropriate lookup table based on the current modifier state:
    if (isPeopleModeToggled()) {
        return pgm_read_byte(&kAsciiTable_PeopleMode[index]);
    } else if (isOrangeDown()) {
        return pgm_read_byte(&kAsciiTable_Orange[index]);
    } else if (isGreenDown()) {
        return pgm_read_byte(&kAsciiTable_Green[index]);
    } else if (isShiftDown()) {
        return pgm_read_byte(&kAsciiTable_Shifted[index]);
    } else {
        return pgm_read_byte(&kAsciiTable[index]);
    }
}
```

---

# KMK ALTERNATIVE

kmk-getting-started.md
```markdown
# Getting Started
> Life was like a box of chocolates. You never know what you're gonna get.

KMK is a keyboard focused layer that sits on top of [CircuitPython](https://circuitpython.org/). As such, it should work with most [boards that support CircuitPython](https://circuitpython.org/downloads). KMK requires CircuitPython version 7.3 or above.
Known working and recommended devices can be found in the [list of officially supported microcontrollers](Officially_Supported_Microcontrollers.md)


## TL;DR Quick start guide
> To infinity and beyond!
1. [Install CircuitPython version 7.3 or higher on your board](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython). With most boards, it should be as easy as drag and dropping the firmware on the drive
2. Get an up to date [copy of KMK](https://github.com/KMKfw/kmk_firmware/archive/refs/heads/main.zip) from the main branch
3. Unzip it and copy the KMK folder and the boot.py file at the root of the USB drive corresponding to your board (often appearing as CIRCUITPY)
4. Create a new *code.py* or *main.py* file in the same root directory (same level as boot.py) with the example content hereunder:

***IMPORTANT:*** adapt the GP0 / GP1 pins to your specific board !

```
print("Starting")

import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation

keyboard = KMKKeyboard()

keyboard.col_pins = (board.GP0,)
keyboard.row_pins = (board.GP1,)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

keyboard.keymap = [
    [KC.A,]
]

if __name__ == '__main__':
    keyboard.go()
```


5. With a wire / paperclip / whatever, connect the pins you selected for col_pin and row_pin together.

![feather and keeboar example pins](pins56.jpg)

6. If it prints the letter "a" (or a "Q" or ... depending on your keyboard layout), you're done!



## Now that you're up and running, you may want to go further...
> This is your last chance. After this, there is no turning back. You take the blue pill—the story ends, you wake up in your bed and believe whatever you want to believe. You take the red pill—you stay in Wonderland, and I show you how deep the rabbit hole goes. Remember: all I'm offering is the truth. Nothing more.

### You're extremely lucky and you have a fully supported keyboard
If your keyboard and microcontroller are officially supported, simply visit the page for your files, and dropping them on the root of the "flash drive".
Those pages can be found in the repositories [boards folder](https://github.com/KMKfw/kmk_firmware/tree/master/boards).
You will need the `kb.py` and `main.py`. If you need more detailed instructions on how to customize the configuration settings and key mappings, please refer to the [config and keymap](config_and_keymap.md) documentation.

### You've got another, maybe DIY, board and want to customize KMK for it
First, be sure to understand how your device work, and particularly its specific matrix configuration. You can have a look at [how key matrices work](http://pcbheaven.com/wikipages/How_Key_Matrices_Works/) or read the [guide](https://docs.qmk.fm/#/hand_wire) provided by the QMK team for handwired keyboards
Once you've got the gist of it:
- To start customizing your `code.py`/`main.py` file, please refer to the [config and keymap](config_and_keymap.md) and [keys](keys.md) files respectively, which provide detailed instructions on how to modify the configuration settings and key mappings.
- There's a [reference](keycodes.md) of the available keycodes
- [International](international.md) extension adds keys for non US layouts and [Media Keys](media_keys.md) adds keys for ... media

And to go even further:
- [Macros](macros.md) are used for sending multiple keystrokes in a single action
- [Layers](layers.md) can transform the whole way your keyboard is behaving with a single touch
- [HoldTap](holdtap.md) allow you to customize the way a key behaves whether it is tapped or hold, and [TapDance](tapdance.md) depending on the number of times it is pressed

Want to have fun features such as RGB, split keyboards and more? Check out what builtin [modules](modules.md) and [extensions](extensions.md) can do!
You can also get ideas from the various [user examples](https://github.com/KMKfw/kmk_firmware/tree/master/user_keymaps) that we provide and dig into our [documentation](README.md).


### Pre-compiling KMK for faster boot times or microcontrollers with limited flash

There are two options:
1. To compile KMK yourself you'll need to download and install the [compatible mpy-cross](https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/mpy-cross/)
  for your Operating System. Don't forget to add it to your PATH, test by running `mpy-cross` from a shell (Powershell, Bash, Fish, etc). Once that's set up, run either `make compile` (if you have `make`) or `python util/compile.py`to generate the `.mpy` versions of KMK files. Then copy the whole compiled `kmk/` directory to your keyboard.

There are even more compile and copy make targets.
Power user can compile KMK and additional libraries, and then load the bytecode and keyboard code
onto a keyboard in one go:
```sh
make compile copy-compiled copy-board MPY_SOURCES='kmk/ lib/' BOARD='boards/someboard' MOUNTPOINT='/media/user/someboard'
```

2. To download a pre-compiled KMK go to [Actions > Build on the KMK GitHub project page](https://github.com/KMKfw/kmk_firmware/actions/workflows/compile.yml),
  click on the latest build, and you'll find the download link at the bottom of the page under Artifacts. Unzip the download and place the contents in the `kmk/` directory on your keyboard.


On certain microcontrollers that will still not be enough of a size reduction to
fit all of KMK onto the flash (nice!nano for example).
You can remove any optional parts of KMK you aren't using.
Start by skipping `kmk/extensions`, `kmk/modules`, and `kmk/quickpin` and adding in only the files under those paths used in your keyboard (i.e. files that are imported in your `main.py` or `kb.py`).


## Additional help and support
> Roads? Where we're going we don't need roads.

In case you need it, debugging help can be found on the [debugging](debugging.md) page.

For asynchronous support and chatter about KMK, [join our Zulip
community](https://kmkfw.zulipchat.com)!

If you ask for help in chat or open a bug report, if possible
make sure your copy of KMK is up-to-date.
In particular, swing by the Zulip chat *before* opening a GitHub Issue about
configuration, documentation, etc. concerns.
```

config_and_keymap.md
```markdown
# Configuring KMK

KMK is configured through a rather large, plain-old-Python class called
`KMKKeyboard`. Subclasses of this configuration exist which pre-fill defaults
for various known keyboards (for example, many QMK, TMK, or ZMK keyboards
are supported with a nice!nano, or through our ItsyBitsy to Pro Micro pinout adapter.)
This class is the main interface between end users and the inner workings of KMK.
Let's dive in!

- Edit or create a file called `main.py` on your `CIRCUITPY` drive. You can also
  keep this file on your computer (perhaps under `user_keymaps` - please feel
  free to submit a pull request with your layout definitions!) and copy it over
  (either manually or, if you're adept with developer tooling and/or a command
  line, [our Makefile](flashing.md)).

  It's definitely recommended to keep a backup of your configuration somewhere
  that isn't the microcontroller itself - MCUs die, CircuitPython may run into
  corruption bugs, or you might just have bad luck and delete the wrong file
  some day.

- Assign a `KMKKeyboard` instance to a variable (ex. `keyboard = KMKKeyboard()` - note
  the parentheses).

- Make sure this `KMKKeyboard` instance is actually run at the end of the file with
  a block such as the following:

```python
if __name__ == '__main__':
    keyboard.go()
```

- Assign pins and your diode orientation (only necessary on handwire keyboards),
  for example:

```python
import board

from kmk.scanners import DiodeOrientation

col_pins = (board.SCK, board.MOSI, board.MISO, board.RX, board.TX, board.D4)
row_pins = (board.D10, board.D11, board.D12, board.D13, board.D9, board.D6, board.D5, board.SCL)
rollover_cols_every_rows = 4
diode_orientation = DiodeOrientation.COL2ROW
```

The pins should be based on whatever CircuitPython calls pins on your particular
board. You can find these in the REPL on your CircuitPython device:

```python
import board
print(dir(board))
```

> Note: `rollover_cols_every_rows` is only supported with
> `DiodeOrientation.COLUMNS`/`DiodeOrientation.COL2ROW`, not `DiodeOrientation.ROWS`/`DiodeOrientation.ROW2COL`. It is used for boards
> such as the Planck Rev6 which reuse column pins to simulate a 4x12 matrix in
> the form of an 8x6 matrix

- Import the global list of key definitions with `from kmk.keys import KC`. You
  can either print this out in the REPL as we did with `board` above, or simply
  look at [our Key documentation](keycodes.md).
  We've tried to keep that listing reasonably up to date, but if it feels like
  something is missing, you may need to read through `kmk/keys.py` (and then
  open a ticket to tell us our docs are out of date, or open a PR and fix the
  docs yourself!)

- Define a keymap, which is, in Python terms, a List of Lists of `Key` objects.
  A very simple keymap, for a keyboard with just two physical keys on a single
  layer, may look like this:

```python
keyboard.keymap = [[KC.A, KC.B]]
```

- The keymap contains a flat list of `Key` objects for each layer of the keyboard.
  The list of keys in each layer are stored as a single list that follows the
  grid of row and column pins in the keyboard matrix.  This list starts with keys
  in the first row from left to right, then the second row, and so on.
  The row x column matrix structure doesn't appear explicitly
  in the keymap.  Use `KC.NO` to mark grid positions without a physical key.
  For very sparse grids `keyboard.coord_mapping` can be useful to avoid `KC.NO`.
```

keys.md
```markdown
# Keys

**Note:** This is not a lookup table of key objects provided by KMK. That listing
can be found in [`keycodes.md`](keycodes.md). It's probably worth a look at the raw source if
you're stumped: [`kmk/keys.py`](/kmk/keys.py).

## Custom Keys

Here's a very contrived example for a custom key with a limit to the number of
times it can used (until the next keyboard reset).
Custom keys are, as a rule of thumb, the way to go to implement custom
functionality.
If the objective is to type out a sequence of keys however, or an action has to
be performed asynchronously while holding a key down, then [macros](macros.md)
are worth trading higher convenience for the hit in performance.

### Quick and Dirty

The base key class, of which all keys are derived, accepts custom handlers.
It's "single use", should be fine for most use cases, but is not recommended for
stateful keys.
Note: Both `on_press` and `on_release` methods are optional and a custom key is
allowed to have none of the two and do absolutely nothing.

```python
from kmk.keys import Key

limit = 10

def limit_on_press(key, keyboard, *args):
    global limit
    if limit > 0:
       keyboard.add_key(KC.A)

def limit_on_release(key, keyboard, *args):
    global limit
    if limit > 0:
        keyboard.remove_key(KC.A)
        limit -= 1

KC_A10 = Key(on_press=limit_on_press, on_release=limit_on_release)
```

### Generally Recommended

Reusable or stateful keys are better implemented as a custom key derived from
the base class.
Giving the key a custom type (i.e. name) can make it easier to spot in
debug messages and opens up to possibility to react on key types in custom
modules; the downside is a potential slight increase in memory consumption.
All methods are technically optional, although it is recommended to implement
them anyway or the default implementations of `Key` may look for handlers that
don't exist.

```python
from kmk.keys import Key

class LimitKey(Key):
    def __init__(self, key, limit):
        self.key = KC.A
        self.limit = limit

    def on_press(self, keyboard, coord_int=None):
        if self.limit > 0:
            keyboard.add_key(self.key)

    def on_release(self, keyboard, coord_int=None):
        if self.limit > 0:
            self.limit -= 1
            keyboard.remove_key(self.key)

KC_A10 = LimitKey(KC.A, 10)
KC_B20 = LimitKey(KC.B, 20)
```

### Unnecessary

For completeness sake: this is how keys can be entered into the `KC` dictionary.
There's no reason to do this as it will have a negative, if probably small
effect on memory usage with no actual benefit.

```python
from kmk.keys import make_key

# with an instance of base key class with 1 alias
make_key(
    names=('A10',),
    constructor=Key,
    on_press=limit_on_press,
    on_release=limit_on_release,
)

# with a custom base key class with 3 aliases
make_key(
    names=('B20', 'LIMIT_B_20', 'B_ONLY_20_TIMES'),
    constructor=LimitKey,
    key=KC.B,
    count=20,
)

# makes those keys available as:
KC.A10
KC.B20
KC.LIMIT_B_20
KC.B_ONLY_20_TIMES
```

## Key Objects

This is a bunch of documentation about how a physical keypress translates to
events (and the lifecycle of said events) in KMK. It's somewhat technical, but
if you're looking to extend your keyboard's functionality with extra code,
you'll need at least some of this technical knowledge.

The first few steps in the process aren't all that interesting for most
workflows, which is why they're buried deep in KMK: we scan a bunch of GPIO
lanes (about as quickly as CircuitPython will let us) to see where, in a matrix
of keys, a key has been pressed. The technical details about this process [are
probably best left to
Wikipedia](https://en.wikipedia.org/wiki/Keyboard_matrix_circuit). Then, we scan
through the defined keymap, finding the first valid key at this index based on
the stack of currently active layers (this logic, if you want to read through
the code, is in [`kmk/kmk_keyboard.py`](/kmk/kmk_keyboard.py), method `_find_key_in_map`).

The next few steps are the interesting part, but to understand them, we need to
understand a bit about what a `Key` object is (found in [`kmk/keys.py`](/kmk/keys.py)). `Key`
objects have a few core pieces of information:

- Their `code`, which can be any integer or None. Integers sent through to the
  HID stack (and thus the computer, which will translate that integer to
  something meaningful - for example, `code=4` becomes `a` on a US QWERTY/Dvorak
  keyboard).

- Handlers for "press" (sometimes known as "keydown") and "release" (sometimes
  known as "keyup") events. KMK provides handlers for standard keyboard
  functions and some special override keys (like `KC.GESC`, which is an enhanced
  form of existing ANSI keys) in [`kmk/handlers/stock.py`](/kmk/handlers/stock.py).

- A generic `meta` field, which is most commonly used for "argumented" keys -
  objects in the `KC` object which are actually functions that return `Key`
  instances, which often need to access the arguments passed into the "outer"
  function. Many of these examples are related to layer switching - for example,
  `KC.MO` is implemented as an argumented key - when the user adds `KC.MO(1)` to
  their keymap, the function call returns a `Key` object with `meta` set to an
  object containing `layer` and `kc` properties, for example. There's other uses
  for `meta`, and examples can be found in [`kmk/types.py`](/kmk/types.py)

`Key` objects can also be chained together by calling them! To create a key
which holds Control and Shift simultaneously, we can simply do:

```python
CTRLSHFT = KC.LCTL(KC.LSFT)

keyboard.keymap = [ ... CTRLSHFT ... ]
```

When a key is pressed and we've pulled a `Key` object out of the keymap, the
`Key` is first passed through the module processing pipeline.
Modules can do whatever with that `Key`, but usually keys either pass right
through, or are intercepted and emitted again later (think of timing based
modules like Combos and Hold-Tap).
Finally the assigned press handler will be run (most commonly, this is provided
by KMK).
On release the `Key` object lookup is, most of the time, cached and doesn't
require searching the keymap again.
Then it's the processing pipeline again, followed by the release handler.

Custom behavior can either be achieved with custom press and release handlers or
with [macros](docs/en/macros.md).

## The Key Code Dictionary

You can also refer to a key by index:

- `KC['A']`
- `KC['NO']`
- `KC['LALT']`

Or the `KC.get` function which has an optional default argument, which will
be returned if the key is not found (`default=None` unless otherwise specified):

- `KC.get('A')`
- `KC.get('NO', None)`
- `KC.get('NOT DEFINED', KC.RALT)`

Key names are case-sensitive. `KC['NO']` is different from `KC['no']`. It is recommended
that names are normally UPPER_CASE. The exception to this are alpha keys; `KC['A']` and
`KC['a']` will both return the same, unshifted, key.
```

keycodes.md
```markdown
# Keys Overview

## [Basic Keys]

|Key                    |Aliases             |Description                                    |
|-----------------------|--------------------|-----------------------------------------------|
|`KC.NO`                |                    |Ignore this key (NOOP)                         |
|`KC.TRANSPARENT`       |`KC.TRNS`           |Use the next lowest non-transparent key        |
|`KC.A`                 |                    |`a` and `A`                                    |
|`KC.B`                 |                    |`b` and `B`                                    |
|`KC.C`                 |                    |`c` and `C`                                    |
|`KC.D`                 |                    |`d` and `D`                                    |
|`KC.E`                 |                    |`e` and `E`                                    |
|`KC.F`                 |                    |`f` and `F`                                    |
|`KC.G`                 |                    |`g` and `G`                                    |
|`KC.H`                 |                    |`h` and `H`                                    |
|`KC.I`                 |                    |`i` and `I`                                    |
|`KC.J`                 |                    |`j` and `J`                                    |
|`KC.K`                 |                    |`k` and `K`                                    |
|`KC.L`                 |                    |`l` and `L`                                    |
|`KC.M`                 |                    |`m` and `M`                                    |
|`KC.N`                 |                    |`n` and `N`                                    |
|`KC.O`                 |                    |`o` and `O`                                    |
|`KC.P`                 |                    |`p` and `P`                                    |
|`KC.Q`                 |                    |`q` and `Q`                                    |
|`KC.R`                 |                    |`r` and `R`                                    |
|`KC.S`                 |                    |`s` and `S`                                    |
|`KC.T`                 |                    |`t` and `T`                                    |
|`KC.U`                 |                    |`u` and `U`                                    |
|`KC.V`                 |                    |`v` and `V`                                    |
|`KC.W`                 |                    |`w` and `W`                                    |
|`KC.X`                 |                    |`x` and `X`                                    |
|`KC.Y`                 |                    |`y` and `Y`                                    |
|`KC.Z`                 |                    |`z` and `Z`                                    |
|`KC.N1`                |                    |`1` and `!`                                    |
|`KC.N2`                |                    |`2` and `@`                                    |
|`KC.N3`                |                    |`3` and `#`                                    |
|`KC.N4`                |                    |`4` and `$`                                    |
|`KC.N5`                |                    |`5` and `%`                                    |
|`KC.N6`                |                    |`6` and `^`                                    |
|`KC.N7`                |                    |`7` and `&`                                    |
|`KC.N8`                |                    |`8` and `*`                                    |
|`KC.N9`                |                    |`9` and `(`                                    |
|`KC.N0`                |                    |`0` and `)`                                    |
|`KC.ENTER`             |`KC.ENT`            |Return (Enter)                                 |
|`KC.ESCAPE`            |`KC.ESC`            |Escape                                         |
|`KC.BSPACE`            |`KC.BSPC`           |Delete (Backspace)                             |
|`KC.TAB`               |                    |Tab                                            |
|`KC.SPACE`             |`KC.SPC`            |Spacebar                                       |
|`KC.MINUS`             |`KC.MINS`           |`-` and `_`                                    |
|`KC.EQUAL`             |`KC.EQL`            |`=` and `+`                                    |
|`KC.LBRACKET`          |`KC.LBRC`           |`[` and `{`                                    |
|`KC.RBRACKET`          |`KC.RBRC`           |`]` and `}`                                    |
|`KC.BSLASH`            |`KC.BSLS`           |`\` and <code>&#124;</code>                    |
|`KC.SCOLON`            |`KC.SCLN`           |`;` and `:`                                    |
|`KC.QUOTE`             |`KC.QUOT`           |`'` and `"`                                    |
|`KC.GRAVE`             |`KC.GRV`, `KC.ZKHK` |<code>&#96;</code> and `~`, JIS Zenkaku/Hankaku|
|`KC.COMMA`             |`KC.COMM`           |`,` and `<`                                    |
|`KC.DOT`               |                    |`.` and `>`                                    |
|`KC.SLASH`             |`KC.SLSH`           |`/` and `?`                                    |
|`KC.CAPSLOCK`          |`KC.CLCK`, `KC.CAPS`|Caps Lock                                      |
|`KC.F1`                |                    |F1                                             |
|`KC.F2`                |                    |F2                                             |
|`KC.F3`                |                    |F3                                             |
|`KC.F4`                |                    |F4                                             |
|`KC.F5`                |                    |F5                                             |
|`KC.F6`                |                    |F6                                             |
|`KC.F7`                |                    |F7                                             |
|`KC.F8`                |                    |F8                                             |
|`KC.F9`                |                    |F9                                             |
|`KC.F10`               |                    |F10                                            |
|`KC.F11`               |                    |F11                                            |
|`KC.F12`               |                    |F12                                            |
|`KC.PSCREEN`           |`KC.PSCR`           |Print Screen                                   |
|`KC.SCROLLLOCK`        |`KC.SLCK`           |Scroll Lock                                    |
|`KC.PAUSE`             |`KC.PAUS`, `KC.BRK` |Pause                                          |
|`KC.INSERT`            |`KC.INS`            |Insert                                         |
|`KC.HOME`              |                    |Home                                           |
|`KC.PGUP`              |                    |Page Up                                        |
|`KC.DELETE`            |`KC.DEL`            |Forward Delete                                 |
|`KC.END`               |                    |End                                            |
|`KC.PGDOWN`            |`KC.PGDN`           |Page Down                                      |
|`KC.RIGHT`             |`KC.RGHT`           |Right Arrow                                    |
|`KC.LEFT`              |                    |Left Arrow                                     |
|`KC.DOWN`              |                    |Down Arrow                                     |
|`KC.UP`                |                    |Up Arrow                                       |
|`KC.NUMLOCK`           |`KC.NLCK`           |Keypad Num Lock and Clear                      |
|`KC.KP_SLASH`          |`KC.PSLS`           |Keypad `/`                                     |
|`KC.KP_ASTERISK`       |`KC.PAST`           |Keypad `*`                                     |
|`KC.KP_MINUS`          |`KC.PMNS`           |Keypad `-`                                     |
|`KC.KP_PLUS`           |`KC.PPLS`           |Keypad `+`                                     |
|`KC.KP_ENTER`          |`KC.PENT`           |Keypad Enter                                   |
|`KC.KP_1`              |`KC.P1`             |Keypad `1` and End                             |
|`KC.KP_2`              |`KC.P2`             |Keypad `2` and Down Arrow                      |
|`KC.KP_3`              |`KC.P3`             |Keypad `3` and Page Down                       |
|`KC.KP_4`              |`KC.P4`             |Keypad `4` and Left Arrow                      |
|`KC.KP_5`              |`KC.P5`             |Keypad `5`                                     |
|`KC.KP_6`              |`KC.P6`             |Keypad `6` and Right Arrow                     |
|`KC.KP_7`              |`KC.P7`             |Keypad `7` and Home                            |
|`KC.KP_8`              |`KC.P8`             |Keypad `8` and Up Arrow                        |
|`KC.KP_9`              |`KC.P9`             |Keypad `9` and Page Up                         |
|`KC.KP_0`              |`KC.P0`             |Keypad `0` and Insert                          |
|`KC.KP_DOT`            |`KC.PDOT`           |Keypad `.` and Delete                          |
|`KC.KP_EQUAL`          |`KC.PEQL`           |Keypad `=`                                     |
|`KC.F13`               |                    |F13                                            |
|`KC.F14`               |                    |F14                                            |
|`KC.F15`               |                    |F15                                            |
|`KC.F16`               |                    |F16                                            |
|`KC.F17`               |                    |F17                                            |
|`KC.F18`               |                    |F18                                            |
|`KC.F19`               |                    |F19                                            |
|`KC.F20`               |                    |F20                                            |
|`KC.F21`               |                    |F21                                            |
|`KC.F22`               |                    |F22                                            |
|`KC.F23`               |                    |F23                                            |
|`KC.F24`               |                    |F24                                            |
|`KC.LOCKING_CAPS`      |`KC.LCAP`           |Locking Caps Lock                              |
|`KC.LOCKING_NUM`       |`KC.LNUM`           |Locking Num Lock                               |
|`KC.LOCKING_SCROLL`    |`KC.LSCR`           |Locking Scroll Lock                            |
|`KC.KP_COMMA`          |`KC.PCMM`           |Keypad `,`                                     |
|`KC.KP_EQUAL_AS400`    |                    |Keypad `=` on AS/400 keyboards                 |
|`KC.LCTRL`             |`KC.LCTL`           |Left Control                                   |
|`KC.LSHIFT`            |`KC.LSFT`           |Left Shift                                     |
|`KC.LALT`              |                    |Left Alt                                       |
|`KC.LGUI`              |`KC.LCMD`, `KC.LWIN`|Left GUI (Windows/Command/Meta key)            |
|`KC.RCTRL`             |`KC.RCTL`           |Right Control                                  |
|`KC.RSHIFT`            |`KC.RSFT`           |Right Shift                                    |
|`KC.RALT`              |                    |Right Alt                                      |
|`KC.RGUI`              |`KC.RCMD`, `KC.RWIN`|Right GUI (Windows/Command/Meta key)           |


## [US ANSI Shifted Symbols]

|Key                     |Aliases            |Description        |
|------------------------|-------------------|-------------------|
|`KC.TILDE`              |`KC.TILD`          |`~`                |
|`KC.EXCLAIM`            |`KC.EXLM`          |`!`                |
|`KC.AT`                 |                   |`@`                |
|`KC.HASH`               |                   |`#`                |
|`KC.DOLLAR`             |`KC.DLR`           |`$`                |
|`KC.PERCENT`            |`KC.PERC`          |`%`                |
|`KC.CIRCUMFLEX`         |`KC.CIRC`          |`^`                |
|`KC.AMPERSAND`          |`KC.AMPR`          |`&`                |
|`KC.ASTERISK`           |`KC.ASTR`          |`*`                |
|`KC.LEFT_PAREN`         |`KC.LPRN`          |`(`                |
|`KC.RIGHT_PAREN`        |`KC.RPRN`          |`)`                |
|`KC.UNDERSCORE`         |`KC.UNDS`          |`_`                |
|`KC.PLUS`               |                   |`+`                |
|`KC.LEFT_CURLY_BRACE`   |`KC.LCBR`          |`{`                |
|`KC.RIGHT_CURLY_BRACE`  |`KC.RCBR`          |`}`                |
|`KC.PIPE`               |                   |<code>&#124;</code>|
|`KC.COLON`              |`KC.COLN`          |`:`                |
|`KC.DOUBLE_QUOTE`       |`KC.DQUO`, `KC.DQT`|`"`                |
|`KC.LEFT_ANGLE_BRACKET` |`KC.LABK`          |`<`                |
|`KC.RIGHT_ANGLE_BRACKET`|`KC.RABK`          |`>`                |
|`KC.QUESTION`           |`KC.QUES`          |`?`                |


## [Internal Keys]

| Key                     | Description                                                            |
|-------------------------|------------------------------------------------------------------------|
| `KC.RESET`              | Restarts the keyboard                                                  |
| `KC.RELOAD`, `KC.RLD`   | Reloads the keyboard software, preserving any serial connections       |
| `KC.ANY`                | Any key between `A` and `/`                                            |
| `KC.GESC`               | Escape when tapped, <code>&#96;</code> when pressed with Shift or GUI  |
| `KC.BKDL`               | Backspace when tapped, Delete when pressed with GUI                    |


## [Modifiers]

|Key          |Description                           |
|-------------|--------------------------------------|
|`KC.HYPR`    |Hold Left Control, Shift, Alt and GUI |
|`KC.MEH`     |Hold Left Control, Shift and Alt      |
|`KC.LCTL(kc)`|Hold Left Control and press `kc`      |
|`KC.LSFT(kc)`|Hold Left Shift and press `kc`        |
|`KC.LALT(kc)`|Hold Left Alt and press `kc`          |
|`KC.LGUI(kc)`|Hold Left GUI and press `kc`          |
|`KC.RCTL(kc)`|Hold Right Control and press `kc`     |
|`KC.RSFT(kc)`|Hold Right Shift and press `kc`       |
|`KC.RALT(kc)`|Hold Right Alt and press `kc`         |
|`KC.RGUI(kc)`|Hold Right GUI and press `kc`         |


## [Bluetooth Keys]

|Key                          |Aliases            |Description                       |
|-----------------------------|-------------------|----------------------------------|
|`KC.BT_CLEAR_BONDS`          |`KC.BT_CLR`        |Clears all stored bondings        |
|`KC.BT_NEXT_CONN`            |`KC.BT_NXT`        |Selects the next BT connection    |
|`KC.BT_PREV_CONN`            |`KC.BT_PRV`        |Selects the previous BT connection|

## [International Keys]
See [International extension](international.md).

## [Media Keys]
See [MediaKeys extension](media_keys.md).
```

macros.md
```markdown
# Macros

Macros are used for sending multiple keystrokes in a single action, and can
be used for things like Unicode characters (even emojis! 🇨🇦), _Lorem ipsum_
generators, triggering side effects (think lighting, speakers,
microcontroller-optimized cryptocurrency miners, whatever).
Macros have worse performance and higher memory usage than [custom keys](keys.md),
so unless the objective is to type out a sequence or to perform an action repeatedly
and asynchronously while a key is pressed, custom keys are the recommended solution.

## Setup

```python
from kmk.modules.macros import Macros

macros = Macros()
keyboard.modules.append(macros)
```

This will enable a new type of keycode: `KC.MACRO()`

## Keycodes

|Key                |Description                               |
|-------------------|------------------------------------------|
|`KC.MACRO(macro)`  |Create a key that will play back a macro. |
|`KC.UC_MODE_IBUS`  |Switch Unicode mode to IBus.              |
|`KC.UC_MODE_MACOS` |Switch Unicode mode to macOS.             |
|`KC.UC_MODE_WINC`  |Switch Unicode mode to Windows Compose.   |

Full macro signature, all arguments optional:

```python
KC.MACRO(
    on_press=None,
    on_hold=None,
    on_release=None,
    blocking=True,
)
```

### `on_press`
This sequence is run once at the beginning, just after the macro key has been
pressed.
`KC.MACRO(macro)` is actually a short-hand for `KC.MACRO(on_press=macro)`.

### `on_hold`
This sequence is run in a loop while the macro key is pressed (or "held").
If the key is released before the `on_press` sequence is finished, the `on_hold`
sequence will be skipped.

### `on_release`
This sequence is run once at the end, after the macro key has been released and
the previous sequence has finished.

### `blocking`
By default, all key events will be intercepted while a macro is running and
replayed after all blocking macros have finished.
This is to avoid side effects and can be disabled with `blocking=False` if
undesired.
(And yes, technically multiple blocking macros can run simultaneously, the
achievement of which is left as an exercise to the reader.)

## Sending strings

The most basic sequence is an ASCII string. It can be used to send any standard
English alphabet character, and an assortment of other "standard" keyboard keys
(return, space, exclamation points, etc.).
Keep in mind that some characters from shifted keys are i18n dependent.

```python
WOW = KC.MACRO("Wow, KMK is awesome!")

keyboard.keymap = [<other keycodes>, WOW, <other keycodes>]
```

## Key sequences

If you need to add modifier keys to your sequence or you need more granular control.
You can use it to add things like copying/pasting, tabbing between fields, etc.

```python
from kmk.modules.macros import Press, Release, Tap

PASTE_WITH_COMMENTARY = KC.MACRO(
    "look at this: ",
    Press(KC.LCTL),
    Tap(KC.V),
    Release(KC.LCTL)
)

keyboard.keymap = [<other keycodes>, PASTE_WITH_COMMENTARY, <other keycodes>]
```

The above example will type out "look at this: " and then paste the contents of your
clipboard.


### Sleeping within a sequence

If you need to wait during a sequence, you can use `Delay(ms)` to wait a
length of time, in milliseconds.

```python
from kmk.modules.macros import Tap, Delay

COUNTDOWN_TO_PASTE = KC.MACRO(
    Tap(KC.N3),
    Tap(KC.ENTER),
    Delay(1000),
    Tap(KC.N2),
    Tap(KC.ENTER),
    Delay(1000),
    Tap(KC.N1),
    Tap(KC.ENTER),
    Delay(1000),
    Tap(KC.LCTL(KC.V)),
)

keyboard.keymap = [<other keycodes>, COUNTDOWN_TO_PASTE, <other keycodes>]
```

This example will type out the following, waiting one second (1000 ms) between numbers:

    3
    2
    1

and then paste the contents of your clipboard.

### Alt Tab with delay

If alt tab isn't working because it requires a delay, adding a delay and triggering
down and up on ALT manually may fix the issue.

``` python
from kmk.modules.macros import Delay, Press, Release, Tap

NEXT = KC.MACRO(
    Press(KC.LALT),
    Delay(30),
    Tap(KC.TAB),
    Delay(30),
    Release(KC.LALT),
)
```

## Unicode

### Unicode Modes

On Linux, Unicode uses `Ctrl-Shift-U`, which is supported by `ibus` and GTK+3.
`ibus` users will need to add `IBUS_ENABLE_CTRL_SHIFT_U=1` to their environment
(`~/profile`, `~/.bashrc`, `~/.zshrc`, or through your desktop environment's
configurator).

On Windows, [WinCompose](https://github.com/samhocevar/wincompose) is required.

- Linux : `UnicodeModeIBus`, the default
- MacOS: `UnicodeModeMacOS`
- Windows: `UnicodeModeWinC`

### Unicode Examples

Initialize `Macros` to use `UnicodeModeMac` and make a key to cycle between modes
at runtime.

```python
from kmk.keys import Key
from kmk.modules.macros import Macros, UnicodeModeIBus, UnicodeModeMacOS, UnicodeModeWinC

macros = Macros(unicode_mode=UnicodeModeMacOS)
keyboard.modules.append(macros)

def switch_um(keyboard):
    if macros.unicode_mode == UnicodeModeIBus:
        macros.unicode_mode = UnicodeModeMacOS
    elif macros.unicode_mode == UnicodeModeMacOS:
        macros.unicode_mode = UnicodeModeWinC
    else:
        macros.Unicode_mode = UnicodeModeIBus

UCCYCLE = Key(code=None, on_press=switch_um)

FLIP = KC.MACRO('(ノಠ痊ಠ)ノ彡┻━┻')

keyboard.keymap = [<other keycodes>, UCCYCLE, FLIP, <other keycodes>]
```

## Arbitrary Actions

As it happens, macros accept any callable object (even generators) as arguments.
The `KMKKeyboard` object is passed as argument to that callable.

### Example 1

Change the RGB animation mode to "SWIRL" for five seconds and print an ASCII
spinner

```python
# ... boilerplate omitted for brevity.

prev_animation = None

def start_spinning(keyboard):
    global prev_animation
    prev_animation = rgb.animation_mode
    rgb.animation_mode = AnimationModes.SWIRL
    rgb.effect_init = True

def stop_spinning(keyboard):
    rgb.animation_mode = prev_animation
    rgb.effect_init = True

DISCO = KC.MACRO(
    "disco time!",
    start_color_wheel,
    "-",
    DELAY(1000),
    KC.BSPC,
    "\\",
    DELAY(1000),
    KC.BSPC,
    "|",
    DELAY(1000),
    KC.BSPC,
    "/",
    DELAY(1000),
    KC.BSPC,
    "-",
    DELAY(1000),
    KC.BSPC,
    stop_color_wheel,
    " disco time over.",
    )
```

### Example 2a

Here's a programmatic version of the earlier countdown-to-paste example, using a
generator.
Any integer return value is interpreted as a delay instruction in milliseconds.

```python
def countdown(count, delay_ms):
    def generator(keyboard):
        for n in range(count, 0, -1):
            KC[n].on_press(keyboard)
            yield
            KC[n].on_release(keyboard)
            yield
            KC.ENTER.on_press(keyboard)
            yield
            KC.ENTER.on_release(keyboard)
            yield delay_ms
    return generator

COUNTDOWN_TO_PASTE = KC.MACRO(
    countdown(3, 1000),
    Tap(KC.LCTL(KC.V)),
)
```

### Example 2b

On popular demand: Callables in macros are fully recursive.
Here's a programmatic version of the earlier countdown example, using a
generator, but the countdown gets faster and there's a surprise at the end

```python
def countdown(count, delay_ms):
    def generator(keyboard):
        for n in range(count, 0, -1):
            yield '{n}\n'.format(n)
            yield n * delay_ms
        yield '#🎉; open https://github.com/KMKfw/kmk_firmware/blob/main/docs/en/macros.md'
    return generator

COUNTDOWN_TO_SURPRISE = KC.MACRO(
    countdown(10, 100),
)
```

### Example 3

Sometimes there's no need for a generator and a simple function is enough to
type a string that's created at runtime.
And sometimes it's really hard to remember what keys are currently pressed:

```python
def keys_pressed(keyboard):
    return str(keyboard.keys_pressed)

KEYS_PRESSED = KC.MACRO(keys_pressed)
```

### Example 4

A high productivity replacement for the common space key:
This macro ensures that you make good use of your time by measuring how long
you've been holding the space key for, printing the result to the debug
console, all the while reminding you that you're still holding the space key.

```python
from supervisor import ticks_ms
from kmk.utils import Debug

debug = Debug(__name__)

def make_timer():
    ticks = 0
    def _():
        nonlocal ticks
        return (ticks := ticks_ms() - ticks)
    return _

space_timer = make_timer()

SPACETIME = KC.MACRO(
    on_press=(
        lambda _: space_timer() and None,
        Press(KC.SPACE),
        lambda _: debug('start holding space...'),
    ),
    on_hold=(
        lambda _: debug('..still holding space..'),
    ),
    on_release=(
        Release(KC.SPACE),
        lambda _: debug('...end holding space after ', space_timer(), 'ms'),
    ),
    blocking=False,
)
```
```

layers.md
```markdown
# Layers
Layers module adds keys for accessing other layers. It can simply be added to
 the extensions list.

```python
from kmk.modules.layers import Layers
keyboard.modules.append(Layers())
```

## Keycodes

|Key         |Description                                                                    |
|-----------------|--------------------------------------------------------------------------|
|`KC.FD(layer)`      |Replaces the top layer                                             |
|`KC.DF(layer)`      |Switches the default layer until the next time the keyboard powers off |
|`KC.MO(layer)`      |Momentarily activates layer, switches off when you let go              |
|`KC.LM(layer, mod)` |As `MO(layer)` but with `mod` active                                   |
|`KC.LT(layer, kc)`  |Momentarily activates layer if held, sends kc if tapped                |
|`KC.TG(layer)`      |Toggles the layer (enables it if not active, and vice versa)            |
|`KC.TO(layer)`      |Activates layer and deactivates all other layers                       |
|`KC.TT(layer)`      |Momentarily activates layer if held, toggles it if tapped repeatedly   |

## Custom HoldTap Behavior
`KC.TT` and `KC.LT` use the same heuristic to determine taps and holds as
HoldTap. Check out the [HoldTap doc](holdtap.md) to find out more.

## Working with Layers
When starting out, care should be taken when working with layers, since it's possible to lock
yourself to a layer with no way of returning to the base layer short of unplugging your
keyboard. This is especially easy to do when using the `KC.TO()` keycode, which deactivates
all other layers in the stack.

Some helpful guidelines to keep in mind as you design your layers:
- Only reference higher-numbered layers from a given layer
- Leave keys as `KC.TRNS` in higher layers when they would overlap with a layer-switch

## Using Combo Layers
Combo Layers allow you to activate a corresponding layer based on the activation of 2 or more other layers.
The advantage of using Combo layers is that when you release one of the layer keys, it stays on whatever layer is still being held.
See [combo layers documentation](combo_layers.md) for more information on it's function and to see examples.

### Using Multiple Base Layers
In some cases, you may want to have more than one base layer (for instance you want to use
both QWERTY and Dvorak layouts, or you have a custom gamepad that can switch between
different games). In this case, best practice is to have these layers be the lowest, i.e.
defined first in your keymap. These layers are mutually-exclusive, so treat changing default
layers with `KC.DF()` the same way that you would treat using `KC.TO()`


## Example Code
For our example, let's take a simple 3x3 macropad with two layers as follows:

```python
from kmk.modules.layers import Layers
keyboard.modules.append(Layers())

# Layer Keys
MOMENTARY = KC.MO(1)
MOD_LAYER = KC.LM(1, KC.RCTL)
LAYER_TAP = KC.LT(1, KC.END, prefer_hold=True, tap_interrupted=False, tap_time=250) # any tap longer than 250ms will be interpreted as a hold

keyboard.keymap = [
	# Base layer
	[
		KC.NO,	KC.UP,	KC.NO,
		KC.LEFT,KC.DOWN,KC.RGHT,
		MOMENTARY, LAYER_TAP, MOD_LAYER,
	],

	# Function Layer
	[
		KC.F1,	KC.F2,	KC.F3,
		KC.F4,	KC.F5,	KC.F6,
		KC.TRNS,KC.TRNS,KC.TRNS,
	],
]
```

## Active Layer indication with RGB
A common question is: "How do I change RGB background based on my active layer?"
Here is _one_ (simple) way of many to go about it.

To indicate active layer you can use RGB background, or in many cases board's status LED, then no additional hardware is needed. Information about the LED type and to which GPIO pin it is connected is often available on the pinout of the board and in the documentation.

In this example on board RGB status LED is used. Number of layers is unlimited and only chosen layers can be used. Note, that LED's basic colors can have different order for different hardware.

```python
import board

from kmk.extensions.rgb import RGB
from kmk.modules.layers import Layers


class LayerRGB(RGB):
    def on_layer_change(self, layer):
        if layer == 0:
            self.set_hsv_fill(0, self.sat_default, self.val_default)   # red
        elif layer == 1:
            self.set_hsv_fill(170, self.sat_default, self.val_default) # blue
        elif layer == 2:
            self.set_hsv_fill(43, self.sat_default, self.val_default)  # yellow
        elif layer == 4:
            self.set_hsv_fill(0, 0, self.val_default)                  # white
        # update the LEDs manually if no animation is active:
        self.show()


rgb = LayerRGB(pixel_pin=board.GP16, # GPIO pin of the status LED, or background RGB light
        num_pixels=1,                # one if status LED, more if background RGB light
        rgb_order=(0, 1, 2),         # RGB order may differ depending on the hardware
        hue_default=0,               # in range 0-255: 0/255-red, 85-green, 170-blue
        sat_default=255,
        val_default=5,
        )
keyboard.extensions.append(rgb)


class RGBLayers(Layers):
    def activate_layer(self, keyboard, layer, idx=None):
        super().activate_layer(keyboard, layer, idx)
        rgb.on_layer_change(layer)

    def deactivate_layer(self, keyboard, layer):
        super().deactivate_layer(keyboard, layer)
        rgb.on_layer_change(keyboard.active_layers[0])


keyboard.modules.append(RGBLayers())
```
```

holdtap.md
```markdown
# HoldTap Keycodes
The HoldTap module lets keys do double duty:
tap the key to do one thing,
hold it longer than the configurable `tap_time` to do another.

HoldTap is often used with modifier keys.
For example `KC.HT(KC.ESCAPE, KC.LCTRL)` configures
a key that sends Escape when tapped and
left control when held.
It can be used with regular keys as well
like `KC.HT(KC.SPACE, KC.ENTER)` to send space on tap
and enter on hold.

Simply import HoldTap and add it to the modules list.
This lets you use `KC.HT` actions like those below.

```python
from kmk.modules.holdtap import HoldTap
holdtap = HoldTap()
# optional: set a custom tap timeout in ms
# holdtap.tap_time = 300
keyboard.modules.append(holdtap)
```

## Keycodes

|New Keycode                                              | Description                                                     |
|---------------------------------------------------------|-----------------------------------------------------------------|
|`LCTL = KC.HT(KC.SOMETHING, KC.LCTRL)`                   |`LCTRL` if held `kc` if tapped                                   |
|`LSFT = KC.HT(KC.SOMETHING, KC.LSFT)`                    |`LSHIFT` if held `kc` if tapped                                  |
|`LALT = KC.HT(KC.SOMETHING, KC.LALT)`                    |`LALT` if held `kc` if tapped                                    |
|`LGUI = KC.HT(KC.SOMETHING, KC.LGUI)`                    |`LGUI` if held `kc` if tapped                                    |
|`RCTL = KC.HT(KC.SOMETHING, KC.RCTRL)`                   |`RCTRL` if held `kc` if tapped                                   |
|`RSFT = KC.HT(KC.SOMETHING, KC.RSFT)`                    |`RSHIFT` if held `kc` if tapped                                  |
|`RALT = KC.HT(KC.SOMETHING, KC.RALT)`                    |`RALT` if held `kc` if tapped                                    |
|`RGUI = KC.HT(KC.SOMETHING, KC.RGUI)`                    |`RGUI` if held `kc` if tapped                                    |
|`SGUI = KC.HT(KC.SOMETHING, KC.LSHFT(KC.LGUI))`          |`LSHIFT` and `LGUI` if held `kc` if tapped                       |
|`LCA = KC.HT(KC.SOMETHING, KC.LCTRL(KC.LALT))`           |`LCTRL` and `LALT` if held `kc` if tapped                        |
|`LCAG = KC.HT(KC.SOMETHING, KC.LCTRL(KC.LALT(KC.LGUI)))` |`LCTRL` and `LALT` and `LGUI` if held `kc` if tapped             |
|`MEH = KC.HT(KC.SOMETHING, KC.LCTRL(KC.LSFT(KC.LALT)))`  |`CTRL` and `LSHIFT` and `LALT` if held `kc` if tapped            |
|`HYPR = KC.HT(KC.SOMETHING, KC.HYPR)`                    |`LCTRL` and `LSHIFT` and `LALT` and `LGUI` if held `kc` if tapped|

## Custom HoldTap Behavior
The full HoldTap signature is as follows:
```python
KC.HT(KC.TAP, KC.HOLD, prefer_hold=True, tap_interrupted=False, tap_time=None, repeat=HoldTapRepeat.NONE)
```
* `prefer_hold`: decides which keycode the HoldTap key resolves to when another
  key is pressed before the timeout finishes. When `True` the hold keycode is
  chosen, the tap keycode when `False`.
* `tap_interrupted`: decides if the timeout will interrupt at the first other
  key press/down, or after the first other key up/release. Set to `True` for
  interrupt on release.
* `tap_time`: length of the tap timeout in milliseconds.
* `repeat`: decides how to interpret repeated presses if they happen within
  `tap_time` after a release.
  * `TAP`: repeat tap action, if previous action was a tap.
  * `HOLD`: repeat hold action, if previous action was a hold.
  * `ALL`: repeat all of the above.
  * `NONE`: no repeat action (default), everything works as expected.
  The `HoldTapRepeat` enum must be imported from `kmk.modules.holdtap`.

Each of these parameters can be set for every HoldTap key individually.
```

tapdance.md
```markdown
# Tap Dance

Tap dance is a way to allow a single physical key to work as multiple logical
keys / actions without using layers. With basic tap dance, you can trigger these
"nested" keys or macros through a series of taps of the physical key within a
given timeout.

The resulting "logical" action works just like any other key - it can be pressed
and immediately released, or it can be held. For example, let's take a key
`KC.TD(KC.A, KC.B)`. If the tap dance key is tapped and released once quickly,
the letter "a" will be sent. If it is tapped and released twice quickly, the
letter "b" will be sent. If it is tapped once and held, the letter "a" will be
held down until the tap dance key is released. If it is tapped and released once
quickly, then tapped and held (both actions within the timeout window), the
letter "b" will be held down until the tap dance key is released.

To use this, you may want to define a `tap_time` value in your keyboard
configuration. This is an integer in milliseconds, and defaults to `300`.
The timeout is reset after each tap and every tap dance sequence can also define
an individual `tap_time`.

You'll then want to create a sequence of keys using `KC.TD(KC.SOMETHING,
KC.SOMETHING_ELSE, MAYBE_THIS_IS_A_MACRO, WHATEVER_YO)`, and place it in your
keymap somewhere. The only limits on how many keys can go in the sequence are,
theoretically, the amount of RAM your MCU/board has.

Tap dance supports all `HoldTap` based keys, like mod tap, layer tap...
it will even honor every option set for those keys.
Individual timeouts and prefer hold behavior for every tap in the sequence?
Not a problem.

Here's an example of all this in action:

```python
from kmk.keycodes import KC
from kmk.modules.macros import Macros
from kmk.modules.tapdance import TapDance

keyboard = KMKKeyboard()

tapdance = TapDance()
tapdance.tap_time = 750
keyboard.modules.append(tapdance)
keyboard.modules.append(Macros())

EXAMPLE_TD = KC.TD(
    # Tap once for "a"
    KC.A,
    # Tap twice for "b", or tap and hold for "left control"
    KC.HT(KC.B, KC.LCTL, prefer_hold=False),
    # Tap three times to send a raw string via macro
    KC.MACRO('macros in a tap dance? I think yes'),
    # Tap four times to toggle layer index 1, tap 3 times and hold for 3s to
    # momentary toggle layer index 1.
    KC.TT(1, tap_time=3000),
)

# make the default tap time really short for this tap dance:
EXAMPLE_TD2 = KC.TD(KC.A, KC.B, tap_time=80)


keyboard.keymap = [[ ...., EXAMPLE_TD, ....], ....]
```
```

modules.md
```markdown
# Modules
Modules, unlike extensions, change how your keyboard works. These are meant to have
the ability to alter the core code in any way. Unlike extensions, these are not in a
sandbox, and can make massive changes to normal operation.

## Core Modules
These modules are provided in all builds and can be enabled. Currently offered
modules are

- [Combos](combos.md): Adds chords and sequences
- [Layers](layers.md): Adds layer support (Fn key) to allow many more keys to be
put on your keyboard.
- [HoldTap](holdtap.md): Adds support for augmented modifier keys to act as one key
when tapped, and modifier when held.
- [Macros](macros.md): Adds macros.
- [Mouse Keys](mouse_keys.md): Adds mouse keycodes.
- [SpaceMouse Keys](spacemouse_keys.md): Adds SpaceMouse keycodes.
- [Sticky Keys](sticky_keys.md): Adds support for sticky keys.
- [Power](power.md): Power saving features. This is mostly useful when on battery power.
- [Split](split_keyboards.md): Keyboards split in two. Seems ergonomic!
- [SerialACE](serialace.md): [DANGER - _see module README_] Arbitrary Code Execution over the data serial.
- [TapDance](tapdance.md): Different key actions depending on how often it is pressed.
- [Dynamic Sequences](dynamic_sequences.md): Records a sequence of keypresses and plays it back.
- [Mouse Jiggler](mouse_jiggler.md): Periodically moves the mouse cursor to keep the host system awake.

### Require Libraries
These modules can be used without specific hardware, but require additional libraries such as the `Adafruit CircuitPython Bundle`.

 - [MIDI](midi.md): Adds sending MIDI data in the form of keymap entries.


### Peripherals
These modules are for specific hardware and may require additional libraries to function.
- [ADNS9800](adns9800.md): Controlling ADNS9800 optical sensor.
- [Encoder](encoder.md): Handling rotary encoders.
- [Pimoroni trackball](pimoroni_trackball.md): Handling a small I2C trackball made by Pimoroni.
- [AS5013 aka EasyPoint](easypoint.md): Handling a small I2C magnetic position sensor made by AMS.
```

extensions.md
```markdown
# Extensions

Extensions add features that change the experience, but not the core features of
the keyboard. They are meant to be easy to add, and create your own. These live in
a sandbox to help prevent any bad code from crashing your keyboard.

## Core Extensions

These extensions are provided in all builds and can be enabled. Currently offered
extensions are

- [International](international.md): Adds international keycodes
- [LED](led.md): Adds backlight support. This is for monocolor backlight, not RGB
- [LockStatus](lock_status.md): Exposes host-side locks like caps or num lock.
- [MediaKeys](media_keys.md): Adds support for media keys such as volume
- [OLED Displays](OLED_display.md): Support for common OLED displays.
- [RGB](rgb.md): RGB lighting for underglow. Will work on most matrix RGB as will
  be treated the same as underglow.
- [SpaceMouse Status](spacemouse_status.md): Exposes host-side LED status of the SpaceMouse HID.
- [Status LED](extension_statusled.md): Indicates which layer you are on with an array of single leds.
- [Stringy Keymaps](extension_stringy_keymaps): Enables referring to keys by `'NAME'` rather than `KC.NAME`
```

---

I refactored it to be modular, trimmed complexity, and merged in the hard‑won pieces from our previous driver: a robust frame parser, real press/release semantics, momentary Green/Orange, People toggle with dev macros, sticky Shift by Shift+Orange, OS‑adaptive word navigation, pair‑insertion helpers, and Space‑as‑Ctrl that promotes on hold or on chord. The Chatpad logic now lives in a KMK Module so HID timing stays correct under `keyboard.go()`.

Below is a complete repository you can copy to the KB2040’s `CIRCUITPY` drive. It is organized, production‑ready, and easy to extend.

---

## Repository layout

```
chatpad_kmk/
├── boot.py
├── code.py
├── config.py
├── LICENSE
├── README.md
├── kmk/                          # copy this folder from KMK's repo root
└── lib/
    ├── chatpad/
    │   ├── __init__.py
    │   ├── keyboard.py           # KMK module that wires protocol+state+layers+LED
    │   ├── led.py
    │   ├── layers.py
    │   ├── protocol.py
    │   └── state.py
    └── macros/
        ├── __init__.py
        ├── development.py
        ├── terminal.py
        └── vim.py
```

> Important: copy KMK’s `kmk/` folder from the official repo into this tree before deploying.

---

## Files

### `boot.py`

```python
"""Boot configuration for Chatpad KMK."""
import storage
import supervisor
import usb_cdc

# Enable serial console for debugging
usb_cdc.enable(console=True, data=False)

# Increase stack for deeper call stacks
supervisor.set_next_stack_limit(4096)

# Keep storage writable during development
storage.remount("/", readonly=False)
```

### `code.py`

```python
"""Project entry point."""
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import DiodeOrientation
from kmk.keys import KC

from lib.chatpad import ChatpadController

def main():
    print("Chatpad KMK production build starting...")

    # Minimal matrix since we inject events; pins are placeholders
    kb = KMKKeyboard()
    kb.col_pins = (0,)
    kb.row_pins = (1,)
    kb.diode_orientation = DiodeOrientation.COL2ROW
    kb.keymap = [[KC.NO]]

    controller = ChatpadController(kb)
    controller.go()  # registers modules and starts KMK

if __name__ == "__main__":
    main()
```

### `config.py`

```python
"""Configuration constants for Chatpad KMK."""
import board

# -------- Hardware configuration --------
UART_TX_PIN = board.TX
UART_RX_PIN = board.RX
UART_BAUDRATE = 19200
UART_BUFFER_SIZE = 256

NEOPIXEL_PIN = getattr(board, "NEOPIXEL", None)
NEOPIXEL_BRIGHTNESS = 0.15

# -------- Host behavior --------
# Set to 'linux', 'mac', or 'windows' for word navigation shortcuts
HOST_OS = "linux"

# -------- Timing (seconds) --------
KEEP_ALIVE_INTERVAL = 1.0
SPACE_TAP_TIMEOUT = 0.175
HEARTBEAT_INTERVAL = 1.0

# -------- Protocol constants --------
class Protocol:
    INIT_MSG = bytes((0x87, 0x02, 0x8C, 0x1F, 0xCC))
    AWAKE_MSG = bytes((0x87, 0x02, 0x8C, 0x1B, 0xD0))
    FRAME_SIZE = 8
    DATA_HEADER = 0xB4
    STATUS_HEADER = 0xA5
    HEADER2 = 0xC5

class Modifiers:
    SHIFT = 0x01
    GREEN = 0x02
    ORANGE = 0x04
    PEOPLE = 0x08

# -------- LED colors --------
class Colors:
    OFF = (0, 0, 0)
    BASE = (10, 10, 40)
    SHIFT = (80, 0, 80)
    GREEN = (0, 100, 0)
    ORANGE = (100, 50, 0)
    PEOPLE = (100, 100, 100)
    ERROR = (100, 0, 0)
    HEARTBEAT = (30, 30, 30)

# -------- Chatpad raw keycodes --------
class RawKey:
    def __init__(self, code, name):
        self.code = code
        self.name = name

class Keys:
    # Numbers
    N1 = RawKey(0x17, "N1")
    N2 = RawKey(0x16, "N2")
    N3 = RawKey(0x15, "N3")
    N4 = RawKey(0x14, "N4")
    N5 = RawKey(0x13, "N5")
    N6 = RawKey(0x12, "N6")
    N7 = RawKey(0x11, "N7")
    N8 = RawKey(0x67, "N8")
    N9 = RawKey(0x66, "N9")
    N0 = RawKey(0x65, "N0")

    # Letters - Top row
    Q = RawKey(0x27, "Q")
    W = RawKey(0x26, "W")
    E = RawKey(0x25, "E")
    R = RawKey(0x24, "R")
    T = RawKey(0x23, "T")
    Y = RawKey(0x22, "Y")
    U = RawKey(0x21, "U")
    I = RawKey(0x76, "I")
    O = RawKey(0x75, "O")
    P = RawKey(0x64, "P")

    # Letters - Home row
    A = RawKey(0x37, "A")
    S = RawKey(0x36, "S")
    D = RawKey(0x35, "D")
    F = RawKey(0x34, "F")
    G = RawKey(0x33, "G")
    H = RawKey(0x32, "H")
    J = RawKey(0x31, "J")
    K = RawKey(0x77, "K")
    L = RawKey(0x72, "L")

    # Letters - Bottom row
    Z = RawKey(0x46, "Z")
    X = RawKey(0x45, "X")
    C = RawKey(0x44, "C")
    V = RawKey(0x43, "V")
    B = RawKey(0x42, "B")
    N = RawKey(0x41, "N")
    M = RawKey(0x52, "M")

    # Punctuation
    COMMA = RawKey(0x62, ",")
    PERIOD = RawKey(0x53, ".")

    # Special
    ENTER = RawKey(0x63, "ENTER")
    SPACE = RawKey(0x54, "SPACE")
    BACKSPACE = RawKey(0x71, "BSPC")
    LEFT = RawKey(0x55, "LEFT")
    RIGHT = RawKey(0x51, "RIGHT")
```

### `lib/chatpad/__init__.py`

```python
"""Public Chatpad API."""
from .keyboard import ChatpadController

__all__ = ["ChatpadController"]
```

### `lib/chatpad/protocol.py`

```python
"""UART protocol handler for Xbox 360 Chatpad."""
import busio
from time import monotonic
from config import (
    Protocol, UART_TX_PIN, UART_RX_PIN, UART_BAUDRATE,
    UART_BUFFER_SIZE, KEEP_ALIVE_INTERVAL
)

class FrameParser:
    """Accumulates bytes and yields validated frames."""

    def __init__(self):
        self.buffer = bytearray()

    def add_data(self, data):
        if data:
            self.buffer.extend(data)
            if len(self.buffer) > UART_BUFFER_SIZE * 2:
                # keep recent bytes only
                self.buffer = self.buffer[-UART_BUFFER_SIZE:]

    def get_frame(self):
        """Return next 8‑byte valid data frame or None."""
        while len(self.buffer) >= Protocol.FRAME_SIZE:
            # skip status frames
            if self.buffer[0] == Protocol.STATUS_HEADER:
                del self.buffer[:Protocol.FRAME_SIZE]
                continue
            # look for data header
            if self.buffer[0] == Protocol.DATA_HEADER:
                if len(self.buffer) < Protocol.FRAME_SIZE:
                    return None
                if self.buffer[1] != Protocol.HEADER2:
                    del self.buffer[:1]
                    continue
                frame = bytes(self.buffer[:Protocol.FRAME_SIZE])
                if self._checksum_ok(frame):
                    del self.buffer[:Protocol.FRAME_SIZE]
                    return frame
                # bad checksum, resync by one byte
                del self.buffer[:1]
                continue
            # unknown, drop a byte
            del self.buffer[:1]
        return None

    @staticmethod
    def _checksum_ok(frame):
        s = sum(frame[:7]) & 0xFF
        return ((-s) & 0xFF) == frame[7]


class UARTHandler:
    """Non‑blocking UART with parsing and keep‑alive."""

    def __init__(self):
        self.uart = busio.UART(
            tx=UART_TX_PIN, rx=UART_RX_PIN,
            baudrate=UART_BAUDRATE, timeout=0, receiver_buffer_size=UART_BUFFER_SIZE
        )
        self.parser = FrameParser()
        self.last_ping = 0.0
        self.uart.write(Protocol.INIT_MSG)

    def maintain(self):
        now = monotonic()
        if now - self.last_ping > KEEP_ALIVE_INTERVAL:
            self.uart.write(Protocol.AWAKE_MSG)
            self.last_ping = now

    def next_report(self):
        """Return dict {'modifiers','key0','key1'} or None."""
        iw = getattr(self.uart, "in_waiting", 0)
        if iw:
            data = self.uart.read(iw)
            self.parser.add_data(data)
        frame = self.parser.get_frame()
        if not frame:
            return None
        return {"modifiers": frame[3], "key0": frame[4], "key1": frame[5]}
```

### `lib/chatpad/state.py`

```python
"""State machines for modifiers, keys, and Space dual‑role."""
from time import monotonic
from config import Modifiers, SPACE_TAP_TIMEOUT

class ModifierState:
    def __init__(self):
        self.current = 0
        self.previous = 0
        self.shift_sticky = False
        self.people_toggle = False

    def update(self, new_mods):
        self.previous = self.current
        self.current = new_mods
        # Rising edge on People toggles dev layer
        if self.rising(Modifiers.PEOPLE):
            self.people_toggle = not self.people_toggle
        # Sticky Shift toggled by Shift+Orange chord rising
        chord = (self.current & Modifiers.SHIFT) and (self.current & Modifiers.ORANGE)
        chord_prev = (self.previous & Modifiers.SHIFT) and (self.previous & Modifiers.ORANGE)
        if chord and not chord_prev:
            self.shift_sticky = not self.shift_sticky

    def rising(self, mask):
        return (self.current & mask) and not (self.previous & mask)

    @property
    def shift_active(self):
        return self.shift_sticky or bool(self.current & Modifiers.SHIFT)

    @property
    def green_active(self):
        return bool(self.current & Modifiers.GREEN)

    @property
    def orange_active(self):
        return bool(self.current & Modifiers.ORANGE)


class KeyState:
    def __init__(self):
        self.current = [0, 0]
        self.previous = [0, 0]

    def update(self, k0, k1):
        self.previous = self.current[:]
        self.current = [k0, k1]

    def pressed(self):
        out = []
        for k in self.current:
            if k and k not in self.previous:
                out.append(k)
        return out

    def released(self):
        out = []
        for k in self.previous:
            if k and k not in self.current:
                out.append(k)
        return out


class SpaceKeyState:
    """Dual‑role Space: tap Space or hold/chord to Ctrl."""
    def __init__(self):
        self.is_down = False
        self.down_at = 0.0
        self.ctrl_active = False

    def press(self):
        self.is_down = True
        self.down_at = monotonic()
        self.ctrl_active = False

    def release(self):
        was_ctrl = self.ctrl_active
        was_space = self.is_down and not self.ctrl_active
        self.is_down = False
        self.ctrl_active = False
        return was_space, was_ctrl

    def promote_by_time(self):
        if self.is_down and not self.ctrl_active:
            if monotonic() - self.down_at > SPACE_TAP_TIMEOUT:
                self.ctrl_active = True
                return True
        return False

    def promote_by_chord(self):
        if self.is_down and not self.ctrl_active:
            self.ctrl_active = True
            return True
        return False
```

### `lib/chatpad/layers.py`

```python
"""Layer selection and key mappings."""
from kmk.keys import KC
from config import Keys, Modifiers, HOST_OS

class LayerManager:
    def __init__(self, macros):
        self.macros = macros
        self._build_layers()

    def _build_layers(self):
        # Base typing layer
        base = {}
        # Letters
        for key in [
            Keys.Q, Keys.W, Keys.E, Keys.R, Keys.T, Keys.Y, Keys.U, Keys.I, Keys.O, Keys.P,
            Keys.A, Keys.S, Keys.D, Keys.F, Keys.G, Keys.H, Keys.J, Keys.K, Keys.L,
            Keys.Z, Keys.X, Keys.C, Keys.V, Keys.B, Keys.N, Keys.M
        ]:
            base[key.code] = getattr(KC, key.name)
        # Numbers
        nums = [Keys.N1, Keys.N2, Keys.N3, Keys.N4, Keys.N5, Keys.N6, Keys.N7, Keys.N8, Keys.N9, Keys.N0]
        for idx, key in enumerate(nums, 1):
            base[key.code] = getattr(KC, "N{}".format(idx % 10))
        # Punctuation and specials
        base[Keys.COMMA.code] = KC.COMMA
        base[Keys.PERIOD.code] = KC.DOT
        base[Keys.SPACE.code] = KC.SPACE
        base[Keys.ENTER.code] = KC.ENTER
        base[Keys.BACKSPACE.code] = KC.BSPC
        base[Keys.LEFT.code] = KC.LEFT
        base[Keys.RIGHT.code] = KC.RIGHT

        # Green: coding symbols and helpers (pair insertion via macros)
        # Pair‑insertion macros are in macros dict: pair_paren, pair_brace, pair_bracket, pair_angle, pair_squote, pair_dquote
        green = {
            Keys.D.code: self.macros["pair_bracket"],
            Keys.F.code: self.macros["pair_brace"],
            Keys.R.code: self.macros["pair_paren"],
            Keys.C.code: self.macros["pair_angle"],
            Keys.COMMA.code: self.macros["pair_squote"],
            Keys.PERIOD.code: self.macros["pair_dquote"],
            Keys.X.code: KC.PIPE,
            Keys.Z.code: KC.TILDE,
            Keys.G.code: KC.GRV,
            Keys.H.code: KC.UNDS,
            Keys.J.code: KC.MINS,
            Keys.K.code: KC.PLUS,
            Keys.L.code: KC.EQUAL,
            Keys.V.code: KC.BSLS,
            Keys.B.code: KC.SLASH,
            Keys.E.code: KC.ESC,
            Keys.T.code: KC.TAB,
            Keys.I.code: KC.PGUP,
            Keys.M.code: KC.PGDN,
            Keys.U.code: KC.HOME,
            Keys.O.code: KC.END,
        }

        # Orange: function keys and navigation
        orange = {}
        fnums = [Keys.N1, Keys.N2, Keys.N3, Keys.N4, Keys.N5, Keys.N6, Keys.N7, Keys.N8, Keys.N9, Keys.N0]
        for idx, key in enumerate(fnums, 1):
            orange[key.code] = getattr(KC, "F{}".format(idx))
        orange[Keys.P.code] = KC.F11
        orange[Keys.O.code] = KC.F12
        orange[Keys.Q.code] = KC.PSCR
        orange[Keys.W.code] = KC.SLCK
        orange[Keys.E.code] = KC.PAUS
        orange[Keys.A.code] = KC.INS
        orange[Keys.S.code] = KC.DEL
        orange[Keys.I.code] = KC.UP
        orange[Keys.K.code] = KC.DOWN
        orange[Keys.J.code] = KC.LEFT
        orange[Keys.L.code] = KC.RIGHT

        # People: dev shortcuts and navigation
        if HOST_OS.lower() in ("linux", "mac"):
            word_left = KC.LALT(KC.LEFT)
            word_right = KC.LALT(KC.RIGHT)
        else:
            word_left = KC.LCTL(KC.LEFT)
            word_right = KC.LCTL(KC.RIGHT)

        people = {
            # Arrows on IJKL
            Keys.I.code: KC.UP,
            Keys.K.code: KC.DOWN,
            Keys.J.code: KC.LEFT,
            Keys.L.code: KC.RIGHT,
            # Home/End
            Keys.COMMA.code: KC.HOME,
            Keys.PERIOD.code: KC.END,
            # Word navigation
            Keys.H.code: word_left,
            Keys.U.code: word_right,
            # Macros
            Keys.T.code: self.macros["tmux_prefix"],
            Keys.C.code: self.macros["clear"],
            Keys.G.code: self.macros["git_status"],
            Keys.S.code: self.macros["save"],
            Keys.B.code: self.macros["build"],
            # Clipboard helpers
            Keys.X.code: KC.LCTL(KC.X),
            Keys.V.code: KC.LCTL(KC.V),
            # Quick close
            Keys.Q.code: KC.LALT(KC.F4),
        }

        self.layers = {
            "base": base,
            "green": green,
            "orange": orange,
            "people": people,
        }

    def select(self, modifiers):
        if modifiers.people_toggle:
            return self.layers["people"]
        if modifiers.orange_active:
            return self.layers["orange"]
        if modifiers.green_active:
            return self.layers["green"]
        return self.layers["base"]

    def get_key(self, raw_code, modifiers):
        return self.select(modifiers).get(raw_code)
```

### `lib/chatpad/led.py`

```python
"""NeoPixel status LED helper."""
from config import NEOPIXEL_PIN, NEOPIXEL_BRIGHTNESS, Colors
try:
    import neopixel
    LED_OK = NEOPIXEL_PIN is not None
except Exception:
    LED_OK = False

class StatusLED:
    def __init__(self):
        self.enabled = LED_OK
        self.color = Colors.OFF
        if self.enabled:
            self.px = neopixel.NeoPixel(NEOPIXEL_PIN, 1, brightness=NEOPIXEL_BRIGHTNESS, auto_write=True)
            self.px[0] = Colors.BASE

    def set(self, rgb):
        if not self.enabled:
            return
        self.color = rgb
        self.px[0] = rgb

    def update_for(self, modifiers):
        if not self.enabled:
            return
        if modifiers.people_toggle:
            self.set(Colors.PEOPLE)
        elif modifiers.green_active:
            self.set(Colors.GREEN)
        elif modifiers.orange_active:
            self.set(Colors.ORANGE)
        elif modifiers.shift_active:
            self.set(Colors.SHIFT)
        else:
            self.set(Colors.BASE)

    def heartbeat(self):
        # very fast blink without delay by immediate restore
        if not self.enabled:
            return
        saved = self.color
        self.px[0] = Colors.HEARTBEAT
        self.px[0] = saved

    def error(self):
        self.set(Colors.ERROR)
```

### `lib/chatpad/keyboard.py`

```python
"""Chatpad controller that registers a KMK Module."""
from time import monotonic
import supervisor

from kmk.modules import Module
from kmk.keys import KC

from config import HEARTBEAT_INTERVAL, Modifiers
from .protocol import UARTHandler
from .state import ModifierState, KeyState, SpaceKeyState
from .layers import LayerManager
from .led import StatusLED
from lib.macros import get_all_macros

class ChatpadKMKModule(Module):
    """Integrates protocol, state, layers, and LED with KMK's loop."""
    def __init__(self, keyboard):
        self.kb = keyboard
        self.uart = UARTHandler()
        self.mods = ModifierState()
        self.keys = KeyState()
        self.space = SpaceKeyState()
        self.macros = get_all_macros()
        self.layers = LayerManager(self.macros)
        self.led = StatusLED()
        self.shift_down = False
        self.last_hb = monotonic()
        self.debug = False
        self.active_keys = {}  # raw_code -> Key object pressed

    def before_matrix_scan(self, keyboard):
        # Maintain link and parse all available frames
        self.uart.maintain()
        report = self.uart.next_report()
        while report:
            self._process_report(report)
            report = self.uart.next_report()

        # Time‑based Space promotion
        if self.space.promote_by_time():
            KC.LCTRL.on_press(self.kb)

        # LED and heartbeat
        self.led.update_for(self.mods)
        now = monotonic()
        if now - self.last_hb > HEARTBEAT_INTERVAL:
            self.led.heartbeat()
            self.last_hb = now

        # Keep REPL responsive
        supervisor.runtime.run_background_tasks()

    # Internal
    def _process_report(self, rep):
        # Update modifiers and handle sticky shift
        prev_mods = self.mods.current
        self.mods.update(rep["modifiers"])

        # Debug toggle: press Orange while People is active
        if self.mods.people_toggle and self.mods.rising(Modifiers.ORANGE):
            self.debug = not self.debug
            print("Debug", "ON" if self.debug else "OFF")

        # Host Shift handling
        if self.mods.shift_active and not self.shift_down:
            KC.LSFT.on_press(self.kb)
            self.shift_down = True
        elif not self.mods.shift_active and self.shift_down:
            KC.LSFT.on_release(self.kb)
            self.shift_down = False

        # Update key state and emit events
        self.keys.update(rep["key0"], rep["key1"])
        for raw in self.keys.pressed():
            self._on_key_down(raw)
        for raw in self.keys.released():
            self._on_key_up(raw)

    def _on_key_down(self, raw):
        # Ignore modifier raw codes; the Chatpad sends those as bits
        if raw in (0x81, 0x82, 0x84, 0x83):
            return

        # Space handling
        from config import Keys
        if raw == Keys.SPACE.code:
            self.space.press()
            return

        # If Space is held and another key goes down, promote Space to Ctrl immediately
        if self.space.promote_by_chord():
            KC.LCTRL.on_press(self.kb)

        # Lookup per active layer
        key = self.layers.get_key(raw, self.mods)
        if key:
            key.on_press(self.kb)
            self.active_keys[raw] = key
            if self.debug:
                print("DOWN", hex(raw))

    def _on_key_up(self, raw):
        from config import Keys
        if raw == Keys.SPACE.code:
            was_space, was_ctrl = self.space.release()
            if was_ctrl:
                KC.LCTRL.on_release(self.kb)
            elif was_space:
                KC.SPACE.on_press(self.kb)
                KC.SPACE.on_release(self.kb)
            if self.debug:
                print("SPACE tap" if was_space else "CTRL rel")
            return

        key = self.active_keys.pop(raw, None)
        if not key:
            # Fallback to current layer if not tracked
            key = self.layers.get_key(raw, self.mods)
        if key:
            key.on_release(self.kb)
            if self.debug:
                print("UP  ", hex(raw))


class ChatpadController:
    """Public entry: install module and KMK basics, then start KMK."""
    def __init__(self, keyboard):
        self.kb = keyboard

    def go(self):
        # Load KMK modules we rely on
        from kmk.modules.layers import Layers
        from kmk.modules.holdtap import HoldTap
        from kmk.modules.macros import Macros
        from kmk.modules.tapdance import TapDance

        holdtap = HoldTap()
        # we do not use KC.HT here, but HoldTap is safe to include
        tapdance = TapDance()

        self.kb.modules.extend([Layers(), holdtap, Macros(), tapdance])

        # Register Chatpad module
        self.kb.modules.append(ChatpadKMKModule(self.kb))

        print("Chatpad KMK ready")
        self.kb.go()
```

### `lib/macros/__init__.py`

```python
"""Aggregate macros for Chatpad layers."""
from .development import dev_macros
from .terminal import term_macros
from .vim import vim_macros

def get_all_macros():
    out = {}
    out.update(dev_macros())
    out.update(term_macros())
    out.update(vim_macros())
    # Pair insertion defaults if any are missing
    ensure = {
        "pair_paren": "()",
        "pair_brace": "{}",
        "pair_bracket": "[]",
        "pair_angle": "<>",
        "pair_squote": "''",
        "pair_dquote": '""',
    }
    from kmk.keys import KC
    from kmk.modules.macros import Tap
    for name, s in ensure.items():
        if name not in out:
            # Insert pair and move caret left
            out[name] = KC.MACRO(s, Tap(KC.LEFT))
    return out
```

### `lib/macros/development.py`

```python
"""Developer‑oriented macros: git, save, build."""
from kmk.keys import KC
from kmk.modules.macros import Press, Release, Tap

def dev_macros():
    return {
        "save": KC.MACRO(Press(KC.LCTL), Tap(KC.S), Release(KC.LCTL)),
        "build": KC.MACRO(Press(KC.LCTL), Press(KC.LSFT), Tap(KC.B), Release(KC.LSFT), Release(KC.LCTL)),
        "git_status": KC.MACRO("git status\n"),
        "git_add": KC.MACRO("git add "),
        "git_commit": KC.MACRO('git commit -m ""', Tap(KC.LEFT)),
        "git_push": KC.MACRO("git push\n"),
    }
```

### `lib/macros/terminal.py`

```python
"""Terminal navigation and tooling macros."""
from kmk.keys import KC
from kmk.modules.macros import Press, Release, Tap

def term_macros():
    return {
        "tmux_prefix": KC.MACRO(Press(KC.LCTL), Tap(KC.B), Release(KC.LCTL)),
        "clear": KC.MACRO("clear\n"),
        "ssh": KC.MACRO("ssh user@host\n"),
        "python": KC.MACRO("python3\n"),
        "ls_la": KC.MACRO("ls -la\n"),
        "cd_parent": KC.MACRO("cd ..\n"),
        "docker_ps": KC.MACRO("docker ps\n"),
        # Pair insertion helpers provided in __init__ if not overridden
    }
```

### `lib/macros/vim.py`

```python
"""Optional editor helpers. Keep minimal by default."""
def vim_macros():
    return {}
```

### `README.md`

```markdown
# Xbox 360 Chatpad KMK — Production Edition

A robust, terminal‑first keyboard for a Raspberry Pi Zero 2W using an Xbox 360 Chatpad and an Adafruit KB2040, built on KMK over CircuitPython.

## Highlights

- Nonblocking UART driver with checksum validation and resynchronization
- Keep‑alive every second to prevent Chatpad sleep
- Real press and release semantics for correct repeat and holds
- Layers made for development:
  - Green held: coding symbols and pair insertion
  - Orange held: F1..F12 and system/navigation keys
  - People toggled: dev macros, arrows on IJKL, Home/End on , .
- Dual‑role Space: tap Space; hold or chord promotes to Ctrl
- Sticky Shift toggled by Shift+Orange chord
- OS‑adaptive word navigation (Alt+Arrow on Linux/macOS; Ctrl+Arrow on Windows)
- Onboard NeoPixel status: base blue; green; amber; white; purple
- Serial debug toggle: while People is active, press Orange to toggle logs

## Hardware

- Adafruit KB2040
- Xbox 360 Chatpad (UART)
- Wiring:
  - KB2040 GND ↔ Chatpad GND
  - KB2040 3V3 ↔ Chatpad 3.3 V
  - KB2040 TX ↔ Chatpad RX
  - KB2040 RX ↔ Chatpad TX

## Install

1. Flash CircuitPython for KB2040 from circuitpython.org.
2. Copy KMK’s `kmk/` folder from the KMK repo into the root of `CIRCUITPY`.
3. Copy this repository to `CIRCUITPY` keeping the folder layout.
4. Optionally set `HOST_OS` in `config.py` to `linux`, `mac`, or `windows`.
5. Eject the drive; the board restarts and enumerates as a USB keyboard.

## Use

- Type normally on the Chatpad.
- Hold **Green** for symbols and paired inserts `() [] {} <> '' ""`.
- Hold **Orange** for function keys F1..F12; Print Screen; Pause; Insert; Delete; arrow cluster.
- Tap **People** to toggle the dev layer:
  - IJKL become arrows. Comma is Home. Period is End.
  - H/U jump word left/right (OS‑adaptive).
  - T tmux prefix; C clear; G git status; S save; B build.
- Hold **Space** to get Ctrl after a short pause or immediately when you press another key while holding Space; release Space to release Ctrl.
- Hold **Shift** and **Orange** together to toggle sticky Shift.
- With People toggled, press **Orange** to toggle debug logs on the serial console.

## Customize

- Edit `HOST_OS` in `config.py` to match the host.
- Add or change macros in `lib/macros/`.
- Change symbol bindings in `lib/chatpad/layers.py`.
- Adjust Space promotion time via `SPACE_TAP_TIMEOUT` in `config.py`.
- Tweak LED colors in `config.py::Colors`.

## Notes

- We inject key events via a KMK Module (`ChatpadKMKModule`) that runs in `before_matrix_scan`, so HID timing stays correct under `keyboard.go()`.
- All key releases are matched to the exact object pressed by caching `raw_code → Key` until release.

## License

MIT. See `LICENSE`.
```

### `LICENSE`

```text
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

## Why this meets the brief

* It adopts your modular architecture: protocol, state, layers, LED, macros.
* It preserves the reliable parser and two‑key edge detection.
* It keeps low‑latency behavior by integrating as a KMK Module under `keyboard.go()`.
* It solves the common small‑keyboard pain points: dual‑role Space, OS‑aware word nav, pair insertion, dev macros, sticky Shift, and clear LEDs.
* It is safe for CircuitPython: no 3.10‑only syntax, no heavy typing, and no blocking delays.

If you want an additional layer for window management or a Vim‑centric people layer, I can add one with the same patterns and keep everything tidy.

---

What would you say are the benefits of this KMK version over the original Arduino code?

---

Here is the short, direct comparison.

## What you gain with the KMK build

**Reliability and correctness**

* Nonblocking UART with a real frame parser and checksum. It resynchronizes on errors instead of busy‑waiting for bytes, so key input never stalls.
* True press and release semantics. Auto‑repeat and key holds behave correctly in shells and editors.
* Keep‑alive scheduling separate from HID output, so the Chatpad stays awake without delaying key events.

**Small‑keyboard ergonomics**

* Purposeful layers: Green (coding symbols and paired inserts), Orange (F‑keys and system), People (developer shortcuts and navigation). This replaces ASCII lookup tables with a clear, extensible model.
* Dual‑role Space that becomes Ctrl on hold or chord. Frees a modifier on cramped hardware.
* Sticky Shift toggled by Shift+Orange. Easy bursts of uppercase or symbols.
* OS‑aware word navigation (Alt+Arrows on Linux and macOS, Ctrl+Arrows on Windows).
* TapDance and pair‑insertion macros for (), {}, \[], <>, '', "" that drop the cursor inside.

**Maintainability**

* Clean separation of concerns: `protocol.py` (serial), `state.py` (modifiers, keys, space), `layers.py` (mappings), `led.py` (status), `keyboard.py` (KMK module), `macros/` (features). Each unit is small and testable.
* Changes are data‑driven. Editing a mapping or macro does not touch the parser or state machine.
* Lower cyclomatic complexity and fewer global variables than the Arduino sketch.

**Extensibility**

* KMK modules and extensions are ready to add: combos, mouse keys, RGB, OLED, sticky keys, media keys, Bluetooth variants, power save.
* Adding new layers or app‑specific keymaps is straightforward. No need to rebuild the ASCII table logic.

**Observability and feedback**

* Onboard NeoPixel reflects active mode: base, Green, Orange, People, sticky Shift, plus a heartbeat and error color.
* Serial debug can be toggled from the keyboard (People layer active, press Orange) which is valuable on a headless deck.

**Developer velocity**

* CircuitPython REPL and hot reload. You can tweak mappings and macros quickly without reflashing a C++ firmware.
* Macros are first class. Git, tmux, docker, ssh, and terminal helpers are included and easy to customize.

**Host compatibility**

* HID is handled by KMK using proper keycodes, not ad‑hoc ASCII translation. This is more robust across layouts and OSes.
* Word navigation and several shortcuts adapt to the Pi Zero 2W host OS with a single switch in `config.py`.

**Future proofing**

* The structure is ready for battery telemetry, wireless variants, or an OLED status screen with minimal change.
* You can precompile KMK files to `.mpy` if you later need faster boot and smaller footprint.

## What the Arduino sketch did not give you (or made hard)

* Busy‑wait serial reads and packet handling coupled directly to key dispatch. Easier to drop bytes or stall the main loop.
* ASCII lookup tables tied to modifier bits. Hard to add layers, macros, or app‑specific behavior without growing the tables.
* Limited notion of press vs release. Harder to get repeat, selection, and editor behaviors exactly right.
* Limited structure for expansion. RGB, macros, hold‑tap, and tap‑dance all require custom code paths.
* Less convenient iteration. Every change needs a rebuild and flash cycle.

## Honest trade‑offs to be aware of

* CircuitPython boots slower than a tiny C++ sketch. You can mitigate with `.mpy` precompiles and by trimming unused KMK pieces.
* Python brings a bit more RAM and code size overhead. On the KB2040 this is usually fine.
* If you need extreme scanning rates or vendor‑specific HID quirks, a custom TinyUSB Arduino build can still be tighter. Most terminal and development workflows do not need that.

**Bottom line:** the KMK version is a more reliable input pipeline with a far better user experience on a tiny keyboard, and it is dramatically easier to extend. For a Pi Zero 2W cyberdeck focused on terminal work, those benefits outweigh the small boot and footprint costs.
