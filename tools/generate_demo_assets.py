"""Generate original geometric demo assets. Optional: Pillow and FFmpeg.

The generated files are included, so normal installation need not run this script.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'frontend/public/demo'
OUT.mkdir(parents=True, exist_ok=True)
for name, color in [('notes', (34, 211, 238)), ('frames', (244, 114, 182)), ('play', (167, 139, 250))]:
    im = Image.new('RGB', (1200, 675), '#090c16')
    d = ImageDraw.Draw(im)
    for x in range(0, 1200, 40): d.line((x, 0, x, 675), fill='#171e31')
    for y in range(0, 675, 40): d.line((0, y, 1200, y), fill='#171e31')
    for i in range(16):
        inset = i * 16
        shade = tuple(int(c * (0.25 + 0.75 * i / 16)) for c in color)
        d.ellipse((350 + inset, 90 + inset // 2, 1050 - inset, 600 - inset // 2), outline=shade, width=3)
    d.rectangle((70, 60, 180, 68), fill=color)
    d.text((70, 480), 'ECLIPSE', font=ImageFont.load_default(size=64), fill='white')
    d.text((74, 565), name.upper() + ' / TEMPLATE DEMO', font=ImageFont.load_default(size=22), fill=color)
    im.save(OUT / f'{name}.png')
subprocess.run([
    'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi',
    '-i', 'gradients=s=960x540:r=24:c0=0x080b19:c1=0x253b66:c2=0x503558:c3=0x125362:n=4:speed=0.08:seed=42',
    '-t', '8', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '25',
    '-movflags', '+faststart', str(OUT / 'ambient.mp4'),
], check=True)
print('Generated 3 covers and 1 silent abstract video.')
