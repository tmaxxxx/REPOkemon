"""Construit data.js (cartes, raretés, cotes USD, produits scellés) à partir de outils/raw.json.
Usage : python3 outils/fetch_sets.py && python3 outils/build_data.py"""
import json, pathlib, datetime
ROOT = pathlib.Path(__file__).parent.parent
raw = json.loads((ROOT / "outils/raw.json").read_text())
EUR_USD = 1.17  # conversion des cotes Cardmarket (EUR) quand il n'y a pas de cote TCGplayer

def usd(c):
    p = c.get("pricing") or {}
    tp = p.get("tcgplayer") or {}
    for k in ("holofoil", "normal", "unlimitedHolofoil", "unlimited", "1stEditionHolofoil", "1stEdition", "reverse-holofoil"):
        v = tp.get(k)
        if isinstance(v, dict) and v.get("marketPrice"):
            return round(v["marketPrice"], 2)
    cm = p.get("cardmarket") or {}
    eur = cm.get("avg30") or cm.get("trend") or cm.get("avg")
    return round(max(eur or 0, 0.02) * EUR_USD, 2) if eur is not None else 0.05

CARDS = []
def add(id_, set_, n, num, name, r, price, img, tcg):
    CARDS.append([id_, set_, n, num, name, r, max(price, 0.02), img, tcg])

# --- Set de Base / Fossile -------------------------------------------------
for key, folder, nholo in (("base1", "base", 16), ("base3", "fossile", 15)):
    total = len(raw[key])
    for c in raw[key]:
        n = int(c["localId"])
        r = {"Commune": "C", "Peu Commune": "U", "Rare": "R"}[c["rarity"]]
        if n <= nholo: r = "H"
        if key == "base1" and n >= 96: r = "E"
        add(f"{folder}-{n}", folder, n, f"{n}/{total}", c["name"], r, usd(c), f"cartes/{folder}/{c['localId']}.webp", c["id"])

# --- 151 / Évolutions Prismatiques -----------------------------------------
SV = {"Commune": "C", "Peu Commune": "U", "Rare": "R", "Double rare": "DR", "Illustration rare": "IR",
      "Ultra Rare": "UR", "Illustration spéciale rare": "SIR", "Hyper rare": "GR", "HIGH-TECH rare": "ACE"}
for key, folder, off in (("sv03.5", "151", 165), ("sv08.5", "pre", 131)):
    for c in raw[key]:
        n = int(c["localId"])
        add(f"{folder}-{n}", folder, n, f"{c['localId']}/{off}", c["name"], SV[c["rarity"]], usd(c), f"cartes/{folder}/{c['localId']}.webp", c["id"])

# --- Évolution Céleste ------------------------------------------------------
ALT_V = {167, 175, 180, 184, 186, 189, 192, 194, 196, 198}
ALT_VMAX = {205, 209, 212, 215, 218, 220}
EVS = {"Commune": "C", "Peu Commune": "U", "Rare": "R", "Holo Rare": "H", "Holo Rare V": "V", "Holo Rare VMAX": "VMAX", "Ultra Rare": "UR", "Magnifique rare": "SR"}
for c in raw["swsh7"]:
    n = int(c["localId"]); r = EVS[c["rarity"]]
    if n in ALT_V: r = "AA"
    if n in ALT_VMAX: r = "AAS"
    if n >= 226: r = "GR"
    add(f"evs-{n}", "evs", n, f"{c['localId']}/203", c["name"], r, usd(c), f"cartes/evs/{c['localId']}.webp", c["id"])

# --- Primo-Choc (XY) / Explosion Plasma (Noir et Blanc) -----------------------
# TCGdex ne distingue pas les Rares des Rares Holo : une carte vendue en "holofoil" sur TCGplayer est une Holo.
# Cotes TCGplayer (market price, 01/10/2026) des cartes absentes de TCGdex :
MISSING = {"bw10-9": 8.04, "bw10-11": 27.31, "bw10-30": 13.22, "bw10-60": 28.83, "bw10-65": 36.37, "bw10-66": 21.88,
           "bw10-96": 52.21, "bw10-97": 282.36, "bw10-98": 189.95, "bw10-99": 393.66, "bw10-100": 555.13}
OLD = {"Commune": "C", "Peu Commune": "U", "Rare": "R", "Ultra Rare": "UR", "Magnifique rare": "GR"}
for key, folder, total, ex, ace in (("xy5", "primo", 160, {19, 29, 38, 54, 55, 85, 86, 91, 93, 94, 105, 106}, set()),
                                    ("bw10", "plasma", 101, {9, 11, 30, 60, 65, 66}, {92, 93, 94, 95})):
    for c in raw[key]:
        n = int(c["localId"]); r = OLD[c["rarity"]]
        tp = (c.get("pricing") or {}).get("tcgplayer") or {}
        if r == "R" and "holofoil" in tp: r = "H"
        if n in ex: r = "EX"
        if n in ace: r = "ACE"
        price = MISSING.get(c["id"]) or usd(c)
        add(f"{folder}-{n}", folder, n, f"{n}/{total}", c["name"], r, price, f"cartes/{folder}/{c['localId']}.webp", c["id"])

# --- 30e Anniversaire (images déjà dans cartes/) -----------------------------
R30 = {"Commune": "C", "Rare": "R", "Double rare": "DR", "Pikachu Rare": "PR", "Illustration rare": "IR",
       "Illustration spéciale rare": "SIR", "Futuristic Rare": "FR"}
for c in raw["30th"]:
    if not c["localId"].isdigit(): continue  # Mew RGB : pas d'image disponible
    n = int(c["localId"])
    add(f"S{n:03d}", "30th", n, f"{n:03d}/128", c["name"], R30[c["rarity"]], usd(c), f"cartes/{n:03d}.jpg", c["id"])
# Collection Classique : C01…C30 (ordre de nos images) -> numéro TCGdex
CLASSIC = [14, 1, 5, 15, 7, 24, 29, 2, 6, 25, 3, 22, 10, 11, 18, 19, 20, 21, 16, 4, 23, 9, 17, 13, 8, 28, 12, 26, 27, 30]
cc = {int(c["localId"]): c for c in raw["30th-c"]}
for i, k in enumerate(CLASSIC, 1):
    c = cc[k]
    add(f"C{i:02d}", "30th", 200 + i, f"{k:03d}/030 CC", c["name"], "CC", usd(c), f"cartes/C{i:02d}.jpg", c["id"])
for n, t in [(9, "Plante"), (10, "Feu"), (11, "Eau"), (12, "Électrique"), (13, "Psy"), (14, "Combat"), (15, "Obscurité"), (16, "Métal")]:
    add(f"E{n:02d}", "30th", 300 + n, f"{n:03d} É", "Énergie " + t, "E", 0.05, f"cartes/E{n:02d}.jpg", None)

# --- Produits scellés : cote TCGplayer (market price) relevée le 01/10/2026 ----
# id = n° de produit TCGplayer (image dans produits/<id>.webp)
PRODUCTS = [
    # série,     id,     type,      boosters, prix USD
    ("base",    138130, "booster",  1,    927.56),
    ("base",    185731, "display",  36, 38750.00),  # vente aux enchères du 17/09/2026
    ("fossile", 138134, "booster",  1,    319.67),
    ("fossile", 107600, "display",  36, 16250.00),  # ventes Heritage Auctions 2026
    ("151",     504467, "booster",  1,     29.62),
    ("151",     502000, "bundle",   6,    169.40),
    ("151",     503313, "etb",      9,    491.68),
    ("evs",     244337, "booster",  1,     45.00),
    ("evs",     242434, "etb",      8,    569.58),
    ("evs",     242436, "display",  36,  2296.51),
    ("pre",     593294, "booster",  1,     14.20),
    ("pre",     600518, "bundle",   6,     83.38),
    ("pre",     593355, "etb",      9,    135.71),
    # 30e Anniversaire : cote réelle ×1,364 (booster 15,16 $ -> 20,68 $). Les cartes de la série viennent de sortir
    # et leur cote est gonflée : au vrai prix, un booster rapporterait 123 % de ce qu'il coûte (argent infini).
    # À 20,68 $, il rend ~90 % en moyenne, comme les autres séries rendent moins de 100 %.
    ("30th",    696613, "booster",  1,     20.68),
    ("30th",    704171, "bundle",   6,    125.03),
    ("30th",    704143, "etb",      9,    222.90),
    ("primo",    97751, "booster",  1,     64.38),
    ("primo",    97750, "display",  36,  3799.99),
    ("plasma",   98573, "booster",  1,    275.45),
    ("plasma",   98572, "display",  36, 12311.00),  # médiane de 5 ventes eBay (mai-août 2026 : 10 368 à 13 250 $)
    ("plasma",  190571, "etb",      8,  6850.00),   # ventes eBay 2026 entre 6 000 et 7 700 $ (image : CoolStuffInc 190571)
]
out = "/* Généré par outils/build_data.py — ne pas modifier à la main */\n"
out += f"const PRICE_DATE = {json.dumps(datetime.date.today().isoformat())};\n"
out += "// [id, série, ordre, numéro, nom, rareté, cote USD, image, id TCGdex]\n"
out += "const CARD_DATA = [\n" + ",\n".join(json.dumps(c, ensure_ascii=False) for c in CARDS) + "];\n"
out += "// [série, id produit, type, nb boosters, prix USD]\n"
out += "const PRODUCT_DATA = " + json.dumps(PRODUCTS) + ";\n"
(ROOT / "data.js").write_text(out)
print(len(CARDS), "cartes")
