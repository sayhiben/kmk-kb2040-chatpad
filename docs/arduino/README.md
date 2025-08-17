# Arduino Chatpad Implementation

This directory contains the original Arduino-based implementation for interfacing an Xbox 360 Chatpad with an Adafruit KB2040 microcontroller.

## Overview

The Arduino implementation provides a basic USB HID keyboard interface using ASCII lookup tables to map Chatpad keycodes to keyboard inputs. It includes:

- Serial communication at 19200 baud with the Chatpad
- Packet validation with checksum verification
- Modifier key support (Shift, Green, Orange, People)
- Toggle modes for Shift and People buttons
- NeoPixel LED feedback for visual status
- Heartbeat LED pattern for debugging

## Key Components

### Chatpad.h
Defines the Chatpad class interface with:
- Raw keycode enumeration matching Chatpad hardware
- Event types (key up/down)
- Callback mechanism for key events
- ASCII conversion based on modifier state

### Chatpad.cpp
Implements the Chatpad protocol:
- 8-byte packet format: `[0xB4, 0xC5, modifiers, key0, key1, 0, 0, checksum]`
- Keep-alive messages every 1000ms
- Two-key rollover detection
- ASCII lookup tables for different modifier states

### Chatpad.ino
Main Arduino sketch that:
- Initializes hardware (Serial, NeoPixel, Keyboard)
- Handles key events from Chatpad
- Sends HID keyboard events to host
- Provides LED feedback based on key types

## Limitations

- **Busy-wait serial reads**: Can stall the main loop waiting for bytes
- **ASCII-based translation**: Limited to basic character mapping
- **Fixed lookup tables**: Difficult to extend with new layers or macros
- **Limited key semantics**: Basic press/release without advanced features
- **No error recovery**: Packet errors can desynchronize communication

## Hardware Requirements

- Adafruit KB2040 (or compatible RP2040 board)
- Xbox 360 Chatpad
- UART connection between KB2040 and Chatpad
- NeoPixel LED (optional, for status indication)

## Usage

1. Install required Arduino libraries:
   - Adafruit_NeoPixel
   - Keyboard (built-in)

2. Connect Chatpad to KB2040:
   - TX/RX pins for UART communication
   - Power and ground connections

3. Upload the sketch to KB2040

4. The device will appear as a USB keyboard to the host

## Protocol Details

The Chatpad communicates using a proprietary protocol:
- **Baud rate**: 19200
- **Init sequence**: `[0x87, 0x02, 0x8C, 0x1F, 0xCC]`
- **Keep-alive**: `[0x87, 0x02, 0x8C, 0x1B, 0xD0]`
- **Checksum**: Sum of bytes 0-6, then negated (two's complement)

## Comparison with KMK Implementation

See the main project documentation for details on why the KMK implementation supersedes this Arduino version, offering better reliability, extensibility, and user experience for terminal-based development work.