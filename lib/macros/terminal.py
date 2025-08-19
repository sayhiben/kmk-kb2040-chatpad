"""Terminal navigation and tooling macros."""
from kmk.keys import KC
from kmk.modules.macros import Press, Release, Tap

def term_macros():
    return {
        "tmux_prefix": [Press(KC.LCTL), Tap(KC.B), Release(KC.LCTL)],
        "clear": "clear\n",
        "ssh": "ssh user@host\n",
        "python": "python3\n",
        "ls_la": "ls -la\n",
        "cd_parent": "cd ..\n",
        "docker_ps": "docker ps\n",
        # Pair insertion helpers provided in __init__ if not overridden
    }