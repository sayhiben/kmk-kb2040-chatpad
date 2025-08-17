"""Layer selection and key mappings."""
from kmk.keys import KC
from config import Keys, Modifiers, HOST_OS

class LayerManager:
    def __init__(self, macros):
        self.macros = macros
        self._build_layers()

    def _build_layers(self):
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
            Keys.D.code: self.macros["pair_bracket"],
            Keys.F.code: self.macros["pair_brace"],
            Keys.R.code: self.macros["pair_paren"],
            Keys.C.code: self.macros["pair_angle"],
            Keys.COMMA.code: self.macros["pair_squote"],
            Keys.PERIOD.code: self.macros["pair_dquote"],
            Keys.X.code: KC.PIPE,
            Keys.Z.code: KC.TILDE,
            Keys.G.code: KC.GRV,
            Keys.H.code: KC.UNDS,
            Keys.J.code: KC.MINS,
            Keys.K.code: KC.PLUS,
            Keys.L.code: KC.EQUAL,
            Keys.V.code: KC.BSLS,
            Keys.B.code: KC.SLASH,
            Keys.E.code: KC.ESC,
            Keys.T.code: KC.TAB,
            Keys.I.code: KC.PGUP,
            Keys.M.code: KC.PGDN,
            Keys.U.code: KC.HOME,
            Keys.O.code: KC.END,
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

        # People: dev shortcuts and navigation
        if HOST_OS.lower() in ("linux", "mac"):
            word_left = KC.LALT(KC.LEFT)
            word_right = KC.LALT(KC.RIGHT)
        else:
            word_left = KC.LCTL(KC.LEFT)
            word_right = KC.LCTL(KC.RIGHT)

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
            # Macros
            Keys.T.code: self.macros["tmux_prefix"],
            Keys.C.code: self.macros["clear"],
            Keys.G.code: self.macros["git_status"],
            Keys.S.code: self.macros["save"],
            Keys.B.code: self.macros["build"],
            # Clipboard helpers
            Keys.X.code: KC.LCTL(KC.X),
            Keys.V.code: KC.LCTL(KC.V),
            # Quick close
            Keys.Q.code: KC.LALT(KC.F4),
        }

        self.layers = {
            "base": base,
            "green": green,
            "orange": orange,
            "people": people,
        }

    def select(self, modifiers):
        if modifiers.people_toggle:
            return self.layers["people"]
        if modifiers.orange_active:
            return self.layers["orange"]
        if modifiers.green_active:
            return self.layers["green"]
        return self.layers["base"]

    def get_key(self, raw_code, modifiers):
        return self.select(modifiers).get(raw_code)