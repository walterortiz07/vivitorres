# external_data.py
import os
import json
import requests
from pathlib import Path
from urllib.parse import quote_plus
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static" / "especies"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    text = text.lower().strip()
    for ch in " áéíóúñäëïöü/(),.'":
        text = text.replace(ch, "_")
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_")


def _cached_path(scientific_name: str) -> Path:
    slug = slugify(scientific_name)
    return STATIC_DIR / f"{slug}.json"


def _save_image(url: str, scientific_name: str) -> Optional[str]:
    if not url:
        return None

    slug = slugify(scientific_name)
    folder = STATIC_DIR / slug
    folder.mkdir(parents=True, exist_ok=True)
    img_path = folder / "image.jpg"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception:
        return None

    with open(img_path, "wb") as f:
        f.write(r.content)

    rel = os.path.relpath(img_path, BASE_DIR / "static")
    return "/static/" + rel.replace(os.sep, "/")


def fetch_from_inaturalist(scientific_name: str) -> dict:
    url = (
        "https://api.inaturalist.org/v1/taxa"
        "?q={}&per_page=1".format(quote_plus(scientific_name))
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return {}

    if not data.get("results"):
        return {}

    taxon = data["results"][0]

    info = {
        "source": "iNaturalist",
        "scientific_name": taxon.get("name") or scientific_name,
        "common_name": taxon.get("preferred_common_name"),
        "summary": taxon.get("wikipedia_summary"),
        "images_remote": [],
        "image_local": None,
        "url": "https://www.inaturalist.org/taxa/{}".format(taxon.get("id")),
    }

    photo_url = None
    if taxon.get("default_photo"):
        photo_url = (
            taxon["default_photo"].get("medium_url")
            or taxon["default_photo"].get("square_url")
        )

    if not photo_url and taxon.get("photos"):
        photo_url = taxon["photos"][0].get("medium_url")

    if photo_url:
        info["images_remote"].append(photo_url)
        local = _save_image(photo_url, scientific_name)
        if local:
            info["image_local"] = local

    return info


def fetch_from_gbif(scientific_name: str) -> dict:
    base = "https://api.gbif.org/v1"
    match_url = base + "/species/match?name={}".format(quote_plus(scientific_name))

    try:
        resp = requests.get(match_url, timeout=10)
        resp.raise_for_status()
        match = resp.json()
    except Exception:
        return {}

    key = match.get("usageKey") or match.get("speciesKey")
    if not key:
        return {}

    try:
        tax_resp = requests.get(base + "/species/{}".format(key), timeout=10)
        tax_resp.raise_for_status()
        tax = tax_resp.json()
    except Exception:
        tax = {}

    countries = []
    try:
        occ_url = (
            base
            + "/occurrence/search?taxon_key={}&limit=0&facet=country&facetLimit=20".format(
                key
            )
        )
        occ_resp = requests.get(occ_url, timeout=10)
        occ_resp.raise_for_status()
        occ = occ_resp.json()
        for facet in occ.get("facets", []):
            if facet.get("field") == "COUNTRY":
                for c in facet.get("counts", []):
                    countries.append(c.get("name"))
    except Exception:
        pass

    return {
        "source": "GBIF",
        "gbif_key": key,
        "kingdom": tax.get("kingdom"),
        "phylum": tax.get("phylum"),
        "class": tax.get("class"),
        "order": tax.get("order"),
        "family": tax.get("family"),
        "genus": tax.get("genus"),
        "species": tax.get("species"),
        "vernacular_name": tax.get("vernacularName"),
        "countries": countries,
        "url": "https://www.gbif.org/species/{}".format(key),
    }


def get_species_info(scientific_name: str) -> dict:
    cache_path = _cached_path(scientific_name)

    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text("utf-8"))
        except Exception:
            pass

    inat = fetch_from_inaturalist(scientific_name)
    gbif = fetch_from_gbif(scientific_name)

    info = {
        "scientific_name": scientific_name,
        "inat": inat,
        "gbif": gbif,
    }

    cache_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), "utf-8")
    return info
