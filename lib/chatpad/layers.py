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

        # Green: symbols layer (hold green button + key)
        green = {
            Keys.Q.code: KC.EXCLAIM,      # Q = !
            Keys.W.code: KC.AT,           # W = @
            Keys.E.code: KC.DOLLAR,       # E = $
            Keys.R.code: KC.HASH,         # R = #
            Keys.T.code: KC.PERCENT,      # T = %
            Keys.Y.code: KC.CIRCUMFLEX,   # Y = ^
            Keys.U.code: KC.AMPERSAND,    # U = &
            Keys.I.code: KC.ASTERISK,     # I = *
            Keys.O.code: KC.LPRN,         # O = (
            Keys.P.code: KC.RPRN,         # P = )
            Keys.A.code: KC.TILDE,        # A = ~
            # S = None
            Keys.D.code: KC.LCBR,         # D = {
            Keys.F.code: KC.RCBR,         # F = }
            # G = None
            Keys.H.code: KC.SLASH,        # H = /
            Keys.J.code: KC.QUOTE,        # J = '
            Keys.K.code: KC.LBRC,         # K = [
            Keys.L.code: KC.RBRC,         # L = ]
            Keys.COMMA.code: KC.COLON,    # , = :
            Keys.Z.code: KC.GRV,          # Z = `
            # X = None
            # C = None
            Keys.V.code: KC.MINUS,        # V = -
            Keys.B.code: KC.PIPE,         # B = |
            Keys.N.code: KC.LABK,         # N = <
            Keys.M.code: KC.RABK,         # M = >
            Keys.PERIOD.code: KC.QUESTION, # . = ?
        }

        # Orange: secondary symbols and special keys (hold orange button + key)
        orange = {
            # Most keys are None except for these:
            Keys.P.code: KC.EQUAL,         # P = =
            Keys.H.code: KC.BSLASH,        # H = \
            Keys.J.code: KC.DQUO,          # J = "
            Keys.COMMA.code: KC.SCOLON,    # , = ;
            Keys.V.code: KC.UNDS,          # V = _
            Keys.B.code: KC.PLUS,          # B = +
            # Keep function keys on number row for convenience
            Keys.N1.code: KC.F1,
            Keys.N2.code: KC.F2,
            Keys.N3.code: KC.F3,
            Keys.N4.code: KC.F4,
            Keys.N5.code: KC.F5,
            Keys.N6.code: KC.F6,
            Keys.N7.code: KC.F7,
            Keys.N8.code: KC.F8,
            Keys.N9.code: KC.F9,
            Keys.N0.code: KC.F10,
            # Additional function keys on unused keys (F/G unused in spec)
            Keys.F.code: KC.F11,
            Keys.G.code: KC.F12,
            # Navigation keys (arrows on dedicated arrow keys)
            Keys.LEFT.code: KC.LEFT,
            Keys.RIGHT.code: KC.RIGHT,
            # Additional arrow cluster on WASD for convenience
            Keys.W.code: KC.UP,
            Keys.A.code: KC.LEFT,
            Keys.S.code: KC.DOWN,
            Keys.D.code: KC.RIGHT,
            # Tab and untab
            Keys.T.code: KC.TAB,
            Keys.Y.code: KC.LSFT(KC.TAB),  # Shift+Tab for untab
            # ESC easily accessible
            Keys.Q.code: KC.ESC,
            # Caps lock toggle is now on Orange+Shift (handled in keyboard.py)
        }

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