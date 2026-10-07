"""Télécharge les cartes (nom FR, rareté, cote USD) des séries depuis l'API TCGdex.
Usage : python3 outils/fetch_sets.py            -> toutes les séries, écrit outils/raw.json
        python3 outils/fetch_sets.py xy5 bw10   -> seulement ces séries (les autres sont gardées)"""
import json, sys, urllib.request, concurrent.futures as cf, pathlib

SETS = ["base1", "base3", "sv03.5", "swsh7", "sv08.5", "30th", "30th-c", "xy5", "bw10"]
API = "https://api.tcgdex.net/v2"
RAW = pathlib.Path(__file__).with_name("raw.json")

def get(url):
    for _ in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "repokemon"}), timeout=30) as r:
                return json.load(r)
        except Exception as e:
            err = e
    raise err

def card(cid):
    fr, en = get(f"{API}/fr/cards/{cid}"), get(f"{API}/en/cards/{cid}")
    return {"id": cid, "localId": fr["localId"], "name": fr["name"], "rarity": fr.get("rarity"),
            "rarity_en": en.get("rarity"), "image": fr.get("image"), "variants": fr.get("variants"),
            "pricing": en.get("pricing") or fr.get("pricing")}

wanted = sys.argv[1:] or SETS
out = json.loads(RAW.read_text()) if RAW.exists() and sys.argv[1:] else {}
with cf.ThreadPoolExecutor(16) as ex:
    for s in wanted:
        ids = [c["id"] for c in get(f"{API}/fr/sets/{s}")["cards"]]
        out[s] = list(ex.map(card, ids))
        print(s, len(out[s]))
RAW.write_text(json.dumps(out, ensure_ascii=False))
