"""Couvertures du classeur : découpe l'illustration du booster de chaque série (sans ses logos imprimés) -> couvertures/<série>.webp.

Zone = (centre x, haut, bas) en fraction de la photo du booster ; la largeur suit la fenêtre de la couverture (0,86 × hauteur).
Pour une nouvelle série : ajouter sa zone ici, lancer le script, vérifier l'image.
Lancer : python3 outils/couvertures.py
"""
import re
from pathlib import Path

from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
ZONES = {"30th": (.46, .31, .66), "151": (.52, .31, .65), "pre": (.48, .32, .67), "dr": (.5, .30, .655), "evs": (.5, .31, .665),
         "primo": (.5, .32, .72), "plasma": (.5, .31, .72), "blk": (.5, .31, .645), "hgss": (.52, .31, .70),
         "fossile": (.47, .37, .80), "base": (.5, .47, .835)}

boosters = dict(re.findall(r'\{ id: "([^"]+)", unlock: \d+, name: "[^"]+", year: \d+, color: "[^"]+", booster: "(\d+)"',
                           (RACINE / "index.html").read_text()))
(RACINE / "couvertures").mkdir(exist_ok=True)
for serie, (cx, haut, bas) in ZONES.items():
    im = Image.open(RACINE / "produits" / f"{boosters[serie]}.webp").convert("RGB")
    W, H = im.size
    h = (bas - haut) * H
    w = min(W * .96, h * .86)
    c = im.crop((round(cx * W - w / 2), round(haut * H), round(cx * W + w / 2), round(bas * H)))
    c.resize((480, round(480 * c.height / c.width)), Image.LANCZOS).save(RACINE / "couvertures" / f"{serie}.webp", "WEBP", quality=86)
    print(serie, "ok")
