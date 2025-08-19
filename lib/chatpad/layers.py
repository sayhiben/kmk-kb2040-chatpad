"""Layer selection and key mappings."""
from config import Keys, Modifiers, HOST_OS

class LayerManager:
    def __init__(self, macros):
        self.macros = macros
        self.layers = {}
        self._layers_built = False
        # Don't build layers yet - KC.MACRO won't exist until Macros module is loaded

    def _build_layers(self):
        # Only build once
        if self._layers_built:
            return
        
        from kmk.keys import KC
        
        # Base typing layer
        base = {}
        # Letters
        for key in [
            Keys.Q, Keys.W, Keys.E, Keys.R, Keys.T, Keys.Y, Keys.U, Keys.I, Keys.O, Keys.P,
            Keys.A, Keys.S, Keys.D, Keys.F, Keys.G, Keys.H, Keys.J, Keys.K, Keys.L,
            Keys.Z, Keys.X, Keys.C, Keys.V, Keys.B, Keys.N, Keys.M
        ]:
            base[key.code] = getattr(KC, key.name)
        # Numbers
        nums = [Keys.N1, Keys.N2, Keys.N3, Keys.N4, Keys.N5, Keys.N6, Keys.N7, Keys.N8, Keys.N9, Keys.N0]
        for idx, key in enumerate(nums, 1):
            base[key.code] = getattr(KC, "N{}".format(idx % 10))
        # Punctuation and specials
        base[Keys.COMMA.code] = KC.COMMA
        base[Keys.PERIOD.code] = KC.DOT
        base[Keys.SPACE.code] = KC.SPACE
        base[Keys.ENTER.code] = KC.ENTER
        base[Keys.BACKSPACE.code] = KC.BSPC
        base[Keys.LEFT.code] = KC.LEFT
        base[Keys.RIGHT.code] = KC.RIGHT

        # Green: coding symbols and helpers (pair insertion via macros)
        # Pair‑insertion macros are in macros dict: pair_paren, pair_brace, pair_bracket, pair_angle, pair_squote, pair_dquote
        green = {
            Keys.D.code: KC.MACRO(self.macros["pair_bracket"]),
            Keys.F.code: KC.MACRO(self.macros["pair_brace"]),
            Keys.R.code: KC.MACRO(self.macros["pair_paren"]),
            Keys.C.code: KC.MACRO(self.macros["pair_angle"]),
            Keys.COMMA.code: KC.MACRO(self.macros["pair_squote"]),
            Keys.PERIOD.code: KC.MACRO(self.macros["pair_dquote"]),
            Keys.X.code: KC.PIPE,
            Keys.Z.code: KC.TILDE,
            Keys.G.code: KC.GRV,
            # Add vim navigation on HJKL (accessible with Green/Shift)
            # Original symbols moved to nearby keys
            Keys.Y.code: KC.UNDS,  # Was on H
            Keys.H.code: KC.LEFT,
            Keys.J.code: KC.DOWN,
            Keys.K.code: KC.UP,
            Keys.L.code: KC.RIGHT,
            Keys.N.code: KC.MINS,  # Was on J
            Keys.V.code: KC.BSLS,
            Keys.B.code: KC.SLASH,
            Keys.E.code: KC.ESC,
            Keys.T.code: KC.TAB,
            Keys.I.code: KC.PGUP,
            Keys.U.code: KC.HOME,
            Keys.O.code: KC.END,
            Keys.P.code: KC.PGDN,  # Moved from M
        }

        # Orange: function keys and navigation
        orange = {}
        fnums = [Keys.N1, Keys.N2, Keys.N3, Keys.N4, Keys.N5, Keys.N6, Keys.N7, Keys.N8, Keys.N9, Keys.N0]
        for idx, key in enumerate(fnums, 1):
            orange[key.code] = getattr(KC, "F{}".format(idx))
        orange[Keys.P.code] = KC.F11
        orange[Keys.O.code] = KC.F12
        orange[Keys.Q.code] = KC.PSCR
        orange[Keys.W.code] = KC.SLCK
        orange[Keys.E.code] = KC.PAUS
        orange[Keys.A.code] = KC.INS
        orange[Keys.S.code] = KC.DEL
        orange[Keys.I.code] = KC.UP
        orange[Keys.K.code] = KC.DOWN
        orange[Keys.J.code] = KC.LEFT
        orange[Keys.L.code] = KC.RIGHT
        # Add PLUS and EQUAL that were displaced from green layer
        orange[Keys.M.code] = KC.PLUS
        orange[Keys.N.code] = KC.EQUAL
        # Add modifier keys for convenience
        orange[Keys.Z.code] = KC.LCTL  # Ctrl on Z
        orange[Keys.X.code] = KC.LALT  # Alt on X  
        orange[Keys.C.code] = KC.LGUI  # Command/Win on C

        # People: dev shortcuts and navigation
        if HOST_OS.lower() in ("linux", "mac"):
            word_left = KC.LALT(KC.LEFT)
            word_right = KC.LALT(KC.RIGHT)
        else:
            word_left = KC.LCTL(KC.LEFT)
            word_right = KC.LCTL(KC.RIGHT)

        # Select appropriate GUI/Alt key based on OS
        if HOST_OS.lower() == "mac":
            gui_key = KC.LGUI  # Command key on macOS
            alt_key = KC.LALT  # Option key on macOS
        else:
            gui_key = KC.LGUI  # Windows key on Windows/Linux
            alt_key = KC.LALT  # Alt key

        people = {
            # Arrows on IJKL
            Keys.I.code: KC.UP,
            Keys.K.code: KC.DOWN,
            Keys.J.code: KC.LEFT,
            Keys.L.code: KC.RIGHT,
            # Home/End
            Keys.COMMA.code: KC.HOME,
            Keys.PERIOD.code: KC.END,
            # Word navigation
            Keys.H.code: word_left,
            Keys.U.code: word_right,
            # Modifier keys
            Keys.A.code: alt_key,   # Alt/Option on A
            Keys.W.code: gui_key,   # Command/Win on W
            # Macros - wrap with KC.MACRO()
            Keys.T.code: KC.MACRO(self.macros["tmux_prefix"]),
            Keys.K.code: KC.MACRO(self.macros["clear"]),  # Changed from C to K
            Keys.G.code: KC.MACRO(self.macros["git_status"]),
            Keys.S.code: KC.MACRO(self.macros["save"]),
            Keys.B.code: KC.MACRO(self.macros["build"]),
            # Clipboard operations (use OS-appropriate modifier)
            Keys.C.code: KC.LCTL(KC.C) if HOST_OS.lower() != "mac" else KC.LGUI(KC.C),  # Copy
            Keys.X.code: KC.LCTL(KC.X) if HOST_OS.lower() != "mac" else KC.LGUI(KC.X),  # Cut
            Keys.V.code: KC.LCTL(KC.V) if HOST_OS.lower() != "mac" else KC.LGUI(KC.V),  # Paste
            Keys.Z.code: KC.LCTL(KC.Z) if HOST_OS.lower() != "mac" else KC.LGUI(KC.Z),  # Undo
            Keys.Y.code: KC.LCTL(KC.Y) if HOST_OS.lower() != "mac" else KC.LGUI(KC.LSFT(KC.Z)),  # Redo
            # Quick close
            Keys.Q.code: KC.LALT(KC.F4),
            # Additional vim-friendly ESC option
            Keys.E.code: KC.ESC,
        }

        self.layers = {
            "base": base,
            "green": green,
            "orange": orange,
            "people": people,
        }
        self._layers_built = True

    def select(self, modifiers):
        # Build layers if not already built (deferred until KC.MACRO exists)
        if not self._layers_built:
            self._build_layers()
            
        if modifiers.people_toggle:
            return self.layers["people"]
        if modifiers.orange_active:
            return self.layers["orange"]
        if modifiers.green_active:
            return self.layers["green"]
        return self.layers["base"]

    def get_key(self, raw_code, modifiers):
        return self.select(modifiers).get(raw_code)