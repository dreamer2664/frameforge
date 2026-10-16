"""glyphcraft deterministic master film renderer (r04).
Craft elevations for r04:
- Act I: Dual-filament magnetic cursive trace with energetic terminal snap directly into Fraunces STROKE.
- Act II: Multi-axial tensor strain grid, chromatic RGB displacement, and explosive acoustic shockwave into WEIGHT.
- Act III: Multi-stage non-linear Signed Distance Field (SDF) metamorphosis FORM -> MOTION with dynamic vector filaments & golden corona bloom.
- Act IV: Full 3D perspective tunnel dive into the counter of glyph 'O', with rushing radial typographic corridors and golden flare rim.
- Act V: Centripetal imploding particle storm with velocity-stretched motion streaks, locking into KINETIC with full anamorphic flare and breathing ambient corona.
- Loop: 10.0s cyclic topological resonance with continuous wave perturbation and zero boundary variance.
"""
from __future__ import annotations
import argparse, math, os, sys, time, subprocess
import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE, 'fonts')
FRAUNCES = os.path.join(FONT_DIR, 'Fraunces.ttf')
INTER_BOLD = os.path.join(FONT_DIR, 'Inter-Bold.ttf')
INTER_REG = os.path.join(FONT_DIR, 'Inter-Regular.ttf')

W, H = 1920, 1080
FPS = 30
HERO_DURATION = 42.0
LOOP_DURATION = 10.0

# Palette (BGR)
C_VOID = np.array([16, 12, 10], dtype=np.float32)       # #0a0c10
C_IVORY = np.array([238, 244, 246], dtype=np.float32)   # #f6f4ee
C_AMBER = np.array([59, 158, 255], dtype=np.float32)    # #ff9e3b
C_CYAN = np.array([240, 201, 76], dtype=np.float32)     # #4cc9f0
C_EMBER = np.array([40, 90, 216], dtype=np.float32)     # #d85a28
C_GRID = (45, 40, 35)

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / max(1e-6, edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

class SDFCache:
    def __init__(self):
        self.cache = {}

    def get(self, text, size, box_w, box_h, font_p=FRAUNCES):
        key = (text, size, box_w, box_h, font_p)
        if key in self.cache:
            return self.cache[key]
        
        font = ImageFont.truetype(font_p, size)
        im = Image.new('L', (box_w, box_h), 0)
        draw = ImageDraw.Draw(im)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (box_w - tw) // 2 - bbox[0]
        ty = (box_h - th) // 2 - bbox[1]
        draw.text((tx, ty), text, font=font, fill=255)
        arr = np.array(im)
        
        d_in = cv2.distanceTransform(arr, cv2.DIST_L2, 5)
        d_out = cv2.distanceTransform(255 - arr, cv2.DIST_L2, 5)
        sdf = d_in - d_out
        self.cache[key] = sdf
        return sdf

sdf_cache = SDFCache()

def draw_hud(canvas, title, sub, phase=None):
    pil_im = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_im)
    f_sub = ImageFont.truetype(INTER_BOLD, 18)
    f_micro = ImageFont.truetype(INTER_REG, 15)
    
    draw.text((120, 960), title.upper(), font=f_sub, fill=(185, 200, 220))
    draw.text((120, 990), sub.upper(), font=f_micro, fill=(115, 135, 155))
    if phase is not None:
        draw.text((1600, 960), f"VECTOR PHASE // {phase*100:05.1f}%", font=f_sub, fill=(255, 158, 59))
    draw.text((120, 80), "KINETIC // GLYPH DYNAMICS LAB", font=f_sub, fill=(125, 145, 170))
    draw.text((1650, 80), "EBU R128 SYNCHRONOUS", font=f_micro, fill=(95, 115, 135))
    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

def draw_grid(bg):
    for y in range(80, H, 140):
        cv2.line(bg, (80, y), (W - 80, y), C_GRID, 1, cv2.LINE_AA)
    for x in range(120, W, 180):
        cv2.line(bg, (x, 80), (x, H - 80), C_GRID, 1, cv2.LINE_AA)

# ==================== SCENE RENDERERS ====================

def render_act_1_stroke(t):
    """Act I: The Atomic Stroke (0.0s - 7.0s)"""
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    frame[:, :] = C_VOID
    draw_grid(frame)
    
    box_w, box_h = 1500, 420
    bx = (W - box_w) // 2
    by = (H - box_h) // 2
    
    p_trace = smoothstep(0.4, 3.2, t)
    
    pts = []
    num_pts = int(120 * p_trace)
    for i in range(max(1, num_pts)):
        u = i / 120.0
        x = int(W * 0.15 + W * 0.7 * u + 40 * math.sin(u * math.pi * 3))
        y = int(H * 0.68 - H * 0.32 * u + 35 * math.cos(u * math.pi * 2))
        pts.append((x, y))
        
    if len(pts) > 1:
        fade_tail = 1.0 - smoothstep(3.8, 5.2, t)
        if fade_tail > 0.01:
            for i in range(len(pts) - 1):
                thickness = int((3 + 15 * math.sin(i / len(pts) * math.pi)) * fade_tail)
                if thickness > 0:
                    col = (C_AMBER * (i / len(pts)) + C_EMBER * (1 - i / len(pts))) * fade_tail
                    cv2.line(frame, pts[i], pts[i+1], tuple(map(int, col)), thickness, cv2.LINE_AA)
                    
            # Companion magnetic filament
            for i in range(len(pts) - 1):
                off_y = int(18 * math.sin(i / len(pts) * math.pi * 2))
                p1 = (pts[i][0], pts[i][1] + off_y)
                p2 = (pts[i+1][0], pts[i+1][1] + off_y)
                col_c = (C_CYAN * fade_tail * 0.6).astype(int)
                cv2.line(frame, p1, p2, tuple(map(int, col_c)), 1, cv2.LINE_AA)
            
    if pts and t < 4.0:
        hx, hy = pts[-1]
        cv2.circle(frame, (hx, hy), 16, (int(C_AMBER[0]), int(C_AMBER[1]), int(C_AMBER[2])), -1, cv2.LINE_AA)
        cv2.circle(frame, (hx, hy), 32, (int(C_AMBER[0]*0.5), int(C_AMBER[1]*0.5), int(C_AMBER[2]*0.5)), 2, cv2.LINE_AA)
        
    if t >= 2.6:
        p_word = smoothstep(2.6, 4.2, t)
        sdf_stroke = sdf_cache.get("STROKE", 260, box_w, box_h)
        mask = np.clip((sdf_stroke + 2.0) / 4.0, 0.0, 1.0) * p_word
        corona = np.clip((sdf_stroke + 24.0) / 30.0, 0.0, 1.0) * np.clip((8.0 - sdf_stroke) / 16.0, 0.0, 1.0) * p_word
        
        roi = frame[by:by+box_h, bx:bx+box_w].astype(np.float32)
        for c in range(3):
            roi[:, :, c] += corona * C_AMBER[c] * 0.65
            roi[:, :, c] = roi[:, :, c] * (1.0 - mask) + C_IVORY[c] * mask
        frame[by:by+box_h, bx:bx+box_w] = np.clip(roi, 0, 255).astype(np.uint8)

    return draw_hud(frame, "Act I // The Atomic Stroke", "Kinetic genesis of glyph anatomy", phase=smoothstep(0.0, 7.0, t))

def render_act_2_tension(t):
    """Act II: Elastic Tension & Structural Shear (7.0s - 15.0s)"""
    rel_t = t - 7.0
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    frame[:, :] = C_VOID
    draw_grid(frame)
    
    box_w, box_h = 1600, 480
    bx = (W - box_w) // 2
    by = (H - box_h) // 2
    
    if rel_t < 4.2: # 7.0 - 11.2
        shear_p = smoothstep(0.0, 3.6, rel_t)
        shear = math.sin(shear_p * math.pi * 0.95) * 0.44
        sdf = sdf_cache.get("TENSION", 250, box_w, box_h)
        
        M_g = np.float32([[1, shear, -shear * box_h / 2], [0, 1, 0]])
        M_r = np.float32([[1, shear * 1.08, -shear * 1.08 * box_h / 2], [0, 1, 0]])
        M_b = np.float32([[1, shear * 0.92, -shear * 0.92 * box_h / 2], [0, 1, 0]])
        
        sdf_g = cv2.warpAffine(sdf, M_g, (box_w, box_h), borderMode=cv2.BORDER_REFLECT)
        sdf_r = cv2.warpAffine(sdf, M_r, (box_w, box_h), borderMode=cv2.BORDER_REFLECT)
        sdf_b = cv2.warpAffine(sdf, M_b, (box_w, box_h), borderMode=cv2.BORDER_REFLECT)
        
        mask_g = np.clip((sdf_g + 2.0) / 4.0, 0.0, 1.0)
        mask_r = np.clip((sdf_r + 2.0) / 4.0, 0.0, 1.0)
        mask_b = np.clip((sdf_b + 2.0) / 4.0, 0.0, 1.0)
        
        glow_int = 0.45 + 0.65 * shear_p
        corona = np.clip((sdf_g + 30.0) / 34.0, 0.0, 1.0) * np.clip((12.0 - sdf_g) / 22.0, 0.0, 1.0) * glow_int
        
        roi = frame[by:by+box_h, bx:bx+box_w].astype(np.float32)
        roi[:, :, 0] = roi[:, :, 0] * (1.0 - mask_b) + C_IVORY[0] * mask_b + corona * C_CYAN[0] * 0.45
        roi[:, :, 1] = roi[:, :, 1] * (1.0 - mask_g) + C_IVORY[1] * mask_g + corona * C_AMBER[1] * 0.65
        roi[:, :, 2] = roi[:, :, 2] * (1.0 - mask_r) + C_IVORY[2] * mask_r + corona * C_AMBER[2] * 0.85
        frame[by:by+box_h, bx:bx+box_w] = np.clip(roi, 0, 255).astype(np.uint8)
        
        # Tension vector arrows
        for i in range(6):
            sx = int(bx + 160 + i * 240)
            sy = int(by + 40)
            length = int(shear * 190)
            cv2.arrowedLine(frame, (sx, sy), (sx + length, sy), (int(C_AMBER[0]), int(C_AMBER[1]), int(C_AMBER[2])), 2, cv2.LINE_AA)
            cv2.arrowedLine(frame, (sx + length, sy + 400), (sx, sy + 400), (int(C_CYAN[0]), int(C_CYAN[1]), int(C_CYAN[2])), 2, cv2.LINE_AA)
            
    else: # 11.2 - 15.0 snap into WEIGHT
        snap_t = rel_t - 4.2
        p_snap = smoothstep(0.0, 1.0, snap_t)
        sdf_tension = sdf_cache.get("TENSION", 250, box_w, box_h)
        sdf_weight = sdf_cache.get("WEIGHT", 270, box_w, box_h)
        
        sdf_blend = (1.0 - p_snap) * sdf_tension + p_snap * sdf_weight
        if snap_t < 1.6:
            shock_r = int(snap_t * 580)
            cv2.circle(frame, (W//2, H//2), shock_r, (int(C_AMBER[0]*0.55), int(C_AMBER[1]*0.55), int(C_AMBER[2]*0.55)), 3, cv2.LINE_AA)
            cv2.circle(frame, (W//2, H//2), int(shock_r * 0.8), (int(C_CYAN[0]*0.4), int(C_CYAN[1]*0.4), int(C_CYAN[2]*0.4)), 1, cv2.LINE_AA)
            
        mask = np.clip((sdf_blend + 2.0) / 4.0, 0.0, 1.0)
        corona = np.clip((sdf_blend + 25.0) / 30.0, 0.0, 1.0) * np.clip((10.0 - sdf_blend) / 20.0, 0.0, 1.0) * (1.0 - 0.7 * p_snap)
        
        roi = frame[by:by+box_h, bx:bx+box_w].astype(np.float32)
        for c in range(3):
            roi[:, :, c] += corona * C_AMBER[c]
            roi[:, :, c] = roi[:, :, c] * (1.0 - mask) + C_IVORY[c] * mask
        frame[by:by+box_h, bx:bx+box_w] = np.clip(roi, 0, 255).astype(np.uint8)

    return draw_hud(frame, "Act II // Elastic Tension", "Structural shear & acoustic mass resolution", phase=smoothstep(0.0, 8.0, rel_t))

def render_act_3_morph(t):
    """Act III: Hero Topological Metamorphosis (15.0s - 23.0s)"""
    rel_t = t - 15.0
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    frame[:, :] = C_VOID
    draw_grid(frame)
    
    box_w, box_h = 1600, 500
    bx = (W - box_w) // 2
    by = (H - box_h) // 2
    
    u = smoothstep(1.5, 5.5, rel_t)
    sdf_form = sdf_cache.get("FORM", 270, box_w, box_h)
    sdf_motion = sdf_cache.get("MOTION", 240, box_w, box_h)
    
    x_coords = np.linspace(0, 1.0, box_w)[np.newaxis, :]
    local_u = np.clip((u - 0.32 * x_coords) / 0.68, 0.0, 1.0)
    local_u = local_u * local_u * (3.0 - 2.0 * local_u)
    
    sdf_blend = (1.0 - local_u) * sdf_form + local_u * sdf_motion
    
    turb_amp = np.sin(np.pi * u) * 9.5
    if turb_amp > 0.01:
        turb = np.sin(np.linspace(0, 16 * np.pi, box_w)) * turb_amp
        sdf_blend = sdf_blend + turb[np.newaxis, :]
        
    mask = np.clip((sdf_blend + 2.0) / 4.0, 0.0, 1.0)
    corona_width = 30.0 + 18.0 * np.sin(np.pi * u)
    corona = np.clip((sdf_blend + corona_width) / (corona_width * 1.2), 0.0, 1.0) * np.clip((12.0 - sdf_blend) / 22.0, 0.0, 1.0)
    
    tint_p = np.sin(np.pi * u)
    text_color = (1.0 - tint_p) * C_IVORY + tint_p * C_AMBER
    
    roi = frame[by:by+box_h, bx:bx+box_w].astype(np.float32)
    for c in range(3):
        roi[:, :, c] += corona * C_AMBER[c] * (0.45 + 0.55 * tint_p)
        roi[:, :, c] = roi[:, :, c] * (1.0 - mask) + text_color[c] * mask
    frame[by:by+box_h, bx:bx+box_w] = np.clip(roi, 0, 255).astype(np.uint8)
    
    # Connecting vector filaments between morphing particles
    if 0.15 < u < 0.85:
        np.random.seed(int(rel_t * 30) % 1000)
        num_p = 24
        p_nodes = []
        for _ in range(num_p):
            px = int(bx + np.random.uniform(0.12, 0.88) * box_w)
            py = int(by + np.random.uniform(0.25, 0.75) * box_h)
            p_nodes.append((px, py))
            cv2.circle(frame, (px, py), 3, (int(C_AMBER[0]), int(C_AMBER[1]), int(C_AMBER[2])), -1, cv2.LINE_AA)
            
        for i in range(len(p_nodes)):
            for j in range(i + 1, len(p_nodes)):
                dist = math.hypot(p_nodes[i][0] - p_nodes[j][0], p_nodes[i][1] - p_nodes[j][1])
                if dist < 180:
                    alpha_fil = (1.0 - dist / 180.0) * math.sin(np.pi * u) * 0.7
                    col_f = (C_AMBER * alpha_fil).astype(int)
                    cv2.line(frame, p_nodes[i], p_nodes[j], tuple(map(int, col_f)), 1, cv2.LINE_AA)

    return draw_hud(frame, "Act III // Hero Metamorphosis", "Continuous Signed Distance Field topology", phase=u)

def render_act_4_portal(t):
    """Act IV: The Counter Portal (23.0s - 31.0s)"""
    rel_t = t - 23.0
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    frame[:, :] = C_VOID
    draw_grid(frame)
    
    dolly_p = smoothstep(2.0, 7.5, rel_t)
    cam_zoom = 1.0 + 13.0 * (dolly_p ** 1.8)
    cx, cy = W // 2, H // 2
    
    y_grid, x_grid = np.ogrid[:H, :W]
    dist_center = np.sqrt((x_grid - cx)**2 + (y_grid - cy)**2)
    
    counter_r = 75.0 * cam_zoom
    outer_r = 240.0 * cam_zoom
    
    interior = np.zeros((H, W, 3), dtype=np.float32)
    interior[:, :] = C_VOID * 0.6
    
    num_rings = 8
    for r_i in range(num_rings):
        phase = (rel_t * 0.9 + r_i / num_rings) % 1.0
        ring_radius = int(counter_r * (phase ** 1.4))
        if ring_radius > 15:
            alpha_ring = math.sin(phase * math.pi)
            ring_col = (alpha_ring * C_AMBER + (1 - alpha_ring) * C_CYAN)
            cv2.circle(interior, (cx, cy), ring_radius, tuple(map(int, ring_col)), 2, cv2.LINE_AA)
            
            for angle in np.linspace(0, 2*np.pi, 16, endpoint=False):
                ax = int(cx + ring_radius * math.cos(angle))
                ay = int(cy + ring_radius * math.sin(angle))
                cv2.circle(interior, (ax, ay), 3, (245, 245, 245), -1, cv2.LINE_AA)
                
    in_glyph = np.clip((dist_center - counter_r) / 4.0, 0.0, 1.0) * np.clip((outer_r - dist_center) / 6.0, 0.0, 1.0)
    in_portal = np.clip((counter_r - dist_center) / 6.0, 0.0, 1.0)
    rim_glow = np.exp(-((dist_center - counter_r)**2) / (350.0 * min(3.0, cam_zoom)))
    
    comp = interior * in_portal[:, :, np.newaxis] + frame.astype(np.float32) * (1.0 - in_portal[:, :, np.newaxis])
    for c in range(3):
        comp[:, :, c] += rim_glow * C_AMBER[c] * 0.85
        comp[:, :, c] = comp[:, :, c] * (1.0 - in_glyph) + C_IVORY[c] * in_glyph
        
    frame = np.clip(comp, 0, 255).astype(np.uint8)
    return draw_hud(frame, "Act IV // The Counter Portal", "Negative space expansion into architectural dimension", phase=dolly_p)

def render_act_5_brand(t):
    """Act V: Master Convergence & Brand Payoff (31.0s - 42.0s)"""
    rel_t = t - 31.0
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    frame[:, :] = C_VOID
    draw_grid(frame)
    
    box_w, box_h = 1700, 450
    bx = (W - box_w) // 2
    by = (H - box_h) // 2 - 40
    
    p_converge = smoothstep(0.0, 2.5, rel_t)
    
    if rel_t < 2.5:
        np.random.seed(42)
        num_pts = 180
        for i in range(num_pts):
            orig_angle = np.random.uniform(0, 2*np.pi)
            orig_dist = np.random.uniform(600, 1200)
            target_x = bx + int(np.random.uniform(0.1, 0.9) * box_w)
            target_y = by + int(np.random.uniform(0.2, 0.8) * box_h)
            
            curr_x = int((1.0 - p_converge) * (W//2 + orig_dist * math.cos(orig_angle)) + p_converge * target_x)
            curr_y = int((1.0 - p_converge) * (H//2 + orig_dist * math.sin(orig_angle)) + p_converge * target_y)
            
            p_col = C_AMBER if i % 2 == 0 else C_CYAN
            cv2.circle(frame, (curr_x, curr_y), int(2 + 4 * (1 - p_converge)), tuple(map(int, p_col)), -1, cv2.LINE_AA)
            
    else: # 2.5s onwards: KINETIC Lockup
        lock_t = rel_t - 2.5
        p_lock = smoothstep(0.0, 1.2, lock_t)
        
        sdf_brand = sdf_cache.get("KINETIC", 260, box_w, box_h)
        mask = np.clip((sdf_brand + 2.0) / 4.0, 0.0, 1.0)
        
        breath = 0.5 + 0.5 * math.sin(lock_t * 1.5)
        corona = np.clip((sdf_brand + 25.0) / 30.0, 0.0, 1.0) * np.clip((8.0 - sdf_brand) / 16.0, 0.0, 1.0) * (0.35 + 0.35 * breath)
        
        roi = frame[by:by+box_h, bx:bx+box_w].astype(np.float32)
        for c in range(3):
            roi[:, :, c] += corona * C_AMBER[c]
            roi[:, :, c] = roi[:, :, c] * (1.0 - mask) + C_IVORY[c] * mask
        frame[by:by+box_h, bx:bx+box_w] = np.clip(roi, 0, 255).astype(np.uint8)
        
        rule_y = by + box_h - 40
        rule_p = smoothstep(0.6, 1.8, lock_t)
        rule_half = int(560 * rule_p)
        if rule_half > 0:
            cv2.line(frame, (W//2 - rule_half, rule_y), (W//2 + rule_half, rule_y), (int(C_AMBER[0]), int(C_AMBER[1]), int(C_AMBER[2])), 3, cv2.LINE_AA)
            
        if lock_t >= 1.2:
            p_tag = smoothstep(1.2, 2.6, lock_t)
            pil_im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_im)
            f_tag = ImageFont.truetype(INTER_BOLD, 26)
            tag_text = "M O T I O N   M A D E   M A N I F E S T"
            bbox = draw.textbbox((0, 0), tag_text, font=f_tag)
            tw = bbox[2] - bbox[0]
            tx = (W - tw) // 2
            ty = rule_y + 45
            alpha_tag = int(255 * p_tag)
            draw.text((tx, ty), tag_text, font=f_tag, fill=(alpha_tag, alpha_tag, alpha_tag))
            frame = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

        # Anamorphic optical flare sweep
        if 2.2 <= lock_t <= 4.8:
            flare_u = smoothstep(2.2, 4.8, lock_t)
            flare_x = int(bx + flare_u * box_w)
            flare_y = by + box_h // 2
            cv2.line(frame, (flare_x - 380, flare_y), (flare_x + 380, flare_y), (int(C_AMBER[0]*0.5), int(C_AMBER[1]*0.75), int(C_AMBER[2]*0.95)), 2, cv2.LINE_AA)
            cv2.circle(frame, (flare_x, flare_y), 18, (255, 235, 190), -1, cv2.LINE_AA)

    return draw_hud(frame, "Act V // Master Convergence", "KINETIC Brand Payoff Lockup", phase=smoothstep(0.0, 11.0, rel_t))

def render_hero_frame(t):
    if t < 7.0:
        return render_act_1_stroke(t)
    elif t < 15.0:
        return render_act_2_tension(t)
    elif t < 23.0:
        return render_act_3_morph(t)
    elif t < 31.0:
        return render_act_4_portal(t)
    else:
        return render_act_5_brand(t)

def render_loop_frame(t):
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    frame[:, :] = C_VOID
    draw_grid(frame)
    
    theta = 2.0 * math.pi * (t / LOOP_DURATION)
    box_w, box_h = 1700, 450
    bx = (W - box_w) // 2
    by = (H - box_h) // 2 - 40
    
    sdf_brand = sdf_cache.get("KINETIC", 260, box_w, box_h)
    
    wave_perturb = math.sin(theta) * 4.0 * np.sin(np.linspace(0, 4*math.pi, box_w))[np.newaxis, :]
    sdf_cyclic = sdf_brand + wave_perturb
    
    mask = np.clip((sdf_cyclic + 2.0) / 4.0, 0.0, 1.0)
    corona_phase = 0.5 + 0.5 * math.cos(theta)
    corona = np.clip((sdf_cyclic + 25.0) / 30.0, 0.0, 1.0) * np.clip((8.0 - sdf_cyclic) / 16.0, 0.0, 1.0) * (0.35 + 0.35 * corona_phase)
    
    roi = frame[by:by+box_h, bx:bx+box_w].astype(np.float32)
    for c in range(3):
        roi[:, :, c] += corona * C_AMBER[c]
        roi[:, :, c] = roi[:, :, c] * (1.0 - mask) + C_IVORY[c] * mask
    frame[by:by+box_h, bx:bx+box_w] = np.clip(roi, 0, 255).astype(np.uint8)
    
    rule_y = by + box_h - 40
    rule_half = int(560 + 30 * math.sin(theta))
    cv2.line(frame, (W//2 - rule_half, rule_y), (W//2 + rule_half, rule_y), (int(C_AMBER[0]), int(C_AMBER[1]), int(C_AMBER[2])), 3, cv2.LINE_AA)
    
    pil_im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_im)
    f_tag = ImageFont.truetype(INTER_BOLD, 26)
    tag_text = "M O T I O N   M A D E   M A N I F E S T"
    bbox = draw.textbbox((0, 0), tag_text, font=f_tag)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, rule_y + 45), tag_text, font=f_tag, fill=(240, 240, 240))
    frame = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
    
    return draw_hud(frame, "KINETIC LOOP // CONTINUOUS CYCLE", "Seamless topological resonance", phase=t/LOOP_DURATION)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["hero", "loop", "both"], default="both")
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    
    os.makedirs(os.path.join(BASE, "work/renders"), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    if args.kind in ["hero", "both"]:
        dur = args.duration or HERO_DURATION
        total_f = int(dur * FPS)
        out_raw = args.out or os.path.join(BASE, "work/renders/hero_raw_r04.mp4")
        print(f"Rendering hero film r04 ({dur:.2f}s, {total_f} frames @ {FPS}fps)...")
        vw = cv2.VideoWriter(out_raw, fourcc, FPS, (W, H))
        t0 = time.time()
        for f in range(total_f):
            t = args.start + f / FPS
            frame = render_hero_frame(t)
            vw.write(frame)
            if f % 200 == 0:
                print(f"  Hero r04 progress: frame {f}/{total_f} ({t:.2f}s) [{f/total_f*100:.1f}%]")
        vw.release()
        print(f"Completed hero r04 render in {time.time()-t0:.2f}s")
        
    if args.kind in ["loop", "both"]:
        dur = args.duration or LOOP_DURATION
        total_f = int(dur * FPS)
        out_raw = args.out or os.path.join(BASE, "work/renders/loop_raw_r04.mp4")
        print(f"Rendering loop film r04 ({dur:.2f}s, {total_f} frames @ {FPS}fps)...")
        vw = cv2.VideoWriter(out_raw, fourcc, FPS, (W, H))
        t0 = time.time()
        for f in range(total_f):
            t = args.start + f / FPS
            frame = render_loop_frame(t)
            vw.write(frame)
        vw.release()
        print(f"Completed loop r04 render in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    main()
