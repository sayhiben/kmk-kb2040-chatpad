"""Developer‑oriented macros: git, save, build."""
from kmk.keys import KC
from kmk.modules.macros import Press, Release, Tap

def dev_macros():
    return {
        "save": KC.MACRO(Press(KC.LCTL), Tap(KC.S), Release(KC.LCTL)),
        "build": KC.MACRO(Press(KC.LCTL), Press(KC.LSFT), Tap(KC.B), Release(KC.LSFT), Release(KC.LCTL)),
        "git_status": KC.MACRO("git status\n"),
        "git_add": KC.MACRO("git add "),
        "git_commit": KC.MACRO('git commit -m ""', Tap(KC.LEFT)),
        "git_push": KC.MACRO("git push\n"),
    }