"""Índice derivado del mapa: las composiciones y fichas personales siguen siendo canónicas.

Los dosieres del Senado identifican la formación presidencial de cada mandato,
que puede ser una coalición, no una certificación de militancia diaria.
No completar huecos presidenciales ni gabinetes con fechas desconocidas.
"""
import concurrent.futures
import hashlib
import json
import pathlib
import re
import sys
import unicodedata
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "test-results/libraries"))
from bs4 import BeautifulSoup

CACHE = ROOT / "test-results/legislaturas-mapa"
CACHE.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "Gobiernos/Autonomías"
CHECKED = "2026-10-17"
DOSSIERS = dict(enumerate([
    "pais-vasco", "cataluna", "galicia", "andalucia", "asturias", "cantabria",
    "la-rioja", "murcia", "valencia", "aragon", "castilla-la-mancha", "canarias",
    "navarra", "extremadura", "baleares", "madrid", "castilla-y-leon",
], 1))

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def norm(s):
    return " ".join("".join(c for c in unicodedata.normalize("NFD", s.lower())
                           if unicodedata.category(c) != "Mn").split())

# Variantes contrastadas expresamente, nunca correspondencias por semejanza.
ALIASES = {
    "Antonio Ramón María Trevín Lombán": "Antonio Ramón Trevín Lombán",
    "Iñigo Urkullu Renteria": "Iñigo Urkullu Rentería",
    "Pasqual Maragall i Mira": "Pascual Maragall i Mira",
    "Joaquim Torra Pla": "Joaquim Torra i Plá",
    "Manuel María Chaves González": "Manuel Chaves González",
    "Pedro Silva Cienfuegos-Jovellanos": "Pedro de Silva Cienfuegos-Jovellanos",
    "María José Sáenz de Buruaga Gómez": "María José Sanz de Buruaga",
    "José Joaquín Martínez Sieso": "José Joaquín Martínez Sieso",
    "Juan Ignacio Diego Palacios": "Juan Ignacio Diego Palacios",
    "Joaquín Espert Pérez-caballero": "Joaquín Espert Pérez-Caballero",
    "Pedro María Sanz Alonso": "Pedro Sanz Alonso",
    "María Antonia Martínez García": "Mª Antonia Martínez García",
    "Eduardo Andrés Julio Zaplana Hernández-Soro": "Eduardo Zaplana Hernández-Soro",
    "Joaquín Francisco Puig Ferrer": "Ximo Puig i Ferrer",
    "Adán Martín Menis": "Adán Pablo Martín Menis",
    "Miren Uxue Barcos Berruezo": "Miren Uxue Barkos Berruezo",
    "Gabriel Cañellas i Fons": "Gabriel Cañellas Fons",
    "Francesc Antich Oliver": "Francesc Antich i Oliver",
    "Jaime Matas i Palou": "Jaime Matas i Palou",
    "Francesca Lluc Armengol Socías": "Francesca Lluch Armengol i Socias",
    "Margalida Prohens Rigo": "Margarita Prohens Rigo",
    "Cristina Cifuentes Cuencas": "María Cristina Cifuentes Cuencas",
    "Esperanza Aguirre Gil de Biedma": "Esperanza Aguirre y Gil de Biedma",
}

def dossier(item):
    number, territory = item
    url = f"https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_{number:02}"
    file = CACHE / f"senado-{number}.html"
    if not file.exists():
        file.write_bytes(urllib.request.urlopen(url, timeout=45).read())
    data = file.read_bytes()
    soup = BeautifulSoup(data, "html.parser")
    entries = []
    for h in soup.select("h3"):
        text = h.get_text(" ", strip=True)
        name = text.split("(")[0].strip()
        parties = [p for p in re.findall(r"\(([^)]+)\)", text) if not re.match(r"\d", p)]
        if parties:
            entries.append({"name": name, "party": parties[-1], "heading": text})
    return territory, {"source": url, "sha256": hashlib.sha256(data).hexdigest(), "entries": entries}

def main():
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        sources = dict(pool.map(dossier, DOSSIERS.items()))
    people = {}
    # Solo se leen metadatos de personas citadas; no duplicar el catálogo biográfico.
    governments = []
    territories = read(DATA / "territorios.json")
    folders = {"Comunidad de Madrid": "Madrid", "Comunidad Foral de Navarra": "Navarra"}
    for t in territories:
        folder = DATA / folders.get(t["name"], t["name"])
        for file in (folder / "Gobierno").glob("*/composicion.json"):
            governments.append((t, file, read(file)))
    ids = {m["person"] for _, _, g in governments for m in g["terms"] if m.get("level") == "president"}
    def person(folder):
        file = folder / "ficha.json"
        if file.exists():
            p = read(file)
            if p["id"] in ids:
                return p["id"], {"name": p.get("fullName", p["name"]), "folder": folder.name}
    with concurrent.futures.ThreadPoolExecutor(32) as pool:
        for p in pool.map(person, (ROOT / "Políticos").iterdir()):
            if p: people[p[0]] = p[1]
    # Casos no cubiertos por los dosieres del Senado. Se conserva su fuente individual.
    curated = read(DATA / "Mapa/vinculaciones-historicas.json")
    overrides = curated["entries"]
    rows, missing = [], []
    for t, file, g in governments:
        for m in g["terms"]:
            if m.get("level") != "president": continue
            start = m.get("start") or g["start"]
            end = m.get("end") or g["end"]
            original = m["name"]
            target = ALIASES.get(original, original)
            entries = sources.get(t["id"], {}).get("entries", [])
            matches = [e for e in entries if norm(e["name"]) == norm(target)]
            party, source = None, None
            if matches:
                parties = {e["party"] for e in matches}
                if len(parties) == 1: party = next(iter(parties))
                elif parties <= {"AP", "PP"}: party = "AP" if start < "1989-01-22" else "PP"
                elif original == "Juan Hormaechea Cazón": party = "AP" if start < "1991" else "UPCA"
                source = sources[t["id"]]["source"]
            override = next((e for e in overrides if e["person"] == m["person"] and
                             e.get("from", "0000") <= start < e.get("until", "9999")), None)
            if override: party, source = override["party"], override["source"]
            if not party: missing.append((t["id"], original, start))
            person = people[m["person"]]
            rows.append({"territory": t["id"], "government": g["id"],
                         "composition": str(file.relative_to(ROOT)).replace("\\", "/"),
                         "person": m["person"], **person, "start": start, "end": end,
                         "role": m["role"], "source": g["source"], "party": party,
                         "partySource": source,
                         "partyChanges": [c for c in curated.get("changes", [])
                                          if c["person"] == m["person"] and start <= c["date"] < (end or "9999")],
                         "dateBasis": "Intervalo documental de la composición regional; no equivale necesariamente a toma de posesión.",
                         "partyBasis": "Formación identificada por la fuente para el mandato; no acredita militancia diaria."})
    output = {"checkedAt": CHECKED, "sources": sources,
              "presidencies": sorted(rows, key=lambda p: (p["start"], p["territory"]))}
    (DATA / "Mapa/historico-presidencias.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", "utf8")
    print("Etapas", len(rows), "personas", len(people), "sin formación contrastada", missing)

if __name__ == "__main__": main()
