#!/usr/bin/env python3
"""Scenes, chapters 8-10: the leaking clock, Patterson's clean room, and what a clock assumes."""
from __future__ import annotations

import math

from film import props as P
from film.cast import Character, Pose, draw
from film.cast_defs import BOLTWOOD, CURATOR, PATTERSON, PATTERSON_OLD
from film.scenes_a import REG, pale, scene
from film.style import (DEEP, INK, INK_SOFT, MOON, OCHRE, PLUM, ROSE, SLATE, SLATE_L,
                    STONE, TERRA, WHITE, Camera, Ink, clamp, ease_io, ease_out, pulse,
                    seg, smooth)


# =====================================================================  8  ====
@scene
def hourglass_honest(ctx):
    """Why an hourglass is honest — and why that is the whole difficulty."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.04, ctx.pix)), (dur, Camera(960, 540, 1.14, ctx.pix))])
    ik = ctx.ink
    b1, b2 = ctx.beat("8.1"), ctx.beat("8.2")
    P.hourglass(ik, 700, 580, s=1.5, fill=clamp(1.0 - ctx.u(b2, b2 + 10.0), 0.05, 1.0), t=ctx.t)
    ik.rrect(1290, 400, 1700, 760, r=14, fill=(252, 249, 240, 220), outline=INK, width=4)
    ctx.leader(760, 500, 1080, 460, "sand in the top", side="l", size=40)
    ctx.leader(760, 700, 1080, 700, "sand in the bottom", side="l", size=40)
    ctx.leader(700, 800, 1080, 860, "a steady neck", side="l", size=40)
    ik.text((1500, 520), "nothing in", role="caps", size=40, fill=(74, 116, 88), anchor="ma")
    ik.text((1500, 590), "nothing out", role="caps", size=40, fill=(74, 116, 88), anchor="ma")
    ik.text((1500, 660), "known start", role="caps", size=40, fill=(74, 116, 88), anchor="ma")
    ctx.key("a bigger problem than it sounds", x=960, y=250, size=76, fill=INK, reveal=ctx.u(b1 + 0.4, b1 + 1.2))


@scene
def three_assumptions(ctx):
    """Three conditions drawn as three closed doors."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.02, ctx.pix)), (dur, Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("8.3")
    labels = (("nothing was in the bottom", "at the start"),
              ("nothing has been added", "since"),
              ("nothing has escaped", "in between"))
    for i, (l1, l2) in enumerate(labels):
        x = 400 + i * 560
        u = ctx.u(b + 0.6 + i * 1.4, b + 1.4 + i * 1.4)
        if u <= 0.01:
            continue
        ik.rrect(x - 230, 460, x + 230, 800, r=16, fill=(252, 249, 240, int(230 * u)), outline=INK, width=4)
        ih = 560
        ik.rrect(x - 120, 520, x + 120, 780, r=8, fill=(206, 196, 172), outline=INK, width=4)
        ik.ellipse(x + 70, ih + 110, x + 92, ih + 132, fill=INK)
        ik.text((x, 850), l1, role="label", size=40, fill=INK, anchor="ma")
        ik.text((x, 900), l2, role="label", size=40, fill=INK_SOFT, anchor="ma")
    ctx.key("three things have to be true", x=960, y=280, size=84, fill=SLATE, reveal=ctx.u(b + 0.2, b + 1.0))


@scene
def helium_leak(ctx):
    """Helium escapes crystals: the first assumption fails."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(900, 580, 1.06, ctx.pix)), (dur, Camera(1000, 560, 1.24, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(196, 190, 176), floor=(140, 128, 110), y=900, dress=("rug", "shelf", "lamp"))
    P.rock_sample(ik, 1560, 900, s=1.1, col=(128, 124, 118))
    P.zircon(ik, 760, 620, s=1.7, glow=0.2)
    b = ctx.beat("8.4")
    for i in range(16):
        ph = (ctx.t * 0.5 + i * 0.11) % 1.0
        a = i * 2.1
        x = 760 + math.cos(a) * (60 + ph * 240)
        y = 620 + math.sin(a) * (40 + ph * 180)
        ik.ellipse(x - 7, y - 7, x + 7, y + 7, fill=(196, 214, 226, int(220 * (1 - ph))))
    ctx.key("helium leaks", x=1420, y=420, size=96, fill=TERRA, anchor="ma", reveal=ctx.u(b + 0.6, b + 1.6))
    ctx.note("out of the crystal, over millions of years", x=1420, y=540, size=46, anchor="ma",
             fill=(114, 108, 100)) if ctx.t > b + 2.4 else None


@scene
def uranium_moves(ctx):
    """Groundwater carries uranium in and out."""
    dur = ctx.p("dur", 26)
    cam = ctx.cam([(0.0, Camera(980, 600, 1.04, ctx.pix)), (dur, Camera(980, 560, 1.18, ctx.pix))])
    ik = ctx.ink
    ctx.sky_ground(horizon=430, sky=(186, 202, 214), ground_col=(150, 138, 120))
    ik.poly([(0, 430), (1920, 430), (1920, 1080), (0, 1080)], fill=(140, 128, 112))
    for i in range(4):
        yy = 520 + i * 130
        ik.line([(0, yy), (1920, yy + 18)], width=5, colour=(120, 110, 96))
    b = ctx.beat("8.4")
    for k in range(9):
        yy = 470 + k * 66
        ik.poly([(300 + k * 120, yy - 26), (760 + k * 120, yy - 26), (900 + k * 120, yy + 2),
                 (440 + k * 120, yy + 2)], fill=(120, 170, 196, 170)) if k < 5 else None
    for k in range(6):
        ph = (ctx.t * 0.7 + k * 0.17) % 1.0
        x = 420 + ph * 1080
        y = 560 + k * 40
        ik.ellipse(x - 12, y - 6, x + 12, y + 6, fill=(150, 208, 224, 200))
    ctx.key("uranium moves", x=960, y=250, size=92, fill=SLATE, reveal=ctx.u(b + 0.4, b + 1.4))
    ctx.stamp("in with the water, out with the water", 960, 990, size=42, fill=(88, 96, 104))


@scene
def scatter_dates(ctx):
    """Early dates disagreed with each other, and everyone could see it."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(960, 580, 1.02, ctx.pix)), (dur, Camera(1000, 560, 1.14, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("8.5")
    ik.rrect(300, 300, 1620, 900, r=14, fill=(252, 249, 240, 230), outline=INK, width=4)
    ik.line([(380, 840), (1540, 840)], width=5, colour=(120, 114, 104))
    ik.line([(380, 840), (380, 360)], width=5, colour=(120, 114, 104))
    for i in range(1, 5):
        x = 380 + i * 232
        ik.line([(x, 830), (x, 850)], width=4, colour=(150, 144, 134))
        ik.text((x, 872), f"{i} Gyr", role="caps", size=32, fill=INK_SOFT, anchor="ma")
    pts = [(0.4, 0.30), (0.9, 0.52), (1.2, 0.44), (1.7, 0.71), (2.0, 0.62), (2.3, 0.88), (1.5, 0.35)]
    for i, (gyr, frac) in enumerate(pts):
        u = ctx.u(b + 0.6 + i * 0.35, b + 1.0 + i * 0.35)
        if u <= 0.01:
            continue
        x = 380 + gyr / 4.4 * 1160
        y = 840 - frac * 420
        ik.ellipse(x - 14 * u, y - 14 * u, x + 14 * u, y + 14 * u, fill=(196, 98, 63, 220), outline=INK, width=3)
    ctx.key("the early dates disagreed", x=960, y=230, size=82, fill=TERRA, reveal=ctx.u(b + 0.4, b + 1.4))
    draw(ik, CURATOR, Pose(hip=(1720, 940), lean=-0.05, hand_l=(1560, 800), hand_r=(1660, 860),
                           eyes="open", brows="worried", mouth="frown"), facing=-1)


@scene
def boltwood(ctx):
    """Boltwood, 1907: the first uranium–lead dating, openly uncertain."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(800, 580, 1.02, ctx.pix)), (dur, Camera(1060, 560, 1.22, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(200, 194, 178), floor=(142, 130, 112), y=890, dress=("rug", "shelf", "lamp", "plant"))
    P.lab_bench(ik, 900, 918, s=1.0, t=ctx.t)
    b = ctx.beat("8.6")
    draw(ik, BOLTWOOD, Pose(hip=(1260, 902), lean=-0.05, hand_l=(1050, 820), hand_r=(1170, 836),
                            eyes="look_down", brows="furrow", mouth="neutral",
                            prop_r="flask"), facing=1)
    P.book(ik, 520, 918, w=160, h=210, title="1907", colour=(96, 106, 122), s=0.85, sub="U to Pb")
    ctx.key("the first real dating", x=960, y=230, size=82, fill=SLATE, reveal=ctx.u(b + 0.6, b + 1.6))
    ctx.key("up to 2 billion years", x=960, y=330, size=74, fill=INK, reveal=ctx.u(b + 3.0, b + 4.0))
    ctx.note("and openly uncertain", x=960, y=1000, size=46, anchor="ma", fill=(130, 122, 112)) \
        if ctx.t > b + 5.0 else None


@scene
def puzzle(ctx):
    """The question that drives the rest of the film."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.04, ctx.pix)), (dur, Camera(960, 540, 1.06, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("8.7")
    P.hourglass(ik, 520, 600, s=0.85, fill=0.8, t=ctx.t, label="410 My")
    P.hourglass(ik, 1400, 600, s=0.85, fill=0.2, t=ctx.t + 1.0, label="2 000 My")
    ik.line([(600, 480), (1320, 480)], width=4, colour=(180, 172, 158))
    draw(ik, CURATOR, Pose(hip=(960, 900), lean=0.0, hand_l=(830, 760), hand_r=(1090, 760),
                           eyes="open", brows="worried", mouth="wobble"), facing=1)
    ctx.key("which clock do you believe?", x=960, y=250, size=92, fill=INK, reveal=ctx.u(b + 0.6, b + 1.6))


# =====================================================================  9  ====
@scene
def whole_system(ctx):
    """The turn: stop asking one rock to be honest."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.04, ctx.pix)), (dur, Camera(960, 540, 1.18, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("9.1")
    for i in range(5):
        x = 340 + i * 310
        u = ctx.u(b + 0.5 + i * 0.45, b + 1.1 + i * 0.45)
        if u <= 0.01:
            continue
        ik.rrect(x - 150, 560, x + 150, 700, r=12, fill=(246, 240, 224, int(240 * u)),
                 outline=INK, width=4)
        P.zircon(ik, x, 660, s=0.62, glow=0.25)
        P.hourglass(ik, x + 76, 620, s=0.38, fill=clamp(0.75 - i * 0.12), t=ctx.t + i)
        age = ("4.4", "3.6", "2.7", "1.8", "0.9")[i]
        ik.text((x, 726), f"{age} billion", role="caps", size=36, fill=SLATE, anchor="ma")
    ik.line([(300, 790), (1620, 790)], width=6, colour=(120, 114, 104))
    for x in (300, 1620):
        ik.line([(x, 790), (x, 820)], width=6, colour=(120, 114, 104))
    ctx.note("minerals of different ages, each one its own clock", x=960, y=840, size=50, anchor="ma",
             fill=(104, 98, 90)) if ctx.t > b + 2.6 else None
    ctx.key("not one rock", x=960, y=270, size=96, fill=(150, 100, 70), reveal=ctx.u(b + 0.8, b + 1.8))
    ctx.key("the whole system", x=960, y=400, size=96, fill=SLATE, reveal=ctx.u(b + 2.8, b + 3.8))


@scene
def patterson_zircon(ctx):
    """1948: Patterson, a zircon, and lead that will not stay out."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(780, 580, 1.02, ctx.pix)), (dur, Camera(1040, 560, 1.22, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(202, 196, 180), floor=(146, 134, 116), y=890, dress=("rug", "shelf", "lamp"))
    P.lab_bench(ik, 960, 918, s=1.05, t=ctx.t)
    b = ctx.beat("9.2")
    draw(ik, PATTERSON, Pose(hip=(1240, 900), lean=-0.06, hand_l=(1020, 826), hand_r=(1130, 838),
                             eyes="look_down", brows="furrow", mouth="neutral", prop_l="shard"), facing=1)
    P.micro_scope(ik, 560, 918, s=1.0)
    ctx.key("1948", x=380, y=280, size=96, fill=SLATE, anchor="ma", reveal=ctx.u(b + 0.5, b + 1.3))
    ctx.key("his lead readings were always too high", x=1160, y=300, size=62, fill=TERRA,
            reveal=ctx.u(b + 4.0, b + 5.0))


@scene
def lead_everywhere(ctx):
    """Lead was not just in the sample. It was in the room, and in him."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.02, ctx.pix)), (dur, Camera(1120, 560, 1.24, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(204, 198, 184), floor=(150, 138, 120), y=890, dress=("rug", "shelf", "lamp", "plant"))
    P.lab_bench(ik, 700, 918, s=0.95, t=ctx.t)
    b = ctx.beat("9.3")
    for i in range(22):
        a = ctx.t * 0.3 + i * 1.7
        x = 400 + (i * 137) % 1300
        y = 300 + (i * 211) % 620
        ik.ellipse(x + math.sin(a) * 24 - 5, y + math.cos(a * 1.3) * 18 - 5,
                   x + math.sin(a) * 24 + 5, y + math.cos(a * 1.3) * 18 + 5, fill=(140, 136, 140, 190))
    draw(ik, PATTERSON, Pose(hip=(1180, 900), lean=-0.08, hand_l=(1000, 700), hand_r=(1090, 826),
                             eyes="wide", brows="raised", mouth="o"), facing=1)
    ctx.key("it was everywhere", x=1420, y=340, size=86, fill=TERRA, anchor="ma", reveal=ctx.u(b + 1.0, b + 2.0))
    for i, lab in enumerate(("dust", "water", "solder", "paint")):
        u = ctx.u(b + 2.6 + i * 0.5, b + 3.2 + i * 0.5)
        if u <= 0.01:
            continue
        ik.text((1420, 460 + i * 62), lab, role="label", size=46, fill=(110, 100, 92), anchor="ma")
    ctx.note("he even tested his own hair", x=1460, y=1030, size=46, anchor="ma", fill=(120, 112, 104)) \
        if ctx.t > b + 4.6 else None


@scene
def clean_room(ctx):
    """The clean room: sealing out the lead."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 580, 1.02, ctx.pix)), (dur, Camera(960, 540, 1.16, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("9.4")
    ik.rrect(240, 200, 1680, 900, r=18, fill=(226, 234, 238, 220), outline=(120, 134, 142), width=6)
    for i in range(7):
        ik.line([(300 + i * 200, 200), (300 + i * 200, 900)], width=2, colour=(180, 196, 204))
    ik.rrect(880, 420, 1040, 720, r=12, fill=(238, 244, 246, 230), outline=(130, 144, 152), width=4)
    ik.text((960, 560), "AIRLOCK", role="caps", size=34, fill=(110, 126, 134), anchor="mm")
    P.lab_bench(ik, 560, 880, s=0.85, t=ctx.t)
    draw(ik, PATTERSON, Pose(hip=(1210, 890), lean=-0.06, hand_l=(1040, 780), hand_r=(1140, 800),
                             eyes="look_down", brows="neutral", mouth="smile"), facing=1)
    ctx.key("acid washed · distilled · filtered", x=960, y=250, size=70, fill=SLATE, reveal=ctx.u(b + 1.0, b + 2.0))
    ctx.key("one of the first clean laboratories", x=960, y=960, size=62, fill=INK, anchor="ma",
            reveal=ctx.u(b + 3.4, b + 4.4))


@scene
def two_clocks(ctx):
    """Two decay chains, one rock: an internal cross-check."""
    dur = ctx.p("dur", 34)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.02, ctx.pix)), (dur, Camera(960, 540, 1.1, ctx.pix))])
    ik = ctx.ink
    b5, b6 = ctx.beat("9.5"), ctx.beat("9.6")
    P.hourglass(ik, 520, 545, s=1.4, fill=clamp(0.9 - ctx.u(b5, b5 + 10), 0.05, 0.9), t=ctx.t)
    P.hourglass(ik, 1080, 545, s=1.4, fill=clamp(0.55 - ctx.u(b5, b5 + 10), 0.05, 0.55), t=ctx.t + 0.6)
    for cx, left, right, y in ((520, "U-238", "Pb-206", 860), (1080, "U-235", "Pb-207", 860)):
        ik.text((cx - 96, y), left, role="caps", size=44, fill=INK, anchor="rm")
        ik.line([(cx - 86, y), (cx + 60, y)], width=5, colour=INK)
        ik.line([(cx + 60, y), (cx + 40, y - 12)], width=5, colour=INK)
        ik.text((cx + 68, y), right, role="caps", size=44, fill=INK, anchor="lm")
    ctx.note("half-life 4.5 billion years", x=520, y=936, size=44, anchor="ma", fill=(120, 112, 104))
    ctx.note("half-life 700 million years", x=1080, y=936, size=44, anchor="ma", fill=(120, 112, 104))
    for k in range(2):                        # sand falling at visibly different rates
        yy = 470 + ((ctx.t * (30 if k == 0 else 86) + k * 90) % 170)
        ik.ellipse(520 - 7, yy - 7, 520 + 7, yy + 7, fill=(230, 190, 110))
        ik.ellipse(1080 - 7, yy - 7, 1080 + 7, yy + 7, fill=(230, 190, 110))
    ik.line([(700, 700), (900, 700)], width=5, colour=(180, 172, 158))
    ik.text((800, 656), "different speeds", role="hand", size=52, fill=(120, 112, 104), anchor="mm")
    ik.rrect(1400, 430, 1840, 760, r=16, fill=(252, 249, 240, 235), outline=INK, width=4)
    P.meteorite(ik, 1620, 660, s=1.05)
    ik.text((1620, 486), "iron meteorite", role="caps", size=38, fill=SLATE, anchor="ma")
    ik.text((1620, 726), "the starting point", role="hand", size=46, fill=(120, 112, 104), anchor="ma")
    ctx.key("two clocks, one answer", x=960, y=250, size=86, fill=SLATE, reveal=ctx.u(b6 + 0.4, b6 + 1.4))


@scene
def meteorite(ctx):
    """Canyon Diablo: a piece of the early solar system."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(900, 600, 1.02, ctx.pix)), (dur, Camera(980, 560, 1.24, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(196, 188, 172), floor=(140, 128, 110), y=900, dress=("rug", "shelf"))
    b = ctx.beat("9.7")
    P.meteorite(ik, 980, 620, s=1.5)
    ik.rrect(300, 720, 700, 900, r=10, fill=(160, 128, 92), outline=(104, 80, 56), width=4)
    ik.text((500, 800), "ARIZONA", role="caps", size=38, fill=(240, 232, 208), anchor="mm")
    ik.text((500, 850), "Canyon Diablo", role="label", size=40, fill=(240, 232, 208), anchor="mm")
    draw(ik, PATTERSON, Pose(hip=(1420, 920), lean=-0.08, hand_l=(1200, 680), hand_r=(1310, 740),
                             eyes="open", brows="raised", mouth="smile"), facing=-1)
    ctx.key("never melted, never rained on", x=960, y=250, size=76, fill=INK, reveal=ctx.u(b + 1.4, b + 2.4))
    ctx.key("never recycled", x=960, y=350, size=76, fill=SLATE, reveal=ctx.u(b + 3.4, b + 4.2))


@scene
def spectrometer(ctx):
    """The instrument reads isotope ratios, not opinions."""
    dur = ctx.p("dur", 26)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.02, ctx.pix)), (dur, Camera(1000, 540, 1.14, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("9.8")
    ctx.room(wall=(196, 192, 180), floor=(140, 132, 118), y=900, dress=("rug", "lamp", "plant"))
    P.mass_spectrometer(ik, 820, 660, s=1.05, t=ctx.t)
    for i, (dx, h, col) in enumerate(((-90, 120, (120, 200, 220)), (-30, 200, (232, 176, 92)),
                                      (30, 160, (232, 176, 92)), (90, 80, (150, 190, 160)))):
        x = 1320 + dx
        ik.rrect(x - 16, 700 - h * (0.6 + 0.4 * math.sin(ctx.t * 2 + i) ** 2), x + 16, 700, r=4, fill=col,
                 outline=INK, width=3)
    ik.line([(1180, 700), (1480, 700)], width=4, colour=(120, 116, 110))
    ik.text((1330, 750), "Pb-207 / Pb-206", role="caps", size=34, fill=INK_SOFT, anchor="ma")
    draw(ik, PATTERSON, Pose(hip=(1700, 900), lean=-0.04, hand_l=(1500, 700), hand_r=(1620, 740),
                             eyes="open", brows="raised", mouth="open"), facing=-1)
    ctx.key("the ratio, not the heap", x=960, y=250, size=80, fill=SLATE, reveal=ctx.u(b + 0.6, b + 1.6))


@scene
def number_1956(ctx):
    """The number, published."""
    dur = ctx.p("dur", 26)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.14, ctx.pix)), (dur, Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("9.8")
    ik.rrect(240, 300, 1680, 800, r=20, fill=(252, 249, 240), outline=INK, width=4)
    ctx.key("4.55 billion years", x=960, y=450, size=124, fill=SLATE, reveal=ctx.u(b + 1.2, b + 2.2))
    ik.line([(660, 540), (1260, 540)], width=4, colour=(180, 172, 158))
    ctx.key("± 70 million", x=960, y=600, size=82, fill=TERRA, reveal=ctx.u(b + 2.8, b + 3.6))
    ctx.stamp("Patterson, 1956 — Earth, meteorite, solar system: the same event", 960, 730, size=40,
              fill=(116, 110, 102))


@scene
def modern_number(ctx):
    """The modern figure and its tiny error bar."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.04, ctx.pix)), (dur, Camera(960, 540, 1.12, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("9.9")
    ik.rrect(300, 300, 1620, 820, r=20, fill=(252, 249, 240), outline=INK, width=4)
    ctx.key("4.54 billion years", x=960, y=440, size=124, fill=SLATE, reveal=ctx.u(b + 1.0, b + 2.0))
    # a bar four billion years long with a visible 1% uncertainty
    ik.rrect(420, 620, 1500, 660, r=8, fill=(178, 190, 200), outline=INK, width=3)
    ik.rrect(982, 610, 1044, 670, r=6, fill=TERRA, outline=INK, width=3)
    ik.text((420, 690), "4 billion", role="caps", size=34, fill=INK_SOFT, anchor="la")
    ik.text((1500, 690), "5 billion", role="caps", size=34, fill=INK_SOFT, anchor="ra")
    ctx.key("an uncertainty of one percent", x=960, y=760, size=64, fill=INK, reveal=ctx.u(b + 3.0, b + 4.0))


@scene
def same_cloud(ctx):
    """We measured the sky because the Earth hides its own age."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.04, ctx.pix)), (dur, Camera(960, 520, 1.2, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(238, 230, 206))
    b = ctx.beat("9.10")
    P.planet(ik, 960, 640, r=250, kind="earth")
    lp.ellipse(840, 560, 1010, 700, fill=(120, 166, 108, 120))
    for i in range(26):
        a = (i * 2.399 + ctx.t * 0.06)
        r = 300 + (i * 37) % 420
        x, y = 960 + math.cos(a) * r, 540 + math.sin(a) * r * 0.55
        lp.ellipse(x - 3, y - 3, x + 3, y + 3, fill=(250, 246, 226, 200))
    ctx.leader(1210, 640, 1500, 700, "the Earth hides its own age", side="r", size=40, colour=(236, 228, 204))
    ctx.key("we measured the sky instead", x=960, y=200, size=88, fill=(240, 232, 206), reveal=ctx.u(b + 0.8, b + 1.8))
    ctx.key("rocks from the same cloud", x=960, y=980, size=76, fill=(228, 190, 130), anchor="ma",
            reveal=ctx.u(b + 3.4, b + 4.4))


# ====================================================================  10  ====
@scene
def epilogue_open(ctx):
    """Patterson's second act."""
    dur = ctx.p("dur", 24)
    cam = ctx.cam([(0.0, Camera(960, 580, 1.04, ctx.pix)), (dur, Camera(1040, 560, 1.16, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(200, 194, 180), floor=(144, 132, 114), y=890, dress=("rug", "shelf", "lamp"))
    P.lab_bench(ik, 900, 918, s=0.9, t=ctx.t)
    b = ctx.beat("10.1")
    draw(ik, PATTERSON_OLD, Pose(hip=(1200, 900), lean=-0.06, hand_l=(1020, 826), hand_r=(1120, 840),
                                 eyes="open", brows="raised", mouth="smile"), facing=1)
    ik.rrect(400, 640, 720, 830, r=10, fill=(196, 216, 226, 220), outline=INK, width=4)
    ik.text((560, 720), "SAMPLES", role="caps", size=38, fill=(70, 92, 104), anchor="mm")
    ik.text((560, 775), "ice  ·  water  ·  blood", role="caps", size=34, fill=(70, 92, 104), anchor="mm")
    ctx.key("an epilogue", x=960, y=250, size=92, fill=SLATE, reveal=ctx.u(b + 0.6, b + 1.4))


@scene
def ocean_lead(ctx):
    """Ocean water: a hundred times the natural background."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 600, 1.02, ctx.pix)), (dur, Camera(1000, 560, 1.16, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("10.2")
    ctx.ink.rrect(-120, -120, 2040, 560, r=0, fill=(196, 216, 228))
    ctx.ink.rrect(-120, 560, 2040, 1240, r=0, fill=(58, 96, 128))
    for i in range(5):
        ik.line([(0, 620 + i * 110), (1920, 600 + i * 110)], width=4, colour=(96, 138, 168))
    P.boat(ik, 700, 560, s=0.6, sail=False)
    ik.rrect(1180, 380, 1720, 760, r=14, fill=(252, 249, 240, 235), outline=INK, width=4)
    ik.line([(1240, 700), (1660, 700)], width=5, colour=(120, 114, 104))
    ik.rrect(1270, 640, 1330, 700, r=4, fill=(120, 160, 190), outline=INK, width=3)
    ik.text((1300, 730), "natural", role="caps", size=32, fill=INK_SOFT, anchor="ma")
    ik.rrect(1400, 420, 1460, 700, r=4, fill=TERRA, outline=INK, width=3)
    ik.text((1430, 380), "industrial", role="caps", size=32, fill=TERRA, anchor="ma")
    ik.text((1560, 560), "×100", role="display", size=76, fill=TERRA, anchor="mm")
    ctx.key("a hundred times the background", x=700, y=340, size=74, fill=(30, 60, 90), reveal=ctx.u(b + 2.0, b + 3.0))


@scene
def ice_core(ctx):
    """Greenland ice: lead rises when the petrol does."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(900, 560, 1.02, ctx.pix)), (dur, Camera(1010, 540, 1.14, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("10.2")
    ik.rrect(240, 300, 640, 940, r=14, fill=(222, 234, 240, 220), outline=(140, 168, 184), width=5)
    for i in range(16):
        ik.line([(260, 340 + i * 38), (620, 340 + i * 38)], width=3, colour=(176, 200, 212))
    ik.text((440, 248), "GREENLAND ICE CORE", role="caps", size=40, fill=SLATE, anchor="ma")
    # lead concentration rising after the 1920s
    ik.rrect(900, 320, 1780, 940, r=14, fill=(252, 249, 240, 235), outline=INK, width=4)
    ik.line([(960, 880), (1720, 880)], width=5, colour=(120, 114, 104))
    ik.line([(960, 880), (960, 400)], width=5, colour=(120, 114, 104))
    pts = [(960, 870)]
    for i in range(19):
        x = 960 + i * 40
        y = 870 - (20 + (i ** 1.8) * 0.55) if i > 8 else 870 - 20 - i * 1.5
        pts.append((x, y))
    u = ctx.u(b + 1.4, b + 4.4)
    cut = int(len(pts) * clamp(u))
    ik.line(pts[: max(2, cut)], width=6, colour=TERRA)
    ik.text((1040, 918), "1850", role="caps", size=34, fill=INK_SOFT, anchor="ma")
    ik.text((1380, 918), "1920s", role="caps", size=34, fill=INK_SOFT, anchor="ma")
    ik.text((1670, 918), "today", role="caps", size=34, fill=INK_SOFT, anchor="ma")
    ik.text((1340, 372), "lead in the ice", role="caps", size=34, fill=INK_SOFT, anchor="ma")
    ctx.key("lead rises with the petrol", x=1340, y=230, size=72, fill=TERRA, anchor="ma",
            reveal=ctx.u(b + 3.4, b + 4.4))


@scene
def products(ctx):
    """The contamination that broke the measurement was in everybody."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.02, ctx.pix)), (dur, Camera(960, 540, 1.06, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("10.3")
    items = (("petrol", (196, 112, 72)), ("paint", (150, 120, 172)), ("solder", (130, 140, 150)),
             ("food cans", (168, 152, 116)))
    for i, (lab, col) in enumerate(items):
        x = 380 + i * 390
        u = ctx.u(b + 0.6 + i * 0.6, b + 1.2 + i * 0.6)
        if u <= 0.01:
            continue
        ik.rrect(x - 160, 460, x + 160, 760, r=16, fill=(252, 249, 240, int(230 * u)), outline=INK, width=4)
        ik.rrect(x - 70, 520, x + 70, 660, r=12, fill=col, outline=INK, width=3)
        ik.text((x, 720), lab, role="caps", size=38, fill=INK_SOFT, anchor="ma")
    ctx.key("tetraethyl lead", x=960, y=280, size=92, fill=TERRA, reveal=ctx.u(b + 0.4, b + 1.4))
    ctx.key("in everybody's blood", x=960, y=930, size=76, fill=INK, reveal=ctx.u(b + 3.4, b + 4.4))


@scene
def blood_lead(ctx):
    """The consequence: lead removed, blood levels falling."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.02, ctx.pix)), (dur, Camera(990, 540, 1.12, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("10.4")
    ik.rrect(320, 300, 1600, 860, r=16, fill=(252, 249, 240, 235), outline=INK, width=4)
    ik.line([(400, 800), (1520, 800)], width=5, colour=(120, 114, 104))
    ik.line([(400, 800), (400, 380)], width=5, colour=(120, 114, 104))
    ik.rrect(430, 420, 560, 800, r=6, fill=(196, 104, 84), outline=INK, width=3)
    ik.text((495, 860), "1976", role="caps", size=34, fill=INK_SOFT, anchor="ma")
    u = ctx.u(b + 1.6, b + 3.6)
    ik.rrect(1220, 800 - 380 * 0.22 * u, 1350, 800, r=6, fill=(96, 148, 118), outline=INK, width=3)
    ik.text((1285, 860), "1990s", role="caps", size=34, fill=INK_SOFT, anchor="ma")
    ik.text((960, 360), "average blood lead, United States", role="label", size=42, fill=INK_SOFT, anchor="ma")
    ik.text((1120, 600), "≈ 80% lower", role="display", size=64, fill=(72, 116, 88), anchor="ma")
    ctx.key("lead out of petrol", x=960, y=230, size=84, fill=SLATE, reveal=ctx.u(b + 0.6, b + 1.6))


@scene
def four_clocks_table(ctx):
    """The four clocks, side by side, each with its assumption."""
    dur = ctx.p("dur", 40)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.0, ctx.pix)), (dur, Camera(960, 540, 1.06, ctx.pix))])
    ik = ctx.ink
    b5, b6 = ctx.beat("10.5"), ctx.beat("10.6")
    C = [("Ussher", "1650", "the record is complete", (196, 98, 63)),
         ("Kelvin", "1862", "nothing heats the inside", (46, 74, 107)),
         ("Rutherford", "1904", "the rock stays sealed", (216, 155, 60)),
         ("Patterson", "1956", "the system, not the sample", (110, 139, 75))]
    for i, (name, year, assume, col) in enumerate(C):
        x = 260 + i * 470
        u = ctx.u(b6 + 0.5 + i * 1.3, b6 + 1.3 + i * 1.3)
        if u <= 0.01:
            continue
        ik.rrect(x - 200, 380, x + 200, 900, r=16, fill=(252, 249, 240, int(235 * u)), outline=INK, width=4)
        ik.rrect(x - 200, 380, x + 200, 452, r=16, fill=col)
        ik.text((x, 398), name, role="display", size=44, fill=(252, 250, 244), anchor="ma")
        ik.text((x, 480), year, role="caps", size=40, fill=INK_SOFT, anchor="ma")
        if i == 0:
            P.scroll_paper(ik, x, 620, s=0.62, w=260, h=110, lines=4)
        elif i == 1:
            P.planet(ik, x, 620, r=54, kind="sun")
        elif i == 2:
            P.hourglass(ik, x, 620, s=0.5, fill=0.6, t=ctx.t)
        else:
            P.meteorite(ik, x, 620, s=0.62)
        ik.text((x, 790), "assumes", role="caps", size=30, fill=(140, 132, 122), anchor="ma")
        ik.text((x, 840), assume, role="label", size=36, fill=INK, anchor="ma")
    ctx.key("each one an assumption", x=960, y=240, size=88, fill=INK, reveal=ctx.u(b5 + 0.5, b5 + 1.5))
    ctx.note("four clocks, four different things taken on trust", x=960, y=992, size=46, anchor="ma",
             fill=(112, 106, 98)) if ctx.t > b6 + 5.6 else None


@scene
def assumptions(ctx):
    """Which parts of the record stayed closed — and which leaked."""
    dur = ctx.p("dur", 34)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.02, ctx.pix)), (dur, Camera(960, 540, 1.06, ctx.pix))])
    ik = ctx.ink
    b7, b8 = ctx.beat("10.7"), ctx.beat("10.8")
    P.hourglass(ik, 560, 600, s=1.05, fill=0.7, t=ctx.t)
    ik.rrect(1180, 420, 1780, 780, r=16, fill=(252, 249, 240, 230), outline=INK, width=4)
    ik.text((1480, 500), "closed", role="display", size=56, fill=(72, 116, 88), anchor="ma")
    ik.text((1480, 580), "leaking", role="display", size=56, fill=TERRA, anchor="ma")
    ik.line([(1250, 640), (1710, 640)], width=4, colour=(180, 172, 158))
    ik.text((1480, 690), "the same question, everywhere", role="label", size=40, fill=INK_SOFT, anchor="ma")
    ctx.key("none of them were stupid", x=960, y=240, size=86, fill=INK, reveal=ctx.u(b7 + 0.6, b7 + 1.6))
    if ctx.t > b8 + 0.6:
        ctx.key("which parts stayed closed?", x=960, y=980, size=72, fill=SLATE, anchor="ma",
                reveal=ctx.u(b8 + 0.8, b8 + 1.8))


@scene
def aging_question(ctx):
    """The open question this film hands back to the viewer."""
    dur = ctx.p("dur", 34)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.02, ctx.pix)), (dur, Camera(960, 540, 1.18, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(236, 226, 200))
    b = ctx.beat("10.9")
    # a figure with two arrows: a countdown and a repair process
    draw(ik, Character(name="You", hair="brown", hair_style="short", head="oval",
                       shirt=(96, 108, 126), trousers=(60, 64, 76), extras=(), kind="adult"),
         Pose(hip=(960, 900), lean=0.0, hand_l=(830, 780), hand_r=(1090, 780),
              eyes="open", brows="neutral", mouth="neutral"), facing=1)
    a = clamp(ctx.u(b + 1.0, b + 2.0))
    if a > 0.05:
        lp.line([(700 - 120 * a, 700), (700 - 120 * a, 380)], width=6, colour=(230, 176, 108))
        lp.poly([(700 - 120 * a, 360), (700 - 120 * a - 18, 396), (700 - 120 * a + 18, 396)], fill=(230, 176, 108))
        ik.text((700 - 120 * a, 330), "a clock", role="caps", size=38, fill=(236, 190, 130), anchor="ma")
    c = clamp(ctx.u(b + 3.0, b + 4.0))
    if c > 0.05:
        pts = []
        for i in range(30):
            ang = -1.6 + i / 29 * 4.6
            pts.append((1320 + math.cos(ang) * 120 * c, 520 + math.sin(ang) * 120 * c))
        lp.line(pts, width=6, colour=(140, 200, 220))
        lp.poly([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 26, pts[-1][1] - 10),
                 (pts[-1][0] - 10, pts[-1][1] + 24)], fill=(140, 200, 220))
        ik.text((1320, 330), "a repair", role="caps", size=38, fill=(150, 206, 226), anchor="ma")
    ctx.key("the clocks inside us", x=960, y=200, size=92, fill=(238, 232, 210), reveal=ctx.u(b + 0.5, b + 1.5))
    ctx.stamp("open question, not a settled answer", 960, 1010, size=40, fill=(198, 190, 176))


@scene
def end_card(ctx):
    """The last line and the credit card."""
    dur = ctx.p("dur", 40)
    cam = ctx.cam([(0.0, Camera(960, 600, 1.06, ctx.pix)), (dur, Camera(960, 520, 0.94, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(238, 230, 206))
    b = ctx.beat("10.10")
    # a shoreline of old rock, a figure looking up, moon and stars: quiet ending
    ctx.ink.rrect(-120, 760, 2040, 1240, r=0, fill=(34, 40, 58))
    lp.line([(0, 792), (420, 748), (900, 790), (1400, 742), (1920, 786)], width=6, colour=(58, 66, 86))
    P.moon(ik, 1560, 260, r=84)
    for i in range(40):
        a = (i * 2.399 + ctx.t * 0.05)
        r = 240 + (i * 53) % 900
        x, y = 960 + math.cos(a) * r, 420 + math.sin(a) * r * 0.4
        lp.ellipse(x - 3, y - 3, x + 3, y + 3, fill=(246, 242, 224, 200))
    draw(ik, Character(name="Keeper", hair="plum", hair_style="bun", head="oval",
                       shirt=(58, 66, 88), trousers=(42, 48, 62), extras=("coat",), kind="adult"),
         Pose(hip=(760, 900), lean=0.0, hand_l=(690, 780), hand_r=(830, 780), prop_r="sample",
              eyes="look_up", brows="raised", mouth="smile", face_dir=0.7), facing=1)
    u = clamp(ctx.u(b + 3.0, b + 5.5))
    if u > 0.02:
        ctx.key("they just keep time", x=960, y=560, size=104, fill=(238, 230, 206), reveal=u)
    if ctx.t > b + 6.0:
        ik.rrect(340, 300, 1580, 780, r=22, fill=(14, 18, 30, 248))
        ik.text((960, 410), "How Old Is the Earth?", role="display", size=96, fill=(248, 244, 232), anchor="ma")
        ik.text((960, 520), "Three clocks that had to be broken", role="label", size=52,
                fill=(232, 216, 184), anchor="ma")
        ik.text((960, 640), "written, drawn, animated and narrated by axiom", role="caps", size=42,
                fill=(214, 220, 232), anchor="ma")
        ik.text((960, 712), "sources listed in the film's release notes", role="caps", size=36,
                fill=(186, 194, 208), anchor="ma")
    ctx.fade_to((12, 15, 24), amount=clamp((ctx.t - (dur - 2.0)) / 1.8) * 0.55)
