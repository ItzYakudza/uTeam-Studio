"""
Episode: 002_american_hoaxes_2026-11-19_1500
Channel: zuppy
Long, about 12 minutes. Five American hoaxes, ending with a hoax about a hoax.
"""

import math
from core.primitives import *

MODE = "long"
CHANNEL_NAME = "zuppy"

TEXTS = [
    # 01 hook (5)
    "In eighteen thirty-five, a respected New York newspaper told its readers that bat-winged people lived on the Moon. "
    "It described blue unicorns, beavers that walked on two legs, and a glittering temple with a golden roof. "
    "Thousands of people believed every word, and they paid a penny a day to read more. "
    "Over the next hundred years, Americans would fall for talking ghosts, a giant buried in a farm field, a miracle cure made from snakes, and an alien invasion on the radio. "
    "Stay until the end, because the last story is a hoax about a hoax.",
    # 02 why (5)
    "Before we meet the liars, we need to understand the crowd. "
    "In the eighteen hundreds, there was no television, no internet, and no way to check a story in seconds. "
    "If a trusted newspaper printed something, most people assumed it was true. "
    "Wonder was also big business, because new telescopes, new machines, and new discoveries seemed to appear every year. "
    "When the real world keeps surprising you, a fake surprise slips right in.",
    # 03 penny press (5)
    "The first hoax came from a new kind of newspaper called the penny press. "
    "In eighteen thirty-three, a printer named Benjamin Day launched The New York Sun and sold it for just one cent, far cheaper than older papers. "
    "Cheap papers needed huge crowds to earn money from advertisements, so editors hunted for shocking stories. "
    "The Sun already printed crime, scandal, and strange news that fancier papers avoided. "
    "All it needed was one story big enough to make the whole city talk.",
    # 04 moon announce (5)
    "On August twenty-fifth, eighteen thirty-five, the Sun began a series of six articles about a stunning discovery. "
    "The articles claimed that Sir John Herschel, a real and famous British astronomer, had pointed a gigantic telescope at the Moon and seen life. "
    "The details came from a Doctor Andrew Grant, who was invented by the writer, and from a science journal that had actually stopped publishing years before. "
    "Herschel really was working in South Africa at the time, so the lie wore a costume made of truth. "
    "Most historians say the author was a Sun reporter named Richard Adams Locke, who did not sign his name.",
    # 05 creatures (5)
    "Each day, the story grew wilder. "
    "Readers met blue goat-like unicorns, and beavers that walked upright and lived in huts with chimneys. "
    "Then came the stars of the show, winged people called man-bats, who seemed to talk, wave their arms, and gather by a lake. "
    "Locke wrote in a calm, scientific style, with measurements and long technical words, so it felt more like a lab report than a fairy tale. "
    "People crowded around newsstands, and sales of the Sun jumped.",
    # 06 reaction (5)
    "So, did everyone really believe it? "
    "Not everyone, but many did, and other papers copied the story as if it were real news. "
    "Some visitors, including scholars, traveled to the Sun's office asking to see the original journal, and they were told it was still at the printer. "
    "Religious groups reportedly even talked about sending missionaries to the Moon. "
    "On September sixteenth, the Sun admitted it was a hoax, and most readers simply laughed.",
    # 07 aftermath (4)
    "The real Herschel was said to be amused at first, then annoyed, as letters from believers kept arriving. "
    "Locke later said he meant it as a joke on far-fetched astronomy claims of the time, but he had badly underestimated how much people wanted it to be true. "
    "Remember that lesson, because it comes back in every story. "
    "A trusted voice, a bit of real science, and a wonderful fantasy make a very powerful mix.",
    # 08 fox setup (5)
    "Now let's jump ahead thirteen years, to a small farmhouse in Hydesville, New York. "
    "In March of eighteen forty-eight, two sisters named Maggie and Kate Fox, aged fourteen and eleven, told their mother that a ghost was knocking in the house. "
    "Their mother asked the ghost questions, and it answered with knocks. "
    "Neighbors poured in to listen, and soon the knocks were said to come from a murdered peddler. "
    "A farmhouse mystery had just become national news.",
    # 09 spreading (5)
    "Their older sister Leah took charge of the show, and moved the girls to Rochester and then to New York City. "
    "Soon the sisters were holding seances, which are gatherings where a medium claims to speak with the dead, for paying guests. "
    "The craze was called Spiritualism, and within a few years it had followers across the country. "
    "Many families were grieving, because disease took so many people, and a message from a lost loved one felt like medicine for the heart. "
    "Spiritualism grew into a movement with newspapers, meetings, and followers by the thousands.",
    # 10 confession (5)
    "Forty years later, Maggie shocked the nation. "
    "On October twenty-first, eighteen eighty-eight, she stood on the stage of the New York Academy of Music in front of about two thousand people. "
    "In her stocking feet, she cracked the joints of her toes, and the loud raps echoed through the hall. "
    "Doctors from the audience came up to check, and they agreed the sounds came from her toes. "
    "She said the whole thing began as a prank on their mother.",
    # 11 aftermath (5)
    "You might expect Spiritualism to collapse that night, but instead it kept growing. "
    "Maggie was reportedly paid for her confession, she was struggling with poverty and alcohol, and a year later she took it back. "
    "Believers argued that the sisters had been genuine at first and had only faked it later. "
    "The sisters died poor and largely forgotten, yet the movement they started outlived them. "
    "Here is the lesson: when a belief gives comfort, a confession alone is not enough to kill it.",
    # 12 cardiff setup (5)
    "Our third hoax began with an argument about the Bible. "
    "In eighteen sixty-eight, a cigar maker named George Hull, an atheist from Binghamton, New York, argued with a believer who insisted that giants once walked the Earth. "
    "Hull decided to give believers their giant. "
    "He had a huge block of gypsum carved into a ten-foot man, then roughened and stained it so it looked ancient. "
    "The whole project cost him about twenty-six hundred dollars, a small fortune at the time.",
    # 13 burial (5)
    "He shipped the giant by train to his cousin's farm in Cardiff, New York, and buried it in the ground. "
    "A year later, in October of eighteen sixty-nine, workers hired to dig a well uncovered a giant stone man. "
    "Within days, the farm was charging visitors admission, and the crowds were enormous. "
    "Preachers said it proved the Bible's giants were real, while some scientists called it a fake right away. "
    "But people kept buying tickets, because it was a great show.",
    # 14 barnum (5)
    "A group of investors led by David Hannum bought the giant and moved it to Syracuse, where ticket sales kept rising. "
    "The famous showman Barnum offered a huge sum for it, reportedly fifty thousand dollars, and Hannum said no. "
    "So Barnum did something wonderfully shameless, and made a plaster copy, displayed it in New York, and called his the real one. "
    "Hannum sued, and was quoted making fun of the crowds who paid to see Barnum's copy, saying that a sucker is born every minute. "
    "People still blame Barnum for that famous line, but the words seem to belong to Hannum.",
    # 15 exposure (4)
    "The truth came out on December tenth, eighteen sixty-nine, when George Hull confessed to the press. "
    "In February, a judge ruled that Barnum could not be sued for calling a fake giant a fake. "
    "In the end, everyone had been fooled, including the man who owned the original fake. "
    "Today the original giant sits in the Farmers' Museum in Cooperstown, New York, and visitors still line up to see it.",
    # 16 snake oil show (5)
    "Not every hoax needed a giant, because some only needed a bottle. "
    "In eighteen ninety-three, a showman named Clark Stanley, who called himself the Rattlesnake King, became a star at the World's Fair in Chicago. "
    "In front of a crowd, he pulled a live rattlesnake from a sack, sliced it open, and dropped it into boiling water so the fat floated to the top. "
    "He skimmed the fat, mixed it into a liniment, and sold bottles of Stanley's Snake Oil to the people watching. "
    "Historians say the snake act was only a show, and the liniment he sold had been prepared ahead of time.",
    # 17 snake oil truth (6)
    "There was a twist, because real snake oil did exist. "
    "Chinese railroad workers in America used oil from the Chinese water snake, which is rich in omega-three fats, to ease their sore joints. "
    "American salesmen copied the idea with rattlesnakes, whose oil has much less of those healthy fats. "
    "In nineteen seventeen, years after the Pure Food and Drug Act, federal investigators seized a shipment of Stanley's bottles and tested it. "
    "They found mostly mineral oil, beef fat, red pepper, and turpentine, but no snake oil. "
    "Stanley was fined twenty dollars, and the words snake oil became a nickname for any fake cure.",
    # 18 war of the worlds setup (6)
    "Our final story happened on October thirtieth, nineteen thirty-eight, the night before Halloween. "
    "A twenty-three-year-old director named Orson Welles put on a radio drama based on the novel The War of the Worlds. "
    "It was staged like a real news broadcast, with reporters describing Martians landing in New Jersey. "
    "The next morning, newspapers across America reported that thousands of people had panicked, fled their homes, and flooded police stations. "
    "For decades, textbooks and documentaries repeated that Welles had terrified a nation. "
    "But historians who studied the evidence found a very different story.",
    # 19 reality (6)
    "That night, a ratings company called Hooper telephoned five thousand households and asked what people were listening to. "
    "Only about two percent said they were tuning in to Welles, while many were hearing a popular comedy show on another station. "
    "Some listeners really were frightened, and some called police and newspapers, but scholars say a check of six New York hospitals found no cases linked to the broadcast. "
    "Many media historians argue that newspapers inflated the panic, because they were fighting radio for advertising money and wanted to show that radio could not be trusted. "
    "A famous book by the psychologist Hadley Cantril in nineteen forty helped turn the legend into accepted fact, even though critics say his numbers were weak. "
    "So the biggest hoax of all may be the story we tell about the people who fell for a hoax.",
    # 20 why (5)
    "So why do smart people fall for these stories? "
    "First, we trust sources that look official, whether that is a newspaper, a scientist's name, or a confident voice on the radio. "
    "Second, we love a story that matches what we already hope is true, like life on the Moon, messages from lost loved ones, or proof of ancient giants. "
    "Third, once we have shared a story, admitting we were wrong feels embarrassing, so many people simply keep believing. "
    "And finally, a hoax that is fun, mysterious, or comforting travels faster than a boring correction.",
    # 21 shield (5)
    "The good news is that you can protect yourself with a few simple questions. "
    "Who is telling this story, and how do they actually know? "
    "Is there a second, independent source, or is everyone copying the same claim? "
    "Who gains money or attention if I believe this, and does it seem too perfect? "
    "Pause for ten seconds before sharing, because that tiny delay stops many hoaxes.",
    # 22 outro (6)
    "From moon men to toe-cracking ghosts, from stone giants to snake oil, American history is full of tall tales that people loved. "
    "The hoaxers were clever, but the real engine was always us, with our curiosity, our hope, and our wish for wonder. "
    "Curiosity is never the problem, as long as it comes with a little healthy doubt. "
    "Which of these five hoaxes surprised you the most? "
    "Tell Zuppy in the comments. "
    "Thanks for watching, and stay curious with Zuppy.",
]

CHAPTERS = [
    "Hook",
    "Why people believed",
    "The penny press",
    "The Great Moon Hoax",
    "Bat-men and unicorns",
    "Did people believe it?",
    "The aftermath",
    "The ghost in Hydesville",
    "Spiritualism spreads",
    "The toe-cracking confession",
    "Why Spiritualism survived",
    "The giant idea",
    "Buried treasure",
    "Barnum joins in",
    "The truth about the giant",
    "The Rattlesnake King",
    "What was in the bottle",
    "War of the Worlds",
    "The panic that wasn't",
    "Why we fall for it",
    "Your hoax shield",
    "Final thoughts",
]

META = {
    "title": "America's Biggest Hoaxes (Why Millions Believed)",
    "description": (
        "In 1835, a New York newspaper said bat-people lived on the Moon, and thousands believed it. "
        "This animated story follows five American hoaxes, from ghost knocks and a buried giant to fake snake oil, "
        "and ends with a twist about the most famous panic of all.\n\n"
        "CHAPTERS\n{chapters}\n\n"
        "SOURCES:\n"
        "- Great Moon Hoax, six articles in The New York Sun, 1835 (Wikipedia overview): https://en.wikipedia.org/wiki/Great_Moon_Hoax\n"
        "- Britannica, The Great Moon Hoax of 1835 Was Sci-Fi Passed Off as News: https://www.britannica.com/story/the-great-moon-hoax-of-1835-was-sci-fi-passed-off-as-news\n"
        "- Matthew Goodman, The Sun and the Moon (2008)\n"
        "- Fox sisters and the Hydesville rappings (Wikipedia overview): https://en.wikipedia.org/wiki/Fox_sisters\n"
        "- Society for Psychical Research, Psi Encyclopedia, Fox Sisters: https://psi-encyclopedia.spr.ac.uk/articles/fox-sisters/\n"
        "- Cardiff Giant (Wikipedia overview): https://en.wikipedia.org/wiki/Cardiff_Giant\n"
        "- NPR Code Switch, A History Of 'Snake Oil Salesmen' (2013): https://www.npr.org/sections/codeswitch/2013/08/26/215761377/a-history-of-snake-oil-salesmen\n"
        "- NPR, 75 Years Ago, 'War Of The Worlds' Started A Panic. Or Did It? (2013): https://www.npr.org/sections/thetwo-way/2013/10/30/241797346/75-years-ago-war-of-the-worlds-started-a-panic-or-did-it\n"
        "- Jefferson Pooley and Michael Socolow, The Myth of the War of the Worlds Panic, Slate (2013)\n"
        "- Hadley Cantril, The Invasion from Mars (1940)\n\n"
        "This video is educational history. Some details, such as audience sizes and sale prices, are estimates that vary between sources.\n\n"
        "#history #hoaxes #americanhistory #animation #facts"
    ),
    "tags": (
        "american hoaxes, biggest hoaxes in history, great moon hoax, fox sisters, cardiff giant, "
        "snake oil salesman, war of the worlds panic, orson welles, history of hoaxes, famous hoaxes, "
        "why people believe hoaxes, fake news history, spiritualism history, american history explained, "
        "history documentary animated, fake news 1800s, barnum hoaxes, 2d animation, animated explainer, zuppy"
    ),
    "pinned_comment": "Which hoax would have fooled YOU back then? Be honest 👇",
}

TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]

# ============================================================
# Palette + helpers
# ============================================================

RED = (210, 60, 60)
BLUE = (60, 90, 190)
YEL = (250, 200, 40)
GRN = (60, 150, 80)
PINK = (255, 190, 200)
SKY = (200, 230, 255)
PAPER = (255, 250, 235)
WARN = (255, 215, 210)
OKAY = (220, 245, 220)
NAVY = (24, 32, 80)
BROWN = (150, 105, 70)
STONE = (200, 200, 195)
MOONC = (245, 240, 200)
CX = 640


def sk(t, T):
    k = 0
    for i in range(len(T) - 1):
        if t >= T[i]:
            k = i
    return k


def wipe(cv):
    rrect(cv, -30, -30, 1310, 750, 1, cv.bg, 0)


def hd(cv, t, T, s):
    title(cv, t, s, 52, 100, a=T[0] + 0.1)


def cap(cv, t, a, s, y, size=46, col=INK, x=CX, maxw=1000):
    k = pop(t, a)
    if k <= 0.03:
        return
    text(cv, x, y, s, fit(s, size, maxw), col, scale=k)


def tag(cv, t, a, s, x, y, size=34, fill=(255, 246, 200), col=INK, maxw=520):
    k = pop(t, a)
    if k <= 0.03:
        return
    sz = fit(s, size, maxw)
    w = twidth(s, sz) / 2 + 24
    h = sz * 0.72
    rrect(cv, x - w * k, y - h * k, x + w * k, y + h * k, 16, fill, 4)
    text(cv, x, y, s, sz, col, scale=k)


def card(cv, t, a, x0, y0, x1, y1, fill=PAPER):
    k = pop(t, a)
    if k <= 0.03:
        return False
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    hw = (x1 - x0) / 2 * k
    hh = (y1 - y0) / 2 * k
    rrect(cv, cx - hw, cy - hh, cx + hw, cy + hh, 22, fill, 5)
    return k >= 0.95


def cross(cv, x, y, s=1.0, col=RED):
    line(cv, [(x - 50 * s, y - 50 * s), (x + 50 * s, y + 50 * s)], 10, col)
    line(cv, [(x + 50 * s, y - 50 * s), (x - 50 * s, y + 50 * s)], 10, col)


def check(cv, x, y, s=1.0, col=GRN):
    line(cv, [(x - 40 * s, y), (x - 10 * s, y + 35 * s), (x + 45 * s, y - 40 * s)], 12, col)


def heart(cv, x, y, s=1.0, col=RED):
    if s < 0.05:
        return
    pts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        px = 16 * math.sin(a) ** 3
        py = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + px * 3 * s, y + py * 3 * s))
    poly(cv, pts, col, 5)


def crowd(cv, t, a, x0, x1, y, n=8, s=1.0):
    for i in range(n):
        k = pop(t, a + i * 0.08, 0.3)
        if k <= 0.03:
            continue
        x = x0 + (x1 - x0) * i / max(1, n - 1)
        ell(cv, x, y + 42 * s, 28 * s * k, 36 * s * k, (200, 215, 240), 4)
        ell(cv, x, y, 24 * s * k, None, WHITE, 4)
        ell(cv, x - 8 * s, y - 3 * s, 2.5 * s * k, None, INK, 0)
        ell(cv, x + 8 * s, y - 3 * s, 2.5 * s * k, None, INK, 0)


def paper(cv, x, y, s=1.0, head="THE SUN", lines=4):
    if s < 0.05:
        return
    rrect(cv, x - 110 * s, y - 140 * s, x + 110 * s, y + 140 * s, 8 * s, PAPER, 5)
    text(cv, x, y - 110 * s, head, fit(head, 30 * s, 190 * s))
    line(cv, [(x - 90 * s, y - 85 * s), (x + 90 * s, y - 85 * s)], 4, INK)
    for i in range(lines):
        yy = y - 55 * s + i * 28 * s
        line(cv, [(x - 90 * s, yy), (x + 90 * s, yy)], 3, (150, 150, 160))
    rrect(cv, x - 90 * s, y + 60 * s, x - 10 * s, y + 120 * s, 4 * s, (210, 215, 225), 3)


def moon(cv, x, y, r, col=MOONC):
    ell(cv, x, y, r, r, col, 6)
    for dx, dy, rr in ((-0.35, -0.25, 0.18), (0.3, 0.1, 0.22), (-0.1, 0.4, 0.14), (0.35, -0.45, 0.1)):
        ell(cv, x + dx * r, y + dy * r, rr * r, rr * r, (225, 220, 175), 3)


def telescope(cv, x, y, s=1.0):
    if s < 0.05:
        return
    ex = x + 230 * s
    ey = y - 170 * s
    line(cv, [(x - 30 * s, y + 20 * s), (x + 30 * s, y - 20 * s)], 10, INK)
    line(cv, [(x, y), (ex, ey)], 36 * s, INK)
    line(cv, [(x, y), (ex, ey)], 26 * s, (180, 150, 100))
    ell(cv, ex, ey, 16 * s, 16 * s, SKY, 4)
    line(cv, [(x + 60 * s, y - 40 * s), (x + 20 * s, y + 90 * s)], 7, INK)
    line(cv, [(x + 60 * s, y - 40 * s), (x + 110 * s, y + 90 * s)], 7, INK)


def batman(cv, x, y, s=1.0, t=0.0):
    if s < 0.05:
        return
    fl = math.sin(t * 6) * 0.35
    for sg in (-1, 1):
        tip = (x + sg * 120 * s, y - 60 * s - 80 * s * fl)
        poly(cv, [(x + sg * 14 * s, y - 40 * s), tip, (x + sg * 95 * s, y + 10 * s + 30 * s * fl),
                  (x + sg * 50 * s, y + 30 * s), (x + sg * 14 * s, y + 30 * s)], (120, 90, 110), 5)
    ell(cv, x, y, 26 * s, 44 * s, (190, 150, 120), 5)
    face(cv, x, y - 62 * s, 24 * s, s * 0.6, "smile")


def unicorn(cv, x, y, s=1.0):
    if s < 0.05:
        return
    blue = (150, 190, 255)
    ell(cv, x, y, 60 * s, 34 * s, blue, 5)
    for dx in (-38, -14, 22, 44):
        line(cv, [(x + dx * s, y + 28 * s), (x + dx * s, y + 80 * s)], 7, INK)
    ell(cv, x + 62 * s, y - 38 * s, 26 * s, 22 * s, blue, 5)
    poly(cv, [(x + 70 * s, y - 56 * s), (x + 92 * s, y - 110 * s), (x + 80 * s, y - 54 * s)], YEL, 4)
    ell(cv, x + 70 * s, y - 42 * s, 3 * s, None, INK, 0)


def beaver(cv, x, y, s=1.0):
    if s < 0.05:
        return
    ell(cv, x, y - 50 * s, 32 * s, 52 * s, BROWN, 5)
    ell(cv, x, y - 118 * s, 26 * s, 24 * s, BROWN, 5)
    ell(cv, x - 9 * s, y - 124 * s, 3 * s, None, INK, 0)
    ell(cv, x + 9 * s, y - 124 * s, 3 * s, None, INK, 0)
    rrect(cv, x - 6 * s, y - 108 * s, x + 6 * s, y - 92 * s, 2, WHITE, 3)
    poly(cv, [(x - 26 * s, y - 6 * s), (x - 84 * s, y + 8 * s), (x - 30 * s, y + 20 * s)], (110, 80, 60), 4)


def house(cv, x, y, s=1.0, col=(235, 225, 205)):
    if s < 0.05:
        return
    rrect(cv, x - 110 * s, y - 90 * s, x + 110 * s, y + 80 * s, 8 * s, col, 5)
    poly(cv, [(x - 130 * s, y - 85 * s), (x, y - 170 * s), (x + 130 * s, y - 85 * s)], (190, 110, 90), 5)
    rrect(cv, x - 24 * s, y + 5 * s, x + 24 * s, y + 80 * s, 6 * s, BROWN, 4)
    rrect(cv, x - 90 * s, y - 50 * s, x - 50 * s, y - 10 * s, 4 * s, SKY, 4)
    rrect(cv, x + 50 * s, y - 50 * s, x + 90 * s, y - 10 * s, 4 * s, SKY, 4)


def ghost(cv, x, y, s=1.0, t=0.0):
    if s < 0.05:
        return
    pts = [(x + 55 * s, y + 55 * s)]
    for i in range(9):
        a = math.pi * i / 8
        pts.append((x + 55 * s * math.cos(a), y - 30 * s - 70 * s * math.sin(a)))
    pts.append((x - 55 * s, y + 55 * s))
    for j in range(1, 4):
        pts.append((x - 55 * s + j * 27.5 * s, y + 55 * s + 10 * s * math.sin(j * 2.4 + t * 5)))
    poly(cv, pts, WHITE, 5)
    ell(cv, x - 18 * s, y - 35 * s, 7 * s, None, INK, 0)
    ell(cv, x + 18 * s, y - 35 * s, 7 * s, None, INK, 0)
    ell(cv, x, y - 8 * s, 10 * s, 14 * s, INK, 0)


def giant(cv, x, y, s=1.0, col=STONE):
    if s < 0.05:
        return
    ell(cv, x, y, 150 * s, 34 * s, col, 6)
    ell(cv, x - 175 * s, y - 6 * s, 34 * s, 30 * s, col, 6)
    ell(cv, x - 182 * s, y - 12 * s, 3 * s, None, INK, 0)
    rrect(cv, x + 120 * s, y - 34 * s, x + 250 * s, y - 6 * s, 10 * s, col, 5)
    rrect(cv, x + 120 * s, y + 4 * s, x + 250 * s, y + 32 * s, 10 * s, col, 5)
    line(cv, [(x - 90 * s, y - 10 * s), (x - 20 * s, y + 6 * s)], 6, col)
    line(cv, [(x - 90 * s, y - 10 * s), (x - 20 * s, y + 6 * s)], 3, (150, 150, 145))
    for dx in (-60, 0, 60, 100):
        line(cv, [(x + dx * s, y - 20 * s), (x + (dx + 14) * s, y - 8 * s)], 3, (150, 150, 145))


def foot(cv, x, y, s=1.0):
    if s < 0.05:
        return
    ell(cv, x, y, 70 * s, 38 * s, (255, 214, 200), 5)
    for dx, dy, r in ((70, -22, 13), (88, -8, 12), (96, 8, 11), (98, 22, 10), (92, 34, 9)):
        ell(cv, x + dx * s, y + dy * s, r * s, None, (255, 214, 200), 4)


def bottle(cv, x, y, s=1.0, col=SKY, label=None, size=18):
    if s < 0.05:
        return
    rrect(cv, x - 30 * s, y - 60 * s, x + 30 * s, y + 70 * s, 16 * s, col, 5)
    rrect(cv, x - 14 * s, y - 96 * s, x + 14 * s, y - 56 * s, 6 * s, col, 5)
    rrect(cv, x - 18 * s, y - 116 * s, x + 18 * s, y - 94 * s, 6 * s, (190, 150, 100), 5)
    if label:
        rrect(cv, x - 26 * s, y - 16 * s, x + 26 * s, y + 36 * s, 6 * s, WHITE, 3)
        text(cv, x, y + 10 * s, label, size * s)


def snake(cv, x, y, s=1.0, t=0.0, col=(120, 160, 70), n=9):
    if s < 0.05:
        return
    pts = [(x + i * 26 * s, y + 18 * s * math.sin(i * 0.9 + t * 3)) for i in range(n)]
    line(cv, pts, 14 * s, INK)
    line(cv, pts, 8 * s, col)
    hx, hy = pts[-1]
    ell(cv, hx + 8 * s, hy, 13 * s, 10 * s, col, 4)
    ell(cv, hx + 12 * s, hy - 3 * s, 2.5 * s, None, INK, 0)


def pot(cv, x, y, s=1.0, t=0.0):
    if s < 0.05:
        return
    rrect(cv, x - 80 * s, y - 40 * s, x + 80 * s, y + 50 * s, 18 * s, (120, 125, 135), 6)
    ell(cv, x, y - 40 * s, 80 * s, 16 * s, (90, 150, 200), 4)
    for i in range(4):
        ell(cv, x - 50 * s + i * 34 * s, y - 48 * s - ((t * 30 + i * 15) % 24) * s, 6 * s, None, WHITE, 3)


def tv(cv, x, y, s=1.0):
    rrect(cv, x - 70 * s, y - 50 * s, x + 70 * s, y + 50 * s, 10 * s, (200, 205, 215), 5)
    rrect(cv, x - 56 * s, y - 38 * s, x + 40 * s, y + 38 * s, 6 * s, SKY, 3)


def phone(cv, x, y, s=1.0):
    rrect(cv, x - 34 * s, y - 62 * s, x + 34 * s, y + 62 * s, 10 * s, (200, 205, 215), 5)
    rrect(cv, x - 26 * s, y - 46 * s, x + 26 * s, y + 40 * s, 4 * s, SKY, 3)


def bulb(cv, x, y, s=1.0):
    if s < 0.05:
        return
    ell(cv, x, y, 36 * s, 36 * s, YEL, 5)
    rrect(cv, x - 16 * s, y + 30 * s, x + 16 * s, y + 58 * s, 4 * s, (190, 190, 200), 4)


def train(cv, x, y, s=1.0):
    if s < 0.05:
        return
    rrect(cv, x - 120 * s, y - 50 * s, x, y + 30 * s, 10 * s, (200, 70, 60), 5)
    rrect(cv, x - 120 * s, y - 90 * s, x - 70 * s, y - 50 * s, 6 * s, (150, 50, 50), 5)
    rrect(cv, x, y - 20 * s, x + 90 * s, y + 30 * s, 6 * s, (190, 150, 100), 5)
    for wx in (-90, -40, 20, 70):
        ell(cv, x + wx * s, y + 38 * s, 16 * s, 16 * s, WHITE, 4)


def museum(cv, x, y, s=1.0):
    if s < 0.05:
        return
    poly(cv, [(x - 140 * s, y - 70 * s), (x, y - 130 * s), (x + 140 * s, y - 70 * s)], (225, 215, 195), 5)
    rrect(cv, x - 140 * s, y + 60 * s, x + 140 * s, y + 85 * s, 4, (210, 205, 195), 5)
    for dx in (-100, -50, 0, 50, 100):
        rrect(cv, x + (dx - 12) * s, y - 62 * s, x + (dx + 12) * s, y + 60 * s, 4, (235, 230, 220), 4)


def gavel(cv, x, y, s=1.0):
    if s < 0.05:
        return
    line(cv, [(x - 25 * s, y - 5 * s), (x + 60 * s, y + 70 * s)], 12 * s, BROWN)
    rrect(cv, x - 70 * s, y - 45 * s, x + 20 * s, y - 5 * s, 8 * s, (170, 120, 80), 5)
    rrect(cv, x + 10 * s, y + 80 * s, x + 130 * s, y + 100 * s, 6 * s, (170, 120, 80), 5)


def radio(cv, x, y, s=1.0, t=0.0):
    if s < 0.05:
        return
    rrect(cv, x - 110 * s, y - 70 * s, x + 110 * s, y + 70 * s, 16 * s, (190, 140, 90), 6)
    ell(cv, x - 50 * s, y, 44 * s, 44 * s, (235, 215, 170), 5)
    for k in range(3):
        line(cv, [(x - 74 * s + k * 24 * s, y - 26 * s), (x - 74 * s + k * 24 * s, y + 26 * s)], 3, INK)
    ell(cv, x + 60 * s, y - 25 * s, 16 * s, 16 * s, WHITE, 4)
    ell(cv, x + 60 * s, y + 25 * s, 16 * s, 16 * s, WHITE, 4)
    line(cv, [(x + 40 * s, y - 70 * s), (x + 90 * s, y - 130 * s)], 5, INK)


def ufo(cv, x, y, s=1.0):
    if s < 0.05:
        return
    ell(cv, x, y - 12 * s, 40 * s, 34 * s, SKY, 5, INK, 180, 360)
    ell(cv, x, y, 90 * s, 24 * s, (190, 195, 205), 5)
    for dx in (-50, 0, 50):
        ell(cv, x + dx * s, y + 2 * s, 7 * s, None, YEL, 3)


def martian(cv, x, y, s=1.0):
    if s < 0.05:
        return
    g = (150, 210, 130)
    line(cv, [(x - 20 * s, y - 60 * s), (x - 30 * s, y - 100 * s)], 4, INK)
    line(cv, [(x + 20 * s, y - 60 * s), (x + 30 * s, y - 100 * s)], 4, INK)
    ell(cv, x - 30 * s, y - 104 * s, 6 * s, None, RED, 3)
    ell(cv, x + 30 * s, y - 104 * s, 6 * s, None, RED, 3)
    ell(cv, x, y, 50 * s, 60 * s, g, 5)
    ell(cv, x - 18 * s, y - 8 * s, 12 * s, 16 * s, WHITE, 4)
    ell(cv, x + 18 * s, y - 8 * s, 12 * s, 16 * s, WHITE, 4)
    ell(cv, x - 18 * s, y - 6 * s, 4 * s, None, INK, 0)
    ell(cv, x + 18 * s, y - 6 * s, 4 * s, None, INK, 0)


def hat(cv, cx, cy, hr, kind="cowboy"):
    if kind == "cowboy":
        ell(cv, cx, cy - hr * 0.85, hr * 1.7, hr * 0.28, (160, 110, 60), 5)
        rrect(cv, cx - hr * 0.7, cy - hr * 1.7, cx + hr * 0.7, cy - hr * 0.85, hr * 0.3, (160, 110, 60), 5)
    else:
        rrect(cv, cx - hr * 0.75, cy - hr * 2.2, cx + hr * 0.75, cy - hr * 0.8, 6, (50, 50, 60), 5)
        line(cv, [(cx - hr * 1.1, cy - hr * 0.85), (cx + hr * 1.1, cy - hr * 0.85)], 8, (50, 50, 60))


def shield(cv, x, y, s=1.0, col=BLUE):
    if s < 0.05:
        return
    poly(cv, [(x - 100 * s, y - 110 * s), (x, y - 135 * s), (x + 100 * s, y - 110 * s),
              (x + 100 * s, y + 10 * s), (x, y + 130 * s), (x - 100 * s, y + 10 * s)], col, 7)


def envelope(cv, x, y, s=1.0):
    if s < 0.05:
        return
    rrect(cv, x - 40 * s, y - 28 * s, x + 40 * s, y + 28 * s, 4 * s, PAPER, 4)
    line(cv, [(x - 40 * s, y - 28 * s), (x, y + 4 * s), (x + 40 * s, y - 28 * s)], 3, INK)


def burst(cv, x, y, r0, r1, n=12, col=RED):
    for i in range(n):
        a = 2 * math.pi * i / n
        line(cv, [(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 7, col)


def hoax_row(cv, t, a, y=420, s=1.0):
    xs = (190, 415, 640, 865, 1090)
    names = ("Moon", "Ghost", "Giant", "Snake oil", "Martians")
    k = [pop(t, a + i * 0.15) for i in range(5)]
    moon(cv, xs[0], y, 55 * s * k[0])
    ghost(cv, xs[1], y, 0.9 * s * k[1], t)
    giant(cv, xs[2] - 40 * s, y, 0.38 * s * k[2])
    bottle(cv, xs[3], y, 0.9 * s * k[3], SKY, "OIL", 16)
    ufo(cv, xs[4], y, 0.9 * s * k[4])
    for i in range(5):
        if k[i] > 0.4:
            text(cv, xs[i], y + 120 * s, names[i], 30, scale=k[i])


# ============================================================
# Scenes
# ============================================================

def s01(cv, t, T):
    # 0 bat-people | 1 unicorns beavers temple | 2 thousands believed, penny | 3 hoaxes ahead | 4 hoax about a hoax
    for i in range(26):
        ell(cv, 90 + (i * 149) % 1100, 70 + (i * 83) % 330, 3, None, WHITE, 0)
    k = sk(t, T)
    if k < 3:
        moon(cv, 640, 400, 150)
        paper(cv, 190, 450, 1.0 * pop(t, T[0] + 0.3), "THE SUN", 4)
        batman(cv, 700, 380, 1.3 * pop(t, T[0] + 0.8), t)
    if k == 0:
        cap(cv, t, T[0] + 0.1, "BAT-PEOPLE ON THE MOON?!", 100, size=64, col=YEL, maxw=1100)
        cap(cv, t, T[0] + 0.6, "New York, 1835", 620, size=40, col=WHITE)
    elif k == 1:
        unicorn(cv, 1020, 520, 0.9 * pop(t, T[1] + 0.2))
        beaver(cv, 900, 600, 0.9 * pop(t, T[1] + 0.8))
        tag(cv, t, T[1] + 0.4, "Blue unicorns", 1020, 360, size=30, maxw=300)
        tag(cv, t, T[1] + 1.0, "Walking beavers", 840, 250, size=30, maxw=300)
        tag(cv, t, T[1] + 1.8, "Golden temple", 330, 200, size=30, maxw=300)
    elif k == 2:
        crowd(cv, t, T[2] + 0.2, 900, 1150, 560, 4, 1.0)
        ell(cv, 960, 400, 60, None, YEL, 6)
        text(cv, 960, 400, "1 cent", 30, scale=pop(t, T[2] + 0.5))
        cap(cv, t, T[2] + 0.2, "Thousands believed it", 100, size=54, col=WHITE)
    elif k == 3:
        wipe(cv)
        for i in range(26):
            ell(cv, 90 + (i * 149) % 1100, 70 + (i * 83) % 330, 3, None, WHITE, 0)
        hoax_row(cv, t, T[3] + 0.2, 380, 1.1)
        cap(cv, t, T[3] + 0.1, "100 years of hoaxes", 100, size=54, col=WHITE)
    else:
        wipe(cv)
        cap(cv, t, T[4] + 0.1, "The last one is", 270, size=64, col=WHITE)
        cap(cv, t, T[4] + 0.6, "a hoax about a hoax", 380, size=76, col=YEL)
        text(cv, 640, 540, "?", 120, WHITE, scale=pop(t, T[4] + 1.2))


def s02(cv, t, T):
    # 0 understand the crowd | 1 no TV, no internet, no fast check | 2 trusted newspaper | 3 wonder | 4 fake surprise slips in
    hd(cv, t, T, "Why People Believed")
    k = sk(t, T)
    if k == 0:
        crowd(cv, t, T[0] + 0.3, 200, 1080, 400, 10, 1.6)
        cap(cv, t, T[0] + 1.0, "First, understand the crowd", 600, size=48, col=BLUE)
    elif k == 1:
        s1 = pop(t, T[1] + 0.2)
        s2 = pop(t, T[1] + 1.0)
        s3 = pop(t, T[1] + 1.8)
        tv(cv, 260, 360, 1.6 * s1)
        phone(cv, 640, 360, 1.5 * s2)
        if s3 > 0.05:
            clock(cv, 1020, 360, 75 * s3, 300, 60, 1.0)
        if s1 > 0.95:
            cross(cv, 260, 360, 1.2)
        if s2 > 0.95:
            cross(cv, 640, 360, 1.2)
        if s3 > 0.95:
            cross(cv, 1020, 360, 1.2)
        cap(cv, t, T[1] + 0.4, "no TV", 520, size=40, x=260, maxw=300)
        cap(cv, t, T[1] + 1.2, "no internet", 520, size=40, x=640, maxw=300)
        cap(cv, t, T[1] + 2.0, "no fast fact-check", 520, size=40, x=1020, maxw=320)
    elif k == 2:
        paper(cv, 640, 400, 1.6 * pop(t, T[2] + 0.2), "NEWS", 5)
        if pop(t, T[2] + 0.9) > 0.95:
            check(cv, 900, 380, 2.0)
        tag(cv, t, T[2] + 1.2, "Printed = must be true?", 640, 640, size=40, maxw=700)
    elif k == 3:
        telescope(cv, 230, 560, 1.4 * pop(t, T[3] + 0.2))
        bulb(cv, 640, 380, 2.0 * pop(t, T[3] + 0.9))
        train(cv, 1020, 470, 1.3 * pop(t, T[3] + 1.6))
        cap(cv, t, T[3] + 0.5, "new telescopes", 640, size=36, x=300, maxw=300)
        cap(cv, t, T[3] + 1.2, "new ideas", 640, size=36, x=640, maxw=300)
        cap(cv, t, T[3] + 1.9, "new machines", 640, size=36, x=1000, maxw=300)
    else:
        tag(cv, t, T[4] + 0.2, "Real surprises", 250, 350, size=40, fill=OKAY, maxw=360)
        if pop(t, T[4] + 0.8) > 0.5:
            arrow(cv, 430, 350, 790, 350, 8, BLUE, rg(t, T[4] + 0.8, T[4] + 1.6))
        tag(cv, t, T[4] + 1.6, "A fake one slips in", 1000, 350, size=40, fill=WARN, maxw=400)
        person(cv, 640, 640, 1.2 * pop(t, T[4] + 2.0), WHITE, "shock", (-40, 55), (40, 55), None, (110, 80, 60))


def s03(cv, t, T):
    # 0 penny press | 1 Day, one cent | 2 crowds, ads | 3 crime scandal strange | 4 one big story
    hd(cv, t, T, "The Penny Press")
    k = sk(t, T)
    if k == 0:
        paper(cv, 520, 430, 1.5 * pop(t, T[0] + 0.3), "NEWS", 5)
        ell(cv, 900, 400, 60 * pop(t, T[0] + 1.0), None, YEL, 6)
        text(cv, 900, 400, "1 cent", 32, scale=pop(t, T[0] + 1.2))
    elif k == 1:
        person(cv, 300, 640, 1.2 * pop(t, T[1] + 0.2), WHITE, "smile", (-40, 55), (40, 55), None, (90, 60, 40))
        paper(cv, 700, 430, 1.2 * pop(t, T[1] + 0.8), "NEW YORK SUN", 4)
        ell(cv, 1000, 400, 55 * pop(t, T[1] + 1.4), None, YEL, 6)
        text(cv, 1000, 400, "1 cent", 30, scale=pop(t, T[1] + 1.6))
        tag(cv, t, T[1] + 0.5, "Benjamin Day, 1833", 300, 220, size=34, maxw=400)
    elif k == 2:
        crowd(cv, t, T[2] + 0.2, 200, 1080, 380, 10, 1.3)
        crowd(cv, t, T[2] + 0.9, 240, 1040, 540, 9, 1.3)
        cap(cv, t, T[2] + 1.6, "$ $ $   ads pay the bills", 220, size=48, col=GRN)
    elif k == 3:
        for i, (lab, x) in enumerate((("CRIME!", 250), ("SCANDAL!", 640), ("STRANGE!", 1030))):
            if card(cv, t, T[3] + 0.2 + i * 0.6, x - 160, 260, x + 160, 560, PAPER):
                text(cv, x, 410, lab, 44, RED)
    else:
        bulb(cv, 640, 360, 3.0 * pop(t, T[4] + 0.2))
        tag(cv, t, T[4] + 1.0, "One story big enough", 640, 620, size=46, maxw=800)


def s04(cv, t, T):
    # 0 Aug 25, six articles | 1 Herschel telescope | 2 invented Grant, dead journal | 3 truth costume | 4 Locke
    hd(cv, t, T, "The Moon Series")
    k = sk(t, T)
    if k == 0:
        if card(cv, t, T[0] + 0.2, 340, 200, 940, 400, PAPER):
            text(cv, 640, 300, "AUGUST 25, 1835", 56, RED)
        for i in range(6):
            paper(cv, 270 + i * 148, 560, 0.45 * pop(t, T[0] + 1.2 + i * 0.25), "SUN", 2)
        cap(cv, t, T[0] + 2.0, "6 articles", 450, size=40, col=BLUE)
    elif k == 1:
        telescope(cv, 330, 590, 1.4 * pop(t, T[1] + 0.3))
        moon(cv, 980, 330, 100 * pop(t, T[1] + 1.0))
        tag(cv, t, T[1] + 0.6, "Sir John Herschel, a real astronomer", 640, 190, size=36, maxw=800)
    elif k == 2:
        tag(cv, t, T[2] + 0.3, "Doctor Andrew Grant: invented", 560, 280, size=38, fill=WARN, maxw=800)
        tag(cv, t, T[2] + 1.8, "Science journal: closed years before", 560, 460, size=38, fill=WARN, maxw=800)
        if pop(t, T[2] + 0.9) > 0.95:
            cross(cv, 1100, 280, 0.6)
        if pop(t, T[2] + 2.4) > 0.95:
            cross(cv, 1100, 460, 0.6)
    elif k == 3:
        card(cv, t, T[3] + 0.2, 120, 220, 600, 520, OKAY)
        card(cv, t, T[3] + 1.2, 680, 220, 1160, 520, WARN)
        cap(cv, t, T[3] + 0.5, "REAL", 290, size=50, col=GRN, x=360, maxw=400)
        cap(cv, t, T[3] + 0.8, "Herschel in", 380, size=36, x=360, maxw=400)
        cap(cv, t, T[3] + 1.0, "South Africa", 430, size=36, x=360, maxw=400)
        cap(cv, t, T[3] + 1.5, "FAKE", 290, size=50, col=RED, x=920, maxw=400)
        cap(cv, t, T[3] + 1.8, "Life on the Moon", 400, size=36, x=920, maxw=400)
    else:
        person(cv, 330, 640, 1.2 * pop(t, T[4] + 0.2), WHITE, "flat", (-40, 55), (40, 55), None, (90, 60, 40))
        paper(cv, 800, 420, 1.3 * pop(t, T[4] + 0.8), "THE SUN", 3)
        text(cv, 800, 440, "?", 110, RED, scale=pop(t, T[4] + 1.4))
        tag(cv, t, T[4] + 0.6, "Richard Adams Locke", 330, 230, size=34, maxw=420)
        tag(cv, t, T[4] + 1.6, "Unsigned", 800, 250, size=34, maxw=300)


def s05(cv, t, T):
    # 0 wilder | 1 unicorns beavers | 2 man-bats | 3 scientific style | 4 newsstands, sales jump
    poly(cv, [(-40, 760), (-40, 540), (300, 500), (640, 560), (1000, 490), (1320, 540), (1320, 760)], (70, 80, 120), 5)
    for i in range(26):
        ell(cv, 90 + (i * 149) % 1100, 70 + (i * 83) % 330, 3, None, WHITE, 0)
    k = sk(t, T)
    if k == 0:
        moon(cv, 640, 320, 130 * pop(t, T[0] + 0.2))
        cap(cv, t, T[0] + 0.6, "Day after day, wilder", 620, size=56, col=WHITE)
    elif k == 1:
        unicorn(cv, 330, 560, 1.4 * pop(t, T[1] + 0.3))
        beaver(cv, 800, 600, 1.3 * pop(t, T[1] + 1.2))
        house(cv, 1040, 560, 0.55 * pop(t, T[1] + 2.0))
        cap(cv, t, T[1] + 0.6, "blue unicorns", 200, size=40, col=WHITE, x=330, maxw=380)
        cap(cv, t, T[1] + 1.5, "upright beavers", 200, size=40, col=WHITE, x=800, maxw=380)
        cap(cv, t, T[1] + 2.3, "huts with chimneys", 280, size=34, col=WHITE, x=1040, maxw=340)
    elif k == 2:
        ell(cv, 640, 600, 240, 40, (90, 150, 220), 5)
        batman(cv, 340, 400, 1.4 * pop(t, T[2] + 0.2), t)
        batman(cv, 640, 300, 1.6 * pop(t, T[2] + 0.7), t + 1.0)
        batman(cv, 940, 400, 1.4 * pop(t, T[2] + 1.2), t + 2.0)
        tag(cv, t, T[2] + 1.0, "Man-bats by the lake", 640, 130, size=42, maxw=800)
    elif k == 3:
        if card(cv, t, T[3] + 0.2, 240, 190, 1040, 520, PAPER):
            text(cv, 640, 300, "Vespertilio-homo", 62, BLUE)
            text(cv, 640, 400, "measurements, long words,", 38)
            text(cv, 640, 450, "calm scientific style", 38)
    else:
        crowd(cv, t, T[4] + 0.2, 160, 600, 560, 5, 1.2)
        for i in range(5):
            h = 60 + 55 * i
            hh = h * rg(t, T[4] + 0.6 + i * 0.2, T[4] + 1.2 + i * 0.2)
            rrect(cv, 700 + i * 90, 560 - hh, 770 + i * 90, 560, 6, GRN, 5)
        cap(cv, t, T[4] + 1.8, "Sales jump!", 200, size=60, col=YEL)


def s06(cv, t, T):
    # 0 did everyone believe | 1 many did, papers copied | 2 scholars, printer | 3 missionaries | 4 Sept 16 admits
    k = sk(t, T)
    if k == 0:
        cap(cv, t, T[0] + 0.1, "Did everyone believe it?", 130, size=64, col=BLUE)
        person(cv, 300, 620, 1.2 * pop(t, T[0] + 0.5), WHITE, "smile", (-40, 55), (40, 55), None, (110, 80, 60))
        person(cv, 640, 620, 1.2 * pop(t, T[0] + 1.0), WHITE, "flat", (-40, 55), (40, 55), None, (110, 80, 60))
        person(cv, 980, 620, 1.2 * pop(t, T[0] + 1.5), WHITE, "angry", (-40, 55), (40, 55), None, (110, 80, 60))
        cap(cv, t, T[0] + 0.8, "believes", 270, size=36, x=300, maxw=260)
        cap(cv, t, T[0] + 1.3, "not sure", 270, size=36, x=640, maxw=260)
        cap(cv, t, T[0] + 1.8, "doubts", 270, size=36, x=980, maxw=260)
    elif k == 1:
        paper(cv, 280, 400, 1.3 * pop(t, T[1] + 0.3), "THE SUN", 4)
        arrow(cv, 460, 400, 800, 400, 8, BLUE, rg(t, T[1] + 1.0, T[1] + 1.8))
        paper(cv, 980, 400, 1.3 * pop(t, T[1] + 1.8), "COPY", 4)
        tag(cv, t, T[1] + 2.2, "Copied as real news", 640, 620, size=42, maxw=700)
    elif k == 2:
        rrect(cv, 800, 250, 1160, 560, 12, (225, 215, 195), 5)
        text(cv, 980, 300, "SUN OFFICE", 40)
        person(cv, 380, 620, 1.2 * pop(t, T[2] + 0.2), WHITE, "flat", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[2] + 0.6, "Show us the original!", 380, 230, size=34, maxw=420)
        tag(cv, t, T[2] + 2.0, "It is still at the printer", 980, 440, size=32, fill=WARN, maxw=340)
    elif k == 3:
        moon(cv, 640, 400, 110 * pop(t, T[3] + 0.2))
        line(cv, [(640, 260), (640, 320)], 9, INK)
        line(cv, [(612, 284), (668, 284)], 9, INK)
        tag(cv, t, T[3] + 0.6, "Missionaries to the Moon?", 640, 160, size=46, maxw=900)
    else:
        cap(cv, t, T[4] + 0.1, "September 16: the Sun admits it", 130, size=56, col=RED, maxw=1100)
        for i, x in enumerate((300, 640, 980)):
            person(cv, x, 620, 1.2 * pop(t, T[4] + 0.6 + i * 0.3), WHITE, "laugh", (-40, 55), (40, 55), None, (110, 80, 60))
        cap(cv, t, T[4] + 1.6, "Most readers laughed", 280, size=44, col=BLUE)


def s07(cv, t, T):
    # 0 Herschel amused then annoyed | 1 Locke's joke, underestimated hope | 2 remember lesson | 3 recipe
    hd(cv, t, T, "The Aftermath")
    k = sk(t, T)
    if k == 0:
        mood = "smile" if t < T[0] + 2.0 else "angry"
        person(cv, 380, 640, 1.3 * pop(t, T[0] + 0.2), WHITE, mood, (-40, 55), (40, 55), None, (200, 200, 200))
        for i in range(8):
            envelope(cv, 800 + (i % 3) * 90, 560 - (i // 3) * 40, 1.0 * pop(t, T[0] + 0.6 + i * 0.2))
        tag(cv, t, T[0] + 0.4, "Herschel", 380, 230, size=36, maxw=300)
    elif k == 1:
        card(cv, t, T[1] + 0.2, 140, 230, 600, 470, OKAY)
        card(cv, t, T[1] + 1.2, 680, 230, 1140, 470, WARN)
        cap(cv, t, T[1] + 0.6, "Meant as a joke", 350, size=42, x=370, maxw=400)
        cap(cv, t, T[1] + 1.6, "Misjudged how much", 320, size=38, x=910, maxw=400)
        cap(cv, t, T[1] + 1.8, "people wanted to believe", 370, size=38, x=910, maxw=400)
    elif k == 2:
        bulb(cv, 640, 330, 3.0 * pop(t, T[2] + 0.2))
        cap(cv, t, T[2] + 0.6, "Remember this lesson", 590, size=56, col=BLUE)
    else:
        for i, (lab, x) in enumerate((("Trusted voice", 230), ("A bit of real science", 640), ("A wonderful fantasy", 1050))):
            if card(cv, t, T[3] + 0.2 + i * 0.7, x - 190, 240, x + 190, 400, PAPER):
                text(cv, x, 320, lab, fit(lab, 38, 340))
            if i < 2:
                cap(cv, t, T[3] + 0.6 + i * 0.7, "+", 320, size=70, x=x + 205, maxw=100)
        cap(cv, t, T[3] + 2.4, "= BELIEF", 560, size=84, col=RED)


def s08(cv, t, T):
    # 0 thirteen years ahead, Hydesville | 1 sisters, ghost knocking | 2 mother asks, knocks answer | 3 murdered peddler | 4 national news
    hd(cv, t, T, "Hydesville, 1848")
    k = sk(t, T)
    if k == 0:
        house(cv, 640, 430, 1.5 * pop(t, T[0] + 0.3))
        moon(cv, 1080, 250, 60)
        cap(cv, t, T[0] + 0.8, "13 years later", 650, size=46, col=BLUE)
    elif k == 1:
        person(cv, 300, 630, 1.0 * pop(t, T[1] + 0.2), (255, 230, 240), "shock", (-40, 55), (40, 55), None, (110, 80, 60))
        person(cv, 540, 630, 0.85 * pop(t, T[1] + 0.6), (230, 240, 255), "shock", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[1] + 0.5, "Maggie, 14", 300, 250, size=34, maxw=300)
        tag(cv, t, T[1] + 0.9, "Kate, 11", 540, 330, size=34, maxw=300)
        tag(cv, t, T[1] + 2.0, "A ghost is knocking!", 960, 420, size=40, fill=WHITE, maxw=420)
    elif k == 2:
        house(cv, 300, 470, 1.2)
        for i, (x, y) in enumerate(((520, 330), (560, 420), (520, 510))):
            text(cv, x, y, "KNOCK!", 40, RED, scale=pop(t, T[2] + 0.8 + i * 0.5), rot=-8 + i * 8)
        tag(cv, t, T[2] + 0.3, "Mother asks questions", 900, 300, size=36, maxw=400)
        tag(cv, t, T[2] + 1.8, "The ghost answers with knocks", 900, 450, size=36, fill=WHITE, maxw=420)
    elif k == 3:
        ghost(cv, 640, 360, 2.0 * pop(t, T[3] + 0.3), t)
        tag(cv, t, T[3] + 1.0, "A murdered peddler?", 640, 170, size=44, maxw=700)
        crowd(cv, t, T[3] + 1.4, 200, 1080, 610, 10, 0.9)
    else:
        paper(cv, 640, 400, 1.6 * pop(t, T[4] + 0.3), "GHOSTS!", 5)
        tag(cv, t, T[4] + 1.0, "National news", 1000, 250, size=40, maxw=360)


def s09(cv, t, T):
    # 0 Leah, Rochester, NYC | 1 seances | 2 Spiritualism craze | 3 grieving | 4 movement
    hd(cv, t, T, "Spiritualism Spreads")
    k = sk(t, T)
    if k == 0:
        tag(cv, t, T[0] + 0.2, "Hydesville", 200, 400, size=34, maxw=300)
        tag(cv, t, T[0] + 1.2, "Rochester", 640, 400, size=34, maxw=300)
        tag(cv, t, T[0] + 2.2, "New York City", 1070, 400, size=34, maxw=320)
        arrow(cv, 330, 400, 500, 400, 7, BLUE, rg(t, T[0] + 0.8, T[0] + 1.3))
        arrow(cv, 780, 400, 920, 400, 7, BLUE, rg(t, T[0] + 1.8, T[0] + 2.3))
        tag(cv, t, T[0] + 0.5, "Sister Leah takes charge", 640, 240, size=42, fill=OKAY, maxw=700)
    elif k == 1:
        ell(cv, 640, 480, 240, 70, BROWN, 6)
        rrect(cv, 628, 380, 652, 460, 3, WHITE, 4)
        ell(cv, 640, 362, 12 * pop(t, T[1] + 0.8), 20 * pop(t, T[1] + 0.8), YEL, 3)
        crowd(cv, t, T[1] + 0.3, 400, 880, 330, 5, 1.0)
        tag(cv, t, T[1] + 1.4, "Seance for paying guests", 640, 640, size=42, maxw=800)
    elif k == 2:
        for i in range(4):
            r = (80 + 110 * i) * rg(t, T[2] + 0.3 + i * 0.4, T[2] + 1.2 + i * 0.4)
            ell(cv, 640, 420, r, r * 0.6, None, 5, (160, 120, 200))
        cap(cv, t, T[2] + 0.3, "SPIRITUALISM", 420, size=64, col=BLUE)
    elif k == 3:
        person(cv, 380, 640, 1.3 * pop(t, T[3] + 0.2), WHITE, "sad", (-40, 55), (40, 55), None, (110, 80, 60))
        heart(cv, 900, 400, 3.0 * pop(t, T[3] + 1.0))
        tag(cv, t, T[3] + 1.6, "A message from a lost loved one", 800, 220, size=36, maxw=700)
    else:
        for i in range(5):
            h = (70 + 65 * i) * rg(t, T[4] + 0.4 + i * 0.3, T[4] + 1.2 + i * 0.3)
            rrect(cv, 330 + i * 120, 600 - h, 410 + i * 120, 600, 6, (160, 120, 200), 5)
        cap(cv, t, T[4] + 0.4, "Newspapers. Meetings.", 200, size=44, col=BLUE)
        cap(cv, t, T[4] + 1.4, "Followers by the thousands.", 260, size=44, col=BLUE)


def s10(cv, t, T):
    # 0 forty years later, shock | 1 stage, 2000 people | 2 toe cracks | 3 doctors check | 4 prank
    hd(cv, t, T, "The Confession")
    k = sk(t, T)
    if k == 0:
        person(cv, 640, 650, 1.5 * pop(t, T[0] + 0.3), (255, 230, 240), "shock", (-40, 55), (40, 55), None, (110, 80, 60))
        cap(cv, t, T[0] + 0.8, "40 years later", 200, size=60, col=RED)
    elif k == 1:
        rrect(cv, 140, 170, 300, 560, 10, (170, 50, 60), 5)
        rrect(cv, 980, 170, 1140, 560, 10, (170, 50, 60), 5)
        rrect(cv, 140, 520, 1140, 570, 8, BROWN, 5)
        person(cv, 640, 530, 1.0 * pop(t, T[1] + 0.4), (255, 230, 240), "flat", (-40, 55), (40, 55), None, (110, 80, 60))
        crowd(cv, t, T[1] + 0.8, 200, 1080, 640, 14, 0.8)
        tag(cv, t, T[1] + 1.4, "About 2,000 people, 1888", 640, 180, size=38, maxw=700)
    elif k == 2:
        foot(cv, 520, 450, 2.2 * pop(t, T[2] + 0.2))
        if pop(t, T[2] + 1.0) > 0.5:
            burst(cv, 760, 400, 50, 100, 10, RED)
            text(cv, 960, 400, "CRACK!", 80, RED, scale=pop(t, T[2] + 1.0), rot=-8)
    elif k == 3:
        person(cv, 250, 640, 1.2 * pop(t, T[3] + 0.2), WHITE, "flat", (-40, 55), (40, 55), None, (200, 200, 200))
        person(cv, 1030, 640, 1.2 * pop(t, T[3] + 0.6), WHITE, "flat", (-40, 55), (40, 55), None, (200, 200, 200))
        foot(cv, 640, 430, 1.4 * pop(t, T[3] + 1.0))
        tag(cv, t, T[3] + 1.6, "Doctors agree: toe joints!", 640, 220, size=42, fill=OKAY, maxw=800)
    else:
        house(cv, 330, 470, 1.2 * pop(t, T[4] + 0.3))
        person(cv, 800, 640, 1.2 * pop(t, T[4] + 0.2), (255, 230, 240), "laugh", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[4] + 0.9, "It began as a prank on Mother", 640, 200, size=42, maxw=900)


def s11(cv, t, T):
    # 0 still grew | 1 paid, poverty, recanted | 2 genuine at first | 3 died poor, movement lived | 4 comfort beats confession
    hd(cv, t, T, "Why It Survived")
    k = sk(t, T)
    if k == 0:
        h = 300 * rg(t, T[0] + 0.3, T[0] + 1.5)
        rrect(cv, 520, 600 - h, 760, 600, 10, (160, 120, 200), 5)
        arrow(cv, 640, 560, 640, 220, 9, GRN, rg(t, T[0] + 1.0, T[0] + 2.0))
        tag(cv, t, T[0] + 0.4, "Confession, 1888", 250, 330, size=36, fill=WARN, maxw=380)
        tag(cv, t, T[0] + 1.6, "Spiritualism keeps growing", 1000, 330, size=36, fill=OKAY, maxw=380)
    elif k == 1:
        tag(cv, t, T[1] + 0.3, "Reportedly paid for it", 640, 230, size=42, maxw=800)
        tag(cv, t, T[1] + 1.3, "Poverty and alcohol", 640, 340, size=42, maxw=800)
        tag(cv, t, T[1] + 2.4, "A year later: she took it back", 640, 450, size=42, fill=WARN, maxw=800)
    elif k == 2:
        person(cv, 640, 640, 1.4 * pop(t, T[2] + 0.2), WHITE, "smile", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[2] + 0.6, "Genuine at first, faked later?", 640, 250, size=44, maxw=900)
    elif k == 3:
        for x in (260, 400):
            rrect(cv, x - 40 * pop(t, T[3] + 0.3), 420, x + 40 * pop(t, T[3] + 0.3), 580, 30, (200, 200, 205), 5)
            text(cv, x, 470, "RIP", 28)
        cap(cv, t, T[3] + 0.4, "died poor", 640, size=38, x=330, maxw=300)
        h = 330 * rg(t, T[3] + 1.2, T[3] + 2.2)
        rrect(cv, 800, 600 - h, 1040, 600, 10, (160, 120, 200), 5)
        cap(cv, t, T[3] + 1.4, "movement lives on", 650, size=36, x=920, maxw=340)
    else:
        heart(cv, 640, 330, 3.4 * pop(t, T[4] + 0.2))
        cap(cv, t, T[4] + 0.8, "Comfort beats confession", 600, size=60, col=BLUE)


def s12(cv, t, T):
    # 0 argument about Bible | 1 Hull vs believer | 2 give them a giant | 3 carved gypsum, stained | 4 cost
    hd(cv, t, T, "The Giant Idea")
    k = sk(t, T)
    if k == 0:
        s = pop(t, T[0] + 0.3)
        rrect(cv, 640 - 150 * s, 420 - 190 * s, 640 + 150 * s, 420 + 190 * s, 14, BROWN, 6)
        if s > 0.95:
            line(cv, [(640, 300), (640, 420)], 12, YEL)
            line(cv, [(600, 340), (680, 340)], 12, YEL)
        cap(cv, t, T[0] + 0.8, "An argument about the Bible", 640, size=52, col=BLUE)
    elif k == 1:
        person(cv, 330, 640, 1.2 * pop(t, T[1] + 0.2), WHITE, "angry", (-40, 55), (40, 55), None, (90, 60, 40))
        person(cv, 950, 640, 1.2 * pop(t, T[1] + 0.6), (60, 60, 70), "angry", (-40, 55), (40, 55), None, (200, 200, 200))
        tag(cv, t, T[1] + 0.4, "George Hull, cigar maker", 330, 200, size=34, maxw=480)
        tag(cv, t, T[1] + 1.2, "Show me proof!", 330, 290, size=36, fill=WHITE, maxw=360)
        tag(cv, t, T[1] + 2.0, "Giants really lived!", 950, 290, size=36, fill=WHITE, maxw=360)
    elif k == 2:
        person(cv, 640, 650, 1.4 * pop(t, T[2] + 0.2), WHITE, "laugh", (-40, 55), (40, 55), None, (90, 60, 40))
        bulb(cv, 640, 210, 1.4 * pop(t, T[2] + 0.8))
        tag(cv, t, T[2] + 1.2, "I will give them a giant!", 640, 320, size=40, maxw=800)
    elif k == 3:
        rrect(cv, 130, 330, 400, 520, 10, STONE, 6)
        text(cv, 265, 425, "GYPSUM", 36, scale=pop(t, T[3] + 0.4))
        arrow(cv, 430, 430, 560, 430, 8, BLUE, rg(t, T[3] + 1.0, T[3] + 1.6))
        giant(cv, 880, 430, 1.0 * pop(t, T[3] + 1.6))
        bottle(cv, 1130, 300, 0.7 * pop(t, T[3] + 2.4), (200, 245, 200), "acid", 16)
        tag(cv, t, T[3] + 0.8, "10 feet tall", 265, 250, size=34, maxw=300)
        tag(cv, t, T[3] + 2.6, "Stained to look ancient", 900, 580, size=34, maxw=480)
    else:
        giant(cv, 500, 480, 0.8 * pop(t, T[4] + 0.2))
        tag(cv, t, T[4] + 0.8, "$2,600", 900, 300, size=84, fill=YEL, maxw=420)
        cap(cv, t, T[4] + 1.6, "a small fortune then", 620, size=42, col=BLUE)


def s13(cv, t, T):
    # 0 train to cousin's farm, buried | 1 well diggers | 2 admission | 3 preachers vs scientists | 4 tickets
    hd(cv, t, T, "Buried Treasure")
    k = sk(t, T)
    if k == 0:
        line(cv, [(40, 400), (1240, 400)], 6, INK)
        train(cv, 200 + 500 * rg(t, T[0] + 0.3, T[0] + 3.0), 340, 1.3)
        rrect(cv, -20, 520, 1300, 760, 1, BROWN, 0)
        giant(cv, 880, 610, 0.8 * pop(t, T[0] + 3.0))
        tag(cv, t, T[0] + 0.5, "Cousin's farm, Cardiff, New York", 640, 200, size=38, maxw=900)
    elif k == 1:
        rrect(cv, -20, 520, 1300, 760, 1, BROWN, 0)
        giant(cv, 640, 620, 1.0 * pop(t, T[1] + 1.2))
        person(cv, 250, 520, 1.0 * pop(t, T[1] + 0.2), WHITE, "shock", (-40, 55), (40, 55), None, (110, 80, 60))
        person(cv, 1030, 520, 1.0 * pop(t, T[1] + 0.5), WHITE, "shock", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[1] + 1.0, "October 1869: a well, and a giant!", 640, 210, size=40, maxw=900)
    elif k == 2:
        rrect(cv, 760, 250, 1100, 560, 12, (225, 215, 195), 5)
        text(cv, 930, 310, "SEE THE GIANT", 36)
        text(cv, 930, 380, "ADMISSION", 30, RED)
        crowd(cv, t, T[2] + 0.3, 160, 640, 560, 6, 1.2)
        cap(cv, t, T[2] + 1.2, "Enormous crowds", 220, size=46, col=BLUE, x=400, maxw=500)
    elif k == 3:
        person(cv, 250, 640, 1.2 * pop(t, T[3] + 0.2), (60, 60, 70), "smile", (-40, 55), (40, 55), None, (200, 200, 200))
        person(cv, 1030, 640, 1.2 * pop(t, T[3] + 1.0), WHITE, "angry", (-40, 55), (40, 55), None, (200, 200, 200))
        giant(cv, 640, 450, 0.5 * pop(t, T[3] + 0.6))
        tag(cv, t, T[3] + 0.6, "Proof of Bible giants!", 250, 260, size=32, fill=OKAY, maxw=380)
        tag(cv, t, T[3] + 1.4, "A fake!", 1030, 260, size=40, fill=WARN, maxw=300)
    else:
        for i in range(6):
            kk = pop(t, T[4] + 0.2 + i * 0.25)
            if kk > 0.03:
                rrect(cv, 140 + i * 170, 330 - 40 * kk, 260 + i * 170, 330 + 40 * kk, 8, YEL, 4)
                text(cv, 200 + i * 170, 330, "$", 40, scale=kk)
        cap(cv, t, T[4] + 1.8, "Tickets kept selling", 540, size=56, col=BLUE)


def s14(cv, t, T):
    # 0 Hannum buys, Syracuse | 1 Barnum offer, no | 2 plaster copy | 3 Hannum sues, sucker line | 4 line is Hannum's
    hd(cv, t, T, "Barnum Joins In")
    k = sk(t, T)
    if k == 0:
        giant(cv, 520, 430, 1.0 * pop(t, T[0] + 0.3))
        crowd(cv, t, T[0] + 1.0, 200, 1080, 600, 10, 0.9)
        tag(cv, t, T[0] + 0.8, "David Hannum's group, Syracuse", 640, 220, size=38, maxw=900)
    elif k == 1:
        person(cv, 300, 640, 1.2 * pop(t, T[1] + 0.2), WHITE, "smile", (-40, 55), (40, 55), None, (110, 80, 60))
        pc = person(cv, 980, 640, 1.2 * pop(t, T[1] + 1.0), WHITE, "angry", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[1] + 0.5, "Barnum: $50,000?", 640, 300, size=48, fill=YEL, maxw=500)
        cap(cv, t, T[1] + 1.8, "NO!", 440, size=100, col=RED)
    elif k == 2:
        giant(cv, 640, 300, 0.6)
        giant(cv, 640, 520, 0.6 * pop(t, T[2] + 0.6))
        tag(cv, t, T[2] + 0.3, "Original (fake)", 230, 300, size=30, maxw=300)
        tag(cv, t, T[2] + 1.2, "Barnum's copy (fake)", 230, 520, size=30, maxw=320)
    elif k == 3:
        person(cv, 640, 650, 1.4 * pop(t, T[3] + 0.2), WHITE, "angry", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[3] + 0.4, "Hannum sues!", 640, 200, size=50, maxw=700)
        tag(cv, t, T[3] + 1.4, "A sucker is born every minute", 640, 320, size=44, fill=WHITE, maxw=900)
    else:
        cap(cv, t, T[4] + 0.2, "Famous line, blamed on Barnum", 300, size=48, col=BLUE, maxw=1100)
        tag(cv, t, T[4] + 1.2, "Said by Hannum", 640, 450, size=64, fill=OKAY, maxw=700)
        check(cv, 1020, 450, 1.5)


def s15(cv, t, T):
    # 0 Dec 10 confession | 1 judge | 2 everyone fooled | 3 museum
    hd(cv, t, T, "The Truth Comes Out")
    k = sk(t, T)
    if k == 0:
        if card(cv, t, T[0] + 0.2, 160, 220, 600, 450, PAPER):
            text(cv, 380, 335, "DEC 10, 1869", 52, RED)
        person(cv, 930, 640, 1.4 * pop(t, T[0] + 0.8), WHITE, "laugh", (-40, 55), (40, 55), None, (90, 60, 40))
        tag(cv, t, T[0] + 1.2, "Hull confesses", 930, 220, size=40, maxw=380)
    elif k == 1:
        gavel(cv, 400, 380, 1.8 * pop(t, T[1] + 0.2))
        tag(cv, t, T[1] + 0.8, "February 1870", 900, 300, size=44, maxw=400)
        tag(cv, t, T[1] + 1.6, "A fake can be called a fake", 900, 420, size=34, fill=OKAY, maxw=480)
    elif k == 2:
        for i, x in enumerate((250, 640, 1030)):
            person(cv, x, 640, 1.2 * pop(t, T[2] + 0.2 + i * 0.4), WHITE, "shock", (-40, 55), (40, 55), None, (110, 80, 60))
        cap(cv, t, T[2] + 1.4, "Everyone was fooled", 230, size=56, col=RED)
    else:
        museum(cv, 640, 380, 1.6 * pop(t, T[3] + 0.3))
        giant(cv, 560, 600, 0.5 * pop(t, T[3] + 1.2))
        tag(cv, t, T[3] + 1.0, "Farmers' Museum, Cooperstown", 640, 190, size=38, maxw=900)


def s16(cv, t, T):
    # 0 some need only a bottle | 1 Stanley at Chicago | 2 snake in boiling water | 3 liniment sold | 4 only a show
    hd(cv, t, T, "The Rattlesnake King")
    k = sk(t, T)
    if k == 0:
        bottle(cv, 640, 430, 2.0 * pop(t, T[0] + 0.3), SKY, "OIL", 22)
        cap(cv, t, T[0] + 0.9, "Some hoaxes only need a bottle", 650, size=46, col=BLUE, maxw=1100)
    elif k == 1:
        cx, cy, _, _ = person(cv, 640, 640, 1.3 * pop(t, T[1] + 0.2), WHITE, "smile", (-40, 55), (40, 55), None, None)
        hat(cv, cx, cy, 42 * 1.3 * pop(t, T[1] + 0.4))
        tag(cv, t, T[1] + 0.8, "Clark Stanley, 1893", 640, 190, size=44, maxw=700)
        tag(cv, t, T[1] + 1.6, "World's Fair, Chicago", 1000, 320, size=34, fill=OKAY, maxw=360)
    elif k == 2:
        snake(cv, 140, 330, 1.4 * pop(t, T[2] + 0.2), t)
        arrow(cv, 560, 330, 760, 400, 8, BLUE, rg(t, T[2] + 1.0, T[2] + 1.8))
        pot(cv, 940, 470, 1.5 * pop(t, T[2] + 1.0), t)
        tag(cv, t, T[2] + 2.2, "The fat floats up!", 940, 290, size=36, maxw=380)
    elif k == 3:
        for i in range(5):
            bottle(cv, 220 + i * 210, 440, 1.2 * pop(t, T[3] + 0.4 + i * 0.3), SKY, "OIL", 16)
        tag(cv, t, T[3] + 1.8, "Sold on the spot", 640, 640, size=46, maxw=700)
    else:
        snake(cv, 200, 380, 1.2 * pop(t, T[4] + 0.2), t)
        tag(cv, t, T[4] + 0.3, "Snake act: just a show", 330, 230, size=36, fill=WARN, maxw=520)
        bottle(cv, 960, 420, 1.4 * pop(t, T[4] + 1.2), SKY, "OIL", 18)
        tag(cv, t, T[4] + 1.4, "Liniment: made ahead", 960, 230, size=36, fill=WARN, maxw=520)


def s17(cv, t, T):
    # 0 real snake oil existed | 1 Chinese workers, omega-3 | 2 rattlesnake copies | 3 1917 test | 4 ingredients | 5 fine
    hd(cv, t, T, "The Twist")
    k = sk(t, T)
    if k == 0:
        snake(cv, 380, 400, 1.6 * pop(t, T[0] + 0.3), t, (80, 170, 110))
        cap(cv, t, T[0] + 0.8, "Real snake oil existed", 620, size=56, col=GRN)
    elif k == 1:
        line(cv, [(60, 560), (1220, 560)], 6, INK)
        for x in range(100, 1200, 80):
            line(cv, [(x, 545), (x, 575)], 5, INK)
        person(cv, 300, 540, 1.2 * pop(t, T[1] + 0.2), WHITE, "smile", (-40, 55), (40, 55), None, (20, 20, 30))
        snake(cv, 620, 300, 1.2 * pop(t, T[1] + 0.8), t, (80, 170, 110), 8)
        tag(cv, t, T[1] + 1.0, "Chinese water snake", 760, 200, size=34, maxw=480)
        tag(cv, t, T[1] + 1.8, "Rich in omega-3 fats", 760, 410, size=34, fill=OKAY, maxw=480)
    elif k == 2:
        snake(cv, 140, 300, 1.3 * pop(t, T[2] + 0.2), t, (160, 150, 120))
        tag(cv, t, T[2] + 0.4, "Rattlesnake copy", 400, 200, size=38, maxw=500)
        h1 = 300 * rg(t, T[2] + 1.0, T[2] + 1.8)
        h2 = 120 * rg(t, T[2] + 1.6, T[2] + 2.2)
        rrect(cv, 820, 620 - h1, 920, 620, 8, GRN, 5)
        rrect(cv, 980, 620 - h2, 1080, 620, 8, (160, 150, 120), 5)
        cap(cv, t, T[2] + 1.2, "water snake", 660, size=30, x=870, maxw=200)
        cap(cv, t, T[2] + 1.8, "rattlesnake", 660, size=30, x=1030, maxw=200)
    elif k == 3:
        s = pop(t, T[3] + 0.3)
        poly(cv, [(640 - 40 * s, 240), (640 + 40 * s, 240), (640 + 150 * s, 560), (640 - 150 * s, 560)], SKY, 6)
        tag(cv, t, T[3] + 0.8, "1917: federal test", 640, 170, size=46, maxw=700)
        cap(cv, t, T[3] + 1.4, "Stanley's Snake Oil", 640, size=40, col=BLUE, maxw=700)
    elif k == 4:
        if card(cv, t, T[4] + 0.2, 300, 180, 980, 600, PAPER):
            for i, lab in enumerate(("Mineral oil", "Beef fat", "Red pepper", "Turpentine")):
                cap(cv, t, T[4] + 0.6 + i * 0.5, lab, 260 + i * 62, size=42)
            cap(cv, t, T[4] + 2.8, "Snake oil: none!", 540, size=46, col=RED)
    else:
        tag(cv, t, T[5] + 0.2, "Fine: $20", 640, 260, size=92, fill=YEL, maxw=700)
        cap(cv, t, T[5] + 1.4, "snake oil = any fake cure", 480, size=52, col=BLUE)


def s18(cv, t, T):
    # 0 Oct 30 1938 | 1 Welles, 23 | 2 fake news bulletins, Martians | 3 papers: panic | 4 repeated | 5 different story
    hd(cv, t, T, "War of the Worlds")
    k = sk(t, T)
    if k == 0:
        if card(cv, t, T[0] + 0.2, 140, 220, 580, 450, PAPER):
            text(cv, 360, 335, "OCT 30, 1938", 52, RED)
        radio(cv, 920, 400, 1.5 * pop(t, T[0] + 0.8), t)
        cap(cv, t, T[0] + 1.6, "the night before Halloween", 600, size=42, col=BLUE, x=640, maxw=900)
    elif k == 1:
        person(cv, 400, 640, 1.4 * pop(t, T[1] + 0.2), WHITE, "smile", (-40, 55), (40, 55), None, (60, 40, 30))
        ell(cv, 540, 430, 18, 26, (90, 90, 100), 5)
        line(cv, [(540, 456), (540, 520)], 6, INK)
        tag(cv, t, T[1] + 0.8, "Orson Welles, age 23", 860, 330, size=42, maxw=500)
        radio(cv, 880, 480, 0.9 * pop(t, T[1] + 1.4), t)
    elif k == 2:
        radio(cv, 640, 470, 1.4 * pop(t, T[2] + 0.2), t)
        ufo(cv, 380, 230, 1.2 * pop(t, T[2] + 1.0))
        martian(cv, 900, 260, 1.0 * pop(t, T[2] + 1.6))
        tag(cv, t, T[2] + 0.6, "Fake news bulletins", 640, 190, size=40, maxw=600)
    elif k == 3:
        paper(cv, 640, 400, 1.7 * pop(t, T[3] + 0.3), "PANIC!", 5)
        tag(cv, t, T[3] + 1.4, "Thousands flee their homes?", 1000, 250, size=34, fill=WARN, maxw=420)
    elif k == 4:
        for i, lab in enumerate(("Textbooks", "Documentaries", "For decades")):
            tag(cv, t, T[4] + 0.2 + i * 0.7, lab, 640, 250 + i * 130, size=50, maxw=700)
    else:
        ell(cv, 600, 380, 110 * pop(t, T[5] + 0.3), None, None, 12)
        line(cv, [(680, 460), (800, 580)], 22 * pop(t, T[5] + 0.3), INK)
        text(cv, 600, 380, "?", 130, RED, scale=pop(t, T[5] + 0.8))
        cap(cv, t, T[5] + 1.0, "A very different story", 630, size=44, col=BLUE, x=640, maxw=900)


def s19(cv, t, T):
    # 0 Hooper phoned 5000 | 1 two percent | 2 hospitals | 3 newspapers inflated | 4 Cantril | 5 hoax about a hoax
    hd(cv, t, T, "What Really Happened")
    k = sk(t, T)
    if k == 0:
        phone(cv, 340, 430, 2.4 * pop(t, T[0] + 0.3))
        tag(cv, t, T[0] + 0.8, "Hooper called 5,000 homes", 860, 330, size=44, maxw=560)
        cap(cv, t, T[0] + 1.6, "What are you listening to?", 450, size=40, col=BLUE, x=860, maxw=560)
    elif k == 1:
        w = 880 * rg(t, T[1] + 0.2, T[1] + 1.2)
        rrect(cv, 200, 330, 200 + w, 440, 8, (190, 195, 205), 5)
        if w > 20:
            rrect(cv, 200, 330, 200 + max(18.0, w * 0.02), 440, 4, RED, 4)
        cap(cv, t, T[1] + 0.6, "2% tuned in to Welles", 250, size=44, col=RED)
        cap(cv, t, T[1] + 1.4, "98% listened to something else", 520, size=44, col=BLUE)
    elif k == 2:
        museum(cv, 400, 440, 1.2 * pop(t, T[2] + 0.2))
        line(cv, [(400, 330), (400, 390)], 14, RED)
        line(cv, [(370, 360), (430, 360)], 14, RED)
        tag(cv, t, T[2] + 0.8, "Six New York hospitals", 900, 330, size=38, maxw=420)
        tag(cv, t, T[2] + 1.8, "No cases linked", 900, 440, size=44, fill=OKAY, maxw=420)
    elif k == 3:
        paper(cv, 280, 420, 1.2 * pop(t, T[3] + 0.2), "NEWS", 4)
        arrow(cv, 460, 420, 780, 420, 8, RED, rg(t, T[3] + 0.8, T[3] + 1.6))
        radio(cv, 980, 440, 1.0 * pop(t, T[3] + 1.4), t)
        tag(cv, t, T[3] + 1.0, "$ Fighting radio for ads", 640, 220, size=38, maxw=700)
        tag(cv, t, T[3] + 2.2, "Panic inflated", 640, 620, size=46, fill=WARN, maxw=600)
    elif k == 4:
        s = pop(t, T[4] + 0.3)
        rrect(cv, 640 - 150 * s, 400 - 170 * s, 640 + 150 * s, 400 + 170 * s, 12, (70, 90, 160), 6)
        if s > 0.95:
            text(cv, 640, 360, "CANTRIL", 52, WHITE)
            text(cv, 640, 430, "1940", 52, YEL)
        tag(cv, t, T[4] + 1.2, "Critics: weak numbers", 1000, 300, size=34, fill=WARN, maxw=380)
    else:
        for i, x in enumerate((300, 980)):
            paper(cv, x, 440, 1.2 * pop(t, T[5] + 0.3 + i * 0.3), "NEWS", 4)
        cap(cv, t, T[5] + 0.6, "A hoax about", 340, size=64, col=RED)
        cap(cv, t, T[5] + 1.0, "a hoax", 430, size=64, col=RED)


def s20(cv, t, T):
    # 0 why smart people fall | 1 official sources | 2 what we hope | 3 admitting wrong | 4 hoax faster than correction
    hd(cv, t, T, "Why We Fall For It")
    k = sk(t, T)
    if k == 0:
        person(cv, 640, 650, 1.5 * pop(t, T[0] + 0.3), WHITE, "shock", (-40, 55), (40, 55), None, (110, 80, 60))
        text(cv, 900, 330, "?", 160, RED, scale=pop(t, T[0] + 0.8))
        text(cv, 380, 330, "?", 160, RED, scale=pop(t, T[0] + 1.2))
    elif k == 1:
        paper(cv, 640, 420, 1.6 * pop(t, T[1] + 0.3), "OFFICIAL", 4)
        text(cv, 820, 520, "OFFICIAL", 56, RED, rot=-14, scale=pop(t, T[1] + 1.0))
        tag(cv, t, T[1] + 1.6, "Looks official = trusted", 640, 640, size=40, maxw=700)
    elif k == 2:
        heart(cv, 640, 380, 3.2 * pop(t, T[2] + 0.2))
        moon(cv, 260, 380, 60 * pop(t, T[2] + 1.0))
        ghost(cv, 1020, 390, 1.0 * pop(t, T[2] + 1.6), t)
        tag(cv, t, T[2] + 0.6, "What we hope is true", 640, 620, size=44, maxw=800)
    elif k == 3:
        person(cv, 640, 650, 1.5 * pop(t, T[3] + 0.3), WHITE, "sad", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[3] + 0.8, "Admitting a mistake is hard", 640, 230, size=46, fill=WARN, maxw=900)
    else:
        arrow(cv, 160, 330, 1120, 330, 12, RED, rg(t, T[4] + 0.3, T[4] + 1.2))
        arrow(cv, 160, 480, 520, 480, 12, (140, 140, 150), rg(t, T[4] + 1.0, T[4] + 2.6))
        cap(cv, t, T[4] + 0.5, "The fun hoax", 270, size=38, col=RED, x=400, maxw=400)
        cap(cv, t, T[4] + 1.4, "The boring correction", 550, size=38, x=360, maxw=400)


def s21(cv, t, T):
    # 0 shield | 1 who says so | 2 second source | 3 who gains | 4 wait ten seconds
    hd(cv, t, T, "Your Hoax Shield")
    shield(cv, 250, 400, 1.5 * pop(t, T[0] + 0.3))
    qs = (("1. Who says it, and how do they know?", 230),
          ("2. Is there a second, independent source?", 340),
          ("3. Who gains if I believe it?", 450),
          ("4. Wait ten seconds before sharing", 560))
    for i, (s, y) in enumerate(qs):
        tag(cv, t, T[i + 1] + 0.3, s, 790, y, size=34, fill=(235, 242, 255), maxw=720)
    if t >= T[4] + 0.6:
        clock(cv, 250, 400, 60 * pop(t, T[4] + 0.6), 0, 60 + 40 * rg(t, T[4] + 0.6, T[4] + 2.0), 1.0)


def s22(cv, t, T):
    # 0 five hoaxes | 1 curiosity hope wonder | 2 healthy doubt | 3 which surprised | 4 comments | 5 sign-off
    k = sk(t, T)
    if k == 0:
        hoax_row(cv, t, T[0] + 0.2, 380, 1.2)
        cap(cv, t, T[0] + 0.1, "Five American tall tales", 120, size=56, col=BLUE)
    elif k == 1:
        person(cv, 640, 650, 1.4 * pop(t, T[1] + 0.2), WHITE, "smile", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[1] + 0.6, "curiosity", 250, 300, size=48, fill=OKAY, maxw=360)
        tag(cv, t, T[1] + 1.4, "hope", 640, 180, size=48, fill=PINK, maxw=360)
        tag(cv, t, T[1] + 2.2, "wonder", 1030, 300, size=48, fill=SKY, maxw=360)
    elif k == 2:
        bulb(cv, 640, 320, 3.0 * pop(t, T[2] + 0.2))
        cap(cv, t, T[2] + 0.8, "Curiosity + a little healthy doubt", 590, size=52, col=BLUE, maxw=1100)
    elif k == 3:
        cap(cv, t, T[3] + 0.1, "Which hoax surprised you most?", 150, size=62, col=BLUE, maxw=1100)
        hoax_row(cv, t, T[3] + 0.5, 400, 1.0)
    elif k == 4:
        if card(cv, t, T[4] + 0.2, 240, 220, 1040, 480, WHITE):
            text(cv, 640, 330, "Tell Zuppy in the comments", 56, BLUE)
            for i in range(3):
                ell(cv, 560 + i * 80, 420, 12, None, INK, 0)
    else:
        wipe(cv)
        person(cv, 640, 650, 1.5 * pop(t, T[5] + 0.2), WHITE, "laugh", (-40, 55), (40, 55), None, (110, 80, 60))
        cap(cv, t, T[5] + 0.3, "Stay curious with Zuppy", 200, size=72, col=RED)


_FN = {
    "s01": s01, "s02": s02, "s03": s03, "s04": s04, "s05": s05, "s06": s06, "s07": s07,
    "s08": s08, "s09": s09, "s10": s10, "s11": s11, "s12": s12, "s13": s13, "s14": s14,
    "s15": s15, "s16": s16, "s17": s17, "s18": s18, "s19": s19, "s20": s20, "s21": s21,
    "s22": s22,
}
_PASTELS = [(255, 248, 225), (232, 240, 255), (255, 236, 230), (236, 250, 236), (245, 236, 255), (255, 244, 214)]
_BG = {}
for _i in range(1, 23):
    _BG["s%02d" % _i] = _PASTELS[_i % len(_PASTELS)]
_BG["s01"] = NAVY
_BG["s05"] = NAVY
ORDER = ["s%02d" % i for i in range(1, 23)]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]