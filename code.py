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