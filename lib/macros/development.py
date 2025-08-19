"""Developer‑oriented macros: git, save, build."""
from kmk.keys import KC
from kmk.modules.macros import Press, Release, Tap

def dev_macros():
    return {
        "save": [Press(KC.LCTL), Tap(KC.S), Release(KC.LCTL)],
        "build": [Press(KC.LCTL), Press(KC.LSFT), Tap(KC.B), Release(KC.LSFT), Release(KC.LCTL)],
        "git_status": "git status\n",
        "git_add": "git add ",
        "git_commit": ['git commit -m ""', Tap(KC.LEFT)],
        "git_push": "git push\n",
    }