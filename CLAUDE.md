# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and other AI assistants when working with this repository.

## Project Overview

KMK-based Xbox 360 Chatpad driver for Adafruit KB2040, creating a USB keyboard optimized for terminal and software development. The Chatpad communicates via UART protocol, which we decode and translate into USB HID events using CircuitPython and KMK firmware.

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
- Tap (<300ms) = Space
- Hold (>300ms) = Ctrl
- Space + key = Immediate Ctrl chord

**Deferred Layer Building**: Layers built after KMK modules loaded to ensure KC.MACRO exists
```python
# In layers.py - build on first access
def select(self, modifiers):
    if not self._layers_built:
        self._build_layers()
```

## Hardware Setup

- **Microcontroller**: Adafruit KB2040 (RP2040-based)
- **Chatpad**: Xbox 360 Chatpad
- **Connections**:
  - Chatpad TX → KB2040 RX (D1/board.RX)
  - Chatpad RX → KB2040 TX (D0/board.TX)
  - Power: 3.3V and GND
- **Dummy Matrix**: D4/D5 (KMK requires matrix pins even for UART input)

## Layer System

### Base Layer
Standard QWERTY layout with numbers and basic punctuation

### Green Layer (Shift/Symbols)
- **Vim Navigation**: H/J/K/L = Left/Down/Up/Right
- **Symbols**: Relocated from HJKL to nearby keys
- **Pair Insertion**: Auto-insert bracket pairs with cursor positioning

### Orange Layer (Function/System)
- F1-F12 keys
- System keys (PrintScreen, ScrollLock, Pause)
- Navigation arrows on IJKL
- Plus/Equal on M/N

### People Layer (Developer)
- **Git macros**: status, add, commit, push
- **Navigation**: IJKL arrows, word navigation
- **Terminal**: clear, tmux prefix
- **Editor**: save (Ctrl+S), build (Ctrl+Shift+B)
- **Toggle with People key**

## Development Workflow

### Setup
```bash
# Clone with submodules
git clone --recursive <repo>

# Or init submodules after clone
git submodule init && git submodule update
```

### Deploy to Device
```bash
# Auto-deploy to CIRCUITPY volume
./deploy.sh

# Force reinstall KMK
./deploy.sh --force-kmk
```

### Debug & Monitor
```bash
# Monitor serial output
screen /dev/tty.usbmodem* 115200

# Debug mode toggle: People + Orange while running
# Or set in code.py:
controller = ChatpadController(kb, simple_space=False, debug=True)
```

## Configuration

### code.py Options
- `simple_space`: `False` for dual-role, `True` for regular spacebar
- `debug`: `True` shows key press/release messages

### config.py Settings
- `HOST_OS`: "linux", "mac", or "windows" (affects shortcuts)
- `SPACE_TAP_TIMEOUT`: Dual-role timeout (default 0.3s)
- `KEEP_ALIVE_INTERVAL`: UART keep-alive (default 1.0s)
- `NEOPIXEL_BRIGHTNESS`: LED intensity (0.0-1.0)

## Protocol Details

### Chatpad Messages
- **Init**: `0x87 0x02 0x8C 0x1F 0xCC`
- **Keep-alive**: `0x87 0x02 0x8C 0x1B 0xD0`
- **Data frame**: `0xB4 0xC5 [reserved] [mods] [key0] [key1] [reserved] [checksum]`
- **Status frame**: Starts with `0xA5`

### Checksum Calculation
```python
checksum = (-sum(frame[:7])) & 0xFF
```

### Raw Key Codes
See `config.py` for complete mapping in `Keys` class

## Adding Features

### New Macros
1. Edit files in `lib/macros/`:
   - `development.py`: Coding shortcuts
   - `terminal.py`: Terminal commands
   - `vim.py`: Editor commands
2. Return dictionary: `{"name": action_sequence}`
3. Actions: strings or lists of `[Press(), Tap(), Release()]`

### Layer Modifications
Edit `lib/chatpad/layers.py`:
1. Modify layer dictionaries in `_build_layers()`
2. Use `KC.MACRO()` for macro sequences
3. Direct KC codes for single keys

### Custom Key Behavior
1. Create custom Key class in `lib/chatpad/keyboard.py`
2. Override `on_press()` and `on_release()`
3. Add to appropriate layer

## Troubleshooting

### Common Issues
1. **No output**: Check TX/RX crossed correctly
2. **KC.MACRO not found**: Macros module must load before layers build
3. **Space issues**: Adjust `SPACE_TAP_TIMEOUT`
4. **Read-only filesystem**: Eject and remount or reset device
5. **Memory errors**: Remove unused KMK modules or precompile to .mpy

### Debug Techniques
- Enable debug output in code.py
- Monitor serial: `screen /dev/tty.usbmodem* 115200`
- Check UART data with test scripts (now removed, see git history)
- Toggle debug at runtime: People + Orange

## Project Structure
```
kmk-kb2040-chatpad/
├── code.py                # Entry point (debug enabled)
├── config.py              # Configuration and key mappings
├── boot.py                # CircuitPython boot config
├── deploy.sh              # Deployment script
├── lib/
│   ├── chatpad/          # Core driver module
│   │   ├── __init__.py   # Public API
│   │   ├── keyboard.py   # KMK module & controller
│   │   ├── layers.py     # Layer definitions
│   │   ├── protocol.py   # UART protocol handler
│   │   ├── state.py      # State machines
│   │   └── led.py        # Status LED (optional)
│   ├── macros/           # Macro definitions
│   └── kmk/              # KMK firmware (git submodule)
└── docs/
    └── kmk-reference/    # KMK documentation
```

## Resources
- [KMK Documentation](docs/kmk-reference/)
- [CircuitPython](https://circuitpython.org/)
- [Adafruit KB2040](https://www.adafruit.com/product/5302)
- [Xbox 360 Chatpad Protocol](https://github.com/xbox360bb/Xbox360-Chatpad-Driver)