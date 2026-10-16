#!/usr/bin/env python3
"""axiom stage — scene framework: backgrounds, camera, keyword typography, diagrams.

A scene is a function(ctx) that draws one instant of one shot. Contexts expose:
  ctx.ink / ctx.img / ctx.t (seconds inside the shot) / ctx.p (shot params)
  ctx.cam(keys)          camera path for this shot
  ctx.bg_paper(palette)  background: parchment / cool paper / workshop tints
  ctx.bg_night()         night sky
  ctx.key(text, ...)     selective keyword type (never the whole narration)
  ctx.chapter_card(...)  chapter question card
  ctx.note(text, ...)    handwritten annotation
  ctx.panel(...)         framed diagram panel
Drawing order is explicit: background first, then world, then overlays in screen space.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFilter

from film import props as P
from film.style import (Camera, DEEP, INK, INK_SOFT, MOSS, NIGHT, OCHRE, PAPER,
                    PAPER_COOL, PAPER_WARM, PLUM, SLATE, SLATE_L, TERRA, WHITE,
                    Ink, cam_path, clamp, ease_io, ease_out, font, grain, measure,
                    night_bg, paper_bg, pulse, seg, smooth, wrap)

BG = {
    "parchment": dict(base=PAPER, tint=(250, 236, 206), vignette=0.06),
    "cool": dict(base=PAPER_COOL, tint=(214, 224, 232), vignette=0.05),
    "workshop": dict(base=(238, 228, 208), tint=(226, 208, 178), vignette=0.07),
    "field": dict(base=(234, 238, 226), tint=(198, 220, 190), vignette=0.05),
    "chapel": dict(base=(232, 226, 214), tint=(206, 196, 186), vignette=0.08),
    "ash": dict(base=(232, 228, 224), tint=(200, 196, 194), vignette=0.08),
    "night": dict(base=(26, 30, 46), tint=(20, 24, 40), vignette=0.10),
    "deep": dict(base=(30, 34, 52), tint=(18, 22, 38), vignette=0.10),
}


@dataclass
class Stage:
    pix: float
    bg: str = "parchment"
    t: float = 0.0
    shot: dict = field(default_factory=dict)
    W: int = 1920
    H: int = 1080
    _cam: Camera | None = None

    def __post_init__(self):
        if self.bg in ("night", "deep"):
            self.img = night_bg(self.W, self.H, seed=hash(self.shot.get("id", "x")) % 999)
        else:
            cfg = BG.get(self.bg, BG["parchment"])
            self.img = paper_bg(self.W, self.H, **cfg)
        self.WW, self.HH = 1920.0, 1080.0        # world (design) size, independent of render scale
        self.cam_ = Camera(pix=self.pix)
        self.ink = Ink(self.img, self.cam_, width=5.0)

    # ---------------------------------------------------------- camera ----
    def cam(self, keys=None):
        if keys:
            self.cam_ = cam_path(self.t, keys)
            self.ink.cam = self.cam_
        return self.cam_

    @property
    def c(self):
        return self.cam_

    def p(self, key, default=None):
        return self.shot.get("params", {}).get(key, default)

    def u(self, t0, t1):
        return seg(self.t, t0, t1)

    # ------------------------------------------------------------ beats ----
    def beat(self, cue_id, default=0.0):
        """Local time (s) inside this shot at which the given narration cue starts."""
        c = self.shot.get("cues", {}).get(cue_id)
        return c["at"] if c else default

    def beat_end(self, cue_id, default=None):
        c = self.shot.get("cues", {}).get(cue_id)
        if not c:
            return default if default is not None else self.p("dur", 20.0)
        return c["end"]

    def beat_u(self, cue_id, lead=0.6, span=0.8):
        """Reveal helper: 0->1 over `span` seconds, starting `lead` seconds after the cue."""
        t0 = self.beat(cue_id) + lead
        return seg(self.t, t0, t0 + span)

    # ------------------------------------------------------ background ----
    def ground(self, y=880, col=(206, 196, 172), line=True):
        self.ink.rrect(-120, y, self.WW + 120, self.HH + 120, r=0, fill=col)
        if line:
            self.ink.line([(-120, y), (self.WW + 120, y)], width=4, colour=(160, 150, 130))

    def floor_grid(self, y=860, col=(180, 172, 154)):
        self.ground(y, col=col)
        for i in range(-3, 8):
            x = 960 + i * 260
            self.ink.line([(x, y), (x + i * 40, self.HH + 40)], width=2.6, colour=(196, 188, 170))

    def room(self, wall=(214, 206, 190), floor=(186, 166, 138), y=800, window=None, clock=None,
             dress=("rug", "shelf", "lamp", "plant")):
        self.ink.rrect(-120, -120, self.WW + 120, y, r=0, fill=wall)
        self.ink.rrect(-120, y, self.WW + 120, self.HH + 120, r=0, fill=floor)
        for item in dress:
            if item == "rug":
                P.rug(self.ink, 960, y + 168, w=780, h=92)
            elif item == "shelf":
                P.bookshelf(self.ink, 240, y + 24, w=360, h=300)
            elif item == "lamp":
                P.lamp(self.ink, 1720, y + 30, s=1.0)
            elif item == "plant":
                P.plant(self.ink, 1500, y + 30, s=0.9)
            elif item == "stool":
                P.stool(self.ink, 1750, y + 40)
        if window:
            x, yy, w, h = window
            P.window_view(self.ink, x, yy, w=w, h=h)
        if clock:
            P.wall_clock(self.ink, clock[0], clock[1], r=clock[2] if len(clock) > 2 else 78, t=self.t)

    def sky_ground(self, horizon=760, sky=(178, 206, 226), ground_col=(150, 168, 116)):
        self.ink.rrect(-120, -120, self.WW + 120, horizon, r=0, fill=sky)
        self.ink.rrect(-120, horizon, self.WW + 120, self.HH + 120, r=0, fill=ground_col)

    # ----------------------------------------------------------- type ----
    def key(self, text, x=960, y=170, size=None, role="display", fill=INK, anchor="ma",
            reveal=None, underline=False, chip=False, chip_col=None, max_w=None):
        """Selective keyword type. Reveals with a small hand-drawn-ish pop."""
        u = 1.0 if reveal is None else clamp(reveal)
        if u <= 0.01:
            return
        size = size or self.p("size", 92)
        grow = 1.0 + (1 - ease_out(u)) * 0.14
        old = self.cam_.zoom
        self.cam_.zoom = old * grow
        if chip:
            f = font(role, int(round(size * self.pix * old * grow)))
            w = f.getlength(text)
            self.ink.rrect(x - w / 2 / (self.pix * old * grow) - 34, y - size * 0.78,
                           x + w / 2 / (self.pix * old * grow) + 34, y + size * 0.44, r=18,
                           fill=chip_col or (255, 249, 232, 235), outline=INK, width=3)
        self.ink.text((x, y), text, role=role, size=size, fill=fill, anchor=anchor)
        if underline:
            f = font(role, int(round(size * self.pix)))
            w = f.getlength(text) / self.pix
            y0 = y + size * 0.30
            pts = []
            n = 9
            for i in range(n + 1):
                ux = -w / 2 + w * i / n
                pts.append((x + ux, y0 + math.sin(i * 1.7) * 3.5))
            self.ink.line(pts, width=5.0, colour=fill)
        self.cam_.zoom = old
        self.ink.cam = self.cam_

    def key_wrapped(self, text, x=960, y=140, size=78, role="display", fill=INK, max_w=1300,
                    anchor="ma", line_gap=1.12):
        lines = wrap(text, role, int(round(size * self.pix)), max_w * self.pix)
        for i, line in enumerate(lines):
            self.ink.text((x, y + i * size * line_gap), line, role=role, size=size, fill=fill, anchor=anchor)

    def chapter_card(self, number, question, t_in, dur=6.0, accent=TERRA, sub=None):
        """Chapter title card: number, question, thin rule. Held or exiting."""
        u = clamp(t_in / 0.55)
        if t_in > dur - 0.5:
            u = 1.0 - clamp((t_in - (dur - 0.5)) / 0.5)
            u = ease_out(u)
        else:
            u = ease_out(u)
        if u <= 0.02:
            return
        scrim = int(120 * u)
        self.ink.rrect(-120, -120, 2040, 1240, r=0, fill=(28, 30, 40, scrim))
        self.ink.rrect(150, 250, 1770, 830, r=28, fill=(255, 252, 244, int(242 * u)), outline=(0, 0, 0, 0))
        self.ink.rrect(150, 250, 1770, 830, r=28, outline=INK, width=3.4, fill=None)
        self.ink.line([(200 - 200 * (1 - u), 336), (560 - 200 * (1 - u), 336)], width=6, colour=accent)
        self.ink.text((200, 292), f"CHAPTER {number}", role="caps", size=44, fill=accent)
        size = 92 if len(question) < 42 else 78
        self.key_wrapped(question, x=960, y=460, size=size, role="display", max_w=1420, anchor="ma")
        if sub:
            self.ink.text((960, 720), sub, role="label", size=44, fill=INK_SOFT, anchor="ma")

    def note(self, text, x, y, size=44, anchor="la", fill=(70, 66, 62), arrow_to=None):
        self.ink.text((x, y), text, role="hand", size=size, fill=fill, anchor=anchor)
        if arrow_to:
            P.arrow(self.ink, x + (60 if anchor == "la" else -60), y - 10, arrow_to[0], arrow_to[1],
                    w=4, colour=fill, head=16)

    def stamp(self, text, x, y, size=38, fill=SLATE, anchor="mm", rotate=0.0):
        self.ink.text((x, y), text, role="caps", size=size, fill=fill, anchor=anchor)

    def panel(self, x, y, w, h, title=None, fill=(252, 249, 240, 235), accent=SLATE):
        self.ink.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, r=16, fill=fill, outline=INK, width=4)
        if title:
            self.ink.rrect(x - w / 2, y - h / 2, x - w / 2 + min(w, 460), y - h / 2 + 62, r=16, fill=accent)
            self.ink.text((x - w / 2 + 22, y - h / 2 + 10), title, role="caps", size=38, fill=(250, 248, 240))

    def leader(self, x0, y0, x1, y1, label, side="r", size=34, colour=INK_SOFT):
        self.ink.line([(x0, y0), (x1, y1)], width=3, colour=colour)
        r = 6
        self.ink.ellipse(x0 - r, y0 - r, x0 + r, y0 + r, fill=colour)
        self.ink.text((x1 + (14 if side == "r" else -14), y1 - size * 0.5), label, role="caps",
                      size=size, fill=colour, anchor="la" if side == "r" else "ra")

    def vignette_text_bar(self, y=980, h=90, alpha=90):
        self.ink.rrect(-10, y, self.WW + 10, y + h, r=0, fill=(20, 20, 26, alpha))

    # ------------------------------------------------------- overlays ----
    def sun_spot(self, x, y, r=520, alpha=70):
        lay = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.ellipse([(x - r) * self.pix, (y - r) * self.pix, (x + r) * self.pix, (y + r) * self.pix],
                  fill=(255, 240, 200, alpha))
        lay = lay.filter(ImageFilter.GaussianBlur(60 * self.pix))
        self.img.alpha = None
        self.img.paste(Image.alpha_composite(self.img.convert("RGBA"), lay).convert("RGB"), (0, 0))

    def fade_to(self, colour=(20, 20, 26), amount=0.0):
        if amount <= 0:
            return
        lay = Image.new("RGB", self.img.size, colour)
        self.img = Image.blend(self.img, lay, clamp(amount))
        self.ink.img = self.img
        self.ink.d = ImageDraw.Draw(self.img, "RGBA")

    def finish(self):
        return self.img
