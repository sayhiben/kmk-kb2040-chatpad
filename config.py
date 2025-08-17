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