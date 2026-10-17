#!/usr/bin/env python3
"""mg.film - the beat timeline. render_frame(t) -> uint8 RGB (H, W, 3)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from engine import (W, H, Canvas, font, text_rgba, rounded_rect, glow_under,
                    smear, place, smoothstep, ease_out, ease_in, ease_io,
                    quad_project)
import scenes as SC
import logo as LOGO

COPY = SC.COPY
SB = SC.SB

_LITHOS = LOGO.mark_rgba(420)
_CURSOR = SC.cursor_rgba(72)


def put_tl(cv, im, x, y, opacity=1.0, add=False):
    """Top-left placement (panel/composer/text call sites)."""
    if im is None or opacity <= 0:
        return
    cv.comp(im, pos=(int(x), int(y)), opacity=opacity, add=add)


def shadowed_text(s, fnt, color, tracking=0.0):
    """Type with a soft dark drop shadow (contrast rule from research)."""
    fg = text_rgba(s, fnt, color, tracking)
    sh = Image.new("RGBA", (fg.size[0] + 16, fg.size[1] + 16), (0, 0, 0, 0))
    dark = np.asarray(fg).copy()
    dark[:, :, 0:3] = 6
    dark[:, :, 3] = (dark[:, :, 3] * 0.55).astype(np.uint8)
    sh.paste(Image.fromarray(dark), (10, 12))
    sh.alpha_composite(fg, dest=(2, 2))
    return sh


def _cam_place(cv, im, x, y, zoom=1.0, opacity=1.0, add=False):
    cx, cy = W / 2, H / 2
    px = cx + (x - cx) * zoom
    py = cy + (y - cy) * zoom
    place(cv, im, px, py, opacity=opacity, add=add, scale=zoom)


def _outro_word(pal, fnt, s):
    return text_rgba(s, fnt, tuple(int(c) for c in pal["type"]))


def render_frame(t):
    pal = SC.palette(t)
    cv = Canvas(bg=(0, 0, 0))

    # ============================== A: hook + wordmark (0.00 - 1.25)
    if t < 1.55:
        zoom = 1.0 + 0.03 * smoothstep(t / 1.25)
        cv.buf += SC.ribbons(t, pal) * (0.85 if t >= 1.25 else 1.0)
        if t < 1.35:
            u = ease_out(np.clip((t - 0.10) / 0.42, 0, 1))
            mark = SC.kmark(340, pal)
            x = 640 - 60 * (1 - u)
            if t >= 1.25:
                wu = np.clip((t - 1.25) / 0.18, 0, 1)
                x -= 900 * ease_in(wu)
                sm = smear(mark, -46, 0, n=10, decay=0.78)
                _cam_place(cv, sm, x, 520, zoom, opacity=1 - wu * 0.9)
            else:
                _cam_place(cv, mark, x, 520, zoom, opacity=smoothstep(u * 2))
            if t >= 0.55:
                line, lw = SC.typed_line(COPY["wordmark"], t, 0.55, font("ui", 128), pal, cps=23.0)
                if line is not None:
                    if t >= 1.25:
                        wu = np.clip((t - 1.25) / 0.18, 0, 1)
                        sm = smear(line, -52, 0, n=10, decay=0.78)
                        _cam_place(cv, sm, 1180 - 900 * ease_in(wu), 530, zoom, opacity=1 - wu * 0.9)
                    else:
                        _cam_place(cv, line, 1180, 530, zoom)

    # ============================== B: tool chips (1.25 - 2.70)
    if 1.25 <= t < 2.70:
        if t >= 1.30:
            cv.buf += SC.ribbons(t, pal) * smoothstep((t - 1.30) / 0.14)
        zoom = 1.0 + 0.04 * smoothstep((t - 1.55) / 1.15)
        icons = ["shape", "score", "light", "cut", "loop"]
        chips, widths = [], []
        for name, icon in zip(COPY["chips"], icons):
            ign = 0.0
            if name == COPY["chip_ignite"]:
                ign = smoothstep((t - 1.85) / 0.22)
                if 2.25 <= t < 2.36:
                    ign = 1.0
            c = SC.chip(name, icon, 38, ignited=ign, pal=pal)
            chips.append(c)
            widths.append(c.size[0])
        gap = 28
        total = sum(widths) + gap * (len(chips) - 1)
        x = (W - total) / 2
        y = H / 2 - 40
        for i, c in enumerate(chips):
            xi = x + sum(widths[:i]) + gap * i
            if t < 1.58:
                u = ease_out(np.clip((t - 1.25 - i * 0.028) / 0.30, 0, 1))
                dx = (1 - u) * (420 if i % 2 == 0 else -420)
                if u < 0.98:
                    sm = smear(c, -np.sign(dx) * 34, 0, n=8, decay=0.75)
                    _cam_place(cv, sm, xi + dx + c.size[0] / 2, y + c.size[1] / 2, zoom,
                               opacity=0.35 + 0.65 * u)
                    continue
            _cam_place(cv, c, xi + c.size[0] / 2, y + c.size[1] / 2, zoom)
        if t >= 1.95:
            cut_i = COPY["chips"].index(COPY["chip_ignite"])
            cx_target = (W - total) / 2 + sum(widths[:cut_i]) + gap * cut_i + widths[cut_i] * 0.62
            cy_target = y + chips[cut_i].size[1] * 0.8
            u = ease_out(np.clip((t - 1.95) / 0.30, 0, 1))
            press = 0.92 if 2.25 <= t < 2.36 else 1.0
            cxp = 1120 + (cx_target - 1120) * u
            cyp = 1150 + (cy_target - 1150) * u
            cur = _CURSOR if press == 1.0 else _CURSOR.resize(
                (int(_CURSOR.size[0] * press), int(_CURSOR.size[1] * press)), Image.LANCZOS)
            _cam_place(cv, cur, cxp, cyp, zoom)
        if 1.34 <= t < 1.42:
            fl = Image.new("RGBA", (W, H), (255, 255, 255, int(50 * (1 - abs(t - 1.375) / 0.045))))
            cv.comp(fl)

    # ============================== C: console + rain + cards (2.70 - 10.30)
    if 2.70 <= t < 10.32:
        bg = SC.ribbons(t, pal)
        world_gain = 1.0
        if 2.70 <= t < 4.30:
            world_gain = 0.16
        if 4.30 <= t < 5.20:
            world_gain = 0.30
        if 5.20 <= t < 6.65:
            world_gain = 0.55
        if 6.65 <= t < 7.30:
            world_gain = 0.32
        if 7.30 <= t < 8.50:
            world_gain = 0.55 - 0.18 * smoothstep((t - 7.3) / 1.2)
        if 8.50 <= t:
            world_gain = 0.9
        cv.buf += bg * world_gain

        if 2.70 <= t < 2.74:
            cv.comp(Image.new("RGBA", (W, H), (255, 255, 255, 38)))

        p1, p1w = SC.typed_line(COPY["prompt1"], t, 2.80, font("mono", 52), pal, cps=24.0)
        p2, p2w = SC.typed_line(COPY["prompt2"], t, 6.70, font("mono", 46), pal, cps=32.0)

        rw = ease_io(np.clip((t - 3.65) / 0.30, 0, 1)) if t >= 3.65 else 0.0
        pw = 1360
        ph = int(620 * (1 - rw) + 120 * rw)
        py = int((160) * (1 - rw) + (860) * rw)  # top-left y of the panel
        px = int((W - pw) / 2)
        hidden = 5.25 <= t < 6.65
        if not hidden and (t < 10.05 or t >= 6.65):
            panel = rounded_rect((pw, ph), 36 if rw < 0.4 else ph // 2,
                                 fill=tuple(int(c) for c in pal["panel"]),
                                 stroke=tuple(int(c) for c in pal["panel_line"]), stroke_w=2)
            put_tl(cv, panel, px, py)

        # composer bar FIRST (opaque), then prompt type on top
        if rw > 0.2 and not hidden:
            glow = smoothstep((t - 7.3) / 1.2) if 7.3 <= t else (0.25 if t < 6.65 else 0.6)
            if 8.5 <= t:
                glow = 1.0
            comp = SC.composer(pal, pw, ph if rw > 0.98 else 120, send_glow=glow)
            put_tl(cv, comp, px, py, opacity=smoothstep((t - 3.75) / 0.25))

        fit = 1.0 - 0.22 * rw  # refit: type shrinks as the panel becomes the bar
        if p1 is not None and t < 6.65:
            op = 1.0 - smoothstep((t - 4.30) / 0.25) if t >= 4.30 else 1.0
            tw, th = int(p1.size[0] * fit), int(p1.size[1] * fit)
            p1s = p1.resize((max(1, tw), max(1, th)), Image.LANCZOS) if fit < 0.999 else p1
            ty = (py + 170) if t < 3.65 else int(py + (ph - p1s.size[1]) / 2)
            put_tl(cv, p1s, px + 80, ty, opacity=op)
            if t < 4.30 and int(t * 2.4) % 2 == 0:
                cx = px + 80 + p1s.size[0] - 8
                cy = ty + int(p1s.size[1] / 2) - int(29 * fit)
                put_tl(cv, rounded_rect((int(18 * fit), int(58 * fit)), 4,
                                        fill=tuple(int(c) for c in pal["accent"])), cx, cy)
        if p2 is not None and not hidden and t < 10.05:
            put_tl(cv, p2, px + 80, int(py + (ph - p2.size[1]) / 2))
            if 6.70 <= t < 7.32 and int(t * 2.4) % 2 == 0:
                put_tl(cv, rounded_rect((18, 50), 4, fill=tuple(int(c) for c in pal["accent"])),
                       px + 80 + p2.size[0] - 8, int(py + ph / 2 - 25))

        if 4.30 <= t < 5.30:
            cam_y = (t - 4.3) * 130
            for depth in (2, 1, 0):
                cv.comp(SC.rain_layer(t, pal, depth, cam_y=cam_y),
                        opacity=0.9 if depth < 2 else 0.7)
        if 5.30 <= t < 6.70:
            for depth in (2, 1):
                cv.comp(SC.rain_layer(t, pal, depth, cam_y=65), opacity=0.45)

        def draw_card(tau, molten_u, x0, y0, yaw_deg, pitch_deg, op, vel=(0, 0), exit_scale=1.0):
            page = SC.card_page(pal, molten_u)
            page = page.resize((1480, 930), Image.LANCZOS)
            yaw = math.radians(yaw_deg)
            pitch = math.radians(pitch_deg)
            cw, chh = page.size
            kx = 0.14 * math.tan(yaw)
            ky = 0.10 * math.tan(pitch)

            def corner(u, v):
                sx = 1 + kx * u
                sy = 1 + ky * v
                return (x0 + u * cw / 2 * sx * exit_scale, y0 + v * chh / 2 * sy * exit_scale)
            corners = [corner(-1, -1), corner(1, -1), corner(1, 1), corner(-1, 1)]
            warped = quad_project(page, corners, (W, H))
            sh = warped.copy()
            sh.putalpha(Image.fromarray((np.asarray(sh)[:, :, 3] * 0.5).astype(np.uint8)))
            sh = sh.filter(ImageFilter.GaussianBlur(26))
            if vel != (0, 0):
                warped = smear(warped, vel[0], vel[1], n=10, decay=0.72)
                sh = sh.filter(ImageFilter.GaussianBlur(42))
            place(cv, sh, x0, y0 + 30, opacity=op)
            place(cv, warped, x0, y0, opacity=op)

        if 5.20 <= t < 6.85:
            u = ease_out(np.clip((t - 5.20) / 0.35, 0, 1))
            x0 = 2320 - 1360 * u
            vel = (60 * (1 - u), 0) if u < 0.98 else (0, 0)
            yaw = 7.5 * math.sin((t - 5.2) * 0.85) - 3 * (1 - u)
            pit = 2.2 * math.sin((t - 5.2) * 0.6 + 1.0)
            if t >= 6.65:
                wu = ease_in(np.clip((t - 6.65) / 0.14, 0, 1))
                draw_card(t, 0.0, 980, 510 - 1200 * wu, yaw, pit, 1 - wu, vel=(0, -85),
                          exit_scale=1 + 0.12 * wu)
            else:
                draw_card(t, 0.0, x0, 510, yaw, pit, smoothstep((t - 5.2) / 0.18), vel=vel)
        if 8.50 <= t < 10.30:
            u = ease_out(np.clip((t - 8.50) / 0.35, 0, 1))
            x0 = -400 + 1380 * u
            vel = (-55 * (1 - u), 0) if u < 0.98 else (0, 0)
            yaw = -7.5 * math.sin((t - 8.5) * 1.05) + 3 * (1 - u)
            pit = 2.4 * math.sin((t - 8.5) * 0.8 + 0.5)
            mu = smoothstep((t - 8.50) / 0.22)
            if t >= 10.05:
                wu = ease_in(np.clip((t - 10.05) / 0.20, 0, 1))
                draw_card(t, mu, 980 + 500 * wu, 510 - 1350 * wu, yaw, pit, 1 - wu, vel=(45, -90),
                          exit_scale=1 + 0.16 * wu)
            else:
                draw_card(t, mu, x0, 510, yaw, pit, smoothstep((t - 8.5) / 0.12), vel=vel)

    # ============================== D: outro (10.15 - 13.0)
    if t >= 10.15:
        if t < 11.95:
            cv.buf += SC.ribbons(t, pal) * 0.18
        if t < 11.95:
            u = ease_out(np.clip((t - 10.15) / 0.28, 0, 1))
            if t >= 11.80:
                wu = np.clip((t - 11.80) / 0.15, 0, 1)
                stretched = _LITHOS.resize(
                    (_LITHOS.size[0], int(_LITHOS.size[1] * (1 + 2.2 * ease_in(wu)))), Image.LANCZOS)
                sm = smear(stretched, 0, 42, n=10, decay=0.7)
                place(cv, sm, 960, 430, opacity=1 - wu)
            else:
                g = glow_under(_LITHOS, tuple(int(c) for c in pal["accent"]), 26, 0.5)
                place(cv, g, 960, 430, opacity=u * 0.8, add=True)
                place(cv, _LITHOS, 960, 430, opacity=u)

        fnt = font("ui", 86)
        s = COPY["outro"]
        widths = [fnt.getlength(c) + 1.5 for c in s]
        total_w = sum(widths)
        x_left = 960 - total_w / 2
        base_y = 640
        wu = np.clip((t - 11.80) / 0.15, 0, 1) if t >= 11.80 else 0.0
        native = _outro_word(pal, fnt, s)
        settle = smoothstep((t - 11.18) / 0.22)  # crossfade to kerned word

        if wu > 0:
            # streak exit on the kerned word
            stretched = native.resize(
                (native.size[0], max(2, int(native.size[1] * (1 + 3.2 * ease_in(wu))))), Image.LANCZOS)
            sm = smear(stretched, 0, 40, n=9, decay=0.68)
            put_tl(cv, sm, 960 - native.size[0] / 2, base_y + 250 * wu, opacity=1 - wu)
        else:
            if settle < 1.0:
                x = x_left
                for i, c in enumerate(s):
                    t0 = 10.35 + i * 0.055
                    u = ease_out(np.clip((t - t0) / 0.38, 0, 1))
                    if u > 0:
                        ch_im = text_rgba(c, fnt, tuple(int(c) for c in pal["type"]))
                        ang = -0.45 + 0.10 * i
                        dx = (1 - u) * 520 * math.cos(ang)
                        dy = (1 - u) * 300 * math.sin(-ang) + 220 * (1 - u)
                        px = x + (widths[i] - ch_im.size[0]) / 2
                        if u < 0.97:
                            sm = smear(ch_im, -dx * 0.08, -dy * 0.08, n=7, decay=0.7)
                            put_tl(cv, sm, px + dx, base_y + dy)
                        else:
                            put_tl(cv, ch_im, px, base_y, opacity=1 - settle)
                    x += widths[i]
            if settle > 0:
                put_tl(cv, native, 960 - native.size[0] / 2, base_y - 10, opacity=settle)

    return cv.finish(seed=int(t * SB["format"]["fps"]))
