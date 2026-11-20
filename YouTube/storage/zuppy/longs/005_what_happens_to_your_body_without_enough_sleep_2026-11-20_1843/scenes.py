"""
Episode: What Happens to Your Body Without Enough Sleep?
Channel: zuppy
"""

from core.toolkit import *

MODE = "long"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "First sentence goes here.",
    "Second sentence goes here.",
]

CHAPTERS = ["Hook", "Main"]

TITLE = 'What Happens to Your Body Without Enough Sleep?'
DESC = """Description.

SOURCES
- ...
"""
TAGS = "tag1, tag2"

def s01(cv, t, T):
    title(cv, t, 'What Happens to Your Body Without Enough Sleep?', 56, 140)

def s02(cv, t, T):
    title(cv, t, "Scene 2", 52, 140)

TRANSITIONS = {}

_FN = {"s01": s01, "s02": s02}
_BG = {"s01": (255, 248, 225), "s02": (232, 240, 255)}
ORDER = ["s01", "s02"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
