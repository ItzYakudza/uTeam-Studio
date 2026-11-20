"""
Episode: Why Your Brain Won't Let You Tickle Yourself 🧠
Channel: zuppy
"""

from core.toolkit import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "First sentence goes here.",
    "Second sentence goes here.",
]

CHAPTERS = ["Hook", "Main"]

TITLE = "Why Your Brain Won't Let You Tickle Yourself 🧠"
DESC = """Description.

SOURCES
- ...
"""
TAGS = "tag1, tag2"

def s01(cv, t, T):
    title(cv, t, "Why Your Brain Won't Let You Tickle Yourself 🧠", 56, 140)

def s02(cv, t, T):
    title(cv, t, "Scene 2", 52, 140)

TRANSITIONS = {}

_FN = {"s01": s01, "s02": s02}
_BG = {"s01": (255, 248, 225), "s02": (232, 240, 255)}
ORDER = ["s01", "s02"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
