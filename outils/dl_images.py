"""Télécharge les images FR des cartes (TCGdex) dans cartes/<série>/<numéro>.webp"""
import json, pathlib, urllib.request, concurrent.futures as cf
ROOT = pathlib.Path(__file__).parent.parent
FOLDER = {"base1": "base", "base3": "fossile", "sv03.5": "151", "swsh7": "evs", "sv08.5": "pre", "30th": "30th",
          "xy5": "primo", "bw10": "plasma"}
raw = json.loads((ROOT / "outils/raw.json").read_text())
jobs = []
for s, folder in FOLDER.items():
    (ROOT / "cartes" / folder).mkdir(parents=True, exist_ok=True)
    for c in raw[s]:
        if s == "30th" and c["localId"].isdigit():
            continue  # déjà dans cartes/001.jpg…
        jobs.append((c["image"] + "/high.webp", ROOT / "cartes" / folder / (c["localId"] + ".webp")))
def dl(job):
    url, dest = job
    if dest.exists() and dest.stat().st_size > 1000: return
    for _ in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "repokemon"}), timeout=40) as r:
                dest.write_bytes(r.read()); return
        except Exception: pass
    print("ÉCHEC", url)
with cf.ThreadPoolExecutor(16) as ex: list(ex.map(dl, jobs))
print("ok", len(jobs))
