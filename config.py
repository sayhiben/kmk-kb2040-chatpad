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
SPACE_TAP_TIMEOUT = 0.300  # Increased from 175ms to 300ms for easier tapping
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