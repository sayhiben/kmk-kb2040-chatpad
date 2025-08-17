# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KMK-based Xbox 360 Chatpad driver for Adafruit KB2040, creating a USB keyboard optimized for terminal software development. The device interfaces with a Raspberry Pi Zero 2W as part of a portable "cyberdeck" setup.

## Architecture

### Data Flow
1. **Chatpad → UART** (19200 baud): Sends 8-byte packets with key events
2. **FrameParser** (`protocol.py`): Validates checksums, handles resync on errors
3. **State Machines** (`state.py`): Tracks modifiers, keys, and dual-role Space
4. **LayerManager** (`layers.py`): Maps raw codes → layer → KMK keycodes
5. **ChatpadKMKModule** (`keyboard.py`): Integrates with KMK event loop
6. **KMK → USB HID**: Sends keyboard events to host

### Key Design Patterns

**Non-blocking I/O**: UART reads with timeout=0, accumulating buffer prevents data loss
```python
# In protocol.py - never blocks waiting for complete frames
iw = getattr(self.uart, "in_waiting", 0)
if iw:
    data = self.uart.read(iw)
    self.parser.add_data(data)
```

**State Machine Pattern**: Clean separation between current/previous states for edge detection
```python
# In state.py - detect rising edges for toggles
def rising(self, mask):
    return (self.current & mask) and not (self.previous & mask)
```

**Dual-role Space**: Time-based promotion with chord detection
```python
# Space becomes Ctrl if held > SPACE_TAP_TIMEOUT or chorded with another key
```

## Development Workflow

### KMK Dependency
KMK firmware is included as a git submodule in `lib/kmk_firmware_repo/` with a symlink at `lib/kmk/`.
```bash
# Initialize if needed
git submodule init && git submodule update
```

### Deploy to Device
```bash
# Use the deployment script (auto-detects CIRCUITPY mount)
./deploy.sh

# Or manually specify mount point
./deploy.sh /Volumes/CIRCUITPY
```

### Debug via REPL
```bash
# Connect at 115200 baud
screen /dev/tty.usbmodem* 115200
# Or use Thonny, Mu, or other CircuitPython IDE

# Test modules directly:
>>> from lib.chatpad.protocol import FrameParser
>>> parser = FrameParser()
>>> parser.add_data(b'\xB4\xC5\x00\x27\x00\x00\x00\x7B')
```

### Monitor Chatpad Protocol
```python
# Enable debug mode: People layer + Orange key
# Or set in code:
self.debug = True  # in ChatpadKMKModule
```

## Critical Protocol Details

### Chatpad Messages
- **Init**: `[0x87, 0x02, 0x8C, 0x1F, 0xCC]` - sent once on startup
- **Keep-alive**: `[0x87, 0x02, 0x8C, 0x1B, 0xD0]` - every 1.0s or Chatpad sleeps
- **Data frame**: `[0xB4, 0xC5, mods, key0, key1, 0, 0, checksum]`
- **Checksum**: `(-sum(bytes[0:7])) & 0xFF`

### Raw Keycode Ranges
- Numbers: `0x11-0x17, 0x65-0x67`
- Letters: `0x21-0x27, 0x31-0x37, 0x41-0x46, 0x52, 0x64-0x77`
- Special: `0x51` (Right), `0x53` (Period), `0x54` (Space), `0x55` (Left), `0x62` (Comma), `0x63` (Enter), `0x71` (Backspace)

## Configuration Points

### config.py
- `HOST_OS`: Controls word navigation shortcuts (Alt vs Ctrl arrows)
- `SPACE_TAP_TIMEOUT`: Threshold for Space→Ctrl promotion (default 175ms)
- `NEOPIXEL_BRIGHTNESS`: LED intensity (0.0-1.0)

### Adding Macros
1. Create function in `lib/macros/development.py` or `terminal.py`
2. Return `KC.MACRO(...)` or sequence
3. Map in `lib/chatpad/layers.py` PEOPLE_MAP

### Modifying Layers
Edit dictionaries in `lib/chatpad/layers.py`:
- `BASE_MAP`: Unmodified keys
- `GREEN_MAP`: Coding symbols layer
- `ORANGE_MAP`: F-keys and system
- `PEOPLE_MAP`: Developer shortcuts

## Memory Optimization

If hitting memory limits:
```bash
# Precompile to .mpy
mpy-cross -O2 lib/chatpad/*.py
# Remove unused KMK modules from lib/kmk/
```

## Hardware Connections

- Chatpad TX → KB2040 RX (board.RX)
- Chatpad RX → KB2040 TX (board.TX)
- Chatpad requires 3.3V power
- NeoPixel on pin 17 (built-in on KB2040)