"""
Episode: 012_doorway_effect_2026-11-20_2240
Channel: zuppy
Topic: doorway effect / location updating and event segmentation
"""

import math
from core.toolkit import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "You enter a room—and forget why. "
    "It feels like a mental reset.",
    "It's called the doorway effect. "
    "Some experiments found memory dips after a room change.",
    "Your brain may be updating its model of the current event. "
    "That shift can interfere with a goal held in mind.",
    "But later experiments found the effect isn't universal. "
    "Has a doorway ever erased your mission?",
]

CHAPTERS = [
    "The blank moment",
    "The doorway effect",
    "A changing mental model",
    "Not always",
]

META = {
    "title": "Why You Forget Why You Entered a Room",
    "description": (
        "You walk into a room and suddenly forget your mission. This is known as the doorway effect—but "
        "the science is more nuanced than the name suggests.\n\n"
        "SOURCES:\n"
        "- Radvansky, G. A. & Copeland, D. E. (2006). Walking through doorways causes forgetting: situation "
        "models and experienced space. Memory & Cognition, 34, 1150–1156. doi:10.3758/BF03193261\n"
        "- Radvansky, G. A., Krawietz, S. A., & Tamplin, A. K. (2011). Walking through doorways causes "
        "forgetting: Further explorations. Quarterly Journal of Experimental Psychology, 64, 1632–1645. "
        "doi:10.1080/17470218.2011.571267\n"
        "- McFadyen, J. et al. (2021). Doorways do not always cause forgetting: a multimodal investigation. "
        "BMC Psychology, 9, 41. doi:10.1186/s40359-021-00536-3\n\n"
        "#shorts #brain #psychology #memory #neuroscience"
    ),
    "tags": (
        "doorway effect, why do I forget why I walked into a room, forget why I entered a room, "
        "memory glitch, everyday brain glitches, brain tricks, psychology facts, neuroscience explained, "
        "working memory, event segmentation, event boundaries, location updating effect, memory and attention, "
        "why we forget, human brain, cognitive psychology, science explained, everyday science, "
        "2d animation, animated explainer, brain facts, memory experiment, doorway memory illusion, "
        "short science video, psychology shorts, zuppy"
    ),
    "pinned_comment": "What was the last thing you forgot the moment you entered a room?",
}
TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]

INK = (28, 28, 34)
WHITE = (255, 255, 255)
RED = (235, 55, 72)
YELLOW = (255, 205, 55)
BLUE = (65, 125, 220)
GREEN = (75, 160, 115)
VIOLET = (44, 30, 88)
PALE = (232, 239, 250)

def thesis(cv, t, T, k, line1, line2=None, col=WHITE, second=YELLOW):
    if not (T[k] <= t < T[k + 1]):
        return
    cx = cv.cfg.center_x
    scale = pop(t, T[k], 0.16)
    size = fit_safe(cv, line1, 55)
    if line2:
        size = min(size, fit_safe(cv, line2, 55))
    text(cv, cx, 865, line1, size, col, stroke=6, scale=scale)
    if line2:
        text(cv, cx, 930, line2, size, second, stroke=6, scale=scale)

def doorway(cv, cx, cy, scale=1.0, col=WHITE, fill=None):
    w, h = 170 * scale, 245 * scale
    line(cv, [(cx - w, cy + h), (cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h)], 10, col)
    line(cv, [(cx + 35 * scale, cy - h + 10), (cx + 35 * scale, cy + h - 10)], 5, col)
    ell(cv, cx + 5 * scale, cy + 8 * scale, 7 * scale, fill=YELLOW, w=0)

def person(cv, x, y, scale=1.0, mood="shock", col=WHITE):
    ell(cv, x, y - 125 * scale, 52 * scale, fill=col, w=6)
    if mood == "shock":
        ell(cv, x - 18 * scale, y - 135 * scale, 7 * scale, fill=INK, w=0)
        ell(cv, x + 18 * scale, y - 135 * scale, 7 * scale, fill=INK, w=0)
        ell(cv, x, y - 110 * scale, 9 * scale, fill=None, w=4, col=INK)
    else:
        line(cv, [(x - 18 * scale, y - 125 * scale), (x + 18 * scale, y - 125 * scale)], 5, INK)
        line(cv, [(x - 12 * scale, y - 108 * scale), (x + 12 * scale, y - 108 * scale)], 4, INK)
    line(cv, [(x, y - 70 * scale), (x, y + 65 * scale)], 13, col)
    line(cv, [(x, y - 25 * scale), (x - 65 * scale, y + 25 * scale)], 10, col)
    line(cv, [(x, y - 25 * scale), (x + 65 * scale, y + 15 * scale)], 10, col)
    line(cv, [(x, y + 65 * scale), (x - 45 * scale, y + 145 * scale)], 11, col)
    line(cv, [(x, y + 65 * scale), (x + 45 * scale, y + 145 * scale)], 11, col)

def keys(cv, x, y, scale=1.0, col=YELLOW):
    ell(cv, x, y, 25 * scale, fill=None, w=9, col=col)
    line(cv, [(x + 22 * scale, y), (x + 100 * scale, y)], 9, col)
    line(cv, [(x + 72 * scale, y), (x + 72 * scale, y + 22 * scale)], 8, col)
    line(cv, [(x + 92 * scale, y), (x + 92 * scale, y + 16 * scale)], 8, col)

def s01(cv, t, T):
    # Hook: the person and doorway are present from frame zero.
    cx = cv.cfg.center_x
    rrect(cv, 0, 0, 720, 1280, 1, VIO, 0)
    doorway(cv, cx + 45, 515, 1.02, WHITE, None)
    person(cv, cx - 155, 655, 1.05, "shock", WHITE)
    keys(cv, cx + 130, 650, 0.75, YELLOW)
    pulse = 1.0 + 0.035 * math.sin(t * 13)
    ell(cv, cx + 45, 515, 215 * pulse, fill=None, w=5, col=RED)
    text(cv, cx, 175, "WHY AM I HERE?", fit_safe(cv, "WHY AM I HERE?", 60), YELLOW, stroke=6)
    if t >= T[1]:
        text(cv, cx, 760, "MENTAL RESET?", 46, WHITE, stroke=5, scale=1 + 0.025 * math.sin(t * 10))
    thesis(cv, t, T, 0, "ENTER A ROOM", "FORGET WHY?")
    thesis(cv, t, T, 1, "A MENTAL", "RESET?")

def s02(cv, t, T):
    cx = cv.cfg.center_x
    rrect(cv, 0, 0, 720, 1280, 1, (239, 232, 220), 0)
    doorway(cv, cx, 500, 1.12, INK, None)
    person(cv, cx - 190, 675, 0.82, "flat", BLUE)
    keys(cv, cx + 115, 690, 0.68, RED)
    if t >= T[1]:
        # A visual "memory drop" as the character crosses the threshold.
        for i in range(5):
            k = pop(t, T[1] + 0.12 * i)
            ell(cv, cx + 120 + i * 28, 760 + i * 16, 8 * k, fill=RED, w=0)
        text(cv, cx, 300, "DOORWAY EFFECT", fit_safe(cv, "DOORWAY EFFECT", 52), RED, stroke=5)
    thesis(cv, t, T, 0, "THE DOORWAY", "EFFECT")
    thesis(cv, t, T, 1, "MEMORY CAN", "DIP AFTER A MOVE")

def s03(cv, t, T):
    cx = cv.cfg.center_x
    rrect(cv, 0, 0, 720, 1280, 1, (220, 235, 249), 0)
    # Two event models: the old room fades as the new one takes focus.
    rrect(cv, 65, 300, 320, 690, 26, (250, 250, 255), 6)
    rrect(cv, 380, 300, 655, 690, 26, (250, 250, 255), 6)
    text(cv, 192, 350, "OLD ROOM", 31, BLUE)
    text(cv, 517, 350, "NEW ROOM", 31, GREEN)
    keys(cv, 165, 505, 0.55, YELLOW)
    arrow(cv, 325, 510, 390, 510, 9, RED, 1.0)
    if t >= T[1]:
        # The remembered goal becomes harder to retrieve amid the context shift.
        ell(cv, 515, 505, 68, fill=(255, 226, 220), w=5, col=RED)
        text(cv, 515, 505, "?", 72, RED)
        text(cv, cx, 760, "GOAL IN WORKING MEMORY", fit_safe(cv, "GOAL IN WORKING MEMORY", 38), INK)
    thesis(cv, t, T, 0, "YOUR BRAIN", "UPDATES THE EVENT")
    thesis(cv, t, T, 1, "THE SHIFT CAN", "INTERFERE WITH A GOAL")

def s04(cv, t, T):
    cx = cv.cfg.center_x
    rrect(cv, 0, 0, 720, 1280, 1, (242, 235, 249), 0)
    ell(cv, cx, 480, 170, fill=WHITE, w=7)
    text(cv, cx, 480, "?", 150, RED, stroke=4)
    if t >= T[1]:
        text(cv, cx, 700, "HAS THIS HAPPENED TO YOU?", fit_safe(cv, "HAS THIS HAPPENED TO YOU?", 42), INK)
        for dx in (-215, 215):
            ell(cv, cx + dx, 480, 20, fill=YELLOW, w=0)
    thesis(cv, t, T, 0, "NOT EVERY STUDY", "FINDS THE EFFECT")
    thesis(cv, t, T, 1, "WHAT DID YOU", "FORGET?")

_FN = {"s01": s01, "s02": s02, "s03": s03, "s04": s04}
_BG = {"s01": VIOLET, "s02": (239, 232, 220), "s03": (220, 235, 249), "s04": (242, 235, 249)}
ORDER = ["s01", "s02", "s03", "s04"]
SCENES = [(_BG[name], _FN[name]) for name in ORDER]
