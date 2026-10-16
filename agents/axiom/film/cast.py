#!/usr/bin/env python3
"""axiom cast — a small poseable character rig with face shapes, hair, costumes and props.

World units: 1920x1080 design space, y down. A character at scale 1.0 is ~300 units tall
(about 28% of frame height). Limbs use two-bone IK so hands/feet always stay attached.

Everything is drawn with the shared style.Ink wrapper; nothing is pre-rendered or traced.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from film.style import (HAIR, INK, INK_SOFT, SKIN, WHITE, font, Ink)

# ------------------------------------------------------------- rig metrics ---
HEAD_RX, HEAD_RY = 55.0, 60.0
NECK = 12.0
TORSO = 92.0
SHOULDER_W = 46.0
HIP_W = 34.0
UPPER_ARM, LOWER_ARM = 48.0, 46.0
THIGH, SHIN = 58.0, 56.0
LIMB_W = 7.5
OUTLINE = 5.0


@dataclass
class Character:
    name: str = "figure"
    scale: float = 1.0
    skin: tuple = SKIN
    hair: str = "brown"            # key of HAIR or an (r,g,b) tuple
    hair_style: str = "short"
    head: str = "oval"             # oval | round | square | tall | wide
    shirt: tuple = (46, 74, 107)
    trousers: tuple = (40, 44, 58)
    shoes: tuple | None = None
    kind: str = "adult"            # adult | child | elder
    extras: tuple = ()             # glasses, beard, moustache, hat, cap, collar, cravat,
                                   # ruff, coat, apron, sash, wig17, wig19, mortarboard,
                                   # goggles, badge, tie, gloves, hairbun
    tint: float = 1.0              # multiply-ish light adjustment for depth


@dataclass
class Pose:
    hip: tuple = (960.0, 760.0)
    lean: float = 0.0              # torso lean, radians (positive = leaning right)
    head_tilt: float = 0.0
    head_off: tuple = (0.0, 0.0)
    hand_l: tuple | None = None    # world target for left hand (viewer left)
    hand_r: tuple | None = None
    elbow_bend_l: float = 1.0      # +1 / -1 elbow direction
    elbow_bend_r: float = -1.0
    foot_l: tuple | None = None
    foot_r: tuple | None = None
    knee_bend_l: float = 1.0
    knee_bend_r: float = 1.0
    eyes: str = "open"
    brows: str = "neutral"
    mouth: str = "neutral"
    face_dir: float = 0.0          # -1 (looking viewer-left) .. +1
    blush: bool = False
    look: tuple = (0.0, 0.0)
    prop_l: str | None = None      # prop ids the hands are holding (drawn by props.py)
    prop_r: str | None = None


# ------------------------------------------------------------------- maths ---
def _rot(px, py, cx, cy, a):
    ca, sa = math.cos(a), math.sin(a)
    dx, dy = px - cx, py - cy
    return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)


def ik2(root, target, l1, l2, bend=1.0):
    """Two-bone IK: returns (joint, end). Bends toward `bend` side of root->target."""
    rx, ry = root
    tx, ty = target
    dx, dy = tx - rx, ty - ry
    dist = math.hypot(dx, dy) or 1e-6
    dist = min(dist, (l1 + l2) * 0.999)
    base = math.atan2(dy, dx)
    cos_a = max(-1.0, min(1.0, (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)))
    a = math.acos(cos_a)
    ang = base + a * bend
    joint = (rx + l1 * math.cos(ang), ry + l1 * math.sin(ang))
    ux, uy = tx - joint[0], ty - joint[1]
    d = math.hypot(ux, uy) or 1e-6
    end = (joint[0] + ux * min(1.0, l2 / d), joint[1] + uy * min(1.0, l2 / d))
    return joint, end


def skeleton(ch: Character, p: Pose, hands=None, feet=None):
    """Compute world-space joints for a character in a pose."""
    s = ch.scale
    hands = hands or {}
    feet = feet or {}
    hip = p.hip
    # torso axis
    sx = hip[0] + math.sin(p.lean) * TORSO * s
    sy = hip[1] - math.cos(p.lean) * TORSO * s
    shoulder_l = (sx - math.cos(p.lean) * SHOULDER_W * s, sy + math.sin(p.lean) * SHOULDER_W * s)
    shoulder_r = (sx + math.cos(p.lean) * SHOULDER_W * s, sy - math.sin(p.lean) * SHOULDER_W * s)
    head_c = (sx + p.head_off[0] * s, sy - (NECK + HEAD_RY) * s + p.head_off[1] * s)
    hx, hy = head_c
    head_c = _rot(hx + HEAD_RX * s * 0.10, hy, sx, sy - (NECK + HEAD_RY) * s, p.head_tilt)

    hand_l_target = p.hand_l if p.hand_l is not None else (hip[0] - 58 * s, hip[1] - 30 * s)
    hand_r_target = p.hand_r if p.hand_r is not None else (hip[0] + 58 * s, hip[1] - 30 * s)
    el_l, hand_l = ik2(shoulder_l, hand_l_target, UPPER_ARM * s, LOWER_ARM * s, p.elbow_bend_l)
    el_r, hand_r = ik2(shoulder_r, hand_r_target, UPPER_ARM * s, LOWER_ARM * s, p.elbow_bend_r)

    foot_l_target = p.foot_l if p.foot_l is not None else (hip[0] - 34 * s, hip[1] + (THIGH + SHIN) * s)
    foot_r_target = p.foot_r if p.foot_r is not None else (hip[0] + 34 * s, hip[1] + (THIGH + SHIN) * s)
    knee_l, foot_l = ik2(hip, foot_l_target, THIGH * s, SHIN * s, p.knee_bend_l)
    knee_r, foot_r = ik2(hip, foot_r_target, THIGH * s, SHIN * s, p.knee_bend_r)

    return {
        "hip": hip, "shoulder_c": (sx, sy), "shoulder_l": shoulder_l, "shoulder_r": shoulder_r,
        "head": head_c, "elbow_l": el_l, "elbow_r": el_r, "hand_l": hand_l, "hand_r": hand_r,
        "knee_l": knee_l, "knee_r": knee_r, "foot_l": foot_l, "foot_r": foot_r,
    }


# -------------------------------------------------------------------- face ---
def _eyes(ink: Ink, cx, cy, s, p: Pose, hair_col):
    """Eyes and brows: the main acting channel. Big enough to read at 1/4 frame size."""
    dx = p.face_dir * 7 * s
    ex, ey = 21 * s, -1 * s
    lx, ly = cx - ex + dx, cy + ey
    rx, ry = cx + ex + dx, cy + ey
    e, w = p.eyes, 4.2 * s
    LR = 10.0 * s
    if e in ("open", "look_up", "look_down", "side", "wide", "squint", "focused"):
        r = LR * (1.05 if e == "wide" else 1.0)
        for (x, y) in ((lx, ly), (rx, ry)):
            ink.ellipse(x - r, y - r * 1.05, x + r, y + r * 1.05, fill=WHITE, outline=INK, width=3.0 * s)
        lk = p.look
        if e == "look_up":
            lk = (0.2, -1)
        elif e == "look_down":
            lk = (0.0, 1)
        elif e == "side":
            lk = (0.6 * (1 if p.face_dir >= 0 else -1), 0.1)
        elif e == "focused":
            lk = (0.0, 0.2)
        for (x, y) in ((lx, ly), (rx, ry)):
            px, py = x + lk[0] * 4.6 * s, y + lk[1] * 4.6 * s
            pr = 4.9 * s * (0.86 if e == "wide" else 1.0)
            ink.ellipse(px - pr, py - pr * 1.08, px + pr, py + pr * 1.08, fill=INK)
            ink.ellipse(px - pr * 1.7, py - pr * 2.2, px - pr * 0.3, py - pr * 0.7, fill=WHITE)
        if e == "squint":
            for (x, y) in ((lx, ly), (rx, ry)):
                ink.line([(x - r, y - r * 1.05), (x + r, y - r * 1.15)], width=2.6 * s, colour=INK)
    elif e == "happy":
        for (x, y) in ((lx, ly), (rx, ry)):
            ink.line([(x - 11 * s, y + 4 * s), (x - 2 * s, y - 4 * s), (x + 11 * s, y + 4 * s)],
                     width=w, colour=INK)
    elif e == "closed":
        for (x, y) in ((lx, ly), (rx, ry)):
            ink.line([(x - 11 * s, y), (x + 3 * s, y + 3 * s), (x + 11 * s, y)], width=w * 0.9, colour=INK)
    elif e == "sad":
        for (x, y) in ((lx, ly), (rx, ry)):
            ink.line([(x - 11 * s, y - 4 * s), (x + 11 * s, y + 5 * s)], width=w, colour=INK)
    elif e == "cross":
        for (x, y) in ((lx, ly), (rx, ry)):
            ink.line([(x - 8 * s, y - 8 * s), (x + 8 * s, y + 8 * s)], width=w, colour=INK)
            ink.line([(x + 8 * s, y - 8 * s), (x - 8 * s, y + 8 * s)], width=w, colour=INK)
    elif e == "spiral":
        for (x, y) in ((lx, ly), (rx, ry)):
            pts = []
            for i in range(26):
                a = i / 26 * 3.6 * math.pi
                rr = (1.4 + i / 26 * 8.4) * s
                pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
            ink.line(pts, width=3.0 * s, colour=INK)
    elif e == "sparkle":
        for (x, y) in ((lx, ly), (rx, ry)):
            for (a, b) in ((-11, 0), (11, 0), (0, -11), (0, 11)):
                ink.line([(x + a * 0.35, y + b * 0.35), (x + a, y + b)], width=w * 0.9, colour=INK)

    bx, by = cx, cy - 27 * s
    b = p.brows
    span = 17 * s
    def brow(x, inner_dy, outer_dy, wdt=6.2, lift=0.0):
        ink.line([(x - span, by + outer_dy * s - lift), (x + span, by + inner_dy * s - lift)],
                 width=wdt * s, colour=hair_col)
    if b == "neutral":
        brow(lx, 0, 0); brow(rx, 0, 0)
    elif b == "raised":
        brow(lx, -3, -4, 5.6, 9 * s); brow(rx, 3, 4, 5.6, 9 * s)
    elif b == "one_up":
        brow(lx, 0, 0); brow(rx, -2, -3, 6.0, 11 * s)
    elif b == "angry":
        brow(lx, -9, 4, 6.6); brow(rx, 9, -4, 6.6)
    elif b == "worried":
        brow(lx, 8, -5, 5.8); brow(rx, -8, 5, 5.8)
    elif b == "flat":
        brow(lx, 0, 0, 5.2); brow(rx, 0, 0, 5.2)
    elif b == "furrow":
        brow(lx, -6, 3, 6.4, 3 * s); brow(rx, 6, -3, 6.4, 3 * s)
    elif b == "quizzical":
        brow(lx, -4, -2, 5.8, 5 * s); brow(rx, 2, 0, 5.8)


def _mouth(ink: Ink, cx, cy, s, p: Pose, dy: float = 0.0):
    m = p.mouth
    my = cy + 34 * s + dy
    w = 4.4 * s
    if m == "neutral":
        ink.line([(cx - 13 * s, my), (cx + 13 * s, my)], width=w, colour=INK)
    elif m == "smile":
        ink.line([(cx - 18 * s, my - 5 * s), (cx - 5 * s, my + 5 * s), (cx + 12 * s, my - 7 * s)],
                 width=w, colour=INK)
    elif m == "grin":
        ink.poly([(cx - 20 * s, my - 6 * s), (cx + 20 * s, my - 6 * s), (cx + 14 * s, my + 12 * s),
                  (cx - 12 * s, my + 12 * s)], fill=(120, 54, 58), outline=INK, width=3 * s)
        ink.poly([(cx - 16 * s, my - 5 * s), (cx + 16 * s, my - 5 * s), (cx + 13 * s, my + 2 * s),
                  (cx - 12 * s, my + 2 * s)], fill=WHITE)
    elif m == "open":
        ink.ellipse(cx - 13 * s, my - 10 * s, cx + 13 * s, my + 18 * s, fill=(120, 54, 58),
                    outline=INK, width=3.4 * s)
    elif m == "o":
        ink.ellipse(cx - 9 * s, my - 9 * s, cx + 9 * s, my + 12 * s, fill=(120, 54, 58),
                    outline=INK, width=3.4 * s)
    elif m == "gasp":
        ink.ellipse(cx - 14 * s, my - 14 * s, cx + 14 * s, my + 20 * s, fill=(120, 54, 58),
                    outline=INK, width=3.8 * s)
    elif m == "frown":
        ink.line([(cx - 16 * s, my + 6 * s), (cx, my - 4 * s), (cx + 16 * s, my + 6 * s)],
                 width=w, colour=INK)
    elif m == "flat":
        ink.line([(cx - 12 * s, my), (cx + 12 * s, my)], width=w + 1.4 * s, colour=INK)
    elif m == "wobble":
        ink.line([(cx - 16 * s, my), (cx - 6 * s, my - 5 * s), (cx + 3 * s, my + 5 * s), (cx + 15 * s, my - 3 * s)],
                 width=w, colour=INK)
    elif m == "smirk":
        ink.line([(cx - 14 * s, my + 4 * s), (cx + 5 * s, my - 3 * s), (cx + 16 * s, my - 8 * s)],
                 width=w, colour=INK)
    elif m == "tongue":
        ink.line([(cx - 14 * s, my - 3 * s), (cx + 14 * s, my - 3 * s)], width=w, colour=INK)
        ink.ellipse(cx - 7 * s, my - 1 * s, cx + 8 * s, my + 13 * s, fill=(196, 110, 120),
                    outline=INK, width=2.4 * s)
    elif m == "bite":
        ink.line([(cx - 17 * s, my), (cx + 17 * s, my)], width=w + 2.4 * s, colour=INK)
        ink.line([(cx - 14 * s, my + 3 * s), (cx + 14 * s, my + 3 * s)], width=1.8 * s, colour=WHITE)


def _head_shape(ink: Ink, cx, cy, s, ch: Character):
    """Head with a chin and a hint of jaw; sized for legibility at small scale."""
    rx, ry = HEAD_RX * s, HEAD_RY * s
    if ch.head == "round":
        ink.ellipse(cx - rx * 1.02, cy - ry * 0.98, cx + rx * 1.02, cy + ry * 0.96, fill=ch.skin,
                    outline=INK, width=OUTLINE * s)
        return
    if ch.head == "square":
        ink.rrect(cx - rx * 0.96, cy - ry * 0.9, cx + rx * 0.96, cy + ry * 1.0, r=26 * s,
                  fill=ch.skin, outline=INK, width=OUTLINE * 0.9 * s)
        return
    if ch.head == "tall":
        ry *= 1.10
    elif ch.head == "wide":
        rx *= 1.10
        ry *= 0.95
    ink.ellipse(cx - rx, cy - ry, cx + rx, cy + ry * 0.92, fill=ch.skin, outline=INK, width=OUTLINE * s)
    # jaw / chin
    ink.poly([(cx - rx * 0.66, cy + ry * 0.62), (cx + rx * 0.66, cy + ry * 0.62),
              (cx + rx * 0.42, cy + ry * 1.06), (cx - rx * 0.42, cy + ry * 1.06)],
             fill=ch.skin)
    ink.line([(cx - rx * 0.66, cy + ry * 0.60), (cx - rx * 0.44, cy + ry * 1.05),
              (cx + rx * 0.44, cy + ry * 1.05), (cx + rx * 0.66, cy + ry * 0.60)],
             width=OUTLINE * s, colour=INK)


def _hair(ink: Ink, cx, cy, s, ch: Character, style, col, back=True):
    """Hair frames the face: a mass behind, a cap over the top third in front."""
    rx, ry = HEAD_RX * s, HEAD_RY * s
    st = style
    if st == "none":
        return
    if back:
        if st in ("bob", "long", "wig17", "wig19", "curly"):
            drop = {"bob": ry * 0.55 + 18 * s, "long": ry * 1.15 + 34 * s,
                    "wig17": ry * 0.95 + 26 * s, "wig19": ry * 0.85 + 22 * s, "curly": ry * 0.35 + 12 * s}[st]
            ink.ellipse(cx - rx - 9 * s, cy - ry - 12 * s, cx + rx + 9 * s, cy + ry * 0.5, fill=col)
            ink.rrect(cx - rx - 9 * s, cy - ry * 0.7, cx + rx + 9 * s, cy + drop, r=32 * s,
                      fill=col, outline=INK, width=3.6 * s)
        elif st == "bun":
            ink.ellipse(cx - 17 * s, cy - ry - 22 * s, cx + 17 * s, cy - ry + 12 * s,
                        fill=col, outline=INK, width=3.6 * s)
        elif st == "ponytail":
            ink.poly([(cx + rx * 0.45, cy - ry * 0.6), (cx + rx + 30 * s, cy - ry * 0.1),
                      (cx + rx + 38 * s, cy + 30 * s), (cx + rx * 0.3, cy + 8 * s)],
                     fill=col, outline=INK)
        elif st == "greyside":
            ink.poly([(cx - rx * 0.98, cy - ry * 0.5), (cx - rx - 12 * s, cy + ry * 0.5),
                      (cx - rx * 0.1, cy - ry * 0.1)], fill=col)
            ink.poly([(cx + rx * 0.98, cy - ry * 0.5), (cx + rx + 12 * s, cy + ry * 0.5),
                      (cx + rx * 0.1, cy - ry * 0.1)], fill=col)
        return
    # front hair: covers the crown, dips toward the temples, never over the eyes
    if st == "greyside":
        return
    if st in ("wig17", "wig19"):
        top = cy - ry * 1.02
        ink.poly([(cx - rx * 1.0, cy - ry * 0.60), (cx - rx * 0.9, cy - ry * 0.88),
                  (cx, top - 10 * s), (cx + rx * 0.9, cy - ry * 0.88),
                  (cx + rx * 1.0, cy - ry * 0.58), (cx + rx * 0.7, cy - ry * 0.76),
                  (cx, cy - ry * 0.86), (cx - rx * 0.7, cy - ry * 0.76)], fill=col)
        ink.line([(cx - rx * 1.0, cy - ry * 0.60), (cx - rx * 0.9, cy - ry * 0.88),
                  (cx, top - 10 * s), (cx + rx * 0.9, cy - ry * 0.88),
                  (cx + rx * 1.0, cy - ry * 0.58)], width=3.6 * s, colour=INK)
        return
    top = cy - ry * 1.04
    pts = [(cx - rx * 1.04, cy - ry * 0.52), (cx - rx * 0.94, cy - ry * 0.88),
           (cx - rx * 0.34, top - 6 * s), (cx + rx * 0.42, top - 7 * s),
           (cx + rx * 0.95, cy - ry * 0.86), (cx + rx * 1.04, cy - ry * 0.50),
           (cx + rx * 0.74, cy - ry * 0.58), (cx + rx * 0.26, cy - ry * 0.74),
           (cx - rx * 0.34, cy - ry * 0.70), (cx - rx * 0.80, cy - ry * 0.58)]
    ink.poly(pts, fill=col)
    ink.line(pts[:6], width=4 * s, colour=INK)
    if st == "swept":
        ink.poly([(cx - rx * 0.24, top - 8 * s), (cx + rx * 1.02, cy - ry * 0.72),
                  (cx + rx * 1.16, cy - ry * 0.34), (cx + rx * 0.22, cy - ry * 0.78)],
                 fill=col, outline=INK)
    if st in ("bun", "ponytail", "bob", "long", "curly", "wig17", "wig19"):
        # soft fringe over the brow line, short enough to keep the eyes clear
        ink.poly([(cx - rx * 1.0, cy - ry * 0.56), (cx - rx * 0.5, cy - ry * 0.80),
                  (cx + rx * 0.5, cy - ry * 0.80), (cx + rx * 1.0, cy - ry * 0.56),
                  (cx + rx * 0.8, cy - ry * 0.68), (cx - rx * 0.8, cy - ry * 0.68)], fill=col)


# ------------------------------------------------------------------- props ---
def _prop_in_hand(ink: Ink, prop, x, y, s, colour=INK):
    """Very small hand props drawn at the hand position."""
    if prop == "quill":
        ink.line([(x - 4 * s, y - 18 * s), (x + 12 * s, y - 44 * s)], width=3.2 * s, colour=INK)
        ink.poly([(x + 8 * s, y - 34 * s), (x + 18 * s, y - 50 * s), (x + 12 * s, y - 46 * s)], fill=WHITE, outline=INK)
    elif prop == "chalk":
        ink.line([(x - 8 * s, y - 3 * s), (x + 12 * s, y - 8 * s)], width=8 * s, colour=WHITE)
    elif prop == "pointer":
        ink.line([(x - 10 * s, y + 8 * s), (x + 74 * s, y - 58 * s)], width=4.6 * s, colour=(140, 96, 60))
    elif prop == "magnifier":
        ink.ellipse(x + 4 * s, y - 34 * s, x + 44 * s, y + 6 * s, outline=INK, width=5 * s)
        ink.line([(x - 2 * s, y + 8 * s), (x + 12 * s, y - 6 * s)], width=5.4 * s)
    elif prop == "book":
        ink.poly([(x - 40 * s, y - 14 * s), (x + 40 * s, y - 14 * s), (x + 40 * s, y + 30 * s),
                  (x - 40 * s, y + 30 * s)], fill=(216, 199, 160), outline=INK, width=4 * s)
    elif prop == "flask":
        ink.poly([(x - 12 * s, y - 40 * s), (x + 12 * s, y - 40 * s), (x + 4 * s, y - 14 * s),
                  (x + 18 * s, y + 20 * s), (x - 18 * s, y + 20 * s), (x - 4 * s, y - 14 * s)],
                 fill=(214, 232, 236), outline=INK, width=4 * s)
    elif prop == "sample":
        ink.poly([(x - 16 * s, y - 16 * s), (x + 17 * s, y - 9 * s), (x + 10 * s, y + 18 * s),
                  (x - 14 * s, y + 13 * s)], fill=(66, 62, 72), outline=INK, width=4 * s)
    elif prop == "hammer":
        ink.line([(x - 6 * s, y + 12 * s), (x + 26 * s, y - 46 * s)], width=7 * s, colour=(140, 96, 60))
        ink.rrect(x + 14 * s, y - 66 * s, x + 54 * s, y - 44 * s, r=5 * s, fill=(96, 100, 110), outline=INK, width=4 * s)
    elif prop == "lantern":
        ink.line([(x - 3 * s, y - 6 * s), (x + 3 * s, y - 26 * s)], width=4 * s)
        ink.rrect(x - 16 * s, y + 2 * s, x + 16 * s, y + 40 * s, r=6 * s, fill=(250, 214, 130), outline=INK, width=4 * s)
    elif prop == "candle":
        ink.rrect(x - 7 * s, y - 2 * s, x + 7 * s, y + 34 * s, r=3 * s, fill=(248, 240, 214), outline=INK, width=3 * s)
        ink.ellipse(x - 5 * s, y - 18 * s, x + 5 * s, y - 2 * s, fill=(252, 198, 84), outline=(230, 150, 40))
    elif prop == "shard":
        ink.poly([(x - 20 * s, y + 10 * s), (x + 4 * s, y - 30 * s), (x + 22 * s, y + 6 * s), (x - 2 * s, y + 26 * s)],
                 fill=(70, 66, 78), outline=INK)
    elif prop == "crown":
        ink.poly([(x - 26 * s, y - 20 * s), (x - 14 * s, y - 40 * s), (x - 2 * s, y - 22 * s),
                  (x + 10 * s, y - 42 * s), (x + 22 * s, y - 20 * s)], fill=(216, 155, 60), outline=INK)


# ------------------------------------------------------------- draw itself ---
def idle(p: Pose, t: float, amount: float = 1.0) -> Pose:
    """Small breathing / weight-shift so a standing figure is never frozen. Deterministic."""
    if amount <= 0:
        return p
    a = 1.0 * amount
    p = Pose(**{**p.__dict__})
    bx = 1.5 * a * math.sin(t * 1.15)
    by = -1.4 * a * math.sin(t * 1.7)
    p.hip = (p.hip[0] + bx, p.hip[1] + by)
    p.head_off = (p.head_off[0] + 0.9 * a * math.sin(t * 1.15 + 1.2),
                  p.head_off[1] + 1.1 * a * math.sin(t * 1.7 + 0.6))
    p.lean = p.lean + 0.006 * a * math.sin(t * 1.05)
    if p.hand_l:
        p.hand_l = (p.hand_l[0], p.hand_l[1] + 1.4 * a * math.sin(t * 1.7 + 0.4))
    if p.hand_r:
        p.hand_r = (p.hand_r[0], p.hand_r[1] + 1.4 * a * math.sin(t * 1.7 + 1.7))
    return p


CURRENT_T = 0.0   # set once per frame by the renderer, so scenes don't have to pass t


def draw(ink: Ink, ch: Character, p: Pose, facing=1, shadow=True, t: float | None = None,
         idle_amount: float = 1.0):
    """Draw a character. `facing` flips handedness (props/labels), not the pose."""
    s = ch.scale
    t = CURRENT_T if t is None else t
    if t:
        p = idle(p, t, idle_amount)
    sk = skeleton(ch, p)
    hair_col = HAIR.get(ch.hair, ch.hair) if isinstance(ch.hair, str) else ch.hair
    lw = LIMB_W * s

    # ground shadow
    if shadow:
        fx = (sk["foot_l"][0] + sk["foot_r"][0]) / 2
        fy = max(sk["foot_l"][1], sk["foot_r"][1])
        ink.ellipse(fx - 78 * s, fy - 9 * s, fx + 78 * s, fy + 12 * s, fill=(0, 0, 0, 32))

    # legs
    for (hip, knee, foot) in ((sk["hip"], sk["knee_l"], sk["foot_l"]),
                              (sk["hip"], sk["knee_r"], sk["foot_r"])):
        ink.line([hip, knee, foot], width=lw + 4.5 * s, colour=ch.trousers)
        ink.line([knee, foot], width=lw + 2.5 * s, colour=ch.trousers)
    for foot in (sk["foot_l"], sk["foot_r"]):
        back, front = foot[0] - 16 * s, foot[0] + 26 * s
        if facing < 0:
            back, front = foot[0] - 26 * s, foot[0] + 16 * s
        ink.ellipse(min(back, front), foot[1] - 7 * s, max(back, front), foot[1] + 9 * s,
                    fill=ch.shoes or (46, 48, 56))

    # far arm (behind torso)
    ink.line([sk["shoulder_r"], sk["elbow_r"], sk["hand_r"]], width=lw, colour=ch.shirt)

    # torso
    hip_a = (sk["hip"][0] - HIP_W * s, sk["hip"][1])
    hip_b = (sk["hip"][0] + HIP_W * s, sk["hip"][1])
    sh_a = (sk["shoulder_c"][0] - SHOULDER_W * s * 1.16, sk["shoulder_c"][1] + 4 * s)
    sh_b = (sk["shoulder_c"][0] + SHOULDER_W * s * 1.16, sk["shoulder_c"][1] + 4 * s)
    body = [sh_a, (sh_a[0] * 0.62 + (sk["shoulder_c"][0]) * 0.38, sk["shoulder_c"][1] - 11 * s),
            (sh_b[0] * 0.62 + (sk["shoulder_c"][0]) * 0.38, sk["shoulder_c"][1] - 11 * s), sh_b,
            (hip_b[0] + 4 * s, hip_b[1] - 2 * s), hip_b, hip_a, (hip_a[0] - 4 * s, hip_a[1] - 2 * s)]
    coat = "coat" in ch.extras or "apron" in ch.extras
    if coat:
        body = [sh_a, (sh_a[0], sk["shoulder_c"][1] - 16 * s), (sh_b[0], sk["shoulder_c"][1] - 16 * s), sh_b,
                (hip_b[0] + 12 * s, hip_b[1] + 34 * s), (hip_a[0] - 12 * s, hip_a[1] + 34 * s)]
    ink.poly(body, fill=ch.shirt, outline=INK)
    if "coat" in ch.extras:                       # lapels
        ink.line([(sk["shoulder_c"][0] - 18 * s, sk["shoulder_c"][1] - 12 * s),
                  (sk["shoulder_c"][0], sk["shoulder_c"][1] + 34 * s),
                  (sk["shoulder_c"][0] + 18 * s, sk["shoulder_c"][1] - 12 * s)], width=3.4 * s, colour=INK)
    if "cravat" in ch.extras:
        sc = sk["shoulder_c"]
        for dy, w in ((0, 15), (16, 19)):
            ink.rrect(sc[0] - w * s, sc[1] - 6 * s + dy * s, sc[0] + w * s, sc[1] + 8 * s + dy * s,
                      r=5 * s, fill=WHITE, outline=INK, width=2.4 * s)
    if "ruff" in ch.extras:
        for a in range(-2, 3):
            ink.ellipse(sk["shoulder_c"][0] + a * 15 * s - 12 * s, sk["shoulder_c"][1] - 24 * s,
                        sk["shoulder_c"][0] + a * 15 * s + 12 * s, sk["shoulder_c"][1] + 2 * s,
                        fill=WHITE, outline=INK, width=3 * s)
    if "tie" in ch.extras:
        ink.poly([(sk["shoulder_c"][0] - 7 * s, sk["shoulder_c"][1] - 12 * s),
                  (sk["shoulder_c"][0] + 7 * s, sk["shoulder_c"][1] - 12 * s),
                  (sk["shoulder_c"][0] + 4 * s, sk["shoulder_c"][1] + 26 * s),
                  (sk["shoulder_c"][0] - 4 * s, sk["shoulder_c"][1] + 24 * s)], fill=(120, 50, 60), outline=INK)
    if "sash" in ch.extras:
        ink.poly([(sk["shoulder_c"][0] - 20 * s, sk["shoulder_c"][1] + 30 * s),
                  (sk["shoulder_c"][0] + 22 * s, sk["shoulder_c"][1] - 6 * s),
                  (sk["shoulder_c"][0] + 30 * s, sk["shoulder_c"][1] + 12 * s),
                  (sk["shoulder_c"][0] - 12 * s, sk["shoulder_c"][1] + 48 * s)], fill=(196, 98, 63), outline=INK)

    # neck + head
    ink.line([(sk["shoulder_c"][0] + p.lean * 6 * s, sk["shoulder_c"][1] - 4 * s), sk["head"]],
             width=12 * s, colour=ch.skin)
    hx, hy = sk["head"]
    _hair(ink, hx, hy, s, ch, ch.hair_style, hair_col, back=True)
    _head_shape(ink, hx, hy, s, ch)
    _hair(ink, hx, hy, s, ch, ch.hair_style, hair_col, back=False)
    if "beard" in ch.extras:
        # Horseshoe: side pieces down the jaw plus a chin wedge, with a clear gap in the
        # middle so the mouth always stays readable (a full beard buried it before).
        for sgn in (-1, 1):
            ink.poly([(hx + sgn * HEAD_RX * 1.04 * s, hy + HEAD_RY * 0.02 * s),
                      (hx + sgn * HEAD_RX * 0.86 * s, hy + HEAD_RY * 0.18 * s),
                      (hx + sgn * HEAD_RX * 0.62 * s, hy + HEAD_RY * 0.48 * s),
                      (hx + sgn * HEAD_RX * 0.46 * s, hy + HEAD_RY * 1.02 * s),
                      (hx + sgn * HEAD_RX * 0.86 * s, hy + HEAD_RY * 0.94 * s),
                      (hx + sgn * HEAD_RX * 1.06 * s, hy + HEAD_RY * 0.36 * s)],
                     fill=hair_col, outline=INK, width=2.4 * s)
        ink.poly([(hx - HEAD_RX * 0.60 * s, hy + HEAD_RY * 0.98 * s),
                  (hx + HEAD_RX * 0.60 * s, hy + HEAD_RY * 0.98 * s),
                  (hx + HEAD_RX * 0.36 * s, hy + HEAD_RY * 1.30 * s),
                  (hx - HEAD_RX * 0.36 * s, hy + HEAD_RY * 1.30 * s)],
                 fill=hair_col, outline=INK, width=2.6 * s)
        ink.line([(hx - HEAD_RX * 0.62 * s, hy + HEAD_RY * 0.16 * s),
                  (hx - HEAD_RX * 0.44 * s, hy + HEAD_RY * 0.92 * s)], width=1.8 * s, colour=INK_SOFT)
        ink.line([(hx + HEAD_RX * 0.62 * s, hy + HEAD_RY * 0.16 * s),
                  (hx + HEAD_RX * 0.44 * s, hy + HEAD_RY * 0.92 * s)], width=1.8 * s, colour=INK_SOFT)
    brow_col = (118, 116, 112) if hair_col in (HAIR["grey"], HAIR["white"]) else hair_col
    _eyes(ink, hx, hy, s, p, brow_col)
    _mouth(ink, hx, hy, s, p, dy=(9.0 if "moustache" in ch.extras else 0.0) * s)
    if "moustache" in ch.extras:
        # above the mouth line with a centre notch, so the mouth stays readable
        ink.poly([(hx - 24 * s, hy + 21 * s), (hx + 24 * s, hy + 21 * s), (hx + 18 * s, hy + 33 * s),
                  (hx, hy + 26 * s), (hx - 18 * s, hy + 33 * s)], fill=hair_col, outline=INK, width=2.4 * s)
    if p.blush:
        ink.ellipse(hx - 44 * s, hy + 10 * s, hx - 20 * s, hy + 24 * s, fill=(230, 150, 150, 130))
        ink.ellipse(hx + 20 * s, hy + 10 * s, hx + 44 * s, hy + 24 * s, fill=(230, 150, 150, 130))
    if "glasses" in ch.extras:
        for dx in (-17 * s, 17 * s):
            ink.ellipse(hx + dx - 16 * s, hy - 18 * s, hx + dx + 16 * s, hy + 10 * s, outline=INK, width=3.4 * s)
        ink.line([(hx - 1 * s, hy - 6 * s), (hx + 1 * s, hy - 6 * s)], width=3.4 * s)
        ink.line([(hx - 33 * s, hy - 6 * s), (hx - HEAD_RX * s, hy - 8 * s)], width=3.4 * s)
        ink.line([(hx + 33 * s, hy - 6 * s), (hx + HEAD_RX * s, hy - 8 * s)], width=3.4 * s)
    if "goggles" in ch.extras:
        for dx in (-19 * s, 19 * s):
            ink.ellipse(hx + dx - 19 * s, hy - 20 * s, hx + dx + 19 * s, hy + 12 * s, outline=INK, width=5 * s)
            ink.ellipse(hx + dx - 15 * s, hy - 16 * s, hx + dx + 15 * s, hy + 8 * s, fill=(150, 200, 210, 120))
    if "hairbun" in ch.extras:
        ink.ellipse(hx - 18 * s, hy - HEAD_RY * s - 24 * s, hx + 18 * s, hy - HEAD_RY * s + 14 * s,
                    fill=hair_col, outline=INK, width=3.4 * s)
    if "mortarboard" in ch.extras:
        ink.rrect(hx - 46 * s, hy - HEAD_RY * s - 12 * s, hx + 46 * s, hy - HEAD_RY * s + 10 * s, r=4 * s,
                  fill=(48, 46, 56), outline=INK)
        ink.poly([(hx - 62 * s, hy - HEAD_RY * s - 6 * s), (hx, hy - HEAD_RY * s - 34 * s),
                  (hx + 62 * s, hy - HEAD_RY * s - 6 * s), (hx, hy - HEAD_RY * s + 22 * s)],
                 fill=(48, 46, 56), outline=INK)
        ink.line([(hx + 52 * s, hy - HEAD_RY * s - 2 * s), (hx + 60 * s, hy - HEAD_RY * s + 44 * s)],
                 width=3.4 * s, colour=(196, 98, 63))
    if "cap" in ch.extras:
        ink.poly([(hx - 44 * s, hy - HEAD_RY * s + 12 * s), (hx + 40 * s, hy - HEAD_RY * s + 12 * s),
                  (hx, hy - HEAD_RY * s - 22 * s)], fill=(70, 92, 140), outline=INK)
        ink.rrect(hx - 6 * s, hy - HEAD_RY * s + 2 * s, hx + 62 * s, hy - HEAD_RY * s + 16 * s, r=6 * s,
                  fill=(70, 92, 140), outline=INK)
    if "wig19" in ch.extras and ch.hair_style != "wig19":
        _hair(ink, hx, hy, s, ch, "wig19", hair_col, back=False)
    if "hat" in ch.extras:
        ink.rrect(hx - 56 * s, hy - HEAD_RY * s - 26 * s, hx + 56 * s, hy - HEAD_RY * s + 6 * s, r=8 * s,
                  fill=(60, 54, 62), outline=INK)
        ink.rrect(hx - 78 * s, hy - HEAD_RY * s + 2 * s, hx + 78 * s, hy - HEAD_RY * s + 20 * s, r=8 * s,
                  fill=(60, 54, 62), outline=INK)

    # near arm (in front)
    ink.line([sk["shoulder_l"], sk["elbow_l"], sk["hand_l"]], width=lw, colour=ch.shirt)
    hand_col = ch.skin if "gloves" not in ch.extras else (70, 74, 84)
    for (hx_, hy_), prop in ((sk["hand_l"], p.prop_l), (sk["hand_r"], p.prop_r)):
        ink.ellipse(hx_ - 10 * s, hy_ - 10 * s, hx_ + 10 * s, hy_ + 10 * s, fill=hand_col,
                    outline=INK, width=3.0 * s)
        if prop:
            ink.line([(hx_ - 6 * s, hy_ - 8 * s), (hx_ + 6 * s, hy_ - 8 * s)], width=2.6 * s, colour=INK_SOFT)

    if p.prop_l:
        _prop_in_hand(ink, p.prop_l, *sk["hand_l"], s)
    if p.prop_r:
        _prop_in_hand(ink, p.prop_r, *sk["hand_r"], s)
    return sk
