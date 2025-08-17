"""Aggregate macros for Chatpad layers."""
from .development import dev_macros
from .terminal import term_macros
from .vim import vim_macros

def get_all_macros():
    out = {}
    out.update(dev_macros())
    out.update(term_macros())
    out.update(vim_macros())
    # Pair insertion defaults if any are missing
    ensure = {
        "pair_paren": "()",
        "pair_brace": "{}",
        "pair_bracket": "[]",
        "pair_angle": "<>",
        "pair_squote": "''",
        "pair_dquote": '""',
    }
    from kmk.keys import KC
    from kmk.modules.macros import Tap
    for name, s in ensure.items():
        if name not in out:
            # Insert pair and move caret left
            out[name] = KC.MACRO(s, Tap(KC.LEFT))
    return out