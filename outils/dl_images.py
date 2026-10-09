"""Télécharge les images FR des cartes (TCGdex) dans cartes/<série>/<numéro>.webp"""
import json, pathlib, urllib.request, urllib.error, concurrent.futures as cf
ROOT = pathlib.Path(__file__).parent.parent
FOLDER = {"base1": "base", "base3": "fossile", "sv03.5": "151", "swsh7": "evs", "sv08.5": "pre", "30th": "30th",
          "xy5": "primo", "bw10": "plasma", "sv10.5b": "blk", "hgss1": "hgss"}
raw = json.loads((ROOT / "outils/raw.json").read_text())
jobs = []
for s, folder in FOLDER.items():
    (ROOT / "cartes" / folder).mkdir(parents=True, exist_ok=True)
    for c in raw[s]:
        if s == "30th" and c["localId"].isdigit():
            continue  # déjà dans cartes/001.jpg…
        if not c.get("image"): continue
        jobs.append((c["image"] + "/high.webp", ROOT / "cartes" / folder / (c["localId"] + ".webp")))
def dl(job):
    url, dest = job
    if dest.exists() and dest.stat().st_size > 1000: return
    # pas d'image FR (ex. Foudre Noire) -> image anglaise
    for u in (url, url.replace("/fr/", "/en/")):
        for _ in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "repokemon"}), timeout=40) as r:
                    dest.write_bytes(r.read()); return
            except urllib.error.HTTPError: break
            except Exception: pass
    print("ÉCHEC", url)
with cf.ThreadPoolExecutor(16) as ex: list(ex.map(dl, jobs))
print("ok", len(jobs))
