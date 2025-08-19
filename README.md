# Xbox 360 Chatpad KMK Driver

A CircuitPython/KMK driver that turns an Xbox 360 Chatpad into a powerful USB keyboard using an Adafruit KB2040 microcontroller, optimized for terminal and software development.

## Features

- **Full QWERTY keyboard** with numbers and punctuation
- **Multiple layers** for symbols, function keys, and developer shortcuts
- **Vim-style navigation** (HJKL arrows in Green layer)
- **Dual-role spacebar** (tap for space, hold for Ctrl)
- **Developer macros** for git, terminal, and editor commands
- **Customizable** layers and macros via Python
- **Debug mode** with serial output for troubleshooting

## Hardware Requirements

- Xbox 360 Chatpad
- Adafruit KB2040 (or compatible RP2040 board)
- Wire connections for UART and power
- USB-C cable

## Wiring

Connect the Chatpad to the KB2040:

| Chatpad | KB2040 |
|---------|--------|
| TX      | RX (D1) |
| RX      | TX (D0) |
| 3.3V    | 3.3V   |
| GND     | GND    |

## Quick Start

1. **Clone the repository with submodules:**
   ```bash
   git clone --recursive https://github.com/yourusername/kmk-kb2040-chatpad.git
   cd kmk-kb2040-chatpad
   ```

2. **Install CircuitPython on KB2040:**
   ```bash
   # Download CircuitPython UF2 from https://circuitpython.org/board/adafruit_kb2040/
   # Hold BOOTSEL button while connecting USB
   # Copy UF2 file to RPI-RP2 drive that appears
   ```

3. **Deploy the driver:**
   ```bash
   ./deploy.sh
   ```

4. **Connect the Chatpad** and start typing!

## Usage

### 📋 Complete Keyboard Cheat Sheet

#### 🔤 Base Layer (Default)
Standard QWERTY layout:
- **Letters**: Q-P, A-L, Z-M (standard QWERTY)
- **Numbers**: 1-9, 0
- **Punctuation**: 
  - `,` = Comma
  - `.` = Period
- **Navigation**: Left/Right arrow keys (dedicated buttons)
- **Special Keys**:
  - `Space` = Space (tap) or Ctrl (hold >300ms) - see Dual-Role Space below
  - `Enter` = Enter
  - `Backspace` = Backspace
  - `Shift` = Shift (combine with Orange for sticky shift)

#### 🟢 Green Layer (Hold Green Key)
Programming symbols and vim navigation:

| Key | Output | Description |
|-----|--------|-------------|
| **Pair Insertion** (auto-inserts matching pair with cursor between) |
| D | `[]` | Square brackets |
| F | `{}` | Curly braces |
| R | `()` | Parentheses |
| C | `<>` | Angle brackets |
| , | `''` | Single quotes |
| . | `""` | Double quotes |
| **Symbols** |
| X | `\|` | Pipe |
| Z | `~` | Tilde |
| G | `` ` `` | Backtick/grave |
| Y | `_` | Underscore |
| N | `-` | Minus/hyphen |
| V | `\` | Backslash |
| B | `/` | Forward slash |
| **Vim Navigation** |
| H | ← | Left arrow |
| J | ↓ | Down arrow |
| K | ↑ | Up arrow |
| L | → | Right arrow |
| **Page Navigation** |
| I | Page Up | |
| U | Home | |
| O | End | |
| P | Page Down | |
| **Other** |
| E | Escape | |
| T | Tab | |

#### 🟠 Orange Layer (Hold Orange Key)
Function keys, system controls, and modifiers:

| Key | Output | Description |
|-----|--------|-------------|
| **Function Keys** |
| 1-9 | F1-F9 | Function keys |
| 0 | F10 | |
| P | F11 | |
| O | F12 | |
| **System Keys** |
| Q | Print Screen | Screenshot |
| W | Scroll Lock | |
| E | Pause | |
| A | Insert | |
| S | Delete | |
| **Navigation** |
| I | ↑ | Up arrow |
| J | ← | Left arrow |
| K | ↓ | Down arrow |
| L | → | Right arrow |
| **Math Symbols** |
| M | + | Plus |
| N | = | Equal |
| **Modifier Keys** |
| Z | Ctrl | Control key |
| X | Alt/Option | Alt (Windows/Linux) or Option (macOS) |
| C | Cmd/Win | Command (macOS) or Windows key |

#### 👥 People Layer (Toggle with People Key)
Developer tools, macros, and extended navigation:

| Key | Output | Description |
|-----|--------|-------------|
| **Navigation** |
| I | ↑ | Up arrow |
| J | ← | Left arrow |
| K | ↓ | Down arrow |
| L | → | Right arrow |
| , | Home | Beginning of line |
| . | End | End of line |
| H | Alt+← | Word left (macOS/Linux) or Ctrl+← (Windows) |
| U | Alt+→ | Word right (macOS/Linux) or Ctrl+→ (Windows) |
| **Modifier Keys** |
| A | Alt/Option | Alt (Windows/Linux) or Option (macOS) |
| W | Cmd/Win | Command (macOS) or Windows key |
| **Developer Macros** |
| G | `git status\n` | Runs git status |
| K | `clear\n` | Clears terminal (moved from C) |
| S | Ctrl+S / Cmd+S | Save file |
| B | Ctrl+Shift+B | Build/compile |
| T | Ctrl+B | tmux prefix |
| **Clipboard & Editing** |
| C | Ctrl+C / Cmd+C | Copy (NEW) |
| X | Ctrl+X / Cmd+X | Cut |
| V | Ctrl+V / Cmd+V | Paste |
| Z | Ctrl+Z / Cmd+Z | Undo (NEW) |
| Y | Ctrl+Y / Cmd+Shift+Z | Redo (NEW) |
| E | Escape | ESC key for vim (NEW) |
| **Window Control** |
| Q | Alt+F4 | Close window |

### ⚡ Special Features

#### Dual-Role Keys

**Spacebar** (tap=Space, hold=Ctrl):
- **Quick tap** (<300ms): Types a space character
- **Hold** (>300ms): Acts as Ctrl modifier
- **Space + another key quickly**: Immediate Ctrl chord (e.g., Space+C = Ctrl+C)

**LEFT Arrow Key** (tap=Left Arrow, hold=Alt/Option):
- **Quick tap** (<200ms): Left arrow
- **Hold** (>200ms): Alt (Windows/Linux) or Option (macOS)
- **LEFT + another key**: Alt/Option chord

**RIGHT Arrow Key** (tap=Right Arrow, hold=Cmd/Win):
- **Quick tap** (<200ms): Right arrow  
- **Hold** (>200ms): Command (macOS) or Windows key
- **RIGHT + another key**: Cmd/Win chord

**Examples**:
- Tap space quickly → ` ` (space character)
- Hold space → Ctrl (can then press other keys for shortcuts)
- Quick Space+S → Ctrl+S (save)
- Quick Space+C → Ctrl+C (copy)

**Disable dual-role keys:**
```python
# In code.py for regular spacebar:
controller = ChatpadController(kb, simple_space=True, debug=True)
# Note: LEFT/RIGHT dual-role is always active for better ergonomics
```

#### Sticky Shift
**Activation**: Hold Shift + Orange together
- Toggles sticky shift mode
- When active, all keys remain shifted until toggled off
- Useful for typing long sequences in CAPS
- Toggle off by pressing Shift + Orange again

#### Layer Indicators & NeoPixel
- **People Layer**: Toggle mode - press People once to activate, press again to deactivate
- **Green/Orange Layers**: Hold mode - only active while holding the key
- **Multiple Layers**: Shift + Green/Orange for shifted symbols
- **NeoPixel LED**: Pulses to show current layer (Blue=Base, Green=Green, Orange=Orange, White=People, Purple=Shift)

#### Debug Mode
Toggle debug output to see key codes and layer changes:
- **Runtime toggle**: People + Orange (while People layer is active)
- **Permanent enable**: Edit `code.py`:
```python
controller = ChatpadController(kb, simple_space=False, debug=True)
```

Monitor debug output:
```bash
screen /dev/tty.usbmodem* 115200
# Press Ctrl+A, K to exit screen
```

## ⚙️ Configuration

### config.py Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `HOST_OS` | `"mac"` | Operating system for shortcuts: `"linux"`, `"mac"`, or `"windows"` |
| `SPACE_TAP_TIMEOUT` | `0.3` | Seconds before held space becomes Ctrl (increase if space turns to Ctrl too quickly) |
| `KEEP_ALIVE_INTERVAL` | `1.0` | Seconds between UART keep-alive messages (prevents Chatpad sleep) |
| `HEARTBEAT_INTERVAL` | `5.0` | LED heartbeat blink interval |
| `NEOPIXEL_BRIGHTNESS` | `0.3` | LED brightness if NeoPixel available (0.0-1.0) |

### 🎨 Customization

#### Customizing Layers
Edit `lib/chatpad/layers.py` to modify key mappings:
```python
# Example: Add a new key mapping to Green layer
green[Keys.A.code] = KC.LCTL(KC.A)  # Select all on Green+A
```

#### Adding Macros
Create custom macros in `lib/macros/`:

**Text macros** (types a string):
```python
# In lib/macros/terminal.py
def terminal_macros():
    return {
        "docker_ps": "docker ps -a\n",
        "npm_start": "npm start\n",
    }
```

**Key sequence macros** (sends key combinations):
```python
# In lib/macros/development.py
from kmk.handlers.sequences import Press, Tap, Release
from kmk.keys import KC

def dev_macros():
    return {
        "select_all": [Press(KC.LCTL), Tap(KC.A), Release(KC.LCTL)],
        "find": [Press(KC.LCTL), Tap(KC.F), Release(KC.LCTL)],
    }
```

Then map them in `lib/chatpad/layers.py`:
```python
people[Keys.D.code] = KC.MACRO(self.macros["docker_ps"])
```

## Project Structure

```
kmk-kb2040-chatpad/
├── code.py              # Main entry point (debug enabled)
├── config.py            # Configuration and key definitions
├── boot.py              # CircuitPython boot configuration
├── deploy.sh            # Deployment script
├── lib/
│   ├── chatpad/        # Core driver module
│   │   ├── __init__.py    # Public API
│   │   ├── keyboard.py    # KMK module & controller
│   │   ├── layers.py      # Layer definitions
│   │   ├── protocol.py    # UART protocol handler
│   │   ├── state.py       # State machines
│   │   └── led.py         # Status LED (optional)
│   ├── macros/         # Macro definitions
│   │   ├── __init__.py
│   │   ├── development.py
│   │   ├── terminal.py
│   │   └── vim.py
│   └── kmk/            # KMK firmware (git submodule)
└── docs/               # Documentation
    └── kmk-reference/  # KMK documentation
```

## Development

### Deployment Options
```bash
# Standard deployment
./deploy.sh

# Force reinstall KMK (if corrupted)
./deploy.sh --force-kmk

# Deploy to specific mount point
./deploy.sh /Volumes/CIRCUITPY
```

### Protocol Details

The Chatpad communicates via UART at 19200 baud with 8-byte frames:
- **Data frame**: `[0xB4, 0xC5, reserved, modifiers, key0, key1, reserved, checksum]`
- **Status frame**: Starts with `0xA5`
- **Init message**: `0x87 0x02 0x8C 0x1F 0xCC`
- **Keep-alive**: `0x87 0x02 0x8C 0x1B 0xD0` (sent every 1s)
- **Checksum**: `(-sum(frame[:7])) & 0xFF`

### Architecture Highlights

- **Non-blocking I/O**: UART reads never block, accumulating buffer handles partial frames
- **State machines**: Clean separation of current/previous states for edge detection
- **Deferred layer building**: Layers built after KMK modules loaded to ensure KC.MACRO exists
- **Modular design**: Clear separation between protocol, state, layers, and KMK integration

## 🔍 Troubleshooting

### Quick Fixes

| Problem | Solution |
|---------|----------|
| **Space not working** | Tap faster (<300ms) or increase `SPACE_TAP_TIMEOUT` in config.py |
| **Stuck modifier** | Press all modifiers once or wait 5 seconds for auto-clear |
| **No output** | Check TX→RX and RX→TX wiring is crossed, verify 3.3V power |
| **Wrong characters** | Set correct `HOST_OS` in config.py ("mac", "linux", "windows") |
| **Layer stuck** | Toggle People key again or press Shift+Orange for sticky shift |

### Connection Setup

**Wiring must be crossed:**
- Chatpad TX → KB2040 RX (D1)
- Chatpad RX → KB2040 TX (D0)  
- 3.3V → 3.3V
- GND → GND

**KB2040 not showing as CIRCUITPY?**
1. Hold BOOTSEL button while connecting USB
2. RPI-RP2 drive appears
3. Copy CircuitPython .uf2 file to it

### Debug Mode

**Enable debug output:**
- Runtime: People + Orange (toggles on/off)
- Permanent: In code.py set `debug=True`

**Monitor output:**
```bash
screen /dev/tty.usbmodem* 115200  # macOS/Linux
# Exit: Ctrl+A, then K
```

**Debug messages:**
- `DOWN 0x23` / `UP 0x23`: Key press/release
- `SPACE tap`: Space typed
- `SPACE → CTRL`: Space held to Ctrl
- `LEFT tap` / `RIGHT tap`: Arrow keys
- `Alt/Opt release` / `Cmd/Win release`: Modifier release

### Common Errors

**`ImportError: no module named 'kmk'`**
```bash
./deploy.sh --force-kmk  # Reinstall KMK
```

**`ValueError: RX in use`**  
Wrong pins - use D4/D5 for dummy matrix, not D0/D1

**`MemoryError`**  
Remove unused KMK modules from `/Volumes/CIRCUITPY/lib/kmk/modules/`

### Recovery

**Device unresponsive?**
1. Press RESET button twice quickly
2. RPI-RP2 drive appears
3. Reinstall CircuitPython

**Clean reinstall:**
```bash
./deploy.sh --force-kmk
```

## Contributing

Contributions are welcome! The codebase is designed to be extensible:
- Add new macros in `lib/macros/`
- Customize layers in `lib/chatpad/layers.py`
- Extend functionality via KMK modules

## License

MIT License - See LICENSE file for details

## Acknowledgments

- [KMK Firmware](https://github.com/KMKfw/kmk_firmware) - The keyboard firmware framework
- [Adafruit CircuitPython](https://circuitpython.org/) - Python for microcontrollers
- Xbox 360 Chatpad protocol reverse engineering community

## Resources

- [KMK Documentation](docs/kmk-reference/) - Local copy included
- [CircuitPython Guide](https://learn.adafruit.com/welcome-to-circuitpython)
- [Adafruit KB2040 Guide](https://learn.adafruit.com/adafruit-kb2040)
- [CLAUDE.md](CLAUDE.md) - AI assistant context for development

---

*Built with the Xbox 360 Chatpad, KMK firmware, and lots of tiny button presses* 🎮⌨️