#!/usr/bin/env python3
"""
Tomba Fly Fishing — Auto-updater v3
Llegeix caudals del GitHub Gist i embalses de embalses.net
Cotos: Anglès, Alfarràs, Pedret, Oliana, Ponts, Alòs, Malagarriga,
       Guingueta d'Àneu, Barruera, Boadella
"""

import json
import re
import sys
import urllib.request
from datetime import datetime

GIST_ID   = "69e1edfe77f4f03d07789ad74500061b"
GIST_FILE = "caudales.json"

COTOS = [
    {
        "name": "Anglès – El Pasteral",
        "river": "Río Ter", "embalse_name": "Susqueda",
        "saih_id": "A097", "embalse_id": "1231",
        "umbral_ok": 8, "umbral_warn": 20,
        "lat": 41.950, "lon": 2.633,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 16, "conca": "Ter",
        "descanso": [1], "temporada": None, "vedaExtra": None
    },
    {
        "name": "Alfarràs",
        "river": "Río Noguera Ribagorzana", "embalse_name": "Canelles",
        "saih_id": "A137", "embalse_id": "1090",
        "umbral_ok": 12, "umbral_warn": 25,
        "lat": 41.723, "lon": 0.558,
        "link": "https://www.saihebro.com/tiempo-real/mapa-aforos-H13-nogueras",
        "plazas": 40, "conca": "Noguera Ribagorzana",
        "descanso": [5], "temporada": None, "vedaExtra": "3er_martes"
    },
    {
        "name": "Pedret",
        "river": "Río Llobregat", "embalse_name": "La Baells",
        "saih_id": None, "embalse_id": "1186",
        "umbral_ok": 6, "umbral_warn": 15,
        "lat": 42.098, "lon": 1.848,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 30, "conca": "Llobregat",
        "descanso": [4], "temporada": None, "vedaExtra": None
    },
    {
        "name": "Oliana",
        "river": "Río Segre", "embalse_name": "Oliana",
        "saih_id": "A023", "embalse_id": "316",
        "umbral_ok": 10, "umbral_warn": 22,
        "lat": 42.072, "lon": 1.319,
        "link": "https://www.saihebro.com",
        "plazas": 50, "conca": "Segre",
        "descanso": [], "temporada": None, "vedaExtra": None
    },
    {
        "name": "Ponts",
        "river": "Río Segre", "embalse_name": "Rialb",
        "saih_id": "A023", "embalse_id": "1102",
        "umbral_ok": 10, "umbral_warn": 22,
        "lat": 41.916, "lon": 1.196,
        "link": "https://www.saihebro.com",
        "plazas": 30, "conca": "Segre",
        "descanso": [1], "temporada": None, "vedaExtra": None
    },
    {
        "name": "Alòs de Balaguer",
        "river": "Río Segre", "embalse_name": "Rialb",
        "saih_id": "A023", "embalse_id": "1102",
        "umbral_ok": 10, "umbral_warn": 22,
        "lat": 41.883, "lon": 0.900,
        "link": "https://www.saihebro.com",
        "plazas": 19, "conca": "Segre",
        "descanso": [], "temporada": None, "vedaExtra": None
    },
    {
        "name": "Malagarriga",
        "river": "Río Cardener", "embalse_name": "Sant Ponç",
        "saih_id": None, "embalse_id": "1229",
        "umbral_ok": 5, "umbral_warn": 10,
        "lat": 41.838, "lon": 1.740,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 25, "conca": "Llobregat",
        "descanso": [], "temporada": None, "vedaExtra": None
    },
    {
        "name": "La Guingueta d'Àneu",
        "river": "Noguera Pallaresa", "embalse_name": "La Torrassa",
        "saih_id": "A252", "embalse_id": None,
        "umbral_ok": 8, "umbral_warn": 18,
        "lat": 42.6698, "lon": 1.0475,
        "link": "https://aplicacions.agricultura.gencat.cat/mediamb_sgll_public/AppJava/zpc/zpcEmissio.do?reqCode=prepareLocale",
        "plazas": 60, "conca": "Noguera Pallaresa",
        "descanso": [], "temporada": {"open": [4,5], "close": [11,2]}, "vedaExtra": None
    },
    {
        "name": "Barruera",
        "river": "Noguera de Tor", "embalse_name": "Barruera",
        "saih_id": "A137", "embalse_id": None,  # Aprox. Pont de Suert
        "umbral_ok": 5, "umbral_warn": 12,
        "lat": 42.5232, "lon": 0.8288,
        "link": "https://aplicacions.agricultura.gencat.cat/mediamb_sgll_public/AppJava/zpc/zpcEmissio.do?reqCode=prepareLocale",
        "plazas": 40, "conca": "Noguera Ribagorzana",
        "descanso": [], "temporada": {"open": [4,12], "close": [10,12]}, "vedaExtra": None
    },
    {
        "name": "Boadella",
        "river": "Río Muga", "embalse_name": "Darnius-Boadella",
        "saih_id": None, "embalse_id": None,
        "umbral_ok": 4, "umbral_warn": 10,
        "lat": 42.3165, "lon": 2.9027,
        "link": "https://aplicacions.agricultura.gencat.cat/mediamb_sgll_public/AppJava/zpc/zpcEmissio.do?reqCode=prepareLocale",
        "plazas": 15, "conca": "Muga",
        "descanso": [], "temporada": None, "vedaExtra": None
    },
]

def fetch_url(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TombaFlyFishing/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  ERROR {url}: {e}", file=sys.stderr)
        return None

def get_caudals_gist():
    url = f"https://gist.githubusercontent.com/roberyto/{GIST_ID}/raw/{GIST_FILE}"
    text = fetch_url(url)
    if not text:
        print("  WARNING: No s'ha pogut llegir el Gist")
        return {}
    try:
        data = json.loads(text)
        print(f"  OK Gist llegit — actualitzat: {data.get('actualitzat', '?')}")
        return data.get("cotos", {})
    except Exception as e:
        print(f"  ERROR Gist: {e}")
        return {}

def get_embalse_nivel(embalse_id):
    url = f"https://www.embalses.net/pantano-{embalse_id}-.html"
    html = fetch_url(url)
    if not html:
        return None
    patterns = [
        r"Porcentaje:\s*(\d+[.,]\d+)\s*%",
        r"Agua embalsada[^%]{0,80}(\d{2,3}[.,]\d+)\s*%",
        r">\s*(\d{2,3}[.,]\d{2})\s*%\s*<",
        r"(\d{2,3}[.,]\d{1,2})\s*%",
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            try:
                val = float(m.group(1).replace(",", "."))
                if 0 < val <= 105:
                    return round(val, 1)
            except:
                pass
    return None

def get_status(caudal, umbral_ok, umbral_warn, is_lake=False):
    if is_lake:
        return "green", "Pescable"
    if caudal is None:
        return "yellow", "Sin datos — consultar"
    if caudal <= umbral_ok:
        return "green", "Pescable"
    elif caudal <= umbral_warn:
        return "yellow", "Condicions límit"
    else:
        return "red", "No pescable"

def get_nota(coto, caudal, embalse_nivel):
    emb = coto["embalse_name"]
    if coto["umbral_ok"] == 999:
        return f"Riu o llac intensiu — sense dependència de cabal"
    if caudal is None:
        return f"Sense dades de cabal — consulta {coto['link']}"
    nivel_str = f" · {emb} al {embalse_nivel}%" if embalse_nivel else ""
    if caudal <= coto["umbral_ok"]:
        return f"Condicions òptimes · {caudal} m³/s{nivel_str}"
    elif caudal <= coto["umbral_warn"]:
        return f"Cabal alt · {caudal} m³/s — vadejar amb precaució{nivel_str}"
    else:
        return f"Cabal excessiu · {caudal} m³/s — no recomanable pescar{nivel_str}"

def main():
    print("🎣 Tomba Fly Fishing — Actualitzant dades...")
    fecha = datetime.now().strftime("%-d de %B de %Y")
    hora  = datetime.now().strftime("%H:%M")

    print("\n  Llegint caudals del Gist...")
    caudals_gist = get_caudals_gist()

    resultados = []
    visitats_embalse = {}

    for coto in COTOS:
        print(f"\n  {coto['name']}")
        is_lake = coto["umbral_ok"] == 999

        caudal = None
        if not is_lake:
            dades = caudals_gist.get(coto["name"], {})
            caudal = dades.get("caudal")
            print(f"     Cabal: {caudal} m³/s")

        embalse_nivel = None
        if coto["embalse_id"]:
            key = coto["embalse_id"]
            if key in visitats_embalse:
                embalse_nivel = visitats_embalse[key]
                print(f"     Embalse {key}: {embalse_nivel}% (reutilitzat)")
            else:
                embalse_nivel = get_embalse_nivel(key)
                visitats_embalse[key] = embalse_nivel
                print(f"     Embalse {key}: {embalse_nivel}%")

        status, badge = get_status(caudal, coto["umbral_ok"], coto["umbral_warn"], is_lake)
        nota = get_nota(coto, caudal, embalse_nivel)

        resultados.append({
            **coto,
            "caudal": caudal,
            "embalseNivel": embalse_nivel,
            "status": status,
            "badge": badge,
            "nota": nota,
        })
        print(f"     Estat: {status} — {badge}")

    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump({"fecha": fecha, "hora": hora, "cotos": resultados}, f, ensure_ascii=False, indent=2)
    print(f"\nOK datos.json guardat")

    update_html(resultados, fecha, hora)
    print("OK index.html actualitzat")
    print(f"\n🎣 Llest — {fecha} {hora}")

def js_val(v):
    """Convertir valor Python a JS"""
    if v is None: return "null"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, str): return f'"{v}"'
    if isinstance(v, list): return "[" + ",".join(str(x) for x in v) + "]"
    if isinstance(v, dict):
        items = ", ".join(f"{k}: {js_val(val)}" for k, val in v.items())
        return "{" + items + "}"
    return str(v)

def update_html(cotos, fecha, hora):
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    cotos_js_items = []
    for c in cotos:
        caudal_val  = c["caudal"]       if c["caudal"]       is not None else "null"
        embalse_val = c["embalseNivel"] if c["embalseNivel"] is not None else "null"
        nota_escaped = c["nota"].replace('"', '\\"').replace('\n', ' ')
        temporada_js = js_val(c.get("temporada"))
        descanso_js  = js_val(c.get("descanso", []))
        vedaExtra_js = js_val(c.get("vedaExtra"))

        item = f"""  {{
    name: "{c['name']}", river: "{c['river']}", embalse: "{c['embalse_name']}",
    caudal: {caudal_val}, embalseNivel: {embalse_val}, status: "{c['status']}", badge: "{c['badge']}",
    nota: "{nota_escaped}",
    link: "{c['link']}",
    plazas: {c['plazas']}, conca: "{c['conca']}", lat: {c['lat']}, lon: {c['lon']},
    descanso: {descanso_js}, temporada: {temporada_js}, vedaExtra: {vedaExtra_js}
  }}"""
        cotos_js_items.append(item)

    nuevo_cotos = "const COTOS = [\n" + ",\n".join(cotos_js_items) + "\n];"
    html = re.sub(r"const COTOS = \[.*?\];", nuevo_cotos, html, flags=re.DOTALL)

    html = re.sub(
        r'id="lastUpdate">[^<]*<',
        f'id="lastUpdate">Actualitzat: {fecha} {hora}<',
        html
    )

    pescables = sum(1 for c in cotos if c["status"] == "green")
    trend = (f"✅ {pescables} coto{'s' if pescables != 1 else ''} pescable{'s' if pescables != 1 else ''}"
             if pescables > 0 else "▼ Embassaments alts")
    html = re.sub(r'class="trend-badge">[^<]*<', f'class="trend-badge">{trend}<', html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
