# KMK KB2040 Chatpad Driver

A KMK (CircuitPython) implementation for interfacing an Xbox 360 Chatpad with an Adafruit KB2040 microcontroller, creating a portable USB keyboard optimized for terminal-based software development.

## Project Structure

```
.
├── boot.py                 # CircuitPython boot configuration
├── code.py                 # Main entry point
├── config.py               # Configuration constants
├── CLAUDE.md               # AI assistant guidance
├── lib/
│   ├── chatpad/           # Core Chatpad modules
│   │   ├── __init__.py    # Public API
│   │   ├── protocol.py    # UART protocol handler
│   │   ├── state.py       # State machines
│   │   ├── layers.py      # Layer mappings
│   │   ├── led.py         # LED status controller
│   │   └── keyboard.py    # Main KMK integration
│   └── macros/            # Macro definitions
│       ├── __init__.py    # Macro aggregation
│       ├── development.py # Git, build commands
│       ├── terminal.py    # Shell navigation
│       └── vim.py         # Editor helpers
├── src/
│   └── arduino/           # Original Arduino implementation
│       ├── Chatpad.h
│       ├── Chatpad.cpp
│       └── Chatpad.ino
└── docs/
    ├── arduino/           # Arduino documentation
    │   └── README.md
    └── kmk-reference/     # KMK documentation
        └── getting-started.md
```

## Features

### Core Functionality
- **Non-blocking UART protocol** with frame validation and error recovery
- **Multi-layer system** with purposeful organization:
  - **Base layer**: Standard QWERTY layout
  - **Green layer**: Coding symbols and paired insertions
  - **Orange layer**: Function keys and system controls
  - **People layer**: Developer shortcuts and navigation
- **Dual-role Space**: Acts as Space on tap, Ctrl when held or chorded
- **Sticky Shift**: Toggle with Shift+Orange for sustained uppercase
- **Visual feedback**: NeoPixel LED indicates active mode

### Developer Ergonomics
- **Pair insertion macros**: Automatically places cursor inside (), [], {}, <>, '', ""
- **OS-aware navigation**: Adapts word navigation for Linux/macOS/Windows
- **Terminal helpers**: Quick access to common shell commands
- **Git integration**: Shortcuts for frequent git operations
- **Debug mode**: Toggle serial debugging from the keyboard

## Installation

### Requirements
- Adafruit KB2040 (or compatible RP2040 board)
- Xbox 360 Chatpad
- CircuitPython 7.3 or higher
- KMK firmware

### Setup Steps

1. **Install CircuitPython** on your KB2040
   - Download from [circuitpython.org](https://circuitpython.org/board/adafruit_kb2040/)
   - Hold BOOTSEL while connecting USB
   - Copy the UF2 file to the RPI-RP2 drive

2. **Clone this repository with submodules**
   ```bash
   git clone --recursive https://github.com/sayhiben/kmk-kb2040-chatpad.git
   cd kmk-kb2040-chatpad
   
   # If you already cloned without --recursive:
   git submodule init
   git submodule update
   ```

3. **Deploy to your KB2040**
   ```bash
   # Automatic deployment (auto-detects CIRCUITPY mount)
   ./deploy.sh
   
   # Or specify mount point manually
   ./deploy.sh /Volumes/CIRCUITPY
   ```

4. **Hardware connections**
   - Connect Chatpad TX to KB2040 RX
   - Connect Chatpad RX to KB2040 TX
   - Connect power and ground

## Configuration

Edit `config.py` to customize:

```python
# Host OS for word navigation
HOST_OS = "linux"  # or "mac", "windows"

# LED brightness
NEOPIXEL_BRIGHTNESS = 0.15

# Timing adjustments
SPACE_TAP_TIMEOUT = 0.175  # seconds
```

## Usage

### Layer Access
- **Green layer**: Hold Green button
- **Orange layer**: Hold Orange button
- **People layer**: Toggle with People button
- **Sticky Shift**: Press Shift+Orange to toggle

### Special Features
- **Debug mode**: While People layer active, press Orange
- **Pair insertion**: Type (, [, {, <, ', or " to insert pair with cursor inside
- **Word navigation**: Alt+Left/Right (Linux/Mac) or Ctrl+Left/Right (Windows)

## Protocol Details

The Chatpad communicates via UART at 19200 baud with 8-byte packets:
- Format: `[0xB4, 0xC5, modifiers, key0, key1, 0, 0, checksum]`
- Checksum: XOR of bytes 0-6, then XOR with 0x55
- Keep-alive: Send `[0x08, 0x1F]` every 900ms

## Development

### Project Goals
This implementation prioritizes:
1. **Reliability**: Non-blocking I/O, proper error handling
2. **Ergonomics**: Optimized for small keyboard development
3. **Extensibility**: Modular architecture for easy customization
4. **Maintainability**: Clean separation of concerns

### Architecture
- **Protocol layer**: Handles UART communication and packet validation
- **State layer**: Manages modifier and key state machines
- **Layer system**: Maps raw keycodes to KMK keycodes
- **LED controller**: Provides visual status feedback
- **Macro system**: Extensible shortcuts and automations

## Comparison with Arduino Version

The KMK implementation offers significant advantages:
- **Better reliability**: Non-blocking I/O, automatic resync
- **Richer features**: Layers, macros, dual-role keys
- **Easier iteration**: CircuitPython REPL and hot reload
- **More extensible**: Modular design, data-driven mappings

See `docs/arduino/README.md` for details on the original implementation.

## License

MIT License - See LICENSE file for details

## Credits

- KMK firmware team for the excellent keyboard framework
- Xbox 360 Chatpad reverse engineering community
- CircuitPython team for the platform