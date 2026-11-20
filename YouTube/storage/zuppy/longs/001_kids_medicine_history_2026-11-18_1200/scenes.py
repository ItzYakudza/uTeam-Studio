"""
Episode: 001_kids_medicine_history_2026-11-18_1200
Channel: zuppy
"""

import math
from core.primitives import *

MODE = "long"
CHANNEL_NAME = "zuppy"

TEXTS = [
    # 01 hook (5)
    "Imagine a world where almost half of all children never reached their fifth birthday. "
    "That was not a distant nightmare, it was ordinary life around the year eighteen hundred. "
    "Parents loved their babies just as much as parents do today, but they had no antibiotics, no vaccines, and no idea that tiny invisible germs caused most of the sickness. "
    "So they tried everything they could think of, and some of those cures were far more dangerous than the illness itself. "
    "This is the story of how children were treated in the past.",
    # 02 numbers (5)
    "Let's start with the numbers, because they explain everything that follows. "
    "Researchers estimate that around the year eighteen hundred, about forty-three out of every one hundred children in the world died before their fifth birthday. "
    "A typical parent of that time lost two or three children, and it was seen as a normal part of life. "
    "Today that number is below four out of one hundred. "
    "Everything you are about to hear happened inside that enormous gap, and it explains why parents grasped at every remedy they could find.",
    # 03 swaddling (5)
    "The first danger began in the very first hour of life. "
    "For thousands of years, newborns were swaddled, which means tightly wrapped in strips of cloth from the shoulders down to the toes. "
    "Famous doctors of ancient Rome, like Galen, recommended it, because they believed it would make a baby's arms and legs grow straight. "
    "A child could stay bound like this for months, with only short breaks for cleaning. "
    "It kept babies warm and quiet, but a tiny body that cannot move, and is rarely checked, can overheat and be easily neglected.",
    # 04 pushback (5)
    "Then, slowly, a few thinkers began to push back. "
    "In sixteen ninety-three, the philosopher John Locke wrote that children's clothes should never be too tight or too hot. "
    "In seventeen forty-eight, a doctor named William Cadogan went further and argued that swaddling should be abandoned completely. "
    "The philosopher Jean-Jacques Rousseau joined the campaign, and by the end of the century, swaddling was fading in Britain and much of Europe. "
    "Funny enough, many modern parents swaddle again, but with loose wraps, free hips, and safe sleep rules that the old versions never had.",
    # 05 teething panic (5)
    "And then came teething, which may be the strangest medical panic in history. "
    "So many babies died around the age when their first teeth appeared that doctors decided teething itself must be the killer. "
    "London's official death lists, called the Bills of Mortality, even named teeth as a cause of death. "
    "In eighteen forty-two, an English report found that nearly five percent of London babies who died before their first birthday were blamed on teething. "
    "Today we know teething does not cause deadly illness, so those babies were dying of other causes that nobody could see yet.",
    # 06 lancing (5)
    "The treatments were almost worse than the theory, and some of them are painful even to describe. "
    "Surgeons recommended lancing, which means cutting the gums with a small blade so the tooth could break through. "
    "Some doctors even placed leeches on a baby's gums, hoping to draw out the trouble. "
    "Other families hung charms around the baby's neck, rubbed the gums with animal substances, or offered a hard root to chew. "
    "Every one of these painful methods was aimed at a problem that did not exist.",
    # 07 opium (5)
    "Now for the part that surprises people the most. "
    "When babies cried, many parents reached for a bottle of soothing medicine, and for more than a century, those bottles often contained opium. "
    "Godfrey's Cordial, a mix of opium, treacle, and sassafras, was so popular that in one English town in the middle of the eighteen hundreds, ten gallons were sold every week, enough for about three thousand infants. "
    "Doctors nicknamed opium the poor child's nurse, because it kept hungry babies quiet while their parents worked. "
    "The tragedy is that a sleepy baby is not a healthy baby, and the drug left many infants too drowsy to eat.",
    # 08 winslow (5)
    "In eighteen forty-nine, an American company launched Missus Winslow's Soothing Syrup. "
    "The ads showed a caring nurse and a happy family, and promised calm and comfort for teething babies. "
    "What the ads did not make clear was that the syrup contained morphine and alcohol, which could be dangerous for a small child. "
    "Doctors raised alarms, and in nineteen eleven the American Medical Association publicly denounced it. "
    "Morphine was removed in the early nineteen hundreds, yet the syrup was still being sold as late as nineteen thirty.",
    # 09 mercury (5)
    "Opium was not the only risky ingredient. "
    "For years, many teething powders sold in drugstores contained calomel, a form of mercury. "
    "Some children developed a painful condition called pink disease, with red, swollen, peeling hands and feet. "
    "Doctors eventually linked it to mercury poisoning, and in nineteen fifty-four calomel was removed from most teething powders. "
    "Stop and think about that date, because some of today's grandparents were babies in a world that still sold those powders.",
    # 10 why (5)
    "To be fair, the people of the past were not careless. "
    "They were guessing, using the best theories they had. "
    "For centuries, doctors believed that disease came from bad air, called miasma, or from an imbalance of fluids inside the body. "
    "If you truly believe that, a cut in the gum sounds logical, and so does a syrup that calms the whole body. "
    "The real enemy, living germs too small to see, was not proven to cause disease until the second half of the eighteen hundreds, thanks to scientists like Louis Pasteur and Robert Koch.",
    # 11 rickets (6)
    "Some killers were not germs at all. "
    "In the crowded, smoky cities of the Industrial Revolution, many children grew up with soft, bowed bones, a disease called rickets. "
    "Doctors argued about the cause for generations, blaming dirty air, poor diet, and a lack of exercise. "
    "In nineteen nineteen, the British scientist Edward Mellanby fed puppies a diet that gave them rickets, then cured them with cod liver oil. "
    "Later experiments showed that sunlight works too, because skin makes vitamin D when sunshine touches it. "
    "A spoonful of fishy oil and a little sunshine helped nearly wipe out a disease that had crippled children for centuries.",
    # 12 variolation (5)
    "Smallpox was the great terror of childhood. "
    "It spread through the air, left survivors scarred, and in the eighteenth century killed enormous numbers of children. "
    "The first real defense did not begin in Europe at all. "
    "In parts of China, India, Africa, and the Ottoman Empire, people practiced variolation, which means putting a tiny amount of smallpox material into a scratch to cause a mild case that protected against the deadly one. "
    "In Boston in seventeen twenty-one, the minister Cotton Mather learned about the technique from an enslaved man named Onesimus, and during an epidemic, those who were inoculated suffered far fewer deaths.",
    # 13 lady mary (5)
    "In Britain, the story starts with a determined woman. "
    "Lady Mary Wortley Montagu, the wife of a British ambassador, watched families in Constantinople use variolation and decided it was worth trying. "
    "In seventeen twenty-one, as smallpox threatened London, she had her young daughter inoculated by a surgeon named Charles Maitland. "
    "Caroline, the Princess of Wales, was curious, and after the first tests went well, she had her own children inoculated too. "
    "It was risky and controversial, yet mothers kept choosing it, because the alternative was waiting for smallpox to arrive.",
    # 14 jenner (6)
    "In seventeen ninety-six, an English doctor named Edward Jenner tried a safer idea. "
    "People had noticed that milkmaids who caught cowpox seemed protected from smallpox. "
    "Jenner took material from a milkmaid's cowpox sore and used it to vaccinate an eight-year-old boy named James Phipps. "
    "Weeks later, he tested the boy with smallpox material, and the boy stayed healthy. "
    "Looking back, that experiment raises serious ethical questions, since the boy was the son of Jenner's gardener and could not truly choose. "
    "But the method spread, and in nineteen eighty the World Health Organization declared smallpox eradicated.",
    # 15 milk (5)
    "Even something as simple as milk could be deadly. "
    "In the eighteen fifties, New York City was growing so fast that fresh milk was hard to find. "
    "Some dairies fed cows the leftover mash from whiskey distilleries, then sold the pale liquid as pure country milk. "
    "In eighteen fifty-eight, a newspaper investigation blamed it for thousands of infant deaths, and one estimate reached eight thousand children in a single year. "
    "Public anger pushed lawmakers to pass milk rules in eighteen sixty-two, and later, pasteurization and cleaner farms made milk much safer.",
    # 16 diphtheria (5)
    "Another killer was diphtheria, a throat infection that could close a child's airway. "
    "Parents called it the strangling angel. "
    "In eighteen ninety, Emil von Behring and Shibasaburo Kitasato showed that an antitoxin made from animal blood could fight the poison the germ produces. "
    "In an eighteen ninety-four report, about one hundred sixty-eight of two hundred twenty sick children treated with the serum recovered, far better odds than before. "
    "Behring won the very first Nobel Prize in Medicine in nineteen oh one, and later vaccines made diphtheria rare in many countries.",
    # 17 law (5)
    "As people learned the truth, laws slowly began to catch up. "
    "In the United States, the Pure Food and Drug Act of nineteen oh six required medicine labels to disclose dangerous ingredients like opium and morphine. "
    "For the first time, a parent could read what was inside a bottle before giving it to a child. "
    "Journalists and doctors kept pushing, and brands that once bragged about being soothing had to change their recipes. "
    "Trust in medicine had to be rebuilt on honesty, not on advertising.",
    # 18 teething today (5)
    "Here is a twist, though, because some old teething habits never fully disappeared. "
    "In twenty eighteen, the United States Food and Drug Administration warned parents to stop using teething necklaces and bracelets, after a toddler was strangled by an amber necklace during a nap. "
    "The agency and the American Academy of Pediatrics also advise against numbing gels that contain benzocaine, which can reduce the oxygen carried by the blood. "
    "Instead, doctors suggest a cool, firm teething ring, a clean wet washcloth, or a gentle rub on the gums with a clean finger. "
    "History keeps reminding us that popular does not always mean safe.",
    # 19 what worked (6)
    "So what really saved children? "
    "It was not one miracle, it was many small, unglamorous improvements stacked together. "
    "Clean water and safer milk reduced deadly stomach infections, which had been one of the biggest killers of babies. "
    "Vaccines prevented diseases that once swept through whole towns and crowded children's wards. "
    "Better food and vitamins protected growing bones, teeth, and immune systems. "
    "Antibiotics, children's hospitals, and honest medicine labels did the rest, and together they changed what childhood looks like.",
    # 20 numbers (4)
    "The result is one of the greatest success stories in human history. "
    "Around eighteen hundred, about forty-three in every one hundred children died before age five, and today that number is below four in one hundred. "
    "In many wealthy countries, it is closer to one in two hundred, which means most families never face that fear. "
    "Every step on that road stands for families who kept a child, and there is still work to do in parts of the world where children die from causes we already know how to prevent.",
    # 21 outro (5)
    "So the next time someone says that life was simpler in the old days, remember the syrups, the cut gums, and the tight wrappings. "
    "People in the past loved their children fiercely, and they did the best they could with the knowledge they had. "
    "Behind every strange old cure was a parent who simply wanted their child to be okay. "
    "Knowledge is what changed the story, one careful question at a time. "
    "Thanks for watching, and stay curious with Zuppy.",
]

CHAPTERS = [
    "Hook",
    "The numbers",
    "Swaddling",
    "Pushing back on swaddling",
    "The teething panic",
    "Lancing and charms",
    "Opium for babies",
    "Mrs Winslow's Soothing Syrup",
    "Mercury teething powders",
    "Why they believed it",
    "Rickets and cod liver oil",
    "Smallpox and variolation",
    "Lady Mary Montagu",
    "Jenner and the vaccine",
    "The swill milk scandal",
    "Diphtheria",
    "Laws and labels",
    "Teething today",
    "What really worked",
    "The big picture",
    "Final thoughts",
]

TITLE = "How Children Were Treated Centuries Ago (And Why So Many Didn't Survive)"
DESC = """For most of history, close to half of all children did not reach their fifth birthday. This animated story shows how parents and doctors tried to treat children before germ theory, from swaddling and the teething panic to opium syrups, mercury powders, rickets, smallpox, dirty milk, and the discoveries that finally changed everything.

CHAPTERS
{chapters}

SOURCES
- Our World in Data (Hannah Ritchie), How child mortality has declined in the last two centuries: https://ourworldindata.org/child-mortality-global-overview
- Our World in Data, Child mortality rate (Gapminder, UN IGME): https://ourworldindata.org/grapher/child-mortality
- Science Museum Group blog, The addictive history of medicine: opium, the poor child's nurse: https://blog.sciencemuseum.org.uk/the-addictive-history-of-medicine-opium-the-poor-childs-nurse
- Wellcome Collection, The poor child's nurse: https://wellcomecollection.org/stories/the-poor-child-s-nurse
- Brecher, Consumers Union Report on Licit and Illicit Drugs (1972), Part I: https://ukcia.org/research/cunion/cu1.htm
- Wood Library-Museum, Mrs. Winslow's Soothing Syrup: https://www.woodlibrarymuseum.org/?p=4211
- Pharmacy Times, Pharmacy's Past: the soothing syrup known for causing death in thousands of babies: https://www.pharmacytimes.com/view/pharmacys-past-the-soothing-syrup-known-for-causing-death-in-thousands-of-babies-
- British Dental Journal (2001), Teething: historical teachings and old wives' tales: https://www.nature.com/bdj/journal/v191/n1/full/4801078a.html
- Hektoen International, Bells, whistles and rattles (Bills of Mortality): https://hekint.org/2025/06/23/bells-whistles-and-rattles-something-to-get-your-teeth-into/
- Wikipedia, Teething (calomel and pink disease): https://en.wikipedia.org/wiki/Teething
- P. M. Dunn, Swaddling the newborn infant: then and now, Infant Journal: https://www.infantjournal.co.uk/journal_article.html?id=7101
- Young V&A, Swaddling: babies in a tight bind: https://www.vam.ac.uk/blog/museum-of-childhood/swaddling-babies-in-a-tight-bind
- Rajakumar (2003), Vitamin D, cod-liver oil, sunlight, and rickets, Pediatrics: https://pubmed.ncbi.nlm.nih.gov/12897318/
- A Brief History of Nutritional Rickets, Frontiers in Endocrinology (2019): https://pmc.ncbi.nlm.nih.gov/articles/PMC6867964
- Country Life, Who administered the first vaccination?: https://countrylife.co.uk/comment-opinion/curious-questions-did-edward-jenner-really-administer-the-first-vaccine-222999
- History News Network, Jenner, Phipps and variolation: https://www.historynewsnetwork.org/article/162034
- Museum of Health Care, From variolation to cowpox vaccination: https://www.museumofhealthcare.ca/blog/from-variolation-to-cowpox-vaccination-the-first-steps-towards-eradicating-smallpox
- World Health Organization, Smallpox: https://www.who.int/health-Topics/smallpox
- Big Think, The swill milk scandal: https://bigthink.com/the-past/swill-milk-scandal/
- Behring and diphtheria serum therapy, PMC review: https://pmc.ncbi.nlm.nih.gov/articles/PMC5347343
- U.S. FDA, The 1906 Food and Drugs Act and its enforcement: https://www.fda.gov/about-fda/changes-science-law-and-regulatory-authorities/part-i-1906-food-and-drugs-act-and-its-enforcement
- HealthyChildren.org (AAP), Teething necklaces and beads: https://www.healthychildren.org/english/ages-stages/baby/teething-tooth-care/pages/amber-teething-necklaces.aspx

This video is educational history. It is not medical advice. Always ask a pediatrician about your child's health.
"""
TAGS = "history of medicine, how children were treated in the past, history of childhood, teething history, swaddling history, opium for babies, soothing syrup, smallpox vaccine history, Edward Jenner, rickets, cod liver oil, swill milk, diphtheria, child mortality, animated history, educational animation, zuppy"

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
CX = 640


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


def baby(cv, x, y, s=1.0, mood="smile", wrap=None, bands=0.0):
    if s < 0.05:
        return
    body = wrap if wrap else (255, 214, 200)
    ell(cv, x, y - 62 * s, 46 * s, 70 * s, body, 5)
    n = int(bands * 4)
    for k in range(n):
        yy = y - (118 - k * 28) * s
        line(cv, [(x - 40 * s, yy), (x, yy + 8 * s), (x + 40 * s, yy)], 4, (150, 120, 110))
    face(cv, x, y - 150 * s, 34 * s, s, mood)


def bottle(cv, x, y, s=1.0, col=SKY, label=None, size=18):
    if s < 0.05:
        return
    rrect(cv, x - 30 * s, y - 60 * s, x + 30 * s, y + 70 * s, 16 * s, col, 5)
    rrect(cv, x - 14 * s, y - 96 * s, x + 14 * s, y - 56 * s, 6 * s, col, 5)
    rrect(cv, x - 18 * s, y - 116 * s, x + 18 * s, y - 94 * s, 6 * s, (190, 150, 100), 5)
    if label:
        rrect(cv, x - 26 * s, y - 16 * s, x + 26 * s, y + 36 * s, 6 * s, WHITE, 3)
        text(cv, x, y + 10 * s, label, size * s)


def tooth(cv, x, y, s=1.0):
    if s < 0.05:
        return
    pts = [(-55, -70), (-28, -85), (0, -70), (28, -85), (55, -70), (62, -10), (45, 40), (36, 90),
           (16, 90), (6, 30), (-6, 30), (-16, 90), (-36, 90), (-45, 40), (-62, -10)]
    poly(cv, [(x + a * s, y + b * s) for a, b in pts], WHITE, 6)


def waves(cv, x, y, col=RED, n=3, amp=8, ph0=0.0):
    for i in range(n):
        xx = x + i * 40
        pts = [(xx + amp * math.sin(j * 0.9 + ph0 + i), y - j * 14) for j in range(7)]
        line(cv, pts, 5, col)


def cross(cv, x, y, s=1.0, col=RED):
    line(cv, [(x - 50 * s, y - 50 * s), (x + 50 * s, y + 50 * s)], 10, col)
    line(cv, [(x + 50 * s, y - 50 * s), (x - 50 * s, y + 50 * s)], 10, col)


def germ(cv, x, y, s=1.0):
    if s < 0.05:
        return
    for k in range(8):
        a = k * math.pi / 4
        line(cv, [(x + 24 * s * math.cos(a), y + 24 * s * math.sin(a)),
                  (x + 38 * s * math.cos(a), y + 38 * s * math.sin(a))], 4, GRN)
    ell(cv, x, y, 24 * s, 24 * s, (170, 220, 140), 4)
    ell(cv, x - 8 * s, y - 4 * s, 3 * s, None, INK, 0)
    ell(cv, x + 8 * s, y - 4 * s, 3 * s, None, INK, 0)


def lancet(cv, x, y, s=1.0):
    poly(cv, [(x - 80 * s, y - 14 * s), (x + 20 * s, y - 14 * s), (x + 90 * s, y),
              (x + 20 * s, y + 14 * s), (x - 80 * s, y + 14 * s)], (225, 230, 240), 5)
    rrect(cv, x - 150 * s, y - 20 * s, x - 80 * s, y + 20 * s, 8 * s, (190, 150, 100), 5)


def leech(cv, x, y, s=1.0, t=0.0):
    pts = [(x - 90 * s + i * 30 * s, y + 14 * s * math.sin(i * 0.9 + t * 3)) for i in range(7)]
    line(cv, pts, 16 * s, (70, 50, 60))


def charm(cv, x, y, s=1.0):
    ell(cv, x, y - 40 * s, 75 * s, 75 * s, None, 5, INK, 0, 180)
    poly(cv, [(x, y + 5 * s), (x + 22 * s, y + 38 * s), (x, y + 71 * s), (x - 22 * s, y + 38 * s)], YEL, 5)


def bone(cv, x0, y0, x1, y1, bow, k=1.0):
    if k < 0.05:
        return
    pts = [(x0 + (x1 - x0) * i / 6 + bow * math.sin(math.pi * i / 6), y0 + (y1 - y0) * i / 6) for i in range(7)]
    line(cv, pts, 20, INK)
    line(cv, pts, 11, WHITE)
    for px, py in (pts[0], pts[-1]):
        ell(cv, px, py, 16, 16, WHITE, 5)


def dog(cv, x, y, s=1.0):
    if s < 0.05:
        return
    fur = (235, 210, 170)
    ell(cv, x, y, 70 * s, 38 * s, fur, 5)
    for dx in (-45, 40):
        line(cv, [(x + dx * s, y + 28 * s), (x + dx * s, y + 80 * s)], 8, INK)
    ell(cv, x + 78 * s, y - 28 * s, 34 * s, 30 * s, fur, 5)
    poly(cv, [(x + 62 * s, y - 52 * s), (x + 50 * s, y - 10 * s), (x + 76 * s, y - 40 * s)], (170, 130, 90), 4)
    ell(cv, x + 90 * s, y - 34 * s, 4 * s, None, INK, 0)
    ell(cv, x + 108 * s, y - 22 * s, 6 * s, None, INK, 0)
    line(cv, [(x - 68 * s, y - 8 * s), (x - 100 * s, y - 40 * s)], 6, INK)


def cow(cv, x, y, s=1.0):
    if s < 0.05:
        return
    rrect(cv, x - 100 * s, y - 50 * s, x + 100 * s, y + 40 * s, 30 * s, WHITE, 5)
    for dx in (-70, -30, 40, 80):
        line(cv, [(x + dx * s, y + 38 * s), (x + dx * s, y + 95 * s)], 6, INK)
    ell(cv, x - 120 * s, y - 30 * s, 40 * s, 34 * s, WHITE, 5)
    ell(cv, x - 132 * s, y - 38 * s, 4 * s, None, INK, 0)
    ell(cv, x - 30 * s, y - 10 * s, 26 * s, 18 * s, (60, 60, 70), 0)
    ell(cv, x + 50 * s, y - 20 * s, 22 * s, 16 * s, (60, 60, 70), 0)


def syringe(cv, x, y, s=1.0):
    if s < 0.05:
        return
    rrect(cv, x - 90 * s, y - 22 * s, x + 60 * s, y + 22 * s, 10 * s, WHITE, 5)
    line(cv, [(x + 60 * s, y), (x + 130 * s, y)], 4, INK)
    line(cv, [(x - 90 * s, y), (x - 130 * s, y)], 8, INK)
    line(cv, [(x - 130 * s, y - 26 * s), (x - 130 * s, y + 26 * s)], 8, INK)
    rrect(cv, x - 60 * s, y - 14 * s, x + 10 * s, y + 14 * s, 6 * s, SKY, 0)


# ============================================================
# Scenes
# ============================================================

def s01(cv, t, T):
    # sentences: 0 half never reached 5 | 1 year 1800 | 2 parents loved | 3 tried everything | 4 story
    a0 = T[0] + 0.2
    n_red = int(43 * rg(t, T[0] + 1.2, T[1] - 0.3))
    for i in range(100):
        r, c = divmod(i, 10)
        k = pop(t, a0 + c * 0.03 + r * 0.02, 0.3)
        if k <= 0.03:
            continue
        ell(cv, 120 + c * 42, 190 + r * 42, 14 * k, 14 * k, RED if i < n_red else WHITE, 4)

    if t < T[4]:
        cap(cv, t, T[1] + 0.2, "Around 1800", 230, size=50, x=880, maxw=520)
        cap(cv, t, T[1] + 0.6, "43 out of 100", 340, size=72, col=RED, x=880, maxw=520)
    if T[2] <= t < T[3]:
        cap(cv, t, T[2] + 0.2, "No antibiotics", 450, size=38, x=880, maxw=520)
        cap(cv, t, T[2] + 0.9, "No vaccines", 500, size=38, x=880, maxw=520)
        cap(cv, t, T[2] + 1.5, "No idea about germs", 550, size=38, x=880, maxw=520)
    if T[3] <= t < T[4]:
        bottle(cv, 880, 470, 1.5 * pop(t, T[3] + 0.2), SKY, "CURE", 18)
        cap(cv, t, T[3] + 1.0, "Cure... or danger?", 625, size=40, col=RED, x=880, maxw=520)
    if t >= T[4]:
        wipe(cv)
        cap(cv, t, T[4] + 0.1, "How were children", 240, size=80, col=BLUE)
        cap(cv, t, T[4] + 0.5, "treated in the past?", 340, size=80, col=BLUE)
        baby(cv, CX, 650, 1.3 * pop(t, T[4] + 0.9), "smile", None, 0)


def s02(cv, t, T):
    # 0 numbers | 1 43 of 100 | 2 parents lost | 3 below four | 4 gap
    hd(cv, t, T, "The Numbers")
    base = 585
    if t >= T[1] + 0.3:
        h1 = 330 * rg(t, T[1] + 0.3, T[1] + 2.8)
        rrect(cv, 150, base - h1, 310, base, 10, RED, 5)
        text(cv, 230, base - h1 - 30, "43 in 100", 34, RED)
        cap(cv, t, T[1] + 0.5, "Around 1800", base + 40, size=30, x=230, maxw=200)
    k = pop(t, T[2] + 0.2)
    if k > 0.05:
        person(cv, 930, 600, 0.9 * k, WHITE, "sad", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[2] + 0.6, "Lost two or three children", 930, 300, size=34, maxw=480)
    if t >= T[3] + 0.3:
        h2 = 31 * rg(t, T[3] + 0.3, T[3] + 1.5)
        rrect(cv, 400, base - h2, 560, base, 8, GRN, 5)
        text(cv, 480, base - h2 - 34, "below 4 in 100", 30, GRN)
        cap(cv, t, T[3] + 0.5, "Today", base + 40, size=30, x=480, maxw=200)
    if t >= T[4] + 0.2:
        cap(cv, t, T[4] + 0.2, "THE GAP", 215, size=70, col=BLUE, x=930, maxw=480)
        arrow(cv, 320, 270, 390, 540, 7, BLUE, rg(t, T[4] + 0.3, T[4] + 1.3))


def s03(cv, t, T):
    # 0 first danger | 1 wrapped | 2 Galen straight | 3 months | 4 warm, overheat
    hd(cv, t, T, "Swaddling")
    wr = ph(t, T[1] + 0.2, T[1] + 2.8)
    mood = "tired" if t >= T[4] else "smile"
    baby(cv, 400, 610, 1.6 * pop(t, T[0] + 0.3), mood, mix((255, 214, 200), (236, 228, 205), wr), wr)
    tag(cv, t, T[2] + 0.2, "Galen, ancient Rome", 900, 240, size=36, maxw=480)
    if T[2] + 0.8 <= t < T[3]:
        rrect(cv, 780, 340, 1020, 380, 8, YEL, 4)
        for i in range(9):
            line(cv, [(790 + i * 28, 340), (790 + i * 28, 358 if i % 2 else 368)], 3)
        cap(cv, t, T[2] + 0.8, "Arms and legs grow straight", 440, size=34, x=900, maxw=420)
    if T[3] <= t < T[4]:
        k = pop(t, T[3] + 0.2)
        if k > 0.05:
            clock(cv, 900, 400, 95, t * 6, t * 72, k)
        cap(cv, t, T[3] + 0.8, "For months!", 540, size=60, col=RED, x=900, maxw=420)
    if t >= T[4] + 0.2:
        waves(cv, 350, 310, RED, 3, 8, t * 4)
        tag(cv, t, T[4] + 0.3, "Easy to overheat", 900, 400, size=40, fill=WARN, maxw=480)
        tag(cv, t, T[4] + 1.3, "Rarely checked", 900, 490, size=40, fill=WARN, maxw=480)


def s04(cv, t, T):
    # 0 push back | 1 Locke | 2 Cadogan | 3 Rousseau | 4 modern
    hd(cv, t, T, "Pushing Back")
    xs = (300, 640, 980)
    names = ("Locke, 1693", "Cadogan, 1748", "Rousseau")
    notes = ("not too tight or hot", "abandon swaddling", "let babies move")
    for i in range(3):
        a = T[i + 1] + 0.2
        k = pop(t, a)
        if k > 0.05:
            person(cv, xs[i], 560, 0.72 * k, WHITE, "smile", (-40, 55), (40, -30), None, (110, 80, 60))
            tag(cv, t, a + 0.4, names[i], xs[i], 315, size=34, maxw=300)
            cap(cv, t, a + 0.9, notes[i], 612, size=30, x=xs[i], maxw=300)
    cap(cv, t, T[4] + 0.2, "Today: loose wrap, free hips, safe sleep", 205, size=40, col=GRN, maxw=1000)


def s05(cv, t, T):
    # 0 panic | 1 blamed | 2 Bills of Mortality | 3 1842 stat | 4 not the killer
    hd(cv, t, T, "Teething Panic")
    if t < T[3] + 0.2:
        tooth(cv, 330, 400, 2.0 * pop(t, T[0] + 0.3))
        cap(cv, t, T[1] + 0.3, "Blamed!", 615, size=58, col=RED, x=330, maxw=420)
    if card(cv, t, T[2] + 0.2, 640, 190, 1180, 580, PAPER):
        text(cv, 910, 235, "Bills of Mortality", 36)
        for j, w in enumerate(("Consumption", "Smallpox", "Teeth", "Fever", "Rickets")):
            text(cv, 910, 300 + j * 52, w, 34, RED if w == "Teeth" else INK)
        a1 = -90 + 360 * rg(t, T[2] + 1.4, T[2] + 2.2)
        if a1 > -85:
            ell(cv, 910, 404, 100, 28, None, 5, RED, -90, a1)
    if t >= T[3] + 0.2:
        cap(cv, t, T[3] + 0.2, "4.8%", 330, size=120, col=RED, x=330, maxw=420)
        cap(cv, t, T[3] + 0.8, "of London babies who died", 440, size=32, x=330, maxw=420)
        cap(cv, t, T[3] + 0.8, "before age one, in 1842,", 482, size=32, x=330, maxw=420)
        cap(cv, t, T[3] + 0.8, "were blamed on teething", 524, size=32, x=330, maxw=420)
    cap(cv, t, T[4] + 0.2, "Teething was not the killer", 640, size=44, col=GRN, maxw=1000)


def s06(cv, t, T):
    # 0 worse than theory | 1 lancing | 2 leeches | 3 charms | 4 problem did not exist
    hd(cv, t, T, "Painful Cures")
    cols = ((90, 420), (475, 805), (860, 1190))
    labels = ("Lancing", "Leeches", "Charms and roots")
    for i in range(3):
        a = T[i + 1] + 0.2
        if card(cv, t, a, cols[i][0], 190, cols[i][1], 540, PAPER):
            cx = (cols[i][0] + cols[i][1]) / 2
            if i == 0:
                lancet(cv, cx + 20, 340, 1.0)
            elif i == 1:
                leech(cv, cx, 340, 1.4, t)
            else:
                charm(cv, cx, 300, 1.2)
            text(cv, cx, 495, labels[i], 34)
    cap(cv, t, T[4] + 0.2, "Aimed at a problem that did not exist", 610, size=44, col=RED, maxw=1000)


def s07(cv, t, T):
    # 0 surprise | 1 soothing bottles | 2 Godfrey's | 3 poor child's nurse | 4 too drowsy
    hd(cv, t, T, "The Poor Child's Nurse")
    bottle(cv, 250, 430, 1.7 * pop(t, T[1] + 0.2), SKY, "Syrup", 18)
    if T[2] <= t < T[3]:
        tag(cv, t, T[2] + 0.2, "Godfrey's Cordial", 860, 230, size=38, maxw=480)
        cap(cv, t, T[2] + 0.8, "10 gallons a week", 330, size=52, col=RED, x=860, maxw=480)
        cap(cv, t, T[2] + 1.4, "for about 3,000 infants", 400, size=40, x=860, maxw=480)
    if T[3] <= t < T[4]:
        k = pop(t, T[3] + 0.2)
        if k > 0.05:
            person(cv, 880, 640, 0.95 * k, WHITE, "tired", (-40, 55), (40, 55), None, (110, 80, 60))
        tag(cv, t, T[3] + 0.5, "Opium kept babies quiet", 880, 250, size=34, fill=WARN, maxw=480)
    if t >= T[4]:
        baby(cv, 880, 630, 1.3 * pop(t, T[4] + 0.2), "sleep", None, 0)
        zzz(cv, 940, 430, t, INK, 40)
        tag(cv, t, T[4] + 0.6, "Too drowsy to eat", 880, 250, size=38, fill=WARN, maxw=480)


def s08(cv, t, T):
    # 0 1849 | 1 ads | 2 ingredients | 3 1911 AMA | 4 sold until 1930
    hd(cv, t, T, "Soothing Syrup")
    tag(cv, t, T[0] + 0.6, "1849", 1090, 100, size=44, fill=(255, 235, 180))
    if card(cv, t, T[1] + 0.2, 90, 170, 600, 570, (255, 243, 215)):
        text(cv, 345, 215, "Soothing Syrup", 40)
        bottle(cv, 200, 410, 1.0, SKY, "Syrup", 16)
        person(cv, 440, 540, 0.6, WHITE, "smile", (-40, 55), (40, 55), None, (110, 80, 60))
    if card(cv, t, T[2] + 0.2, 680, 170, 1190, 400, WHITE):
        text(cv, 935, 215, "What was inside?", 36)
        if t >= T[2] + 0.9:
            text(cv, 935, 290, "Morphine", 52, RED, scale=pop(t, T[2] + 0.9))
        if t >= T[2] + 1.5:
            text(cv, 935, 350, "Alcohol", 52, RED, scale=pop(t, T[2] + 1.5))
    tag(cv, t, T[3] + 0.3, "1911: AMA denounces it", 935, 470, size=36, fill=WARN, maxw=500)
    tag(cv, t, T[4] + 0.3, "Still sold as late as 1930", 935, 560, size=36, fill=WARN, maxw=500)


def s09(cv, t, T):
    # 0 not only | 1 calomel | 2 pink disease | 3 mercury, 1954 | 4 grandparents
    hd(cv, t, T, "Teething Powders")
    if card(cv, t, T[1] + 0.2, 110, 190, 470, 430, (255, 245, 215)):
        text(cv, 290, 245, "TEETHING POWDER", 30)
        text(cv, 290, 320, "contains calomel", 34, RED)
        text(cv, 290, 375, "(a form of mercury)", 28)
    if t >= T[2] + 0.2:
        k = pop(t, T[2] + 0.2)
        baby(cv, 880, 610, 1.5 * k, "sad", PINK, 0)
        for j in range(7):
            ell(cv, 830 + (j * 23) % 70, 520 + (j * 29) % 90, 6 * k, 6 * k, RED, 0)
        tag(cv, t, T[2] + 0.5, "Pink disease", 880, 230, size=40, fill=WARN, maxw=420)
    tag(cv, t, T[3] + 0.3, "Cause: mercury poisoning", 290, 500, size=34, fill=WARN, maxw=340)
    tag(cv, t, T[3] + 1.2, "Removed in 1954", 290, 580, size=40, fill=(220, 245, 220), maxw=340)


def s10(cv, t, T):
    # 0 not careless | 1 guessing | 2 miasma/fluids | 3 logical | 4 germs, Pasteur, Koch
    hd(cv, t, T, "Not Careless")
    if T[1] <= t < T[2] + 0.2:
        k = pop(t, T[1] + 0.2)
        if k > 0.05:
            ell(cv, 640, 360, 190 * k, 120 * k, WHITE, 5)
            ell(cv, 520, 500, 22 * k, 22 * k, WHITE, 4)
            ell(cv, 470, 545, 12 * k, 12 * k, WHITE, 4)
            text(cv, 640, 360, "?", 130, BLUE, scale=k)
    if T[2] + 0.2 <= t < T[4]:
        if card(cv, t, T[2] + 0.2, 110, 190, 600, 520, (232, 240, 255)):
            text(cv, 355, 235, "Bad air (miasma)", 36)
            waves(cv, 250, 470, BLUE, 4, 10, t * 3)
        if card(cv, t, T[2] + 1.0, 680, 190, 1170, 520, (255, 240, 230)):
            text(cv, 925, 235, "Unbalanced fluids", 36)
            for j in range(4):
                ell(cv, 790 + j * 85, 400, 24, 34, (210, 90, 90) if j % 2 == 0 else (90, 130, 210), 4)
        if t < T[4]:
            tag(cv, t, T[3] + 0.3, "Wrong theory, wrong cure", 640, 600, size=44, fill=WARN, maxw=700)
    if t >= T[4] + 0.2:
        for x, nm in ((330, "Louis Pasteur"), (950, "Robert Koch")):
            k = pop(t, T[4] + 0.2)
            if k > 0.05:
                person(cv, x, 600, 0.75 * k, WHITE, "smile", (-40, 55), (40, -35), None, (110, 80, 60))
                tag(cv, t, T[4] + 0.6, nm, x, 340, size=34, maxw=330)
        germ(cv, 640, 420, 2.2 * pop(t, T[4] + 1.0))
        cap(cv, t, T[4] + 1.4, "Germs cause disease", 560, size=40, col=GRN, maxw=400)


def s11(cv, t, T):
    # 0 not germs | 1 rickets | 2 argued | 3 Mellanby | 4 sunlight | 5 nearly wiped out
    hd(cv, t, T, "Rickets")
    if t >= T[1] + 0.2:
        k = pop(t, T[1] + 0.2)
        bone(cv, 330, 240, 330, 540, -50 * k, k)
        bone(cv, 450, 240, 450, 540, 50 * k, k)
        cap(cv, t, T[1] + 0.8, "Soft, bowed bones", 590, size=38, x=390, maxw=380)
    if T[2] <= t < T[3]:
        cap(cv, t, T[2] + 0.2, "Dirty air?", 260, size=42, col=BLUE, x=900, maxw=420)
        cap(cv, t, T[2] + 0.8, "Poor diet?", 340, size=42, col=BLUE, x=900, maxw=420)
        cap(cv, t, T[2] + 1.4, "No exercise?", 420, size=42, col=BLUE, x=900, maxw=420)
    if t >= T[3] + 0.2:
        k = pop(t, T[3] + 0.2)
        dog(cv, 960, 540, 1.3 * k)
        bottle(cv, 770, 520, 1.0 * k, (255, 230, 150), "Cod oil", 16)
        tag(cv, t, T[3] + 0.6, "Mellanby, 1919", 880, 260, size=36, maxw=420)
    if t >= T[4] + 0.2:
        k = pop(t, T[4] + 0.2)
        for j in range(10):
            a = j * math.pi / 5 + t * 0.5
            line(cv, [(1080 + 62 * k * math.cos(a), 340 + 62 * k * math.sin(a)),
                      (1080 + 85 * k * math.cos(a), 340 + 85 * k * math.sin(a))], 6, YEL)
        ell(cv, 1080, 340, 48 * k, 48 * k, YEL, 5)
        cap(cv, t, T[4] + 0.8, "vitamin D", 450, size=36, x=1080, maxw=240)
    cap(cv, t, T[5] + 0.2, "A disease nearly wiped out", 645, size=42, col=GRN, maxw=1000)


def s12(cv, t, T):
    # 0 terror | 1 scars | 2 not Europe | 3 variolation | 4 Boston
    hd(cv, t, T, "Smallpox")
    k = pop(t, T[1] + 0.2)
    if k > 0.05:
        face(cv, 330, 400, 110 * k, 2.0 * k, "sad")
        if k > 0.9:
            for dx, dy in ((-50, -40), (30, -60), (60, -10), (-70, 10), (10, -20), (-20, 50), (50, 50), (-40, -5), (0, 70)):
                ell(cv, 330 + dx, 400 + dy, 7, 7, RED, 0)
    if t < T[4]:
        tag(cv, t, T[2] + 0.2, "Not in Europe!", 900, 215, size=40, fill=WARN, maxw=420)
    if T[3] <= t < T[4]:
        for j, w in enumerate(("China", "India", "Africa", "Ottoman Empire")):
            tag(cv, t, T[3] + 0.2 + 0.45 * j, w, 900, 290 + j * 62, size=34, maxw=400)
        cap(cv, t, T[3] + 1.5, "Variolation: a tiny scratch, a mild case", 620, size=36, col=BLUE, maxw=1000)
    if t >= T[4]:
        tag(cv, t, T[4] + 0.2, "Boston, 1721", 860, 215, size=40, fill=WARN, maxw=420)
        for x, nm in ((730, "Cotton Mather"), (990, "Onesimus")):
            kk = pop(t, T[4] + 0.5)
            if kk > 0.05:
                person(cv, x, 620, 0.75 * kk, WHITE, "smile", (-40, 55), (40, 55), None, (110, 80, 60))
                tag(cv, t, T[4] + 0.9, nm, x, 380, size=32, maxw=240)


def s13(cv, t, T):
    # 0 determined woman | 1 Lady Mary | 2 1721 daughter | 3 Caroline | 4 risky choice
    hd(cv, t, T, "Lady Mary's Experiment")
    k1 = pop(t, T[1] + 0.2)
    if k1 > 0.05:
        person(cv, 240, 620, 0.9 * k1, (240, 200, 235), "smile", (-40, 55), (40, 55), None, (90, 60, 60))
        tag(cv, t, T[1] + 0.5, "Lady Mary Montagu", 240, 330, size=32, maxw=320)
        tag(cv, t, T[1] + 1.3, "Constantinople", 240, 275, size=32, maxw=320)
    if t < T[3]:
        if card(cv, t, T[2] + 0.2, 440, 190, 780, 430, PAPER):
            text(cv, 610, 300, "1721", 84, RED)
            text(cv, 610, 380, "London", 38)
        kd = pop(t, T[2] + 0.8)
        if kd > 0.05:
            person(cv, 900, 620, 0.5 * kd, WHITE, "smile", (-40, 55), (40, 55), None, (90, 60, 60))
            tag(cv, t, T[2] + 1.2, "Her daughter", 900, 470, size=30, maxw=240)
    if T[3] <= t < T[4]:
        kc = pop(t, T[3] + 0.2)
        if kc > 0.05:
            person(cv, 640, 620, 0.85 * kc, (255, 225, 160), "smile", (-40, 55), (40, 55), None, (120, 90, 60))
            person(cv, 780, 620, 0.45 * kc, WHITE, "smile", (-40, 55), (40, 55), None, None)
            person(cv, 860, 620, 0.45 * kc, WHITE, "smile", (-40, 55), (40, 55), None, None)
            if kc > 0.9:
                poly(cv, [(615, 386), (622, 358), (632, 376), (640, 352), (648, 376), (658, 358), (665, 386)], YEL, 4)
        tag(cv, t, T[3] + 0.5, "Princess Caroline", 640, 300, size=34, maxw=320)
        tag(cv, t, T[3] + 1.2, "Her children", 820, 440, size=30, maxw=240)
    if t >= T[4]:
        wipe(cv)
        hd(cv, t, T, "Lady Mary's Experiment")
        if card(cv, t, T[4] + 0.2, 110, 230, 560, 560, (225, 245, 225)):
            text(cv, 335, 330, "Inoculate", 56, GRN)
            text(cv, 335, 420, "A small, planned risk", 32)
        text(cv, CX, 395, "or", 50, scale=pop(t, T[4] + 0.6))
        if card(cv, t, T[4] + 0.9, 720, 230, 1170, 560, (255, 228, 225)):
            text(cv, 945, 330, "Wait", 56, RED)
            text(cv, 945, 420, "for smallpox to arrive", 32)


def s14(cv, t, T):
    # 0 1796 | 1 cowpox/milkmaids | 2 Jenner + Phipps | 3 stayed healthy | 4 ethics | 5 1980
    hd(cv, t, T, "Jenner's Idea")
    cow(cv, 230, 520, 0.85 * pop(t, T[1] + 0.2))
    tag(cv, t, T[1] + 0.5, "Cowpox", 230, 420, size=34, maxw=280)
    km = pop(t, T[1] + 1.2)
    if km > 0.05:
        person(cv, 500, 620, 0.7 * km, (255, 200, 215), "smile", (-40, 55), (40, 55), None, (120, 80, 50))
        tag(cv, t, T[1] + 1.4, "Milkmaids", 500, 390, size=32, maxw=240)
    kj = pop(t, T[2] + 0.3)
    if kj > 0.05:
        person(cv, 770, 620, 0.78 * kj, WHITE, "smile", (-40, 55), (40, 55), None, (150, 150, 160))
        tag(cv, t, T[2] + 0.5, "Dr Jenner", 770, 380, size=32, maxw=240)
    kb = pop(t, T[2] + 1.0)
    if kb > 0.05:
        person(cv, 1010, 620, 0.5 * kb, WHITE, "smile", (-40, 55), (40, 55), None, None)
        tag(cv, t, T[2] + 1.3, "James Phipps, age 8", 1010, 460, size=28, maxw=300)
    if t < T[5]:
        cap(cv, t, T[3] + 0.3, "Immune!", 205, size=54, col=GRN, maxw=500)
        tag(cv, t, T[4] + 0.3, "Could he truly choose?", 640, 275, size=34, fill=WARN, maxw=520)
    if t >= T[5]:
        cap(cv, t, T[5] + 0.3, "1980: smallpox eradicated", 235, size=54, col=BLUE, maxw=1000)


def s15(cv, t, T):
    # 0 milk deadly | 1 New York | 2 distillery mash | 3 newspaper 1858 | 4 rules + pasteurization
    hd(cv, t, T, "Dangerous Milk")
    if T[1] <= t < T[2]:
        tag(cv, t, T[1] + 0.2, "New York City, 1850s", CX, 215, size=40, maxw=600)
        for j, (x0, w, h) in enumerate(((150, 120, 200), (290, 150, 280), (460, 110, 170), (590, 160, 320),
                                        (770, 130, 230), (920, 150, 260), (1090, 90, 180))):
            kk = pop(t, T[1] + 0.4 + j * 0.15, 0.5)
            if kk > 0.03:
                rrect(cv, x0, 620 - h * kk, x0 + w, 620, 6, (210, 215, 235), 5)
    if T[2] <= t < T[3]:
        cow(cv, 300, 480, 1.3 * pop(t, T[2] + 0.2))
        bottle(cv, 900, 520, 1.7 * pop(t, T[2] + 1.0), WHITE, "PURE", 18)
        tag(cv, t, T[2] + 0.6, "Fed whiskey mash", 300, 340, size=36, fill=WARN, maxw=400)
        tag(cv, t, T[2] + 1.4, "Sold as pure country milk", 900, 250, size=34, maxw=420)
    if T[3] <= t < T[4]:
        if card(cv, t, T[3] + 0.2, 380, 180, 900, 570, PAPER):
            text(cv, 640, 235, "NEWSPAPER, 1858", 34)
            text(cv, 640, 340, "Up to 8,000", 84, RED)
            text(cv, 640, 430, "infant deaths in one year", 36)
    if t >= T[4]:
        tag(cv, t, T[4] + 0.2, "1862: first milk rules", 360, 330, size=40, fill=(220, 245, 220), maxw=500)
        k = pop(t, T[4] + 0.8)
        if k > 0.05:
            rrect(cv, 960, 250, 1000, 480, 18, WHITE, 5)
            rrect(cv, 966, 480 - 200 * k, 994, 480, 12, RED, 0)
            ell(cv, 980, 510, 34, 34, RED, 5)
        cap(cv, t, T[4] + 1.2, "Pasteurization: heat kills germs", 600, size=38, col=BLUE, maxw=1000)


def s16(cv, t, T):
    # 0 diphtheria airway | 1 strangling angel | 2 antitoxin 1890 | 3 1894 report | 4 Nobel 1901
    hd(cv, t, T, "The Strangling Angel")
    kf = pop(t, T[0] + 0.4)
    if kf > 0.05:
        face(cv, 330, 400, 110 * kf, 2.0 * kf, "sad")
        if kf > 0.9:
            ell(cv, 330, 545, 70, 24, None, 7, RED)
    cap(cv, t, T[0] + 1.0, "Closing airway", 625, size=38, col=RED, x=330, maxw=420)
    tag(cv, t, T[1] + 0.3, "'Strangling angel'", 900, 230, size=40, fill=WARN, maxw=460)
    if t >= T[2] + 0.2:
        syringe(cv, 900, 330, 1.0 * pop(t, T[2] + 0.2))
        tag(cv, t, T[2] + 0.8, "Antitoxin, 1890", 900, 400, size=34, maxw=420)
    if t >= T[3] + 0.2:
        cap(cv, t, T[3] + 0.2, "168 of 220 children recovered", 470, size=34, x=900, maxw=480)
        w = 440 * 0.764 * rg(t, T[3] + 0.6, T[3] + 2.4)
        if w > 12:
            rrect(cv, 683, 503, 680 + w - 3, 542, 12, GRN, 0)
        rrect(cv, 680, 500, 1120, 545, 16, None, 5)
    if t >= T[4] + 0.2:
        k = pop(t, T[4] + 0.2)
        ell(cv, 760, 610, 36 * k, 36 * k, YEL, 5)
        tag(cv, t, T[4] + 0.6, "1901 Nobel Prize in Medicine", 960, 610, size=32, maxw=400)


def s17(cv, t, T):
    # 0 laws catch up | 1 1906 act | 2 read the label | 3 journalists + doctors | 4 honesty
    hd(cv, t, T, "Laws Catch Up")
    if card(cv, t, T[1] + 0.2, 110, 180, 560, 570, PAPER):
        text(cv, 335, 260, "Pure Food and", 44)
        text(cv, 335, 320, "Drug Act", 44)
        text(cv, 335, 420, "1906", 84, RED)
    bottle(cv, 900, 300, 1.1 * pop(t, T[2] + 0.2), SKY, "Label", 14)
    tag(cv, t, T[2] + 0.7, "Opium and morphine must be listed", 900, 420, size=32, maxw=500, fill=WHITE)
    k = pop(t, T[3] + 0.2)
    if k > 0.05:
        person(cv, 740, 650, 0.55 * k, WHITE, "smile", (-40, 55), (40, 55), None, (110, 80, 60))
        person(cv, 1000, 650, 0.55 * k, WHITE, "smile", (-40, 55), (40, 55), None, (150, 150, 160))
        tag(cv, t, T[3] + 0.5, "Journalists", 740, 470, size=28, maxw=220)
        tag(cv, t, T[3] + 0.9, "Doctors", 1000, 470, size=28, maxw=220)
    if t >= T[4]:
        wipe(cv)
        cap(cv, t, T[4] + 0.2, "Trust is built on honesty,", 290, size=70, col=BLUE)
        cap(cv, t, T[4] + 0.7, "not on advertising", 390, size=70, col=BLUE)


def s18(cv, t, T):
    # 0 twist | 1 necklaces 2018 | 2 benzocaine | 3 safe options | 4 popular != safe
    hd(cv, t, T, "Old Habits Return")
    k1 = pop(t, T[1] + 0.2)
    if k1 > 0.05:
        charm(cv, 260, 360, 1.5 * k1)
        if k1 > 0.9:
            cross(cv, 260, 400, 1.2)
        tag(cv, t, T[1] + 0.7, "2018: FDA warning", 260, 560, size=34, fill=WARN, maxw=380)
    k2 = pop(t, T[2] + 0.2)
    if k2 > 0.05:
        rrect(cv, 540, 340, 740, 410, 20 * k2, (240, 230, 250), 5)
        rrect(cv, 740, 355, 800, 395, 8, (200, 160, 220), 5)
        text(cv, 640, 375, "GEL", 36)
        if k2 > 0.9:
            cross(cv, 640, 380, 1.2)
        tag(cv, t, T[2] + 0.7, "Benzocaine gels", 640, 560, size=34, fill=WARN, maxw=300)
    if t >= T[3] + 0.2:
        tag(cv, t, T[3] + 0.2, "Cool teething ring", 1010, 270, size=32, fill=(220, 245, 220), maxw=340)
        tag(cv, t, T[3] + 0.8, "Clean wet washcloth", 1010, 350, size=32, fill=(220, 245, 220), maxw=340)
        tag(cv, t, T[3] + 1.4, "Gentle finger rub", 1010, 430, size=32, fill=(220, 245, 220), maxw=340)
        kr = pop(t, T[3] + 1.0)
        if kr > 0.05:
            ell(cv, 1010, 530, 40 * kr, 40 * kr, None, 14, GRN)
    cap(cv, t, T[4] + 0.3, "Popular does not mean safe", 640, size=40, col=BLUE, maxw=1000)


def s19(cv, t, T):
    # 0 question | 1 many small improvements | 2 water+milk | 3 vaccines | 4 food+vitamins | 5 antibiotics etc.
    hd(cv, t, T, "What Really Worked")
    if t < T[1] + 0.2:
        cap(cv, t, T[0] + 0.3, "?", 400, size=220, col=BLUE)
    tag(cv, t, T[1] + 0.3, "Many small improvements", CX, 205, size=40, maxw=700)
    rows = (
        (T[2], 590, "Clean water + safe milk", SKY),
        (T[3], 510, "Vaccines", (200, 240, 200)),
        (T[4], 430, "Better food + vitamins", (255, 235, 170)),
        (T[5], 350, "Antibiotics, children's hospitals, honest labels", (255, 205, 215)),
    )
    for a0, y, s, col in rows:
        k = pop(t, a0 + 0.2)
        if k > 0.05:
            rrect(cv, CX - 330 * k, y - 34, CX + 330 * k, y + 34, 14, col, 5)
            text(cv, CX, y, s, fit(s, 36, 620), INK, scale=k)


def s20(cv, t, T):
    # 0 success story | 1 43 -> 4 | 2 1 in 200 | 3 still work to do
    hd(cv, t, T, "A Success Story")
    for i in range(100):
        r, c = divmod(i, 10)
        k = pop(t, T[1] + 0.2 + c * 0.02 + r * 0.02, 0.3)
        if k > 0.03:
            ell(cv, 160 + c * 34, 200 + r * 34, 11 * k, 11 * k, RED if i < 43 else WHITE, 3)
        k2 = pop(t, T[1] + 1.5 + c * 0.02 + r * 0.02, 0.3)
        if k2 > 0.03:
            ell(cv, 800 + c * 34, 200 + r * 34, 11 * k2, 11 * k2, GRN if i < 4 else WHITE, 3)
    cap(cv, t, T[1] + 0.5, "Around 1800: 43 in 100", 550, size=32, x=307, maxw=340)
    cap(cv, t, T[1] + 1.5, "Today: below 4 in 100", 550, size=32, x=947, maxw=340)
    if t >= T[1] + 1.2:
        arrow(cv, 500, 350, 770, 350, 8, BLUE, rg(t, T[1] + 1.2, T[1] + 2.2))
    tag(cv, t, T[2] + 0.3, "Many rich countries: about 1 in 200", 947, 590, size=30, fill=(220, 245, 220), maxw=380)
    cap(cv, t, T[3] + 0.3, "Still work to do", 640, size=38, col=BLUE, maxw=1000)


def s21(cv, t, T):
    # 0 syrups, gums, wraps | 1 parents loved | 2 wanted child okay | 3 knowledge | 4 stay curious
    hd(cv, t, T, "Looking Back")
    if t < T[1]:
        bottle(cv, 250, 400, 1.2 * pop(t, T[0] + 0.3), SKY, "Syrup", 16)
        tooth(cv, 640, 380, 1.2 * pop(t, T[0] + 0.9))
        baby(cv, 1030, 520, 1.1 * pop(t, T[0] + 1.5), "smile", (236, 228, 205), 1.0)
        cap(cv, t, T[0] + 0.6, "syrups", 560, size=34, x=250, maxw=280)
        cap(cv, t, T[0] + 1.2, "cut gums", 560, size=34, x=640, maxw=280)
        cap(cv, t, T[0] + 1.5, "tight wraps", 560, size=34, x=1030, maxw=280)
    if T[1] <= t < T[3]:
        k = pop(t, T[1] + 0.3)
        if k > 0.05:
            person(cv, 560, 630, 1.0 * k, WHITE, "smile", (-40, 55), (40, 55), None, (110, 80, 60))
            baby(cv, 760, 630, 1.0 * k, "smile", None, 0)
        if t < T[2]:
            tag(cv, t, T[1] + 0.5, "They loved their children fiercely", CX, 215, size=40, maxw=900)
        else:
            tag(cv, t, T[2] + 0.3, "A parent who wanted their child to be okay", CX, 215, size=38, fill=WARN, maxw=1000)
            kh = pop(t, T[2] + 0.6)
            if kh > 0.05:
                poly(cv, [(660, 330 + 40 * kh), (610, 280), (630, 255), (660, 275), (690, 255), (710, 280)], RED, 5)
    if t >= T[3]:
        wipe(cv)
        k = pop(t, T[3] + 0.2)
        ell(cv, CX, 300, 80 * k, 80 * k, YEL, 6)
        rrect(cv, CX - 30 * k, 300 + 78 * k, CX + 30 * k, 300 + 118 * k, 8 * k, (200, 200, 210), 5)
        cap(cv, t, T[3] + 0.5, "Knowledge changed the story", 520, size=54, col=BLUE)
    if t >= T[4]:
        cap(cv, t, T[4] + 0.3, "Stay curious with Zuppy", 615, size=56, col=RED)


_FN = {
    "s01": s01, "s02": s02, "s03": s03, "s04": s04, "s05": s05, "s06": s06, "s07": s07,
    "s08": s08, "s09": s09, "s10": s10, "s11": s11, "s12": s12, "s13": s13, "s14": s14,
    "s15": s15, "s16": s16, "s17": s17, "s18": s18, "s19": s19, "s20": s20, "s21": s21,
}
_BG = {
    "s01": (255, 248, 225), "s02": (232, 240, 255), "s03": (255, 236, 230), "s04": (236, 250, 236),
    "s05": (245, 236, 255), "s06": (255, 244, 214), "s07": (232, 240, 255), "s08": (255, 236, 230),
    "s09": (236, 250, 236), "s10": (245, 236, 255), "s11": (255, 248, 225), "s12": (255, 236, 230),
    "s13": (232, 240, 255), "s14": (236, 250, 236), "s15": (255, 244, 214), "s16": (245, 236, 255),
    "s17": (255, 248, 225), "s18": (232, 240, 255), "s19": (236, 250, 236), "s20": (255, 244, 214),
    "s21": (245, 236, 255),
}
ORDER = ["s%02d" % i for i in range(1, 22)]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
