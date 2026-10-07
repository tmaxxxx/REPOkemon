"""Détoure les photos produits (fond blanc -> transparent), recadre et enregistre en .webp"""
import pathlib
from collections import deque
from PIL import Image
D = pathlib.Path(__file__).parent.parent / "produits"
def near_white(p, tol=28): return p[0] > 255 - tol and p[1] > 255 - tol and p[2] > 255 - tol
for f in sorted(D.glob("*.jpg")):
    im = Image.open(f).convert("RGBA"); w, h = im.size; px = im.load()
    seen = bytearray(w * h); q = deque()
    for x in range(w): q += [(x, 0), (x, h - 1)]
    for y in range(h): q += [(0, y), (w - 1, y)]
    while q:
        x, y = q.popleft(); i = y * w + x
        if seen[i] or not near_white(px[x, y]): continue
        seen[i] = 1; px[x, y] = (255, 255, 255, 0)
        if x > 0: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y > 0: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))
    im = im.crop(im.getbbox())
    im.thumbnail((800, 800))
    im.save(f.with_suffix(".webp"), quality=88)
    print(f.name, im.size)
