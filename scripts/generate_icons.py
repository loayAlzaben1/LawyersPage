"""
Generate simple scales-of-justice PNG icons at multiple common favicon sizes using Pillow.
Writes files into static/img/
Requires Pillow to be installed in the environment that runs the script.
"""
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img')
os.makedirs(OUT_DIR, exist_ok=True)

BACKGROUND = (13, 110, 253, 255)  # #0d6efd
FOREGROUND = (255, 255, 255, 255)

sizes = {
    'favicon-16x16.png': 16,
    'favicon-32x32.png': 32,
    'apple-touch-icon.png': 180,
    'android-chrome-192x192.png': 192,
    'android-chrome-512x512.png': 512,
}

def draw_scales(draw, w, h, fg):
    # Draw a centered simplified scales icon using basic shapes
    # central pillar
    pw = max(2, w // 20)
    ph = int(h * 0.4)
    px = w // 2 - pw // 2
    py = int(h * 0.15)
    draw.rectangle([px, py, px + pw, py + ph], fill=fg)
    # base plate
    bw = int(w * 0.25)
    bh = max(2, h // 40)
    bx = w // 2 - bw // 2
    by = py + ph
    draw.rectangle([bx, by, bx + bw, by + bh], fill=fg)
    # beam
    beam_h = max(2, h // 28)
    beam_w = int(w * 0.6)
    bx1 = w // 2 - beam_w // 2
    by1 = py
    draw.rectangle([bx1, by1, bx1 + beam_w, by1 + beam_h], fill=fg)
    # left chain/pan
    lx1 = bx1 + int(beam_w * 0.12)
    ly1 = by1
    lx2 = lx1 - int(w * 0.12)
    ly2 = by1 + int(h * 0.2)
    draw.line([lx1, ly1 + beam_h//2, lx2, ly2], fill=fg, width=max(1, w//60))
    # left pan
    pan_w = int(w * 0.16)
    pan_h = max(2, int(h * 0.05))
    draw.ellipse([lx2 - pan_w//2, ly2, lx2 + pan_w//2, ly2 + pan_h], fill=fg)
    # right chain/pan
    rx1 = bx1 + int(beam_w * 0.88)
    ry1 = by1
    rx2 = rx1 + int(w * 0.12)
    ry2 = by1 + int(h * 0.2)
    draw.line([rx1, ry1 + beam_h//2, rx2, ry2], fill=fg, width=max(1, w//60))
    draw.ellipse([rx2 - pan_w//2, ry2, rx2 + pan_w//2, ry2 + pan_h], fill=fg)

for name, size in sizes.items():
    im = Image.new('RGBA', (size, size), BACKGROUND)
    draw = ImageDraw.Draw(im)
    draw_scales(draw, size, size, FOREGROUND)
    out_path = os.path.join(OUT_DIR, name)
    im.save(out_path)
    print('Wrote', out_path)

# Create favicon.ico with 16x16 and 32x32
ico_sizes = [(16,16), (32,32)]
ico_path = os.path.join(OUT_DIR, 'favicon.ico')
imgs = []
for s in [16,32]:
    imgs.append(Image.open(os.path.join(OUT_DIR, f'favicon-{s}x{s}.png')))
imgs[0].save(ico_path, sizes=[(16,16),(32,32)])
print('Wrote', ico_path)
