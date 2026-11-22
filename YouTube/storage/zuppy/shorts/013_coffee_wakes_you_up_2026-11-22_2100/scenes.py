"""Episode: coffee_wakes_you_up | Channel: zuppy | Strict style"""

import math
from core.primitives import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "Coffee wakes you up—but adds no energy. Your brain builds adenosine while you're awake. It signals growing sleep pressure.",
    "Caffeine blocks the receptors that detect it. Think of it as a fake key. It jams the sleep signal's lock.",
    "But the sleepy chemical remains. Caffeine only masks tiredness for now. When it fades, will sleepiness return?",
]

CHAPTERS = ["The Wake-Up Trick", "Blocking Sleepiness"]

META = {
    "title": "Coffee Wakes You Up Without Energy (Here's Why)",
    "description": (
        "Coffee wakes you up—but it doesn't add energy. "
        "Here's the caffeine trick that blocks sleepiness.\n\n"
        "SOURCES:\n"
        "- NIH News in Health, Tired or Wired? Caffeine and Your Brain\n"
        "- Caffeine, StatPearls / NCBI Bookshelf\n"
        "- Review of caffeine's effects on cognitive, physical and occupational performance, Neurobiology of Aging\n\n"
        "#shorts #science #coffee #brain #psychology"
    ),
    "tags": (
        "why coffee wakes you up, caffeine explained, coffee energy, caffeine and adenosine, "
        "why caffeine works, brain science, sleep pressure, tiredness explained, neuroscience, "
        "health science, psychology facts, coffee facts, science shorts, 2d animation, "
        "animated explainer, science explained, everyday science, caffeine receptors, "
        "adenosine receptor blocker, how caffeine works in your brain, alertness mechanism"
    ),
    "pinned_comment": "Does coffee wake you up—or just hide your tiredness? 👇",
}
TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]


INK = (35, 35, 45)
WHITE = (255, 255, 255)
YEL = (255, 220, 55)
RED = (220, 65, 65)
BLUE = (65, 115, 210)
GRN = (65, 175, 115)
BG1 = (40, 45, 105)
BG2 = (225, 240, 255)
BG3 = (255, 235, 190)

def thesis(cv, t, T, k, l1, l2=None, col=WHITE):
    if not (T[k] <= t < T[k + 1]):
        return
    scale = pop(t, T[k], 0.18)
    sz = fit(l1, 54, 500)
    if l2:
        sz = min(sz, fit(l2, 54, 500))
    text(cv, cv.cfg.center_x, 850, l1, sz, col, stroke=5, scale=scale)
    if l2:
        text(cv, cv.cfg.center_x, 915, l2, sz, col, stroke=5, scale=scale)

def cup(cv, x, y, s=1.0, tilt=0.0, steam=True):
    # Cup body, handle, rim and coffee surface—only existing primitives.
    x += 5 * math.sin(tilt * 3)
    rrect(cv, x - 120*s, y - 85*s, x + 120*s, y + 150*s, 26*s, WHITE, 7)
    ell(cv, x + 145*s, y + 10*s, 55*s, 68*s, WHITE, 6)
    ell(cv, x + 145*s, y + 10*s, 33*s, 46*s, cv.bg, 0)
    ell(cv, x, y - 75*s, 105*s, 22*s, (95, 60, 35), 0)
    line(cv, [(x-90*s,y-50*s),(x+90*s,y-50*s)], 8*s, (125,85,60))
    if steam:
        for i, dx in enumerate((-55,0,55)):
            sway = math.sin(tilt*2.5+i)*20*s
            line(cv, [(x+dx*s,y-130*s),(x+(dx+18)*s+sway,y-175*s),
                      (x+(dx-12)*s-sway,y-220*s)], 7*s, WHITE)

def molecule(cv, x, y, s=1.0, rotation=0.0, fill=(155,185,245)):
    # Adenosine symbol assembled from a central dot and orbiting circles.
    ell(cv,x,y,46*s,46*s,fill,5)
    text(cv,x,y,"A",48*s,INK,stroke=1)
    for i in range(6):
        a=rotation+i*math.tau/6
        px=x+math.cos(a)*78*s
        py=y+math.sin(a)*78*s
        line(cv,[(x+math.cos(a)*38*s,y+math.sin(a)*38*s),(px,py)],5*s,fill)
        ell(cv,px,py,17*s,17*s,fill,3)

def lock(cv, x, y, s=1.0, open_=False, occupied=False):
    # Receptor as an open docking pocket.
    line(cv,[(x-58*s,y-55*s),(x-58*s,y+45*s),(x,y+88*s),
              (x+58*s,y+45*s),(x+58*s,y-55*s)],14*s,INK)
    if occupied:
        ell(cv,x,y-16*s,43*s,43*s,YEL,4)
        text(cv,x,y-16*s,"C",38*s,INK,stroke=1)
    if open_:
        line(cv,[(x+58*s,y-55*s),(x+105*s,y-90*s)],12*s,RED)

def s01(cv,t,T):
    # Hook frame: sleepy character beside an oversized, pulsing coffee cup.
    pulse=1+0.025*math.sin(24*t)
    cup(cv,205,390,0.88*pulse,tilt=math.sin(18*t),steam=True)
    person(cv,500,690,1.45,shirt=(245,195,80),mood="tired",L=(-70,20),R=(80,-35))
    text(cv,350,165,"NO ENERGY IN COFFEE?",56,WHITE,stroke=5,scale=1+0.02*math.sin(20*t))
    # Adenosine begins accumulating as the character stays awake.
    if t>=T[1]:
        n=max(1,int(2+5*rg(t,T[1],T[2])))
        for i in range(n):
            a=t*1.4+i*math.tau/n
            molecule(cv,350+math.cos(a)*170,360+math.sin(a)*110,0.34,rotation=a)
    if t>=T[2]:
        text(cv,350,500,"SLEEP PRESSURE BUILS",40,YEL,stroke=4,scale=pop(t,T[2],0.18))
    thesis(cv,t,T,0,"COFFEE ≠ ENERGY")
    thesis(cv,t,T,1,"ADENOSINE BUILDS")
    thesis(cv,t,T,2,"SLEEP PRESSURE RISES")

def s02(cv,t,T):
    rrect(cv,-20,-20,740,1300,1,BG2,0)
    # The molecule approaches its receptor, then caffeine occupies the docking site.
    x=190+230*rg(t,T[0],T[1])
    molecule(cv,x,355,0.78,rotation=t*0.7)
    lock(cv,505,355,1.0,occupied=False)
    text(cv,350,160,"THE SIGNAL GETS BLOCKED",48,INK,stroke=4)
    if t>=T[1]:
        # Caffeine is the blocking occupant; animate a direct replacement.
        lock(cv,505,355,1.0,occupied=True)
        text(cv,505,265,"CAFFEINE",32,RED,stroke=3,scale=pop(t,T[1],0.2))
        line(cv,[(x+85,355),(420,355)],9,RED)
        ell(cv,420,355,22,22,RED,0)
    if t>=T[2]:
        # Adenosine remains around the occupied receptor.
        for i in range(5):
            a=t*0.6+i*math.tau/5
            molecule(cv,350+math.cos(a)*210,400+math.sin(a)*145,0.28,rotation=a)
        text(cv,350,510,"THE SLEEP SIGNAL REMAINS",38,RED,stroke=4,scale=pop(t,T[2],0.2))
    thesis(cv,t,T,0,"CAFFEINE BLOCKS")
    thesis(cv,t,T,1,"THE RECEPTOR")
    thesis(cv,t,T,2,"BUT THE SIGNAL REMAINS",col=INK)

def s03(cv,t,T):
    rrect(cv,-20,-20,740,1300,1,BG3,0)
    # Cup shrinks/drifts away as the sleepy character slumps back.
    cup(cv,170,420,0.58*(1-0.35*rg(t,T[1],T[2])),tilt=math.sin(t*2),steam=False)
    mood="tired" if t<T[2] else "sleep"
    person(cv,500,760,1.55,shirt=(245,195,80),mood=mood,L=(-55,65),R=(70,80))
    # Persistent molecules are still present as the caffeine effect recedes.
    for i in range(7):
        a=t*0.35+i*math.tau/7
        rad=160+35*math.sin(t*1.2+i)
        molecule(cv,350+math.cos(a)*rad,340+math.sin(a)*rad*0.72,0.32,rotation=a)
    if t>=T[1]:
        text(cv,350,170,"CAFFEINE FADES",52,RED,stroke=4,scale=pop(t,T[1],0.18))
        line(cv,[(290,570),(410,570)],12,RED)
    if t>=T[2]:
        text(cv,350,500,"SLEEPINESS COMES BACK?",42,INK,stroke=4,scale=1+0.03*math.sin(18*t))
    thesis(cv,t,T,0,"IT ONLY MASKS TIREDNESS")
    thesis(cv,t,T,1,"WHEN CAFFEINE FADES…")
    thesis(cv,t,T,2,"DO YOU FEEL IT AGAIN?",col=INK)

_FN = {"s01": s01, "s02": s02, "s03": s03}
_BG = {"s01": BG1, "s02": BG2, "s03": BG3}
ORDER = ["s01", "s02", "s03"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
