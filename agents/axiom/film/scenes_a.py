#!/usr/bin/env python3
"""Scenes, chapters 1-4: the date in the margin, Ussher's clock, the world that did not
fit, and Hutton's rock."""
from __future__ import annotations

import math

from film import props as P
from film.cast import Character, Pose, draw
from film.cast_defs import CLERK, CURATOR, HALL, HUTTON, NATURALIST, PLAYFAIR, SCRIBE, USSHER, CHILD
from film.style import (DEEP, INK, INK_SOFT, MOON, MOSS, NIGHT, OCHRE, PAPER, PLUM,
                    ROSE, SAND, SAND_D, SLATE, SLATE_L, STONE, STONE_D, TERRA, WHITE,
                    Camera, Ink, cam_path, clamp, ease_io, ease_out, pulse, seg, smooth)

REG = {}


def scene(fn):
    REG[fn.__name__] = fn
    return fn


def pale(ctx, width=5.0, colour=(238, 232, 208)):
    return Ink(ctx.img, ctx.cam_, width=width, colour=colour)


# =====================================================================  1  ====
@scene
def date_void(ctx):
    """Hook: a date written in the dark, over an ink clock."""
    cam = ctx.cam([(0.0, Camera(960, 540, 1.0, ctx.pix)), (ctx.p("dur", 30), Camera(980, 520, 1.22, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx)
    cx, cy, r = 960, 470, 250
    lp.ellipse(cx - r, cy - r, cx + r, cy + r, outline=(120, 128, 150), width=5)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        lp.line([(cx + math.sin(a) * r * 0.84, cy - math.cos(a) * r * 0.84),
                 (cx + math.sin(a) * r * 0.94, cy - math.cos(a) * r * 0.94)], width=3.4, colour=(110, 118, 140))
    a = ctx.t * 0.5
    lp.line([(cx, cy), (cx + math.sin(a) * r * 0.5, cy - math.cos(a) * r * 0.5)], width=6, colour=MOON)
    lp.line([(cx, cy), (cx + math.sin(a * 7) * r * 0.76, cy - math.cos(a * 7) * r * 0.76)], width=4, colour=MOON)

    b2 = ctx.beat("1.2")
    ctx.key("4004 BC", x=960, y=cy + 300, size=170, fill=(248, 240, 210), reveal=ctx.u(b2, b2 + 0.8))
    ctx.note("the night before 23 October", x=960, y=cy + 400, size=54, anchor="ma",
             fill=(214, 208, 186), arrow_to=None) if ctx.t > b2 + 1.0 else None


@scene
def ussher_study(ctx):
    """Ussher at his desk, candle, folio; camera pushes in on the page."""
    cam = ctx.cam([(0.0, Camera(960, 600, 1.0, ctx.pix)), (ctx.p("dur", 20), Camera(1010, 560, 1.5, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(206, 190, 166), floor=(150, 118, 88), y=840,
             window=(1560, 430, 320, 420), dress=("rug", "shelf", "lamp"))
    P.table(ik, 1000, 902, w=700, h=30, legs=170)
    P.chair(ik, 1320, 950, s=1.05, col=(122, 92, 64))
    # folio + quill on the desk
    P.open_folio(ik, 920, 856, s=0.86, title="ANNALES", left_lines=4)
    P.book(ik, 1340, 902, w=130, h=170, title="1650", colour=(122, 70, 62), s=0.7)
    ink_l = ctx.img
    b1, b2 = ctx.beat("1.3"), ctx.beat("1.3") + 1.4
    p = Pose(hip=(1150, 872), lean=-0.10, hand_l=(960, 806), hand_r=(1060, 818), prop_l="quill",
             mouth="neutral", brows="furrow", eyes="look_down", face_dir=-0.4)
    if ctx.t > b1 + 1.1:
        p.mouth, p.brows, p.eyes = "smile", "raised", "happy"
        p.hand_l = (950 + math.sin(ctx.t * 3.2) * 12, 806 + math.cos(ctx.t * 3.2) * 6)
    draw(ik, USSHER, p, facing=1)
    # candle
    P.book(ik, 1520, 902, w=80, h=110, title="", colour=(94, 88, 80), s=0.7)
    ik.rrect(1510, 868, 1530, 902, r=4, fill=(248, 240, 214), outline=INK, width=3)
    flick = 1.0 + 0.3 * math.sin(ctx.t * 11.0)
    ik.ellipse(1514, 852 - 12 * flick, 1526, 868, fill=(252, 196, 84))
    ctx.sun_spot(940, 830, r=440, alpha=54)
    ctx.key("1650", x=430, y=250, size=96, fill=SLATE, reveal=ctx.u(b1 - 0.6, b1 + 0.5),
            underline=True)


@scene
def bible_margins(ctx):
    """Close-up: a printed Bible page with the date in the margin."""
    cam = ctx.cam([(0.0, Camera(960, 540, 1.0, ctx.pix)), (ctx.p("dur", 16), Camera(900, 560, 1.34, ctx.pix))])
    ik = ctx.ink
    ik.rrect(300, 150, 1620, 980, r=14, fill=(246, 240, 224), outline=(150, 138, 116), width=6)
    ik.line([(960, 150), (960, 980)], width=3, colour=(196, 186, 166))
    # printed columns as measured ruled lines (legible structure, not fake text)
    for col in (0, 1):
        x0 = 360 + col * 660
        for i in range(22):
            y = 230 + i * 32
            w = 520 if (i % 7) else 400
            ik.line([(x0, y), (x0 + w, y)], width=2.4, colour=(168, 160, 146))
    # the margin date
    b = ctx.beat("1.3")
    ik.line([(960, 150), (960, 980)], width=3, colour=(196, 186, 166))
    ik.rrect(1636, 330, 1880, 470, r=10, fill=(252, 246, 226), outline=TERRA, width=3.4,
             ) if False else None
    ctx.key("4004 BC", x=1090, y=352, size=74, fill=TERRA, anchor="la", reveal=ctx.u(b + 0.8, b + 1.6))
    ik.line([(1082, 300), (1082, 400)], width=3.4, colour=TERRA)
    ctx.note("in the margin", x=1180, y=440, size=48, fill=(120, 76, 60)) if ctx.t > b + 1.5 else None
    # a hand resting on the page
    p = Pose(hip=(1420, 1120), lean=0.1, hand_l=(1120, 860), hand_r=(1330, 900),
             eyes="closed", mouth="smile", brows="neutral")
    draw(ik, Character(name="reader", hair="brown", hair_style="short", shirt=(96, 84, 74),
                       extras=(), scale=1.0), p, facing=-1, shadow=False)


@scene
def bible_row(ctx):
    """The date printed for two centuries: repeating editions receding in perspective."""
    cam = ctx.cam([(0.0, Camera(760, 540, 1.0, ctx.pix)), (ctx.p("dur", 26), Camera(1020, 540, 1.06, ctx.pix))])
    ik = ctx.ink
    for i in range(6):
        s = 1.0 - i * 0.11
        x = 300 + i * 300
        y = 980 - i * 26
        ik.poly([(x - 150 * s, y), (x + 150 * s, y - 20 * s), (x + 150 * s, y - 300 * s),
                 (x - 150 * s, y - 280 * s)], fill=(240 - i * 6, 232 - i * 5, 210 - i * 5),
                outline=(150, 140, 122), width=4)
        ik.line([(x, y - 6 * s), (x, y - 286 * s)], width=3, colour=(180, 170, 152))
        if i < 4:
            ik.text((x + 60 * s, y - 200 * s), "4004 BC", role="caps", size=34 * s, fill=(150, 96, 70))
    b = ctx.beat("1.4")
    ctx.key("printed in the margins", x=960, y=170, size=86, fill=SLATE, reveal=ctx.u(b + 0.6, b + 1.5))
    ctx.note("...of English Bibles, for two hundred years", x=960, y=280, size=48, anchor="ma",
             fill=(110, 104, 96)) if ctx.t > b + 2.2 else None


@scene
def ussher_writing(ctx):
    """The pivot: a serious scholar with a sealed assumption."""
    cam = ctx.cam([(0.0, Camera(1000, 560, 1.5, ctx.pix)), (ctx.p("dur", 20), Camera(900, 540, 1.15, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(198, 182, 158), floor=(146, 114, 84), y=850, window=(300, 400, 300, 380),
             dress=("rug", "shelf"))
    P.table(ik, 1000, 912, w=720, h=28, legs=170)
    P.open_folio(ik, 1000, 866, s=0.86, title="GENESIS", left_lines=3)
    b = ctx.beat("1.5")
    p = Pose(hip=(1180, 884), lean=-0.06, hand_l=(1060, 812), hand_r=(1130, 842), prop_l="quill",
             eyes="look_down", brows="furrow", mouth="neutral")
    if ctx.t > b + 1.2:
        p.eyes, p.brows, p.head_tilt, p.face_dir = "open", "one_up", -0.06, 0.6
        p.hand_r = (1080, 700)
    draw(ik, USSHER, p, facing=1)
    ctx.key("not the arithmetic", x=1420, y=300, size=84, fill=TERRA, anchor="ma",
            reveal=ctx.u(b + 0.4, b + 1.2))
    ctx.key("the assumption", x=1420, y=410, size=84, fill=SLATE, anchor="ma",
            reveal=ctx.u(b + 2.2, b + 3.0))


@scene
def three_clocks_tease(ctx):
    """Title card: three clocks, teasing the structure of the film."""
    cam = ctx.cam([(0.0, Camera(960, 540, 1.06, ctx.pix)), (ctx.p("dur", 24), Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("1.6")
    for i, (label, mk) in enumerate((("the scroll", 1), ("the cooling ball", 2), ("the hourglass", 3))):
        x = 420 + i * 540
        r = 24 if mk != 2 else 74
        u = ctx.u(b + 0.6 + i * 0.75, b + 1.3 + i * 0.75)
        if u <= 0.01:
            continue
        col = (TERRA, SLATE, OCHRE)[i]
        ik.rrect(x - 190, 560, x + 190, 860, r=18, fill=(252, 249, 240, int(220 * u)), outline=INK, width=4)
        if mk == 1:
            P.scroll_paper(ik, x, 700, s=0.62, w=280, h=130, lines=5)
        elif mk == 2:
            P.planet(ik, x, 700, r=62, kind="sun")
            for k in range(3):
                ik.line([(x + 70 + k * 8, 700 - 30 + k * 18), (x + 112 + k * 10, 700 - 44 + k * 22)],
                        width=4, colour=TERRA)
        else:
            P.hourglass(ik, x, 700, s=0.62, fill=0.72 - i * 0.1, t=ctx.t)
        ik.text((x, 812), label, role="caps", size=36, fill=INK_SOFT, anchor="ma")
    ctx.key("Three clocks", x=960, y=300, size=118, fill=INK, reveal=ctx.u(b + 0.1, b + 0.7))
    ctx.key("that had to be broken", x=960, y=428, size=74, fill=TERRA, reveal=ctx.u(b + 1.0, b + 1.8))
    ctx.note("How Old Is the Earth?", x=960, y=214, size=58, anchor="ma", fill=(110, 104, 96)) \
        if ctx.t > b + 2.4 else None


# =====================================================================  2  ====
@scene
def genealogy(ctx):
    """Genesis generations as a readable list, then as a sum."""
    cam = ctx.cam([(0.0, Camera(880, 560, 1.0, ctx.pix)), (ctx.p("dur", 24), Camera(940, 540, 1.12, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("2.2")
    u = ctx.u(b + 0.5, b + 3.2)
    P.genealogy_grid(ik, 820, 300, s=1.15, rows=6,
                     names=["Adam", "Seth", "Enosh", "Kenan", "Mahalalel", "Jared"],
                     reveal=u, highlight=0 if u > 0.2 else None)
    ctx.key("930 years", x=1520, y=372, size=76, fill=TERRA, anchor="ma", reveal=ctx.u(b + 1.1, b + 1.8))
    ctx.key("912", x=1520, y=468, size=76, fill=SLATE, anchor="ma", reveal=ctx.u(b + 2.6, b + 3.2))
    ctx.note("Genesis 5 and 11", x=820, y=210, size=56, anchor="ma", fill=(96, 90, 84))
    CUR = CURATOR
    draw(ik, CUR, Pose(hip=(330, 900), lean=0.05, hand_l=(560, 620), hand_r=(470, 760),
                       eyes="open", brows="raised", mouth="smile", prop_l="pointer"), facing=1)


@scene
def genealogy_anchor(ctx):
    """The chain needs one outside anchor."""
    cam = ctx.cam([(0.0, Camera(960, 540, 1.0, ctx.pix)), (ctx.p("dur", 22), Camera(1060, 560, 1.2, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("2.3")
    for i in range(9):
        x = 300 + i * 150
        ik.ellipse(x - 22, 470, x + 22, 514, fill=(SLATE_L if i < 4 else TERRA), outline=INK, width=4)
        if i < 8:
            ik.line([(x + 22, 492), (x + 128, 492)], width=6, colour=INK if i < 3 else (170, 164, 152))
    ik.text((280, 560), "genealogies", role="caps", size=40, fill=INK_SOFT)
    ik.text((1330, 560), "an anchor date", role="caps", size=40, fill=TERRA)
    ctx.key("one date, known from outside", x=960, y=760, size=76, fill=INK, reveal=ctx.u(b + 1.0, b + 1.9))
    ctx.key("tie it to history", x=960, y=860, size=76, fill=SLATE, reveal=ctx.u(b + 2.4, b + 3.2))


@scene
def babylon(ctx):
    """Nebuchadnezzar in clay: a dated tablet and a scribe."""
    cam = ctx.cam([(0.0, Camera(900, 560, 1.05, ctx.pix)), (ctx.p("dur", 22), Camera(1010, 540, 1.3, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(196, 172, 140), floor=(140, 110, 80), y=870, window=None,
             dress=("rug", "stool"))
    P.table(ik, 1000, 906, w=620, h=26, legs=170)
    b = ctx.beat("2.4")
    ik.rrect(840, 660, 1180, 790, r=10, fill=(184, 148, 104), outline=(120, 92, 60), width=5)
    for i in range(5):
        ik.line([(870 + i * 12, 684 + i * 20), (1140 - i * 10, 684 + i * 20)], width=3.4, colour=(120, 92, 60))
    ctx.key("Nebuchadnezzar", x=1010, y=300, size=78, fill=TERRA, reveal=ctx.u(b + 0.6, b + 1.5))
    ctx.key("died 562 BC", x=1010, y=404, size=70, fill=INK, reveal=ctx.u(b + 2.0, b + 2.8))
    draw(ik, SCRIBE, Pose(hip=(1350, 906), lean=-0.1, hand_l=(1130, 800), hand_r=(1215, 830),
                          eyes="look_down", brows="neutral", mouth="neutral", prop_l="quill"), facing=1)
    ctx.note("a king with surviving records", x=1010, y=520, size=46, anchor="ma", fill=(110, 104, 96)) \
        if ctx.t > b + 3.0 else None


@scene
def count_back(ctx):
    """Counting backwards: years ticking off a long rule."""
    dur = ctx.p("dur", 20)
    b = ctx.beat("2.4")
    cam = ctx.cam([(0.0, Camera(1500, 540, 1.0, ctx.pix)), (dur, Camera(560, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    y = 560
    ik.line([(100, y), (3200, y)], width=6, colour=(150, 144, 132))
    for i in range(40):
        x = 2600 - i * 72
        ik.line([(x, y - (34 if i % 10 == 0 else 16)), (x, y + (34 if i % 10 == 0 else 16))],
                width=5 if i % 10 == 0 else 3, colour=(104, 98, 90))
        if i % 10 == 0:
            ik.text((x, y + 52), f"{562 + i * 50}", role="caps", size=40, fill=(70, 66, 62), anchor="ma")
    for ex, label, col in ((2600, "562 BC\nNebuchadnezzar dies", SLATE),
                           (1148, "2348 BC\nthe flood", (86, 96, 120)),
                           (500, "4004 BC\ncreation", TERRA)):
        ik.ellipse(ex - 13, y - 13, ex + 13, y + 13, fill=col, outline=INK, width=3)
        ik.line([(ex, y - 15), (ex, y - 74)], width=3.4, colour=(120, 114, 104))
        for k, ln in enumerate(label.split("\n")):
            ik.text((ex, y - 104 + k * 32), ln, role="caps", size=36, fill=col, anchor="ma")
    x_now = 2600 - clamp(ctx.u(b - 0.4, b + 4.4)) * 2880
    ik.line([(x_now, y - 150), (x_now, y + 90)], width=7, colour=TERRA)
    ik.ellipse(x_now - 17, y - 167, x_now + 17, y - 133, fill=TERRA, outline=INK, width=3)
    ctx.key("count backwards", x=960, y=250, size=84, fill=SLATE, reveal=ctx.u(b - 0.2, b + 0.6))


@scene
def harvest(ctx):
    """Autumn equinox: the year begins when it has something to show."""
    cam = ctx.cam([(0.0, Camera(960, 620, 1.02, ctx.pix)), (ctx.p("dur", 22), Camera(1080, 560, 1.14, ctx.pix))])
    ik = ctx.ink
    ctx.sky_ground(horizon=720, sky=(196, 214, 226), ground_col=(198, 176, 108))
    b = ctx.beat("2.5")
    P.planet(ik, 1560, 260, r=86, kind="sun")
    for i in range(14):
        x = 120 + i * 130
        ik.line([(x, 800), (x - 6, 730)], width=5, colour=(170, 148, 84))
        ik.ellipse(x - 16, 726, x + 16, 782, fill=(214, 176, 88), outline=(150, 120, 60), width=3)
    draw(ik, Character(name="Reaper", hair="gold", hair_style="bun", shirt=(146, 116, 76),
                       trousers=(120, 96, 64), extras=("hat",), kind="adult"),
         Pose(hip=(700, 900), lean=0.12, hand_l=(600, 760), hand_r=(700, 800), prop_r="hammer",
              eyes="look_down", brows="neutral", mouth="smile"), facing=1)
    draw(ik, CHILD, Pose(hip=(1240, 946), lean=-0.05, hand_l=(1150, 890), hand_r=(1300, 880),
                         eyes="happy", brows="raised", mouth="grin"), facing=-1)
    ctx.key("the harvest", x=960, y=200, size=92, fill=(168, 116, 44), reveal=ctx.u(b + 0.7, b + 1.6))
    ctx.note("a year should start when it has something to show", x=960, y=300, size=46, anchor="ma",
             fill=(120, 96, 60)) if ctx.t > b + 2.6 else None


@scene
def date_stamp(ctx):
    """The headline claim, as a date on the page."""
    cam = ctx.cam([(0.0, Camera(960, 540, 1.18, ctx.pix)), (ctx.p("dur", 20), Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("2.6")
    ik.rrect(360, 250, 1560, 830, r=20, fill=(252, 247, 232), outline=(160, 148, 126), width=5)
    ctx.key("23 October", x=960, y=420, size=132, fill=INK, reveal=ctx.u(b + 0.5, b + 1.3))
    ctx.key("4004 BC", x=960, y=600, size=152, fill=TERRA, reveal=ctx.u(b + 1.6, b + 2.4))
    ctx.note("the night before", x=960, y=730, size=52, anchor="ma", fill=(120, 112, 102)) \
        if ctx.t > b + 2.6 else None


@scene
def two_corrections(ctx):
    """Honesty beat: what is really in the text, and what is not Ussher."""
    cam = ctx.cam([(0.0, Camera(960, 540, 1.0, ctx.pix)), (ctx.p("dur", 26), Camera(960, 540, 1.05, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("2.7")
    ctx.panel(560, 620, 700, 420, title="IN THE TEXT", accent=(74, 116, 88))
    ctx.panel(1360, 620, 700, 420, title="NOT HIS", accent=TERRA)
    P.genealogy_grid(ik, 560, 520, s=0.72, rows=4, names=["Adam", "Seth", "Enosh", "Kenan"], reveal=1.0)
    ik.text((1360, 620), "9 a.m.", role="display", size=96, fill=(120, 112, 100), anchor="ma")
    ik.line([(1180, 560), (1540, 700)], width=6, colour=TERRA)
    ik.line([(1540, 560), (1180, 700)], width=6, colour=TERRA)
    ctx.note("another scholar, another calculation", x=1360, y=760, size=42, anchor="ma", fill=(130, 120, 110))
    ctx.key("the list is real", x=560, y=880, size=58, fill=(74, 116, 88), anchor="ma",
            reveal=ctx.u(b + 0.6, b + 1.3))
    ctx.key("the clock is still a book", x=1360, y=880, size=58, fill=TERRA, anchor="ma",
            reveal=ctx.u(b + 2.6, b + 3.4))


# =====================================================================  3  ====
@scene
def study_wide(ctx):
    """Widening out: the study can't contain the world."""
    cam = ctx.cam([(0.0, Camera(960, 620, 1.1, ctx.pix)), (ctx.p("dur", 18), Camera(960, 560, 0.92, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(198, 182, 158), floor=(146, 114, 84), y=848)
    P.table(ik, 1080, 900, w=640, h=26, legs=170)
    P.open_folio(ik, 1040, 858, s=0.8, title="ANNALES", left_lines=3)
    draw(ik, USSHER, Pose(hip=(1240, 872), lean=-0.05, hand_l=(1100, 800), hand_r=(1180, 820),
                          eyes="open", brows="worried", mouth="frown", head_tilt=0.05), facing=1)
    b = ctx.beat("3.1")
    ctx.key("so where did it go wrong?", x=960, y=230, size=88, fill=INK, reveal=ctx.u(b + 0.6, b + 1.4))


@scene
def archive(ctx):
    """Egyptian king lists and Chinese records: the archive refuses to shrink."""
    cam = ctx.cam([(0.0, Camera(940, 560, 1.0, ctx.pix)), (ctx.p("dur", 34), Camera(1120, 540, 1.16, ctx.pix))])
    ik = ctx.ink
    b2, b3 = ctx.beat("3.2"), ctx.beat("3.3")
    ctx.room(wall=(184, 176, 158), floor=(132, 120, 100), y=872, dress=("shelf", "lamp"))
    P.bench(ik, 700, 850, w=900, h=30, legs=150)
    P.scroll_paper(ik, 480, 700, s=1.0, w=520, h=210, lines=7)
    ik.rrect(760, 620, 1180, 800, r=8, fill=(238, 226, 196), outline=(150, 134, 108), width=4)
    for i in range(7):                       # Egyptian king list: ruled rows of marks
        yy = 646 + i * 22
        ik.line([(790, yy), (1150 - (i % 3) * 30, yy)], width=4, colour=(146, 130, 104))
        for k in range(2 + (i % 3)):
            xx = 810 + k * 96
            ik.line([(xx, yy - 13), (xx + 8, yy - 13)], width=4, colour=TERRA)
            ik.ellipse(xx - 20, yy - 5, xx - 10, yy + 5, outline=TERRA, width=3)
    for i in range(6):                       # Chinese record: dense vertical columns
        yy = 640 + i * 26
        ik.line([(1210, yy), (1570, yy)], width=4, colour=(118, 110, 98))
        for k in range(9):
            xx = 1228 + k * 38
            ik.line([(xx, yy - 10), (xx, yy + 4)], width=3.4, colour=(92, 86, 78))
    ik.rrect(1180, 610, 1600, 800, r=8, fill=(246, 238, 214), outline=(150, 134, 108), width=4)
    ctx.stamp("EGYPT", 480, 570, size=42, fill=TERRA)
    ctx.stamp("CHINA", 1390, 570, size=42, fill=SLATE)
    ctx.key("other records", x=960, y=280, size=86, fill=INK, reveal=ctx.u(b2 + 0.7, b2 + 1.5))
    ctx.key("go back further", x=960, y=390, size=86, fill=TERRA, reveal=ctx.u(b3 + 0.4, b3 + 1.2))
    draw(ik, CLERK, Pose(hip=(1740, 880), lean=-0.08, hand_l=(1560, 720), hand_r=(1660, 760),
                         eyes="look_down", brows="neutral", mouth="neutral"), facing=1)


@scene
def fossil_hill(ctx):
    """Shells in mountains: the observation that keeps asking for time."""
    cam = ctx.cam([(0.0, Camera(960, 620, 1.0, ctx.pix)), (ctx.p("dur", 24), Camera(1080, 640, 1.35, ctx.pix))])
    ik = ctx.ink
    ctx.sky_ground(horizon=700, sky=(188, 208, 224), ground_col=(150, 162, 118))
    P.hill(ik, 1000, 1040, w=2200, h=420, col=(140, 154, 112), col2=(116, 132, 92))
    ik.poly([(560, 900), (760, 560), (980, 900)], fill=(148, 144, 138), outline=INK, width=5)
    ik.poly([(700, 900), (900, 620), (1120, 900)], fill=(168, 164, 156), outline=INK, width=5)
    for i in range(5):                       # bedding planes: this rock was laid down flat
        k = i / 5
        ik.line([(600 + k * 90, 900 - k * 250), (960 - k * 40, 900 - k * 250)],
                width=3.4, colour=(112, 108, 102))
        ik.line([(740 + k * 90, 900 - k * 200), (1080 - k * 30, 900 - k * 200)],
                width=3.4, colour=(126, 122, 116))
    b = ctx.beat("3.4")
    # fossil shells in the rock face
    for i, (sx, sy) in enumerate(((742, 700), (812, 748), (866, 660), (930, 790))):
        u = ctx.u(b + 0.4 + i * 0.25, b + 0.9 + i * 0.25)
        if u <= 0.01:
            continue
        ik.ellipse(sx - 18 * u, sy - 14 * u, sx + 18 * u, sy + 14 * u, fill=(232, 222, 196), outline=(140, 118, 92), width=3)
        for k in range(3):
            ik.line([(sx - 12 * u, sy - 6 * u + k * 6 * u), (sx + 12 * u, sy - 6 * u + k * 6 * u)], width=2, colour=(150, 126, 96))
    draw(ik, NATURALIST, Pose(hip=(1240, 900), lean=-0.12, hand_l=(940, 700), hand_r=(1010, 780),
                              eyes="wide", brows="raised", mouth="gasp", prop_l="magnifier"), facing=-1)
    ctx.key("seashells", x=430, y=300, size=94, fill=TERRA, anchor="ma", reveal=ctx.u(b + 1.0, b + 1.7))
    ctx.key("in the mountains", x=430, y=420, size=76, fill=INK, anchor="ma", reveal=ctx.u(b + 2.2, b + 3.0))


@scene
def flood(ctx):
    """The one-year answer to all of geology's questions."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.04, ctx.pix)), (dur, Camera(1040, 600, 1.18, ctx.pix))])
    ik = ctx.ink
    b5, b6 = ctx.beat("3.5"), ctx.beat("3.6")
    ctx.ink.rrect(-120, -120, 2040, 820, r=0, fill=(126, 136, 148))
    ctx.ink.rrect(-120, 820, 2040, 1200, r=0, fill=(72, 92, 116))
    for i in range(26):
        x = 60 + i * 76
        y0 = 200 + (i * 137) % 520
        ik.line([(x, y0), (x - 22, y0 + 70)], width=3.4, colour=(168, 182, 196))
    ik.rrect(-120, 700, 2040, 1200, r=0, fill=(58, 84, 112))
    ik.line([(-120, 700), (2040, 700)], width=6, colour=(196, 214, 230))
    P.boat(ik, 1180, 706, s=0.9, sail=False)
    # layered strata appear under the water as the flood explanation builds
    u = ctx.u(b5 + 1.0, b5 + 3.0)
    for i in range(4):
        y = 830 + i * 46
        ik.rrect(-120, y, 2040, y + 40, r=0, fill=(160 - i * 12, 140 - i * 10, 112 - i * 8, int(200 * u)))
    ctx.key("one year", x=420, y=280, size=104, fill=(240, 240, 236), anchor="ma", reveal=ctx.u(b5 + 0.5, b5 + 1.2))
    ctx.key("...for all of geology?", x=1500, y=320, size=74, fill=(236, 208, 168), anchor="ma",
            reveal=ctx.u(b6 + 0.6, b6 + 1.5))
    if ctx.t > b6 + 1.6:
        ctx.note("the rocks are not in a hurry", x=1500, y=420, size=52, anchor="ma", fill=(214, 196, 176))


@scene
def stretch_date(ctx):
    """Stretching the date: patches on patches."""
    dur = ctx.p("dur", 24)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.0, ctx.pix)), (dur, Camera(1240, 540, 1.2, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("3.7")
    y = 560
    ik.line([(180, y), (1780, y)], width=8, colour=(120, 114, 104))
    for i in range(11):
        x = 260 + i * 150
        ik.line([(x, y - 26), (x, y + 26)], width=4, colour=(120, 114, 104))
    pulls = ctx.u(b - 1.0, b + 2.0)
    for i, x in enumerate((700, 1000, 1300)):
        ik.rrect(x - 40, y + 40, x + 40, y + 92, r=8, fill=(246, 232, 190), outline=(180, 150, 96), width=3.4)
        ik.text((x, y + 66), ("gaps", "patches", "ages")[i], role="caps", size=30, fill=(150, 116, 66), anchor="mm")
        ik.line([(x, y + 40), (x, y + 6)], width=3.4, colour=(180, 150, 96))
    if pulls > 0:
        ik.line([(180 - 40 * pulls, y), (420 - 40 * pulls, y)], width=8, colour=TERRA)
        ik.line([(1540 + 40 * pulls, y), (1780 + 40 * pulls, y)], width=8, colour=TERRA)
    ctx.key("what if the problem", x=960, y=250, size=88, fill=INK, reveal=ctx.u(b + 1.6, b + 2.4))
    ctx.key("is the clock?", x=960, y=370, size=112, fill=TERRA, reveal=ctx.u(b + 2.8, b + 3.6))


# =====================================================================  4  ====
@scene
def coast_1788(ctx):
    """The boat at Siccar Point, 1788: three friends, one outcrop."""
    dur = ctx.p("dur", 26)
    cam = ctx.cam([(0.0, Camera(700, 600, 1.0, ctx.pix)), (dur, Camera(1180, 620, 1.2, ctx.pix))])
    ik = ctx.ink
    ctx.sky_ground(horizon=660, sky=(176, 202, 220), ground_col=(96, 116, 128))
    ik.rrect(-120, 900, 2040, 1200, r=0, fill=(60, 74, 92))
    for i in range(10):
        ik.line([(140 + i * 40, 960 + i * 12), (520 + i * 60, 960 + i * 12)], width=3,
                colour=(112, 132, 152))
    P.outcrop_siccar(ik, 1180, 880, s=0.78)
    P.boat(ik, 470, 830, s=0.5, sail=True)
    b = ctx.beat("4.2")
    u = ctx.u(b + 1.0, b + 4.5)
    for i, (who, x0, y0, x1) in enumerate(((HUTTON, 470, 830, 900), (PLAYFAIR, 440, 850, 980), (HALL, 500, 860, 1040))):
        xx = x0 + (x1 - x0) * clamp(u - i * 0.08)
        draw(ik, who, Pose(hip=(xx, y0 - 40), lean=0.04, hand_l=(xx - 50, y0 - 90), hand_r=(xx + 50, y0 - 96),
                           eyes="open", brows="raised", mouth="smile"), facing=1, shadow=False)
    ctx.key("Siccar Point, 1788", x=960, y=240, size=92, fill=SLATE, reveal=ctx.u(b + 0.6, b + 1.6))
    ctx.note("Hutton, Playfair, Hall", x=960, y=340, size=50, anchor="ma", fill=(96, 100, 106)) \
        if ctx.t > b + 3.4 else None


@scene
def siccar_rock(ctx):
    """The outcrop as a labelled diagram: vertical grey beds, flat red beds."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 620, 1.05, ctx.pix)), (dur, Camera(960, 600, 1.28, ctx.pix))])
    ik = ctx.ink
    ctx.sky_ground(horizon=560, sky=(186, 206, 220), ground_col=(132, 142, 120))
    b3, b4 = ctx.beat("4.3"), ctx.beat("4.4")
    P.outcrop_siccar(ik, 960, 780, s=1.0)
    draw(ik, HUTTON, Pose(hip=(300, 900), lean=0.06, hand_l=(470, 720), hand_r=(410, 760),
                          eyes="open", brows="raised", mouth="open"), facing=1)
    u = ctx.u(b4 + 0.4, b4 + 1.6)
    if u > 0.05:
        ctx.leader(700, 640, 560, 480, "red sandstone, flat", side="l", size=40)
        ctx.leader(880, 760, 700, 900, "grey beds, almost vertical", side="l", size=40)
    ctx.key("a mistake in stone", x=1420, y=300, size=78, fill=SLATE, anchor="ma", reveal=ctx.u(b3 + 0.5, b3 + 1.3))


@scene
def siccar_steps(ctx):
    """Four-step diagram build: deposit, fold, erode, deposit again."""
    dur = ctx.p("dur", 34)
    cam = ctx.cam([(0.0, Camera(1340, 600, 1.1, ctx.pix)), (dur, Camera(1160, 620, 1.02, ctx.pix))])
    ik = ctx.ink
    b, step_times = ctx.beat("4.6"), ctx.beat("4.6")
    steps = [("1. sediment settles flat", 0.0), ("2. folded and lifted", 0.22), ("3. worn flat by sea and weather", 0.46),
             ("4. new red beds laid on top", 0.72)]
    for i, (label, ph) in enumerate(steps):
        u = ctx.u(b + ph * 8.0, b + ph * 8.0 + 0.9)
        if u <= 0.01:
            continue
        x, y = 700 + (i % 2) * 900, 420 + (i // 2) * 420
        ik.rrect(x - 380, y - 180, x + 380, y + 180, r=16, fill=(252, 249, 240, int(225 * u)),
                 outline=INK, width=4)
        ik.text((x - 350, y - 156), label, role="caps", size=34, fill=INK_SOFT)
        if i == 0:
            P.rock_layers_tilt(ik, x, y + 60, w=560, h=140, angle=0.0, layers=4)
        elif i == 1:
            P.rock_layers_tilt(ik, x, y + 60, w=560, h=140, angle=0.42, layers=4)
        elif i == 2:
            P.rock_layers_tilt(ik, x, y + 60, w=560, h=140, angle=0.42, layers=4)
            ik.line([(x - 190, y - 40), (x + 190, y - 30)], width=6, colour=TERRA)
            ctx.note("worn flat", x + 240, y - 46, size=40, fill=TERRA)
        else:
            P.rock_layers_tilt(ik, x, y + 60, w=560, h=140, angle=0.42, layers=4)
            ik.line([(x - 190, y - 40), (x + 190, y - 30)], width=6, colour=TERRA)
            P.rock_layers_tilt(ik, x, y - 6, w=560, h=90, angle=0.0, layers=2,
                               palette=[(186, 96, 72), (170, 84, 64)])
    ctx.key("read the rock in order", x=960, y=180, size=76, fill=SLATE,
            reveal=ctx.u(ctx.beat("4.5") + 0.4, ctx.beat("4.5") + 1.2))


@scene
def siccar_slow(ctx):
    """Time as the slow, ordinary repetition of small days."""
    dur = ctx.p("dur", 22)
    cam = ctx.cam([(0.0, Camera(900, 620, 1.05, ctx.pix)), (dur, Camera(1060, 600, 1.2, ctx.pix))])
    ik = ctx.ink
    ctx.sky_ground(horizon=680, sky=(198, 214, 226), ground_col=(122, 138, 108))
    P.outcrop_siccar(ik, 900, 800, s=0.9)
    b = ctx.beat("4.7")
    # ordinary days: repeated small markers accumulating
    for i in range(26):
        u = ctx.u(b + 0.8 + i * 0.09, b + 1.2 + i * 0.09)
        if u <= 0.01:
            continue
        x = 180 + (i % 13) * 130
        y = 980 if i < 13 else 1030
        ik.line([(x, y - 8 * u), (x, y + 8 * u)], width=4, colour=(120, 116, 106))
    ctx.key("one day at a time", x=960, y=230, size=92, fill=INK, reveal=ctx.u(b + 1.6, b + 2.4))
    ctx.key("repeated beyond counting", x=960, y=350, size=74, fill=SLATE, reveal=ctx.u(b + 3.6, b + 4.4))


@scene
def hutton_phrase(ctx):
    """Hutton's sentence, in his own words."""
    dur = ctx.p("dur", 24)
    cam = ctx.cam([(0.0, Camera(960, 600, 1.12, ctx.pix)), (dur, Camera(1010, 570, 1.0, ctx.pix))])
    ik = ctx.ink
    ctx.sky_ground(horizon=700, sky=(190, 208, 222), ground_col=(112, 128, 104))
    P.outcrop_siccar(ik, 1080, 860, s=0.7)
    b = ctx.beat("4.8")
    draw(ik, HUTTON, Pose(hip=(560, 880), lean=0.05, hand_l=(700, 700), hand_r=(520, 720),
                          eyes="open", brows="raised", mouth="open", face_dir=0.4), facing=1)
    ctx.key_wrapped("no vestige of a beginning,\nno prospect of an end", x=1060, y=330, size=76,
                    role="hand", fill=(66, 72, 82), max_w=820, anchor="ma")
    ctx.stamp("— Hutton, 1788", 1060, 560, size=44, fill=(120, 116, 108))
    ik.poly([(1180, 700), (1360, 560), (1250, 560)], fill=(252, 249, 240), outline=INK)
    ik.poly([(1188, 692), (1236, 648), (1240, 566), (1300, 620)], fill=(236, 232, 216), outline=None)


@scene
def playfair_giddy(ctx):
    """The abyss of time: a horizon that tips and a mind that reels."""
    dur = ctx.p("dur", 30)
    tilt = math.sin(clamp(ctx.t / dur) * 2.2) * 0.10
    cam = Camera(960 + math.sin(ctx.t * 0.7) * 26, 560 + math.cos(ctx.t * 0.6) * 14,
                 1.06 + math.sin(ctx.t * 0.5) * 0.03, ctx.pix)
    ctx.cam([(ctx.t, cam)])
    ik = ctx.ink
    ctx.ink.img  # keep reference; horizon painted tilted below
    ctx.ink.rrect(-200, -200, 2120, 700, r=0, fill=(186, 206, 222))
    ctx.ink.rrect(-200, 700, 2120, 1300, r=0, fill=(104, 122, 100))
    ik.line([(0, 700 + tilt * 600), (1920, 700 - tilt * 600)], width=5, colour=(90, 100, 92))
    b = ctx.beat("4.9")
    draw(ik, PLAYFAIR, Pose(hip=(700, 880), lean=-0.08, hand_l=(560, 700), hand_r=(860, 690),
                            eyes="spiral" if ctx.t < b + 5 else "wide", brows="raised", mouth="gasp" if ctx.t < b + 5 else "o",
                            head_tilt=-0.08), facing=1)
    for i in range(6):
        a = ctx.t * (0.6 + i * 0.2)
        r = 120 + i * 68
        ik.line([(700 + math.cos(a) * r, 380 + math.sin(a) * r * 0.4),
                 (700 + math.cos(a + 0.5) * r, 380 + math.sin(a + 0.5) * r * 0.4)], width=3, colour=(150, 156, 168))
    ctx.key("the abyss of time", x=1350, y=340, size=104, fill=(60, 68, 80), anchor="ma",
            reveal=ctx.u(b + 1.4, b + 2.3))
    ctx.stamp("— Playfair, remembering the trip", 1350, 470, size=40, fill=(96, 102, 112))


@scene
def no_measurement(ctx):
    """Hutton gives depth, not a number."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.06, ctx.pix)), (dur, Camera(980, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b10, b11 = ctx.beat("4.10"), ctx.beat("4.11")
    # a canyon that keeps going: solid rock either side, darker with depth
    for i in range(14):
        k = i / 13
        y0 = 700 + k * 380
        y1 = y0 + 380 / 13 + 1
        inset = 40 + k * 150
        ik.rrect(-120, y0, 420 + inset, y1, r=0, fill=(150 - int(40 * k), 142 - int(38 * k), 128 - int(34 * k)))
        ik.rrect(1500 - inset, y0, 2040, y1, r=0, fill=(150 - int(40 * k), 142 - int(38 * k), 128 - int(34 * k)))
    ik.rrect(420, 700, 1500, 1080, r=0, fill=(58, 54, 50))
    for i, (yy, w) in enumerate(((760, 7), (860, 6), (960, 5), (1040, 4))):
        ik.line([(430 + i * 14, yy), (1490 - i * 14, yy)], width=w, colour=(96, 90, 84))
    # a measuring rod with no numbers on it
    ik.rrect(300, 620, 1620, 668, r=8, fill=(246, 240, 222), outline=INK, width=4)
    for i in range(19):
        xx = 330 + i * 66
        ik.line([(xx, 668), (xx, 668 - (30 if i % 2 == 0 else 18))], width=4, colour=(96, 90, 84))
    ctx.key("a feeling", x=1400, y=300, size=88, fill=INK, anchor="ma", reveal=ctx.u(b10 + 0.6, b10 + 1.4))
    ctx.key("not a measurement", x=1400, y=410, size=78, fill=TERRA, anchor="ma", reveal=ctx.u(b10 + 2.0, b10 + 2.8))
    ik.text((1560, 560), "?", role="display", size=140, fill=(120, 112, 102), anchor="ma")
    if ctx.t > b11 + 0.4:
        ctx.key("so somebody built a clock", x=960, y=250, size=80, fill=SLATE, reveal=ctx.u(b11 + 0.6, b11 + 1.5))
