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