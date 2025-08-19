"""Xbox 360 Chatpad KMK Firmware."""
import board
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import DiodeOrientation
from kmk.keys import KC

from lib.chatpad import ChatpadController

# Initialize keyboard with minimal matrix
# The Chatpad uses UART for input, not a key matrix
kb = KMKKeyboard()
kb.col_pins = (board.D4,)  # Dummy pin (TX/RX are D0/D1)
kb.row_pins = (board.D5,)  # Dummy pin
kb.diode_orientation = DiodeOrientation.COL2ROW
kb.keymap = [[KC.NO]]  # Placeholder since we inject keys via UART

# Configure and start Chatpad controller
# Options:
#   simple_space: False = dual-role space (tap for space, hold for Ctrl)
#                 True = regular spacebar
#   debug: True = show key press/release messages
controller = ChatpadController(kb, simple_space=False, debug=True)
controller.go()