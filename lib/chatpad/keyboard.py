"""Chatpad controller that registers a KMK Module."""
from time import monotonic
import supervisor

from kmk.modules import Module
from kmk.keys import KC

import config
from config import HEARTBEAT_INTERVAL, Modifiers
from .protocol import UARTHandler
from .state import ModifierState, KeyState, SpaceKeyState, DualRoleKeyState
from .layers import LayerManager
from .led import StatusLED
from lib.macros import get_all_macros

class ChatpadKMKModule(Module):
    """Integrates protocol, state, layers, and LED with KMK's loop."""
    def __init__(self, keyboard, simple_space=False):
        self.kb = keyboard
        self.uart = UARTHandler()
        self.mods = ModifierState()
        self.keys = KeyState()
        self.space = SpaceKeyState()
        self.left_key = DualRoleKeyState(tap_timeout=0.200)  # LEFT as dual-role
        self.right_key = DualRoleKeyState(tap_timeout=0.200)  # RIGHT as dual-role
        self.macros = get_all_macros()
        self.layers = LayerManager(self.macros)
        self.led = StatusLED()
        self.shift_down = False
        self.last_hb = monotonic()
        self.debug = False
        self.simple_space = simple_space  # Option to disable dual-role space
        self.active_keys = {}  # raw_code -> Key object pressed
        self.last_activity = monotonic()  # Track last key activity for safety reset

    def during_bootup(self, keyboard):
        """Called once during keyboard initialization."""
        # Initialize UART and send init message during bootup
        self.uart.maintain()
        if self.debug:
            print("ChatpadKMKModule initialized")
        return
    
    def after_matrix_scan(self, keyboard):
        """Called after matrix scan."""
        return
    
    def before_hid_send(self, keyboard):
        """Called before HID report is sent."""
        return
    
    def after_hid_send(self, keyboard):
        """Called after HID report is sent."""
        return
    
    def process_key(self, keyboard, key, is_pressed, int_coord):
        """Process key events - we pass through since we inject our own."""
        return key

    def before_matrix_scan(self, keyboard):
        # Maintain link and parse all available frames
        self.uart.maintain()
        report = self.uart.next_report()
        while report:
            self._process_report(report)
            report = self.uart.next_report()

        # Time‑based Space promotion (only happens once when timeout is reached)
        if not self.simple_space and self.space.promote_by_time():
            self.kb.pre_process_key(KC.LCTRL, True, None)
            if self.debug:
                print("SPACE → CTRL (timeout)")
        
        # Time-based LEFT/RIGHT key promotion
        if self.left_key.promote_by_time():
            if config.HOST_OS.lower() == "mac":
                self.kb.pre_process_key(KC.LALT, True, None)
            else:
                self.kb.pre_process_key(KC.LALT, True, None)
            if self.debug:
                print("LEFT → Alt/Option (timeout)")
                
        if self.right_key.promote_by_time():
            if config.HOST_OS.lower() == "mac":
                self.kb.pre_process_key(KC.LGUI, True, None)
            else:
                self.kb.pre_process_key(KC.LGUI, True, None)
            if self.debug:
                print("RIGHT → Cmd/Win (timeout)")
        
        # Safety: Clear stuck modifiers if no activity for 5 seconds
        now = monotonic()
        if self.active_keys or self.shift_down or self.space.is_down:
            self.last_activity = now
        elif now - self.last_activity > 5.0:
            if self.shift_down:
                self.kb.pre_process_key(KC.LSFT, False, None)
                self.shift_down = False
                if self.debug:
                    print("Safety: cleared stuck shift")
            if self.space.ctrl_active:
                self.kb.pre_process_key(KC.LCTRL, False, None)
                self.space.ctrl_active = False
                self.space.is_down = False
                if self.debug:
                    print("Safety: cleared stuck ctrl")
            # Reset sticky states
            if self.mods.shift_sticky:
                self.mods.shift_sticky = False
                if self.debug:
                    print("Safety: cleared sticky shift")

        # LED and heartbeat
        self.led.update_for(self.mods)
        now = monotonic()
        if now - self.last_hb > HEARTBEAT_INTERVAL:
            self.led.heartbeat()
            self.last_hb = now

        # Return None (no extra matrix update needed)
        return

    # Internal
    def _process_report(self, rep):
        # Update modifiers and handle sticky shift
        prev_mods = self.mods.current
        self.mods.update(rep["modifiers"])

        # Check for shift double-tap → ESC
        if self.mods.check_shift_double_tap():
            # Send ESC on double-tap
            self.kb.pre_process_key(KC.ESC, True, None)
            self.kb.pre_process_key(KC.ESC, False, None)
            if self.debug:
                print("SHIFT double-tap → ESC")
            # Don't process shift normally for this tap
            return

        # Debug toggle: press Orange while People is active
        if self.mods.people_toggle and self.mods.rising(Modifiers.ORANGE):
            self.debug = not self.debug
            print("Debug", "ON" if self.debug else "OFF")
        
        # Caps Lock toggle: press Shift while Orange is held
        if (self.mods.current & Modifiers.ORANGE) and self.mods.rising(Modifiers.SHIFT):
            # Send Caps Lock key press and release
            self.kb.pre_process_key(KC.CAPS, True, None)
            self.kb.pre_process_key(KC.CAPS, False, None)
            if self.debug:
                print("Orange+Shift → CAPS LOCK toggle")
            # Don't process shift normally for this event
            return

        # Host Shift handling
        if self.mods.shift_active and not self.shift_down:
            self.kb.pre_process_key(KC.LSFT, True, None)
            self.shift_down = True
        elif not self.mods.shift_active and self.shift_down:
            self.kb.pre_process_key(KC.LSFT, False, None)
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

        from config import Keys
        
        # LEFT key handling (dual-role: tap=Left Arrow, hold=Alt/Option)
        if raw == Keys.LEFT.code:
            self.left_key.press()
            return
            
        # RIGHT key handling (dual-role: tap=Right Arrow, hold=Cmd/Win)
        if raw == Keys.RIGHT.code:
            self.right_key.press()
            return
        
        # If LEFT is held and another key pressed, promote to Alt
        if self.left_key.promote_by_chord():
            if config.HOST_OS.lower() == "mac":
                self.kb.pre_process_key(KC.LALT, True, None)  # Option on Mac
            else:
                self.kb.pre_process_key(KC.LALT, True, None)  # Alt on Windows/Linux
                
        # If RIGHT is held and another key pressed, promote to Cmd/Win
        if self.right_key.promote_by_chord():
            if config.HOST_OS.lower() == "mac":
                self.kb.pre_process_key(KC.LGUI, True, None)  # Command on Mac
            else:
                self.kb.pre_process_key(KC.LGUI, True, None)  # Windows key
        
        # Space handling
        if raw == Keys.SPACE.code:
            if self.simple_space:
                # Simple space - just press it
                self.kb.pre_process_key(KC.SPACE, True, None)
                self.active_keys[raw] = KC.SPACE
                if self.debug:
                    print("SPACE DOWN (simple)")
            else:
                # Dual-role space
                self.space.press()
            return

        # If Space is held and another key goes down, promote Space to Ctrl immediately
        if not self.simple_space and self.space.promote_by_chord():
            self.kb.pre_process_key(KC.LCTRL, True, None)

        # Lookup per active layer
        key = self.layers.get_key(raw, self.mods)
        if key:
            self.kb.pre_process_key(key, True, None)
            self.active_keys[raw] = key
            if self.debug:
                print("DOWN", hex(raw))

    def _on_key_up(self, raw):
        from config import Keys
        import config
        
        # LEFT key release
        if raw == Keys.LEFT.code:
            was_tap, was_hold = self.left_key.release()
            if was_hold:
                # Release Alt/Option
                if config.HOST_OS.lower() == "mac":
                    self.kb.pre_process_key(KC.LALT, False, None)
                else:
                    self.kb.pre_process_key(KC.LALT, False, None)
            elif was_tap:
                # Send Left Arrow
                self.kb.tap_key(KC.LEFT)
            if self.debug:
                print("LEFT tap" if was_tap else "Alt/Opt release" if was_hold else "")
            return
            
        # RIGHT key release  
        if raw == Keys.RIGHT.code:
            was_tap, was_hold = self.right_key.release()
            if was_hold:
                # Release Cmd/Win
                if config.HOST_OS.lower() == "mac":
                    self.kb.pre_process_key(KC.LGUI, False, None)
                else:
                    self.kb.pre_process_key(KC.LGUI, False, None)
            elif was_tap:
                # Send Right Arrow
                self.kb.tap_key(KC.RIGHT)
            if self.debug:
                print("RIGHT tap" if was_tap else "Cmd/Win release" if was_hold else "")
            return
        
        if raw == Keys.SPACE.code:
            if self.simple_space:
                # Simple space release
                self.kb.pre_process_key(KC.SPACE, False, None)
                if raw in self.active_keys:
                    del self.active_keys[raw]
                if self.debug:
                    print("SPACE UP (simple)")
            else:
                # Dual-role space
                was_space, was_ctrl = self.space.release()
                if was_ctrl:
                    self.kb.pre_process_key(KC.LCTRL, False, None)
                elif was_space:
                    if self.debug:
                        print(f"Sending SPACE via tap_key, KC.SPACE={KC.SPACE}")
                    self.kb.tap_key(KC.SPACE)
                if self.debug:
                    print("SPACE tap" if was_space else "CTRL rel")
            return

        key = self.active_keys.pop(raw, None)
        if not key:
            # Fallback to current layer if not tracked
            key = self.layers.get_key(raw, self.mods)
        if key:
            self.kb.pre_process_key(key, False, None)
            if self.debug:
                print("UP  ", hex(raw))


class ChatpadController:
    """Public entry: install module and KMK basics, then start KMK."""
    def __init__(self, keyboard, simple_space=False, debug=False):
        self.kb = keyboard
        self.simple_space = simple_space
        self.debug = debug

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

        # Register Chatpad module with configuration
        chatpad = ChatpadKMKModule(self.kb, simple_space=self.simple_space)
        chatpad.debug = self.debug
        self.kb.modules.append(chatpad)

        print("Chatpad KMK ready")
        self.kb.go()