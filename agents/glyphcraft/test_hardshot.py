"""Hard-shot prototype renderer: testing 6.0s of Act III Hero Morph (FORM -> MOTION)
Tests Signed Distance Field continuous interpolation, glow integration, and audio mux.
"""
import os, sys, time, subprocess
import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw, ImageFilter

W, H = 1920, 1080
FPS = 30
DURATION = 6.0
TOTAL_FRAMES = int(FPS * DURATION)

FONT_PATH = "frameforge/agents/glyphcraft/fonts/Fraunces.ttf"
INTER_PATH = "frameforge/agents/glyphcraft/fonts/Inter-Bold.ttf"

def make_text_sdf(text, font_size, box_w, box_h, font_p=FONT_PATH):
    font = ImageFont.truetype(font_p, font_size)
    im = Image.new('L', (box_w, box_h), 0)
    draw = ImageDraw.Draw(im)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (box_w - tw) // 2 - bbox[0]
    ty = (box_h - th) // 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=255)
    arr = np.array(im)
    
    # Compute signed distance field
    d_in = cv2.distanceTransform(arr, cv2.DIST_L2, 5)
    d_out = cv2.distanceTransform(255 - arr, cv2.DIST_L2, 5)
    sdf = d_in - d_out
    return sdf

print("Precomputing SDFs for FORM and MOTION...")
t0 = time.time()
BOX_W, BOX_H = 1600, 500
sdf_form = make_text_sdf("FORM", 260, BOX_W, BOX_H)
sdf_motion = make_text_sdf("MOTION", 230, BOX_W, BOX_H)
print(f"Precomputed SDFs in {time.time()-t0:.2f}s")

def render_frame(t):
    # Normalized progress in the 6.0s shot
    # 0.0 - 1.5s: FORM holds with dynamic tension pulse
    # 1.5 - 4.0s: Hero topological SDF metamorphosis FORM -> MOTION
    # 4.0 - 6.0s: MOTION resolves with radiant kinetic amber corona
    p = t / DURATION

    # Background: deep obsidian gradient
    bg = np.zeros((H, W, 3), dtype=np.uint8)
    bg[:, :] = [10, 12, 16] # BGR [16, 12, 10]
    
    # Add subtle background grid lines (Inter precision)
    grid_alpha = 0.15
    grid_color = (40, 45, 60)
    for y in range(100, H, 160):
        cv2.line(bg, (100, y), (W - 100, y), grid_color, 1, cv2.LINE_AA)
    for x in range(160, W, 200):
        cv2.line(bg, (x, 100), (x, H - 100), grid_color, 1, cv2.LINE_AA)

    # Calculate morph blend parameter alpha
    if t < 1.5:
        alpha = 0.0
        # subtle breathing scale
        scale = 1.0 + 0.02 * np.sin(t * 4.0)
    elif t < 4.0:
        # Smooth S-curve easing
        u = (t - 1.5) / 2.5
        alpha = u * u * (3.0 - 2.0 * u) # smoothstep
        scale = 1.0 + 0.08 * np.sin(np.pi * u) # tension ballooning during morph
    else:
        alpha = 1.0
        scale = 1.0

    # Interpolate SDFs
    sdf_blend = (1.0 - alpha) * sdf_form + alpha * sdf_motion
    
    # Add dynamic kinetic turbulence to SDF during mid-morph
    if 0.0 < alpha < 1.0:
        turb = np.sin(np.linspace(0, 12*np.pi, BOX_W)) * 6.0 * np.sin(np.pi * alpha)
        sdf_blend = sdf_blend + turb[np.newaxis, :]

    # Convert SDF to antialiased mask
    # Inside is sdf > 0
    mask = np.clip((sdf_blend + 2.0) / 4.0, 0.0, 1.0)
    
    # Create amber glow corona from SDF proximity [-15, 5]
    corona = np.clip((sdf_blend + 25.0) / 30.0, 0.0, 1.0) * np.clip((10.0 - sdf_blend) / 20.0, 0.0, 1.0)
    
    # Compose text onto canvas
    # Bounding box center: (W//2, H//2)
    bx1 = (W - BOX_W) // 2
    by1 = (H - BOX_H) // 2
    
    # Render into BGR layer
    roi = bg[by1:by1+BOX_H, bx1:bx1+BOX_W].astype(np.float32)
    
    # Colors (BGR)
    ivory = np.array([238, 244, 246], dtype=np.float32)
    amber = np.array([59, 158, 255], dtype=np.float32) # #ff9e3b in BGR
    cyan = np.array([240, 201, 76], dtype=np.float32)
    
    # Morph tint: shifts from ivory -> molten amber -> ivory
    tint_p = np.sin(np.pi * alpha)
    text_color = (1.0 - tint_p) * ivory + tint_p * amber
    
    # Apply corona glow
    for c in range(3):
        roi[:, :, c] += corona * amber[c] * 0.45 * (0.5 + 0.5 * tint_p)
        roi[:, :, c] = roi[:, :, c] * (1.0 - mask) + text_color[c] * mask
        
    bg[by1:by1+BOX_H, bx1:bx1+BOX_W] = np.clip(roi, 0, 255).astype(np.uint8)
    
    # Add technical metadata HUD (Inter font)
    # PIL draw overlay for razor-sharp typography
    pil_img = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    inter_small = ImageFont.truetype(INTER_PATH, 18)
    draw.text((120, 960), "TOPOLOGICAL METAMORPHOSIS // VECTOR CONTINUUM", font=inter_small, fill=(160, 175, 195))
    draw.text((1600, 960), f"PHASE: {alpha*100:05.1f}%", font=inter_small, fill=(255, 158, 59))
    draw.text((120, 100), "KINETIC MOTION LAB", font=inter_small, fill=(100, 120, 140))
    
    # Convert back to BGR for video frame
    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return frame

out_mp4 = "frameforge/agents/glyphcraft/work/renders/hardshot_raw.mp4"
os.makedirs("frameforge/agents/glyphcraft/work/renders", exist_ok=True)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
vw = cv2.VideoWriter(out_mp4, fourcc, FPS, (W, H))

print(f"Rendering {TOTAL_FRAMES} frames for hardshot prototype...")
for f in range(TOTAL_FRAMES):
    t = f / FPS
    frame = render_frame(t)
    vw.write(frame)
vw.release()
print(f"Wrote raw prototype to {out_mp4}")
