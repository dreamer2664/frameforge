#!/usr/bin/env python3
"""lithos logo - 'stone cut with light'. SVG + PNG deliverables + in-film mark.

The mark: a hexagonal stone facet with a chiseled seam of light through it and
a bright core. Reads at 16 px; works on dark and light.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw


def hexagon(cx, cy, r, rot=0.0):
    return [(cx + r * math.cos(rot + i * math.pi / 3),
             cy + r * math.sin(rot + i * math.pi / 3)) for i in range(6)]


def svg(out_path, size=512, fg="#F4F6FB", seam="#FFB347", bg=None):
    c, r = size / 2, size * 0.42
    pts = hexagon(c, c, r, rot=math.pi / 6)
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    ang = math.radians(-58)

    def P(d, w):
        return (c + d * math.cos(ang) + w * math.cos(ang + math.pi / 2),
                c + d * math.sin(ang) + w * math.sin(ang + math.pi / 2))
    s1, s2 = P(-r * 0.72, -r * 0.06), P(r * 0.72, -r * 0.06)
    s3, s4 = P(r * 0.72, r * 0.06), P(-r * 0.72, r * 0.06)
    seam_poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in (s1, s2, s3, s4))
    facets = "".join(
        f'<line x1="{c:.1f}" y1="{c:.1f}" x2="{p[0]:.1f}" y2="{p[1]:.1f}" '
        f'stroke="{fg}" stroke-opacity="0.18" stroke-width="{size * 0.008:.1f}"/>'
        for p in pts)
    bgrect = f'<rect width="{size}" height="{size}" fill="{bg}"/>' if bg else ""
    doc = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
{bgrect}
<polygon points="{poly}" fill="{fg}"/>
{facets}
<polygon points="{seam_poly}" fill="{seam}"/>
<circle cx="{c:.1f}" cy="{c:.1f}" r="{size * 0.055:.1f}" fill="{seam}"/>
</svg>'''
    Path(out_path).write_text(doc)
    return out_path


def mark_rgba(size=512, fg=(244, 246, 251), seam=(255, 179, 71)):
    """Raster mark with alpha, for compositing in the film."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r = size / 2, size * 0.42
    d.polygon(hexagon(c, c, r, rot=math.pi / 6), fill=fg + (255,))
    ang = math.radians(-58)

    def P(dd, w):
        return (c + dd * math.cos(ang) + w * math.cos(ang + math.pi / 2),
                c + dd * math.sin(ang) + w * math.sin(ang + math.pi / 2))
    quad = [P(-r * 0.72, -r * 0.06), P(r * 0.72, -r * 0.06),
            P(r * 0.72, r * 0.06), P(-r * 0.72, r * 0.06)]
    d.polygon(quad, fill=seam + (255,))
    rr = size * 0.055
    d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=seam + (255,))
    return im


if __name__ == "__main__":
    out = Path("out")
    out.mkdir(exist_ok=True)
    svg(out / "lithos-logo.svg", 512)
    mark_rgba(512).save(out / "lithos-logo.png")
    mark_rgba(512, fg=(10, 15, 30), seam=(255, 179, 71)).save(out / "lithos-logo-dark.png")
    print("logo written:", sorted(str(p) for p in out.glob("lithos-logo*")))
