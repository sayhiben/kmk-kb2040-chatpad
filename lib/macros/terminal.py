"""Terminal navigation and tooling macros."""
from kmk.keys import KC
from kmk.modules.macros import Press, Release, Tap

def term_macros():
    return {
        "tmux_prefix": KC.MACRO(Press(KC.LCTL), Tap(KC.B), Release(KC.LCTL)),
        "clear": KC.MACRO("clear\n"),
        "ssh": KC.MACRO("ssh user@host\n"),
        "python": KC.MACRO("python3\n"),
        "ls_la": KC.MACRO("ls -la\n"),
        "cd_parent": KC.MACRO("cd ..\n"),
        "docker_ps": KC.MACRO("docker ps\n"),
        # Pair insertion helpers provided in __init__ if not overridden
    }