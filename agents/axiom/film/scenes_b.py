#!/usr/bin/env python3
"""Scenes, chapters 5-7: Kelvin's cooling clock, the heat inside, Rutherford's hourglass."""
from __future__ import annotations

import math

from film import props as P
from film.cast import Character, Pose, draw
from film.cast_defs import CURATOR, KELVIN, PERRY, PLAYFAIR, RUTHERFORD
from film.scenes_a import REG, pale, scene
from film.style import (DEEP, INK, INK_SOFT, MOON, OCHRE, PLUM, ROSE, SLATE, SLATE_L,
                    STONE, TERRA, WHITE, Camera, Ink, clamp, ease_io, ease_out, pulse,
                    seg, smooth)


# =====================================================================  5  ====
@scene
def glasgow_board(ctx):
    """Kelvin at the board, 1862: a man who trusts the arithmetic."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(760, 560, 1.0, ctx.pix)), (dur, Camera(1120, 540, 1.14, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(196, 190, 176), floor=(140, 126, 106), y=880, window=(230, 500, 300, 330),
             dress=("rug", "shelf", "lamp"))
    P.chalkboard(ik, 980, 470, w=900, h=520, title="ON THE SECULAR COOLING OF THE EARTH",
                 writing=["dT/dt = k ∇²T", "", "heat lost = heat stored"], t=ctx.t)
    b1, b2 = ctx.beat("5.1"), ctx.beat("5.2")
    draw(ik, KELVIN, Pose(hip=(1360, 880), lean=-0.06, hand_l=(1180, 560), hand_r=(1300, 700),
                          eyes="open", brows="raised", mouth="open", prop_l="chalk"), facing=-1)
    ctx.key("1862", x=300, y=252, size=96, fill=SLATE, anchor="ma", reveal=ctx.u(b1 + 0.6, b1 + 1.4))
    ctx.note("heat moves through rock slowly", x=300, y=372, size=48, anchor="ma", fill=(104, 98, 90)) \
        if ctx.t > b2 + 0.6 else None
    ctx.note("William Thomson, later Lord Kelvin", x=1360, y=1022, size=46, anchor="ma", fill=(96, 92, 88)) \
        if ctx.t > b2 + 2.4 else None


@scene
def cooling_ball(ctx):
    """The cooling ball argument as a cutaway with escaping heat."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.0, ctx.pix)), (dur, Camera(960, 540, 1.22, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(238, 226, 200))
    b = ctx.beat("5.3")
    cx, cy, r = 760, 560, 230
    lp.ellipse(cx - r, cy - r, cx + r, cy + r, fill=(96, 54, 40), outline=(240, 226, 200), width=5)
    lp.ellipse(cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82, fill=(168, 80, 44))
    lp.ellipse(cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5, fill=(246, 186, 96))
    for i in range(10):
        a = i / 10 * 2 * math.pi + ctx.t * 0.12
        x0 = cx + math.cos(a) * (r + 16)
        y0 = cy + math.sin(a) * (r + 16)
        x1 = cx + math.cos(a) * (r + 16 + 34 + 16 * math.sin(ctx.t * 1.6 + i))
        y1 = cy + math.sin(a) * (r + 16 + 34 + 16 * math.sin(ctx.t * 1.6 + i))
        lp.line([(x0, y0), (x1, y1)], width=4, colour=(240, 190, 120, 220))
    ctx.leader(cx, cy - r - 40, cx - 300, cy - r - 140, "molten", side="l", size=38, colour=(238, 226, 200))
    ctx.leader(cx + r + 40, cy + 60, cx + 300, cy + 150, "heat into space", side="r", size=38, colour=(238, 226, 200))
    ctx.key("a cooling ball", x=1400, y=340, size=100, fill=(240, 230, 206), anchor="ma",
            reveal=ctx.u(b + 0.7, b + 1.7))
    ctx.key("measure the leak, count back", x=1400, y=470, size=62, fill=(226, 176, 110), anchor="ma",
            reveal=ctx.u(b + 3.4, b + 4.4))
    if ctx.t > b + 5.0:
        ctx.note("no heat source inside. none needed.", x=1400, y=580, size=48, anchor="ma", fill=(206, 198, 182))


@scene
def elegant_law(ctx):
    """One measurement, one law."""
    dur = ctx.p("dur", 26)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.04, ctx.pix)), (dur, Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("5.4")
    for i, (t, sub) in enumerate((("one measurement", "how much heat leaves today"),
                                 ("one law", "heat flows from hot to cold"),
                                 ("nothing but physics", "no scripture required"))):
        x = 380 + i * 580
        u = ctx.u(b + 0.5 + i * 0.9, b + 1.2 + i * 0.9)
        if u <= 0.01:
            continue
        ik.rrect(x - 250, 480, x + 250, 760, r=18, fill=(252, 249, 240, int(225 * u)), outline=INK, width=4)
        ik.text((x, 570), t, role="display", size=54, fill=INK, anchor="ma")
        ik.text((x, 650), sub, role="label", size=38, fill=INK_SOFT, anchor="ma")
    ctx.key("an elegant argument", x=960, y=280, size=84, fill=SLATE, reveal=ctx.u(b + 0.4, b + 1.2))


@scene
def measure_heat(ctx):
    """Measuring the leak: a borehole, a thermometer, an honest instrument."""
    dur = ctx.p("dur", 24)
    cam = ctx.cam([(0.0, Camera(700, 620, 1.0, ctx.pix)), (dur, Camera(900, 640, 1.2, ctx.pix))])
    ik = ctx.ink
    ctx.sky_ground(horizon=700, sky=(178, 198, 214), ground_col=(160, 146, 120))
    P.tunnel(ik, 820, 700, s=1.0, depth=380)
    b = ctx.beat("5.5")
    ik.line([(820, 720), (820, 1040)], width=4, colour=(120, 112, 100))
    ik.ellipse(796, 690, 844, 748, fill=(248, 246, 236), outline=INK, width=4)
    ik.line([(820, 720), (860, 700)], width=5, colour=TERRA)
    ctx.leader(880, 900, 1180, 960, "temperature rises with depth", side="r", size=42)
    ctx.key("measure the leak", x=1240, y=300, size=82, fill=SLATE, anchor="ma", reveal=ctx.u(b + 0.5, b + 1.3))
    draw(ik, Character(name="Driller", hair="brown", hair_style="short", head="round",
                       shirt=(126, 116, 96), trousers=(88, 80, 66), extras=("cap",), kind="adult"),
         Pose(hip=(480, 900), lean=0.1, hand_l=(700, 760), hand_r=(560, 700), prop_r="lantern",
              eyes="look_down", brows="raised", mouth="open"), facing=1)


@scene
def kelvin_number(ctx):
    """The number, then the tighter number."""
    dur = ctx.p("dur", 26)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.1, ctx.pix)), (dur, Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("5.5")
    ik.rrect(320, 300, 1600, 800, r=20, fill=(252, 249, 240), outline=INK, width=4)
    ctx.key("100 million years", x=960, y=440, size=110, fill=SLATE, reveal=ctx.u(b + 1.2, b + 2.2))
    ctx.key("then 20 – 40 million", x=960, y=620, size=96, fill=TERRA, reveal=ctx.u(b + 4.6, b + 5.6))
    ik.line([(640, 540), (1280, 540)], width=4, colour=(180, 172, 158))
    ctx.stamp("1862, and tighter later", 960, 742, size=40, fill=(120, 112, 102))


@scene
def sun_budget(ctx):
    """The same physics applied to the Sun shrinks every budget at once."""
    dur = ctx.p("dur", 26)
    cam = ctx.cam([(0.0, Camera(960, 520, 1.0, ctx.pix)), (dur, Camera(1080, 500, 1.16, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(246, 226, 170))
    b = ctx.beat("5.6")
    P.planet(ik, 700, 520, r=170, kind="sun")
    for i in range(12):
        a = i / 12 * 2 * math.pi + ctx.t * 0.3
        lp.line([(700 + math.cos(a) * 190, 520 + math.sin(a) * 190),
                 (700 + math.cos(a) * 250, 520 + math.sin(a) * 250)], width=5, colour=(240, 196, 110, 190))
    ctx.key("tens of millions of years", x=1420, y=420, size=82, fill=(244, 226, 176), anchor="ma",
            reveal=ctx.u(b + 0.7, b + 1.7))
    ctx.key("of sunlight, no more", x=1420, y=552, size=64, fill=(226, 190, 130), anchor="ma",
            reveal=ctx.u(b + 2.6, b + 3.6))
    if ctx.t > b + 4.0:
        ctx.note("the same reasoning, on a much bigger stage", x=1420, y=690, size=46, anchor="ma",
                 fill=(202, 196, 182))


@scene
def darwin_worry(ctx):
    """Darwin's problem: not enough time for slow selection."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(760, 560, 1.06, ctx.pix)), (dur, Camera(1000, 570, 1.24, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(206, 190, 166), floor=(150, 122, 92), y=860, window=(1660, 380, 240, 320),
             dress=("rug", "shelf", "plant"))
    P.table(ik, 900, 922, w=700, h=28, legs=170)
    P.chair(ik, 640, 962)
    for i in range(4):
        ik.rrect(700 + (i % 2) * 90, 852 - i * 14, 830 + (i % 2) * 90, 882 - i * 14, r=4,
                 fill=(246, 240, 224), outline=(160, 150, 130), width=3)
    b = ctx.beat("5.7")
    draw(ik, Character(name="Naturalist 19c", hair="grey", hair_style="greyside", head="tall",
                       shirt=(56, 54, 60), trousers=(48, 46, 52), extras=("coat", "beard", "cravat"), kind="elder"),
         Pose(hip=(1080, 900), lean=-0.05, hand_l=(990, 826), hand_r=(1150, 816),
              eyes="worried" if False else "open", brows="worried", mouth="frown", prop_r="quill"), facing=-1)
    ctx.key("not enough time", x=1180, y=290, size=86, fill=TERRA, anchor="ma", reveal=ctx.u(b + 0.8, b + 1.7))
    ctx.note("for slow selection to work with", x=1180, y=400, size=46, anchor="ma", fill=(120, 112, 104)) \
        if ctx.t > b + 2.6 else None


@scene
def kelvin_honest(ctx):
    """Fair to Kelvin: right physics, wrong planet."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.04, ctx.pix)), (dur, Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("5.8")
    ctx.panel(560, 600, 720, 420, title="RIGHT", accent=(74, 116, 88))
    ctx.panel(1360, 600, 720, 420, title="WRONG", accent=TERRA)
    ik.text((560, 640), "the physics", role="display", size=68, fill=(60, 84, 66), anchor="ma")
    ik.text((1360, 640), "the planet", role="display", size=68, fill=(140, 74, 50), anchor="ma")
    for i, lab in enumerate(("thermodynamics", "conductivity", "arithmetic")):
        ik.text((560, 730 + i * 56), lab, role="label", size=40, fill=(80, 96, 84), anchor="ma")
    for i, lab in enumerate(("no heat inside", "no motion", "one closed system")):
        ik.text((1360, 730 + i * 56), lab, role="label", size=40, fill=(140, 96, 76), anchor="ma")
    draw(ik, KELVIN, Pose(hip=(960, 990), lean=0.0, hand_l=(830, 900), hand_r=(1090, 900),
                          eyes="open", brows="neutral", mouth="neutral"), facing=1)
    ctx.key("he did what we ask scientists to do", x=960, y=250, size=74, fill=INK,
            reveal=ctx.u(b + 0.7, b + 1.6))


# =====================================================================  6  ====
@scene
def perry_office(ctx):
    """Perry: a former assistant who saw the flaw."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(820, 560, 1.0, ctx.pix)), (dur, Camera(1080, 560, 1.2, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(198, 190, 174), floor=(142, 126, 104), y=880, dress=("rug", "shelf", "plant"))
    P.table(ik, 940, 918, w=760, h=28, legs=170)
    P.scroll_paper(ik, 900, 862, s=0.9, w=520, h=140, lines=5)
    b1, b2 = ctx.beat("6.1"), ctx.beat("6.2")
    draw(ik, PERRY, Pose(hip=(1160, 902), lean=-0.08, hand_l=(980, 822), hand_r=(1090, 836),
                         eyes="open", brows="raised", mouth="open", prop_l="quill"), facing=1)
    ctx.key("1895", x=380, y=300, size=96, fill=SLATE, anchor="ma", reveal=ctx.u(b1 + 0.6, b1 + 1.3))
    ctx.note("a cooling ball is a poor model of a planet", x=960, y=300, size=52, anchor="ma",
             fill=(86, 82, 78)) if ctx.t > b2 + 0.8 else None


@scene
def convection(ctx):
    """Convection: the moving interior Kelvin's equation could not see."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.04, ctx.pix)), (dur, Camera(960, 540, 1.2, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(232, 224, 204))
    b = ctx.beat("6.3")
    cx, cy, r = 780, 540, 250
    lp.ellipse(cx - r, cy - r, cx + r, cy + r, fill=(84, 56, 46), outline=(236, 226, 206), width=5)
    lp.ellipse(cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86, fill=(178, 92, 52))
    for k in range(3):
        rr = r * (0.72 - k * 0.19)
        pts = []
        for i in range(48):
            a = i / 47 * 1.75 * math.pi + ctx.t * (0.5 + k * 0.12)
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.92))
        lp.line(pts, width=6, colour=(250, 208, 150, 220))
        a_end = 1.75 * math.pi + ctx.t * (0.5 + k * 0.12)
        ex, ey = cx + math.cos(a_end) * rr, cy + math.sin(a_end) * rr * 0.92
        ang = math.atan2(ey - cy, ex - cx) + math.pi / 2
        lp.poly([(ex + math.cos(ang) * 16, ey + math.sin(ang) * 16),
                 (ex + math.cos(ang + 2.4) * 20, ey + math.sin(ang + 2.4) * 20),
                 (ex + math.cos(ang - 2.4) * 20, ey + math.sin(ang - 2.4) * 20)], fill=(250, 208, 150))
    ctx.key("convection", x=1440, y=380, size=110, fill=(240, 230, 206), anchor="ma",
            reveal=ctx.u(b + 0.6, b + 1.6))
    ctx.key("not conduction", x=1440, y=500, size=64, fill=(226, 170, 104), anchor="ma",
            reveal=ctx.u(b + 2.6, b + 3.4))
    if ctx.t > b + 4.0:
        ctx.note("heat rides the rock that moves", x=1440, y=610, size=46, anchor="ma", fill=(206, 198, 182))


@scene
def perry_number(ctx):
    """Perry's number, a century early."""
    dur = ctx.p("dur", 26)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.12, ctx.pix)), (dur, Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("6.4")
    ctx.key("in 1895", x=960, y=262, size=78, fill=TERRA, reveal=ctx.u(b + 0.4, b + 1.2))
    ik.rrect(300, 340, 1620, 820, r=20, fill=(252, 249, 240), outline=INK, width=4)
    ctx.key("2 – 3 billion years", x=960, y=500, size=112, fill=SLATE, reveal=ctx.u(b + 0.8, b + 1.9))
    ctx.stamp("from fluid dynamics, not from doctrine", 960, 700, size=42, fill=(112, 106, 96))
    # the convective cell that made the difference, drawn small beside the number
    cx, cy, r = 700, 940, 62
    ik.ellipse(cx - r, cy - r, cx + r, cy + r, fill=(246, 214, 150), outline=INK, width=4)
    for k in range(3):
        a = ctx.t * 0.9 + k * 2.1
        ik.line([(cx + math.cos(a) * (r - 22), cy + math.sin(a) * (r - 22)),
                 (cx + math.cos(a + 0.9) * (r - 22), cy + math.sin(a + 0.9) * (r - 22))],
                width=4, colour=(176, 116, 52))
    ik.line([(cx + r + 10, cy), (cx + r + 70, cy)], width=4, colour=(176, 116, 52))
    ctx.note("heat that moves beats heat that conducts", x=1120, y=930, size=46, anchor="lm",
             fill=(104, 98, 90))


@scene
def forgotten_paper(ctx):
    """The neglected paper: read, filed, forgotten."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.06, ctx.pix)), (dur, Camera(1180, 580, 1.24, ctx.pix))])
    ik = ctx.ink
    ctx.room(wall=(188, 178, 160), floor=(128, 114, 94), y=890, dress=("rug", "lamp"),
             clock=(1700, 330, 76))
    for s in range(3):
        x = 560 + s * 420
        ik.rrect(x - 190, 360, x + 190, 880, r=10, fill=(150, 118, 84), outline=(96, 74, 52), width=4)
        for l in range(3):
            ik.line([(x - 190, 430 + l * 170), (x + 190, 430 + l * 170)], width=6, colour=(122, 94, 66))
    ik.rrect(700, 470, 800, 546, r=4, fill=(240, 232, 208), outline=(160, 148, 124), width=3)
    ik.rrect(760, 486, 860, 562, r=4, fill=(232, 224, 200), outline=(160, 148, 124), width=3)
    b = ctx.beat("6.5")
    for i in range(7):
        a = (ctx.t * 0.4 + i * 0.9)
        ik.ellipse(810 + math.cos(a) * 30, 300 + math.sin(a * 1.3) * 20,
                   816 + math.cos(a) * 30, 306 + math.sin(a * 1.3) * 20, fill=(190, 184, 170, 160))
    draw(ik, CURATOR, Pose(hip=(1620, 900), lean=0.04, hand_l=(1440, 700), hand_r=(1520, 780),
                           eyes="closed", brows="neutral", mouth="flat"), facing=-1)
    ctx.key("read, filed, forgotten", x=960, y=250, size=88, fill=(110, 104, 96), reveal=ctx.u(b + 0.8, b + 1.8))
    ctx.note("rediscovered by other scientists in 2007", x=960, y=1020, size=42, anchor="ma",
             fill=(140, 132, 122)) if ctx.t > b + 3.0 else None


@scene
def becquerel_drawer(ctx):
    """1896: a drawer, a plate, and a discovery nobody ordered."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(760, 620, 1.0, ctx.pix)), (dur, Camera(980, 640, 1.28, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(226, 214, 180))
    b = ctx.beat("6.6")
    ctx.ink.rrect(-120, -120, 2040, 900, r=0, fill=(38, 42, 58))
    ctx.ink.rrect(-120, 900, 2040, 1240, r=0, fill=(60, 54, 48))
    P.table(ik, 900, 900, w=820, h=30, legs=120, top=(112, 92, 70), dark=(84, 68, 52))
    ik.rrect(560, 760, 1240, 860, r=6, fill=(146, 124, 98), outline=(92, 76, 58), width=5)
    glow = pulse(ctx.t, 2.6, 1.4)
    lp.ellipse(700, 700, 850, 790, fill=(120 + 90 * glow, 190 + 40 * glow, 170, 200))
    lp.rrect(860, 690, 1150, 800, r=6, fill=(236, 230, 224), outline=(150, 144, 138), width=4)
    ctx.leader(790, 780, 700, 940, "uranium salts", side="l", size=42, colour=(232, 222, 196))
    ctx.leader(1020, 700, 1150, 470, "fogged plate", side="r", size=42, colour=(232, 222, 196))
    ctx.key("no sunlight", x=1470, y=250, size=96, fill=(240, 232, 206), anchor="ma",
            reveal=ctx.u(b + 1.6, b + 2.6))
    ctx.key("still a mark", x=1470, y=380, size=72, fill=(226, 176, 110), anchor="ma",
            reveal=ctx.u(b + 3.2, b + 4.0))
    draw(ik, Character(name="Becquerel", hair="ink", hair_style="short", head="oval",
                       shirt=(52, 56, 72), trousers=(46, 48, 58), extras=("coat", "moustache"), kind="adult"),
         Pose(hip=(1500, 900), lean=-0.06, hand_l=(1240, 760), hand_r=(1330, 700),
              eyes="wide", brows="raised", mouth="open", face_dir=-0.5), facing=-1)


@scene
def radioactive_rock(ctx):
    """The rock has been keeping its own heat, all along."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.06, ctx.pix)), (dur, Camera(960, 540, 1.24, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(244, 214, 160))
    b = ctx.beat("6.7")
    P.zircon(ik, 820, 560, s=1.9, glow=0.6 + 0.4 * math.sin(ctx.t * 2.2))
    for i in range(14):
        a = i / 14 * 2 * math.pi
        rr = 120 + ((ctx.t * 90 + i * 30) % 220)
        x = 820 + math.cos(a) * rr
        y = 560 + math.sin(a) * rr * 0.8
        lp.ellipse(x - 6, y - 6, x + 6, y + 6, fill=(250, 226, 160, 210))
    ctx.leader(880, 500, 1180, 400, "alpha particles become helium", side="r", size=38, colour=(238, 226, 196))
    ctx.key("radioactive", x=1420, y=560, size=104, fill=(246, 226, 170), anchor="ma",
            reveal=ctx.u(b + 0.6, b + 1.6))
    ctx.key("all along", x=1420, y=690, size=88, fill=(230, 176, 104), anchor="ma",
            reveal=ctx.u(b + 2.4, b + 3.2))


@scene
def heat_correction(ctx):
    """The honest correction: it was convection, not radioactivity, that broke Kelvin."""
    dur = ctx.p("dur", 34)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.0, ctx.pix)), (dur, Camera(960, 540, 1.04, ctx.pix))])
    ik = ctx.ink
    b8, b9 = ctx.beat("6.8"), ctx.beat("6.9")
    ctx.panel(520, 620, 760, 460, title="THE STANDARD STORY", accent=(150, 112, 84))
    ctx.panel(1400, 620, 760, 460, title="WHAT ACTUALLY BREAKS IT", accent=(74, 116, 88))
    ik.text((520, 600), "add radioactive heat", role="label", size=44, fill=(110, 96, 84), anchor="ma")
    ik.text((520, 670), "still a young Earth", role="display", size=56, fill=(150, 100, 70), anchor="ma")
    ik.line([(410, 664), (368, 664)], width=6, colour=(150, 100, 70))
    ik.line([(410, 664), (392, 652)], width=6, colour=(150, 100, 70))
    ik.text((1400, 600), "the interior flows", role="label", size=44, fill=(84, 100, 88), anchor="ma")
    ik.text((1400, 670), "the equation fails", role="display", size=56, fill=(60, 96, 74), anchor="ma")
    ik.line([(1290, 664), (1248, 664)], width=6, colour=(60, 96, 74))
    ik.line([(1290, 664), (1272, 652)], width=6, colour=(60, 96, 74))
    P.hourglass(ik, 520, 860, s=0.5, fill=0.10, t=ctx.t)
    P.planet(ik, 1400, 860, r=64, kind="earth")
    ctx.key("a correction", x=960, y=250, size=92, fill=TERRA, reveal=ctx.u(b8 + 0.6, b8 + 1.5))
    ctx.key("convection, not radioactivity", x=960, y=370, size=74, fill=SLATE, reveal=ctx.u(b9 + 0.6, b9 + 1.6))


@scene
def new_clock(ctx):
    """The prize: a clock of their own."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 600, 1.0, ctx.pix)), (dur, Camera(960, 540, 1.24, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(244, 230, 186))
    b = ctx.beat("6.10")
    P.hourglass(ik, 960, 560, s=1.5, fill=clamp(1.0 - ctx.u(b + 2.0, b + 12.0), 0.02, 1.0),
                sand=(250, 206, 118), t=ctx.t)
    for i in range(10):
        a = i / 10 * 2 * math.pi + ctx.t * 0.6
        r = 320 + 40 * math.sin(ctx.t + i)
        lp.line([(960 + math.cos(a) * r, 560 + math.sin(a) * r * 0.7),
                 (960 + math.cos(a + 0.35) * r, 560 + math.sin(a + 0.35) * r * 0.7)],
                width=4, colour=(240, 220, 160, 170))
    ctx.key("a clock of their own", x=960, y=180, size=96, fill=(240, 230, 200), reveal=ctx.u(b + 0.7, b + 1.7))


# =====================================================================  7  ====
@scene
def royal_institution(ctx):
    """London, 1904: Rutherford at the lectern."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(700, 600, 1.0, ctx.pix)), (dur, Camera(1000, 560, 1.18, ctx.pix))])
    ik = ctx.ink
    ctx.ink.rrect(-120, -120, 2040, 760, r=0, fill=(64, 58, 62))
    ctx.ink.rrect(-120, 760, 2040, 1240, r=0, fill=(96, 78, 62))
    for i in range(5):
        ik.rrect(120 + i * 380, 470, 420 + i * 380, 760, r=10, fill=(78, 70, 74), outline=(52, 48, 52), width=3)
        ik.ellipse(200 + i * 380, 500, 260 + i * 380, 560, fill=(180, 172, 166))
        ik.ellipse(300 + i * 380, 500, 360 + i * 380, 560, fill=(170, 162, 156))
    ik.rrect(840, 640, 1240, 700, r=10, fill=(120, 96, 72), outline=INK, width=4)
    ik.rrect(900, 700, 1180, 780, r=8, fill=(104, 82, 62), outline=INK, width=4)
    b = ctx.beat("7.1")
    draw(ik, RUTHERFORD, Pose(hip=(1040, 700), lean=-0.04, hand_l=(900, 560), hand_r=(1160, 540),
                              eyes="open", brows="raised", mouth="open"), facing=-1)
    ik.rrect(1230, 560, 1330, 640, r=8, fill=(232, 236, 240), outline=INK, width=3)
    ik.ellipse(1250, 590, 1310, 630, fill=(150, 196, 176, 180), outline=INK, width=2.4)
    ctx.key("Royal Institution, 1904", x=960, y=250, size=80, fill=(240, 232, 210), reveal=ctx.u(b + 0.6, b + 1.6))
    ctx.note("Ernest Rutherford, arriving with an answer", x=960, y=350, size=46, anchor="ma",
             fill=(206, 198, 182)) if ctx.t > b + 2.6 else None


@scene
def decay_steadfast(ctx):
    """Half-life: the fraction flips, whatever you do to the atoms."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.05, ctx.pix)), (dur, Camera(960, 540, 1.18, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(236, 224, 190))
    b = ctx.beat("7.2")
    for i in range(16):
        col = i % 2
        x = 320 + (i % 8) * 170
        y = 460 + (i // 8) * 200
        u = clamp((ctx.t - b - i * 0.16) / 0.5)
        lp.ellipse(x - 26, y - 26, x + 26, y + 26, fill=(240, 210, 170) if col == 0 else (170, 200, 214),
                   outline=(250, 240, 210), width=3)
        lp.text((x, y), "U" if col == 0 else "Pb", role="caps", size=30,
                fill=(30, 30, 40) if col == 0 else (30, 30, 40), anchor="mm")
    ctx.key("heat them, freeze them, bury them", x=960, y=250, size=70, fill=(238, 228, 200),
            reveal=ctx.u(b + 1.2, b + 2.2))
    ctx.key("the same fraction, the same time", x=960, y=880, size=74, fill=(226, 182, 116),
            reveal=ctx.u(b + 4.0, b + 5.0))


@scene
def good_clock(ctx):
    """What makes a clock good: indifference, and a sealed room."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.04, ctx.pix)), (dur, Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("7.3")
    ctx.room(wall=(204, 196, 182), floor=(146, 128, 106), y=880)
    P.wall_clock(ik, 700, 420, r=110, t=ctx.t)
    ik.rrect(1240, 340, 1600, 700, r=14, fill=(226, 232, 236, 200), outline=INK, width=4)
    P.hourglass(ik, 1420, 520, s=0.7, fill=1.0 - (ctx.t % 12) / 14.0, t=ctx.t)
    ik.line([(1240, 700), (1600, 700)], width=6, colour=(120, 130, 138))
    ctx.key("it runs whether or not anyone watches", x=960, y=250, size=74, fill=INK,
            reveal=ctx.u(b + 0.7, b + 1.7))
    ctx.note("and it does not care what happens to the room", x=960, y=960, size=48, anchor="ma",
             fill=(104, 100, 94)) if ctx.t > b + 3.2 else None


@scene
def rutherford_sample(ctx):
    """Five hundred million years, held in one hand."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(900, 560, 1.04, ctx.pix)), (dur, Camera(1060, 540, 1.3, ctx.pix))])
    ik = ctx.ink
    ctx.ink.rrect(-120, -120, 2040, 780, r=0, fill=(70, 62, 64))
    ctx.ink.rrect(-120, 780, 2040, 1240, r=0, fill=(96, 78, 62))
    b = ctx.beat("7.4")
    draw(ik, RUTHERFORD, Pose(hip=(1140, 880), lean=-0.05, hand_l=(900, 620), hand_r=(1230, 780),
                              eyes="open", brows="raised", mouth="open", prop_l="sample"), facing=-1)
    P.hourglass(ik, 520, 620, s=0.8, fill=0.35, t=ctx.t)
    ctx.key("500 million years", x=960, y=250, size=104, fill=(240, 232, 208), reveal=ctx.u(b + 1.0, b + 2.0))
    ctx.note("measured from helium and lead inside a mineral", x=960, y=1000, size=46, anchor="ma",
             fill=(208, 200, 184)) if ctx.t > b + 3.0 else None


@scene
def kelvin_asleep(ctx):
    """Rutherford's own anecdote, played as the story it is."""
    dur = ctx.p("dur", 34)
    cam = ctx.cam([(0.0, Camera(760, 600, 1.05, ctx.pix)), (dur, Camera(1000, 580, 1.22, ctx.pix))])
    ik = ctx.ink
    ctx.ink.rrect(-120, -120, 2040, 760, r=0, fill=(60, 54, 58))
    ctx.ink.rrect(-120, 760, 2040, 1240, r=0, fill=(92, 74, 58))
    b5, b6 = ctx.beat("7.5"), ctx.beat("7.6")
    u_open = ctx.u(b6 + 0.2, b6 + 1.2)
    eyes = "closed" if u_open < 0.5 else "side"
    brows = "neutral" if u_open < 0.5 else "one_up"
    P.bench(ik, 700, 760, w=520, h=26, legs=90)
    draw(ik, KELVIN, Pose(hip=(700, 700), lean=-0.36, head_tilt=0.24, hand_l=(640, 700), hand_r=(770, 690),
                          eyes=eyes, brows=brows, mouth="flat" if u_open < 0.5 else "smirk"), facing=-1, shadow=False)
    for i in range(3):
        r = 8 + i * 5
        ik.ellipse(790 + i * 26, 520 - i * 22, 790 + i * 26 + r * 2, 520 - i * 22 + r * 2,
                   outline=(230, 226, 214), width=3)
    draw(ik, RUTHERFORD, Pose(hip=(1420, 880), lean=-0.03, hand_l=(1200, 620), hand_r=(1300, 700),
                              eyes="wide", brows="worried", mouth="open", head_tilt=0.06), facing=-1)
    ctx.key("asleep in the front row", x=700, y=250, size=78, fill=(238, 230, 208), anchor="ma",
            reveal=ctx.u(b5 + 1.2, b5 + 2.2))
    if ctx.t > b6 + 1.0:
        ctx.key("one eye, baleful", x=1420, y=320, size=76, fill=(232, 172, 110), anchor="ma",
                reveal=ctx.u(b6 + 1.2, b6 + 2.0))
    ctx.stamp("Rutherford's own account, told years later", 960, 1010, size=38, fill=(206, 198, 182))


@scene
def escape_line(ctx):
    """The proviso: 'provided no new source of energy was discovered'."""
    dur = ctx.p("dur", 30)
    cam = ctx.cam([(0.0, Camera(900, 560, 1.06, ctx.pix)), (dur, Camera(1000, 540, 1.16, ctx.pix))])
    ik = ctx.ink
    ctx.ink.rrect(-120, -120, 2040, 760, r=0, fill=(64, 58, 62))
    ctx.ink.rrect(-120, 760, 2040, 1240, r=0, fill=(96, 78, 62))
    b = ctx.beat("7.7")
    draw(ik, RUTHERFORD, Pose(hip=(760, 880), lean=0.02, hand_l=(940, 620), hand_r=(600, 660),
                              eyes="open", brows="raised", mouth="grin"), facing=-1)
    ctx.key("provided no new source", x=1180, y=480, size=84, fill=(244, 236, 214), anchor="ma",
            reveal=ctx.u(b + 0.8, b + 1.8))
    ctx.key("was discovered", x=1180, y=600, size=72, fill=(232, 186, 118), anchor="ma",
            reveal=ctx.u(b + 2.0, b + 2.8))
    if ctx.t > b + 3.2:
        ctx.key("this evening: radium", x=1180, y=760, size=76, fill=(250, 226, 160), anchor="ma",
                reveal=ctx.u(b + 3.4, b + 4.2))


@scene
def footnote(ctx):
    """Honesty about the anecdote."""
    dur = ctx.p("dur", 26)
    cam = ctx.cam([(0.0, Camera(960, 540, 1.06, ctx.pix)), (dur, Camera(960, 540, 1.0, ctx.pix))])
    ik = ctx.ink
    b = ctx.beat("7.8")
    ctx.panel(960, 560, 1180, 460, title="FOOTNOTE", accent=SLATE)
    ik.text((960, 590), "a good anecdote, not a transcript", role="display", size=62, fill=INK, anchor="ma")
    ik.text((960, 690), "the measurement and the idea are the solid parts", role="label", size=44,
            fill=INK_SOFT, anchor="ma")
    ctx.key("worth keeping honest", x=960, y=196, size=78, fill=SLATE, reveal=ctx.u(b + 0.8, b + 1.6))


@scene
def hourglass_start(ctx):
    """Lock a radioactive element in a crystal: the hourglass starts."""
    dur = ctx.p("dur", 28)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.06, ctx.pix)), (dur, Camera(960, 540, 1.22, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(244, 232, 190))
    b = ctx.beat("7.9")
    P.zircon(ik, 640, 600, s=1.5, glow=0.4)
    ik.line([(760, 600), (900, 600)], width=5, colour=(230, 200, 140))
    P.hourglass(ik, 1080, 600, s=1.0, fill=clamp(1.0 - ctx.u(b + 2.0, b + 12.0), 0.05, 1.0),
                sand=(250, 210, 120), t=ctx.t, label="U to Pb")
    ctx.key("lock it in a crystal", x=960, y=250, size=88, fill=(242, 232, 202), reveal=ctx.u(b + 0.8, b + 1.8))
    ctx.key("and it starts running", x=960, y=930, size=80, fill=(228, 184, 118), anchor="ma",
            reveal=ctx.u(b + 3.0, b + 4.0))


@scene
def seal_crack(ctx):
    """The condition: the hourglass has to stay sealed."""
    dur = ctx.p("dur", 34)
    cam = ctx.cam([(0.0, Camera(960, 560, 1.08, ctx.pix)), (dur, Camera(1000, 560, 1.3, ctx.pix))])
    ik, lp = ctx.ink, pale(ctx, colour=(244, 224, 190))
    b = ctx.beat("7.10")
    P.hourglass(ik, 900, 560, s=1.5, fill=0.62, sand=(246, 202, 118), t=ctx.t)
    u = ctx.u(b + 1.6, b + 2.8)
    if u > 0.02:
        # a crack and sand escaping sideways
        lp.line([(1000, 560), (1046, 596), (1010, 636)], width=5, colour=(250, 170, 120))
        for i in range(9):
            ph = (ctx.t * 1.2 + i * 0.14) % 1.0
            lp.ellipse(1040 + ph * 190, 600 + ph * ph * 190, 1048 + ph * 190, 608 + ph * ph * 190,
                       fill=(250, 210, 130, int(220 * (1 - ph))))
    ctx.key("if it stays sealed", x=960, y=250, size=96, fill=(244, 232, 204), reveal=ctx.u(b + 0.8, b + 1.8))
    if ctx.t > b + 3.0:
        ctx.key("a rock is not a sealed glass", x=960, y=940, size=76, fill=(238, 150, 116), anchor="ma",
                reveal=ctx.u(b + 3.2, b + 4.2))
