#!/usr/bin/env python3
"""Tomba Fly Fishing — Auto-updater"""

import json, os, re, ssl, sys
import urllib.request
from datetime import datetime

MESES = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
         7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}

def fecha_es():
    n = datetime.now()
    return f"{n.day} de {MESES[n.month]} de {n.year}", n.strftime("%H:%M")

COTOS = [
    {"name":"Anglès – El Pasteral","river":"Río Ter","embalse_name":"Susqueda",
     "aca_sensor":"EA060","embalse_id":"1231","umbral_ok":8,"umbral_warn":20,
     "lat":41.950,"lon":2.633,"link":"https://aplicacions.aca.gencat.cat/aetr/vishid/",
     "plazas":16,"conca":"Ter"},
    {"name":"Alfarràs","river":"Río Noguera Ribagorzana","embalse_name":"Canelles",
     "aca_sensor":None,"embalse_id":"1090","umbral_ok":12,"umbral_warn":25,
     "lat":41.723,"lon":0.558,"link":"https://www.saihebro.com/tiempo-real/mapa-aforos-H13-nogueras",
     "plazas":40,"conca":"Noguera Ribagorçana"},
    {"name":"Pedret","river":"Río Llobregat","embalse_name":"La Baells",
     "aca_sensor":"EA034","embalse_id":"1186","umbral_ok":6,"umbral_warn":15,
     "lat":42.098,"lon":1.848,"link":"https://aplicacions.aca.gencat.cat/aetr/vishid/",
     "plazas":30,"conca":"Llobregat"},
    {"name":"Oliana","river":"Río Segre","embalse_name":"Oliana",
     "aca_sensor":None,"embalse_id":"316","umbral_ok":10,"umbral_warn":22,
     "lat":42.072,"lon":1.319,"link":"https://www.saihebro.com",
     "plazas":25,"conca":"Segre"},
    {"name":"Ponts","river":"Río Segre","embalse_name":"Rialb",
     "aca_sensor":None,"embalse_id":"1228","umbral_ok":10,"umbral_warn":22,
     "lat":41.916,"lon":1.196,"link":"https://www.saihebro.com",
     "plazas":20,"conca":"Segre"},
    {"name":"Alòs de Balaguer","river":"Río Segre","embalse_name":"Rialb",
     "aca_sensor":None,"embalse_id":"1228","umbral_ok":10,"umbral_warn":22,
     "lat":41.883,"lon":0.900,"link":"https://www.saihebro.com",
     "plazas":20,"conca":"Segre"},
    {"name":"Malagarriga","river":"Río Cardener","embalse_name":"Sant Ponç",
     "aca_sensor":"EA026","embalse_id":"311","umbral_ok":5,"umbral_warn":10,
     "lat":41.838,"lon":1.740,"link":"https://aplicacions.aca.gencat.cat/aetr/vishid/",
     "plazas":25,"conca":"Llobregat"},
    {"name":"La Torrassa","river":"Lago intensivo","embalse_name":"La Torrassa",
     "aca_sensor":None,"embalse_id":None,"umbral_ok":999,"umbral_warn":999,
     "lat":42.200,"lon":1.050,"link":"https://www.embalses.net",
     "plazas":50,"conca":"Noguera Pallaresa"},
]

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 TombaFlyFishing/1.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  ERROR {url}: {e}", file=sys.stderr)
        return None

def get_caudal(sensor_id):
    """API Sentilo ACA — sin problemas SSL"""
    for base in ["https://aplicacions.aca.gencat.cat", "http://aca-web.gencat.cat"]:
        url = f"{base}/sentilo-catalog-web/api/data/AFORAMENT-EST/{sensor_id}"
        html = fetch(url)
        if not html:
            continue
        try:
            data = json.loads(html)
            obs = data.get("observations", [])
            if obs:
                val = float(str(obs[0].get("value","0")).replace(",","."))
                if 0 < val < 5000:
                    return round(val, 1)
        except Exception as e:
            print(f"  Parse error: {e}", file=sys.stderr)
    return None

def get_embalse(embalse_id):
    html = fetch(f"https://www.embalses.net/pantano-{embalse_id}-.html")
    if not html:
        return None
    for m in re.finditer(r'(\d{1,3}[,.]\d{1,2})\s*%', html):
        try:
            val = float(m.group(1).replace(",","."))
            if 0 < val <= 110:
                return round(val, 1)
        except:
            pass
    return None

def get_status(caudal, ok, warn, lake=False):
    if lake: return "green","Pescable"
    if caudal is None: return "yellow","Sin datos — consultar"
    if caudal <= ok: return "green","Pescable"
    if caudal <= warn: return "yellow","Condiciones límite"
    return "red","No pescable"

def get_nota(coto, caudal, embalse):
    if coto["umbral_ok"] == 999:
        return "Lago artificial — sin dependencia de caudal"
    niv = f" · {coto['embalse_name']} al {embalse}%" if embalse else ""
    if caudal is None: return f"Sin datos de caudal disponibles{niv}"
    if caudal <= coto["umbral_ok"]: return f"Condiciones óptimas · {caudal} m³/s{niv}"
    if caudal <= coto["umbral_warn"]: return f"Caudal algo alto · {caudal} m³/s{niv}"
    return f"Caudal excesivo · {caudal} m³/s — no recomendable{niv}"

def update_html(cotos, fecha, hora):
    if not os.path.exists("index.html"):
        print(f"ERROR: index.html no encontrado en {os.getcwd()}", file=sys.stderr)
        return False
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    items = []
    for c in cotos:
        cv = c["caudal"] if c["caudal"] is not None else "null"
        ev = c["embalseNivel"] if c["embalseNivel"] is not None else "null"
        nota = c["nota"].replace('"',"'")
        items.append(f"""  {{name:"{c['name']}",river:"{c['river']}",embalse:"{c['embalse_name']}",caudal:{cv},embalseNivel:{ev},status:"{c['status']}",badge:"{c['badge']}",nota:"{nota}",link:"{c['link']}",plazas:{c['plazas']},conca:"{c['conca']}",lat:{c['lat']},lon:{c['lon']}}}""")
    nuevo = "const COTOS = [\n" + ",\n".join(items) + "\n];"
    html = re.sub(r"const COTOS = \[.*?\];", nuevo, html, flags=re.DOTALL)
    html = re.sub(r'id="lastUpdate">[^<]*<', f'id="lastUpdate">Actualizado: {fecha} {hora}<', html)
    pescables = sum(1 for c in cotos if c["status"]=="green")
    no_pesc = sum(1 for c in cotos if c["status"]=="red")
    if pescables > 0: trend = f"✅ {pescables} coto{'s' if pescables>1 else ''} pescable{'s' if pescables>1 else ''}"
    elif no_pesc > 0: trend = f"❌ {no_pesc} cotos no pescables"
    else: trend = "⚠️ Consultar condiciones"
    html = re.sub(r'class="trend-badge">[^<]*<', f'class="trend-badge">{trend}<', html)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    return True

def main():
    print("🎣 Tomba Fly Fishing — Actualizando datos...")
    print(f"   Dir: {os.getcwd()} | Archivos: {os.listdir('.')}")
    fecha, hora = fecha_es()
    resultados = []
    for coto in COTOS:
        print(f"\n  📍 {coto['name']}")
        is_lake = coto["umbral_ok"] == 999
        caudal = None
        if not is_lake and coto["aca_sensor"]:
            print(f"     → ACA Sentilo {coto['aca_sensor']}...")
            caudal = get_caudal(coto["aca_sensor"])
            print(f"     → Caudal: {caudal} m³/s")
        embalse = None
        if coto["embalse_id"]:
            print(f"     → Embalse {coto['embalse_id']}...")
            embalse = get_embalse(coto["embalse_id"])
            print(f"     → Embalse: {embalse}%")
        status, badge = get_status(caudal, coto["umbral_ok"], coto["umbral_warn"], is_lake)
        nota = get_nota(coto, caudal, embalse)
        resultados.append({**coto,"caudal":caudal,"embalseNivel":embalse,"status":status,"badge":badge,"nota":nota})
        print(f"     → {status} — {badge}")
    with open("datos.json","w",encoding="utf-8") as f:
        json.dump({"fecha":fecha,"hora":hora,"cotos":resultados}, f, ensure_ascii=False, indent=2)
    print("\n✅ datos.json guardado")
    if update_html(resultados, fecha, hora):
        print("✅ index.html actualizado")
    else:
        sys.exit(1)
    print(f"\n🎣 Listo — {fecha} {hora}")

if __name__ == "__main__":
    main()
