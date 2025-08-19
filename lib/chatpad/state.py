"""State machines for modifiers, keys, and Space dual‑role."""
from time import monotonic
from config import Modifiers, SPACE_TAP_TIMEOUT

class ModifierState:
    def __init__(self):
        self.current = 0
        self.previous = 0
        self.shift_sticky = False
        self.people_toggle = False

    def update(self, new_mods):
        self.previous = self.current
        self.current = new_mods
        # Rising edge on People toggles dev layer
        if self.rising(Modifiers.PEOPLE):
            self.people_toggle = not self.people_toggle
        # Sticky Shift toggled by Shift+Orange chord rising
        chord = (self.current & Modifiers.SHIFT) and (self.current & Modifiers.ORANGE)
        chord_prev = (self.previous & Modifiers.SHIFT) and (self.previous & Modifiers.ORANGE)
        if chord and not chord_prev:
            self.shift_sticky = not self.shift_sticky

    def rising(self, mask):
        return (self.current & mask) and not (self.previous & mask)

    @property
    def shift_active(self):
        return self.shift_sticky or bool(self.current & Modifiers.SHIFT)

    @property
    def green_active(self):
        return bool(self.current & Modifiers.GREEN)

    @property
    def orange_active(self):
        return bool(self.current & Modifiers.ORANGE)


class KeyState:
    def __init__(self):
        self.current = [0, 0]
        self.previous = [0, 0]

    def update(self, k0, k1):
        self.previous = self.current[:]
        self.current = [k0, k1]

    def pressed(self):
        out = []
        for k in self.current:
            if k and k not in self.previous:
                out.append(k)
        return out

    def released(self):
        out = []
        for k in self.previous:
            if k and k not in self.current:
                out.append(k)
        return out


class SpaceKeyState:
    """Dual‑role Space: tap Space or hold/chord to Ctrl."""
    def __init__(self):
        self.is_down = False
        self.down_at = 0.0
        self.ctrl_active = False

    def press(self):
        self.is_down = True
        self.down_at = monotonic()
        self.ctrl_active = False

    def release(self):
        was_ctrl = self.ctrl_active
        was_space = self.is_down and not self.ctrl_active
        self.is_down = False
        self.ctrl_active = False
        return was_space, was_ctrl

    def promote_by_time(self):
        if self.is_down and not self.ctrl_active:
            if monotonic() - self.down_at > SPACE_TAP_TIMEOUT:
                self.ctrl_active = True
                return True
        return False

    def promote_by_chord(self):
        if self.is_down and not self.ctrl_active:
            self.ctrl_active = True
            return True
        return False


class DualRoleKeyState:
    """Generic dual-role key: tap for one action, hold for modifier."""
    def __init__(self, tap_timeout=0.200):
        self.is_down = False
        self.down_at = 0.0
        self.mod_active = False
        self.tap_timeout = tap_timeout

    def press(self):
        self.is_down = True
        self.down_at = monotonic()
        self.mod_active = False

    def release(self):
        was_mod = self.mod_active
        was_tap = self.is_down and not self.mod_active
        self.is_down = False
        self.mod_active = False
        return was_tap, was_mod

    def promote_by_time(self):
        if self.is_down and not self.mod_active:
            if monotonic() - self.down_at > self.tap_timeout:
                self.mod_active = True
                return True
        return False

    def promote_by_chord(self):
        if self.is_down and not self.mod_active:
            self.mod_active = True
            return True
        return False