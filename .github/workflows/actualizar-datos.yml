#!/usr/bin/env python3
"""
Tomba Fly Fishing — Auto-updater
Consulta caudales (SAIH Ebro) y embalses (embalses.net)
y actualiza el HTML con datos frescos cada mañana.
"""

import json
import locale
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime

# Forzar fecha en español
MESES = {
    1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
    7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"
}

def fecha_es():
    now = datetime.now()
    return f"{now.day} de {MESES[now.month]} de {now.year}", now.strftime("%H:%M")

# ── Configuración de cotos ────────────────────────────────────────────────────
COTOS = [
    {
        "name": "Anglès – El Pasteral",
        "river": "Río Ter", "embalse_name": "Susqueda",
        "saih_id": "A097",
        "embalse_id": "1231",   # embalses.net/pantano-1231-susqueda
        "umbral_ok": 8, "umbral_warn": 20,
        "lat": 41.950, "lon": 2.633,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 16, "conca": "Ter"
    },
    {
        "name": "Alfarràs",
        "river": "Río Noguera Ribagorzana", "embalse_name": "Canelles",
        "saih_id": "A137",
        "embalse_id": "1090",   # embalses.net/pantano-1090-canelles
        "umbral_ok": 12, "umbral_warn": 25,
        "lat": 41.723, "lon": 0.558,
        "link": "https://www.saihebro.com/tiempo-real/mapa-aforos-H13-nogueras",
        "plazas": 40, "conca": "Noguera Ribagorçana"
    },
    {
        "name": "Pedret",
        "river": "Río Llobregat", "embalse_name": "La Baells",
        "saih_id": None,
        "embalse_id": "1186",   # embalses.net/pantano-1186-la-baells
        "umbral_ok": 6, "umbral_warn": 15,
        "lat": 42.098, "lon": 1.848,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 30, "conca": "Llobregat"
    },
    {
        "name": "Oliana",
        "river": "Río Segre", "embalse_name": "Oliana",
        "saih_id": "A023",
        "embalse_id": "316",    # embalses.net/pantano-316-oliana
        "umbral_ok": 10, "umbral_warn": 22,
        "lat": 42.072, "lon": 1.319,
        "link": "https://www.saihebro.com",
        "plazas": 25, "conca": "Segre"
    },
    {
        "name": "Ponts",
        "river": "Río Segre", "embalse_name": "Rialb",
        "saih_id": "A023",
        "embalse_id": "1228",   # embalses.net/pantano-1228-rialb
        "umbral_ok": 10, "umbral_warn": 22,
        "lat": 41.916, "lon": 1.196,
        "link": "https://www.saihebro.com",
        "plazas": 20, "conca": "Segre"
    },
    {
        "name": "Alòs de Balaguer",
        "river": "Río Segre", "embalse_name": "Rialb",
        "saih_id": "A023",
        "embalse_id": "1228",
        "umbral_ok": 10, "umbral_warn": 22,
        "lat": 41.883, "lon": 0.900,
        "link": "https://www.saihebro.com",
        "plazas": 20, "conca": "Segre"
    },
    {
        "name": "Malagarriga",
        "river": "Río Cardener", "embalse_name": "Sant Ponç",
        "saih_id": None,
        "embalse_id": "311",    # embalses.net/pantano-311-sant-ponc
        "umbral_ok": 5, "umbral_warn": 10,
        "lat": 41.838, "lon": 1.740,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 25, "conca": "Llobregat"
    },
    {
        "name": "La Torrassa",
        "river": "Lago intensivo", "embalse_name": "La Torrassa",
        "saih_id": None,
        "embalse_id": None,
        "umbral_ok": 999, "umbral_warn": 999,
        "lat": 42.200, "lon": 1.050,
        "link": "https://www.embalses.net",
        "plazas": 50, "conca": "Noguera Pallaresa"
    },
]

# ── SSL permisivo ─────────────────────────────────────────────────────────────
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def fetch_url(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; TombaFlyFishing/1.0)"
        })
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  ERROR descargando {url}: {e}", file=sys.stderr)
        return None

def get_caudal_saih(station_id):
    """Consulta caudal del SAIH Ebro via API JSON."""
    urls = [
        f"https://www.saihebro.com/saihebro/index.php?url=/datos/json/ultimos/estacion:{station_id}",
        f"http://www.saihebro.com/saihebro/index.php?url=/datos/json/ultimos/estacion:{station_id}",
    ]
    for url in urls:
        html = fetch_url(url)
        if not html:
            continue
        try:
            data = json.loads(html)
            # Buscar caudal en JSON — puede ser dict o lista
            def buscar_caudal(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if "caudal" in k.lower() or k in ("Q", "q"):
                            try:
                                val = float(str(v).replace(",", "."))
                                if 0 < val < 5000:
                                    return round(val, 1)
                            except:
                                pass
                        result = buscar_caudal(v)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = buscar_caudal(item)
                        if result:
                            return result
                return None
            result = buscar_caudal(data)
            if result:
                return result
        except json.JSONDecodeError:
            # Buscar patrón específico de caudal en m³/s — evitar años (4 dígitos)
            # Buscamos números como: 12.5, 125.3, 1250.4 pero NO 2234 (año)
            matches = re.findall(r'\b(\d{1,4}[.,]\d+)\s*(?:m|M)', html)
            for m in matches:
                try:
                    val = float(m.replace(",", "."))
                    if 0 < val < 3000:
                        return round(val, 1)
                except:
                    pass
    return None

def get_embalse_nivel(embalse_id):
    """Consulta nivel de embalse en embalses.net."""
    url = f"https://www.embalses.net/pantano-{embalse_id}-.html"
    html = fetch_url(url)
    if not html:
        return None
    # El porcentaje en embalses.net aparece en formato "97,85 %"
    # Buscamos el primer porcentaje razonable (entre 0 y 110)
    matches = re.findall(r'(\d{1,3}[,\.]\d{1,2})\s*%', html)
    for m in matches:
        try:
            val = float(m.replace(",", "."))
            if 0 < val <= 110:
                return round(val, 1)
        except:
            pass
    # Buscar también porcentaje entero
    matches2 = re.findall(r'\b(\d{1,3})\s*%', html)
    for m in matches2:
        try:
            val = float(m)
            if 0 < val <= 110:
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
        return "yellow", "Condiciones límite"
    else:
        return "red", "No pescable"

def get_nota(coto, caudal, embalse_nivel):
    emb = coto["embalse_name"]
    if coto["umbral_ok"] == 999:
        return "Lago artificial — sin dependencia de caudal"
    nivel_str = f" · {emb} al {embalse_nivel}%" if embalse_nivel else ""
    if caudal is None:
        return f"Sin datos de caudal disponibles{nivel_str}"
    if caudal <= coto["umbral_ok"]:
        return f"Condiciones óptimas · {caudal} m³/s{nivel_str}"
    elif caudal <= coto["umbral_warn"]:
        return f"Caudal algo alto · {caudal} m³/s — vadear con precaución{nivel_str}"
    else:
        return f"Caudal excesivo · {caudal} m³/s — no recomendable{nivel_str}"

def update_html(cotos, fecha, hora):
    if not os.path.exists("index.html"):
        print(f"  ERROR: index.html no encontrado en {os.getcwd()}", file=sys.stderr)
        print(f"  Archivos: {os.listdir('.')}", file=sys.stderr)
        return False

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    cotos_js_items = []
    for c in cotos:
        caudal_val = c["caudal"] if c["caudal"] is not None else "null"
        embalse_val = c["embalseNivel"] if c["embalseNivel"] is not None else "null"
        nota_safe = c["nota"].replace('"', "'")
        item = f"""  {{
    name: "{c['name']}", river: "{c['river']}", embalse: "{c['embalse_name']}",
    caudal: {caudal_val}, embalseNivel: {embalse_val}, status: "{c['status']}", badge: "{c['badge']}",
    nota: "{nota_safe}",
    link: "{c['link']}",
    plazas: {c['plazas']}, conca: "{c['conca']}", lat: {c['lat']}, lon: {c['lon']}
  }}"""
        cotos_js_items.append(item)

    nuevo_cotos = "const COTOS = [\n" + ",\n".join(cotos_js_items) + "\n];"
    html = re.sub(r"const COTOS = \[.*?\];", nuevo_cotos, html, flags=re.DOTALL)

    html = re.sub(
        r'id="lastUpdate">[^<]*<',
        f'id="lastUpdate">Actualizado: {fecha} {hora}<',
        html
    )

    pescables = sum(1 for c in cotos if c["status"] == "green")
    no_pescables = sum(1 for c in cotos if c["status"] == "red")
    if pescables > 0:
        trend = f"✅ {pescables} coto{'s' if pescables > 1 else ''} pescable{'s' if pescables > 1 else ''}"
    elif no_pescables > 0:
        trend = f"❌ {no_pescables} cotos no pescables"
    else:
        trend = "⚠️ Consultar condiciones"
    html = re.sub(r'class="trend-badge">[^<]*<', f'class="trend-badge">{trend}<', html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    return True

def main():
    print("🎣 Tomba Fly Fishing — Actualizando datos...")
    print(f"   Directorio: {os.getcwd()}")
    print(f"   Archivos: {os.listdir('.')}")

    fecha, hora = fecha_es()
    resultados = []

    for coto in COTOS:
        print(f"\n  📍 {coto['name']}")
        is_lake = coto["umbral_ok"] == 999

        caudal = None
        if not is_lake and coto["saih_id"]:
            print(f"     → Consultando SAIH {coto['saih_id']}...")
            try:
                caudal = get_caudal_saih(coto["saih_id"])
            except Exception as e:
                print(f"     → Error SAIH: {e}", file=sys.stderr)
            print(f"     → Caudal: {caudal} m³/s")

        embalse_nivel = None
        if coto["embalse_id"]:
            print(f"     → Consultando embalse {coto['embalse_id']}...")
            try:
                embalse_nivel = get_embalse_nivel(coto["embalse_id"])
            except Exception as e:
                print(f"     → Error embalse: {e}", file=sys.stderr)
            print(f"     → Embalse: {embalse_nivel}%")

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
        print(f"     → Estado: {status} — {badge}")

    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump({"fecha": fecha, "hora": hora, "cotos": resultados}, f, ensure_ascii=False, indent=2)
    print(f"\n✅ datos.json guardado")

    ok = update_html(resultados, fecha, hora)
    if ok:
        print("✅ index.html actualizado")
    else:
        print("❌ index.html NO actualizado", file=sys.stderr)
        sys.exit(1)

    print(f"\n🎣 Listo — {fecha} {hora}")

if __name__ == "__main__":
    main()


# ── Configuración de cotos ────────────────────────────────────────────────────
COTOS = [
    {
        "name": "Anglès – El Pasteral",
        "river": "Río Ter", "embalse_name": "Susqueda",
        "saih_id": "A097",
        "embalse_id": "1231",
        "umbral_ok": 8, "umbral_warn": 20,
        "lat": 41.950, "lon": 2.633,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 16, "conca": "Ter"
    },
    {
        "name": "Alfarràs",
        "river": "Río Noguera Ribagorzana", "embalse_name": "Canelles",
        "saih_id": "A137",
        "embalse_id": "1049",
        "umbral_ok": 12, "umbral_warn": 25,
        "lat": 41.723, "lon": 0.558,
        "link": "https://www.saihebro.com/tiempo-real/mapa-aforos-H13-nogueras",
        "plazas": 40, "conca": "Noguera Ribagorçana"
    },
    {
        "name": "Pedret",
        "river": "Río Llobregat", "embalse_name": "La Baells",
        "saih_id": None,
        "embalse_id": "1186",
        "umbral_ok": 6, "umbral_warn": 15,
        "lat": 42.098, "lon": 1.848,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 30, "conca": "Llobregat"
    },
    {
        "name": "Oliana",
        "river": "Río Segre", "embalse_name": "Oliana",
        "saih_id": "A023",
        "embalse_id": "1095",
        "umbral_ok": 10, "umbral_warn": 22,
        "lat": 42.072, "lon": 1.319,
        "link": "https://www.saihebro.com",
        "plazas": 25, "conca": "Segre"
    },
    {
        "name": "Ponts",
        "river": "Río Segre", "embalse_name": "Rialb",
        "saih_id": "A023",
        "embalse_id": "1228",
        "umbral_ok": 10, "umbral_warn": 22,
        "lat": 41.916, "lon": 1.196,
        "link": "https://www.saihebro.com",
        "plazas": 20, "conca": "Segre"
    },
    {
        "name": "Alòs de Balaguer",
        "river": "Río Segre", "embalse_name": "Rialb",
        "saih_id": "A023",
        "embalse_id": "1228",
        "umbral_ok": 10, "umbral_warn": 22,
        "lat": 41.883, "lon": 0.900,
        "link": "https://www.saihebro.com",
        "plazas": 20, "conca": "Segre"
    },
    {
        "name": "Malagarriga",
        "river": "Río Cardener", "embalse_name": "Sant Ponç",
        "saih_id": None,
        "embalse_id": "1199",
        "umbral_ok": 5, "umbral_warn": 10,
        "lat": 41.838, "lon": 1.740,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 25, "conca": "Llobregat"
    },
    {
        "name": "La Torrassa",
        "river": "Lago intensivo", "embalse_name": "La Torrassa",
        "saih_id": None,
        "embalse_id": None,
        "umbral_ok": 999, "umbral_warn": 999,
        "lat": 42.200, "lon": 1.050,
        "link": "https://www.embalses.net",
        "plazas": 50, "conca": "Noguera Pallaresa"
    },
]

# ── Funciones de consulta ─────────────────────────────────────────────────────

# Contexto SSL permisivo para servidores con certificados problemáticos
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def fetch_url(url, timeout=15):
    """Descarga una URL y devuelve el texto."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; TombaFlyFishing/1.0)"
        })
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  ERROR descargando {url}: {e}", file=sys.stderr)
        return None

def get_caudal_saih(station_id):
    """Consulta caudal via API JSON del SAIH Ebro."""
    # Intentar con la API JSON del SAIH Ebro
    urls = [
        f"https://www.saihebro.com/saihebro/index.php?url=/datos/json/ultimos/estacion:{station_id}",
        f"http://www.saihebro.com/saihebro/index.php?url=/datos/json/ultimos/estacion:{station_id}",
    ]
    for url in urls:
        html = fetch_url(url)
        if not html:
            continue
        try:
            data = json.loads(html)
            # Buscar caudal en la respuesta JSON
            for key in ["caudal", "Caudal", "Q", "q"]:
                if key in data:
                    val = float(str(data[key]).replace(",", "."))
                    if 0 < val < 10000:
                        return round(val, 1)
            # Buscar en estructura anidada
            if isinstance(data, list) and len(data) > 0:
                for item in data:
                    if isinstance(item, dict):
                        for key in ["caudal", "Caudal", "valor", "value"]:
                            if key in item:
                                try:
                                    val = float(str(item[key]).replace(",", "."))
                                    if 0 < val < 10000:
                                        return round(val, 1)
                                except:
                                    pass
        except json.JSONDecodeError:
            # Si no es JSON, buscar número en el texto
            m = re.search(r'(\d+[\.,]\d+)\s*m.{0,3}3', html, re.IGNORECASE)
            if m:
                try:
                    val = float(m.group(1).replace(",", "."))
                    if 0 < val < 10000:
                        return round(val, 1)
                except:
                    pass
    return None

def get_embalse_nivel(embalse_id):
    """Consulta nivel de embalse en embalses.net."""
    url = f"https://www.embalses.net/pantano-{embalse_id}-.html"
    html = fetch_url(url)
    if not html:
        return None
    # Buscar porcentaje — aparece como "97,85 %" o similar
    patterns = [
        r'(\d{1,3}[,\.]\d{1,2})\s*%',
        r'(\d{1,3})\s*%',
    ]
    for pat in patterns:
        for m in re.finditer(pat, html):
            try:
                val = float(m.group(1).replace(",", "."))
                if 0 < val <= 110:
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
        return "yellow", "Condiciones límite"
    else:
        return "red", "No pescable"

def get_nota(coto, caudal, embalse_nivel):
    emb = coto["embalse_name"]
    if coto["umbral_ok"] == 999:
        return "Lago artificial — sin dependencia de caudal"
    nivel_str = f" · {emb} al {embalse_nivel}%" if embalse_nivel else ""
    if caudal is None:
        return f"Sin datos de caudal disponibles{nivel_str}"
    if caudal <= coto["umbral_ok"]:
        return f"Condiciones óptimas · {caudal} m³/s{nivel_str}"
    elif caudal <= coto["umbral_warn"]:
        return f"Caudal algo alto · {caudal} m³/s — vadear con precaución{nivel_str}"
    else:
        return f"Caudal excesivo · {caudal} m³/s — no recomendable{nivel_str}"

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import os
    print("🎣 Tomba Fly Fishing — Actualizando datos...")
    print(f"   Directorio: {os.getcwd()}")
    print(f"   Archivos: {os.listdir('.')}")

    fecha = datetime.now().strftime("%-d de %B de %Y")
    hora = datetime.now().strftime("%H:%M")

    resultados = []

    for coto in COTOS:
        print(f"\n  📍 {coto['name']}")
        is_lake = coto["umbral_ok"] == 999

        caudal = None
        if not is_lake and coto["saih_id"]:
            print(f"     → Consultando SAIH {coto['saih_id']}...")
            try:
                caudal = get_caudal_saih(coto["saih_id"])
            except Exception as e:
                print(f"     → Error SAIH: {e}", file=sys.stderr)
            print(f"     → Caudal: {caudal} m³/s")

        embalse_nivel = None
        if coto["embalse_id"]:
            print(f"     → Consultando embalse {coto['embalse_id']}...")
            try:
                embalse_nivel = get_embalse_nivel(coto["embalse_id"])
            except Exception as e:
                print(f"     → Error embalse: {e}", file=sys.stderr)
            print(f"     → Embalse: {embalse_nivel}%")

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
        print(f"     → Estado: {status} — {badge}")

    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump({"fecha": fecha, "hora": hora, "cotos": resultados}, f, ensure_ascii=False, indent=2)
    print(f"\n✅ datos.json guardado")

    ok = update_html(resultados, fecha, hora)
    if ok:
        print("✅ index.html actualizado")
    else:
        print("❌ index.html NO actualizado — ver error arriba", file=sys.stderr)
        sys.exit(1)

    print(f"\n🎣 Listo — {fecha} {hora}")

def update_html(cotos, fecha, hora):
    import os
    if not os.path.exists("index.html"):
        print("  ERROR: index.html no encontrado en:", os.getcwd(), file=sys.stderr)
        print("  Archivos disponibles:", os.listdir("."), file=sys.stderr)
        return False

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    cotos_js_items = []
    for c in cotos:
        caudal_val = c["caudal"] if c["caudal"] is not None else "null"
        embalse_val = c["embalseNivel"] if c["embalseNivel"] is not None else "null"
        nota_safe = c["nota"].replace('"', "'")
        item = f"""  {{
    name: "{c['name']}", river: "{c['river']}", embalse: "{c['embalse_name']}",
    caudal: {caudal_val}, embalseNivel: {embalse_val}, status: "{c['status']}", badge: "{c['badge']}",
    nota: "{nota_safe}",
    link: "{c['link']}",
    plazas: {c['plazas']}, conca: "{c['conca']}", lat: {c['lat']}, lon: {c['lon']}
  }}"""
        cotos_js_items.append(item)

    nuevo_cotos = "const COTOS = [\n" + ",\n".join(cotos_js_items) + "\n];"
    html = re.sub(r"const COTOS = \[.*?\];", nuevo_cotos, html, flags=re.DOTALL)

    html = re.sub(
        r'id="lastUpdate">[^<]*<',
        f'id="lastUpdate">Actualizado: {fecha} {hora}<',
        html
    )

    pescables = sum(1 for c in cotos if c["status"] == "green")
    if pescables > 0:
        trend = f"✅ {pescables} coto{'s' if pescables > 1 else ''} pescable{'s' if pescables > 1 else ''}"
    else:
        trend = "▼ Embalses bajando"
    html = re.sub(r'class="trend-badge">[^<]*<', f'class="trend-badge">{trend}<', html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    return True

if __name__ == "__main__":
    main()


# ── Configuración de cotos ────────────────────────────────────────────────────
# saih_id: estación de aforo del SAIH Ebro (None si no aplica)
# embalse_id: ID en embalses.net
# umbral_ok: caudal máximo pescable (m³/s)
# umbral_warn: caudal máximo condiciones límite (m³/s)

COTOS = [
    {
        "name": "Anglès – El Pasteral",
        "river": "Río Ter", "embalse_name": "Susqueda",
        "saih_id": "A097",          # Estación Ter - Anglès (SAIH Ebro)
        "embalse_id": "1231",       # Susqueda en embalses.net
        "umbral_ok": 8,
        "umbral_warn": 20,
        "lat": 41.950, "lon": 2.633,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 16, "conca": "Ter"
    },
    {
        "name": "Alfarràs",
        "river": "Río Noguera Ribagorzana", "embalse_name": "Canelles",
        "saih_id": "A137",          # Estación NR - Pont de Suert
        "embalse_id": "1049",       # Canelles en embalses.net
        "umbral_ok": 12,
        "umbral_warn": 25,
        "lat": 41.723, "lon": 0.558,
        "link": "https://www.saihebro.com/tiempo-real/mapa-aforos-H13-nogueras",
        "plazas": 40, "conca": "Noguera Ribagorçana"
    },
    {
        "name": "Pedret",
        "river": "Río Llobregat", "embalse_name": "La Baells",
        "saih_id": None,
        "embalse_id": "1186",       # La Baells en embalses.net
        "umbral_ok": 6,
        "umbral_warn": 15,
        "lat": 42.098, "lon": 1.848,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 30, "conca": "Llobregat"
    },
    {
        "name": "Oliana",
        "river": "Río Segre", "embalse_name": "Oliana",
        "saih_id": "A023",          # Estación Segre - Oliana
        "embalse_id": "1095",       # Oliana en embalses.net
        "umbral_ok": 10,
        "umbral_warn": 22,
        "lat": 42.072, "lon": 1.319,
        "link": "https://www.saihebro.com",
        "plazas": 25, "conca": "Segre"
    },
    {
        "name": "Ponts",
        "river": "Río Segre", "embalse_name": "Rialb",
        "saih_id": "A023",
        "embalse_id": "1228",       # Rialb en embalses.net
        "umbral_ok": 10,
        "umbral_warn": 22,
        "lat": 41.916, "lon": 1.196,
        "link": "https://www.saihebro.com",
        "plazas": 20, "conca": "Segre"
    },
    {
        "name": "Alòs de Balaguer",
        "river": "Río Segre", "embalse_name": "Rialb",
        "saih_id": "A023",
        "embalse_id": "1228",
        "umbral_ok": 10,
        "umbral_warn": 22,
        "lat": 41.883, "lon": 0.900,
        "link": "https://www.saihebro.com",
        "plazas": 20, "conca": "Segre"
    },
    {
        "name": "Malagarriga",
        "river": "Río Cardener", "embalse_name": "Sant Ponç",
        "saih_id": None,
        "embalse_id": "1199",       # Sant Ponç en embalses.net
        "umbral_ok": 5,
        "umbral_warn": 10,
        "lat": 41.838, "lon": 1.740,
        "link": "https://aplicacions.aca.gencat.cat/aetr/vishid/",
        "plazas": 25, "conca": "Llobregat"
    },
    {
        "name": "La Torrassa",
        "river": "Lago intensivo", "embalse_name": "La Torrassa",
        "saih_id": None,
        "embalse_id": None,         # Lago privado, sin datos públicos
        "umbral_ok": 999,
        "umbral_warn": 999,
        "lat": 42.200, "lon": 1.050,
        "link": "https://www.embalses.net",
        "plazas": 50, "conca": "Noguera Pallaresa"
    },
]

# ── Funciones de consulta ─────────────────────────────────────────────────────

def fetch_url(url, timeout=10):
    """Descarga una URL y devuelve el texto."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TombaFlyFishing/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  ERROR descargando {url}: {e}", file=sys.stderr)
        return None

def get_caudal_saih(station_id):
    """Consulta caudal en tiempo real del SAIH Ebro."""
    url = f"http://www.saihebro.com/semobile/index.php?url=/tr/ficha/estacion:{station_id}"
    html = fetch_url(url)
    if not html:
        return None
    # Buscar el caudal en la página
    patterns = [
        r'Caudal[^:]*:\s*</[^>]+>\s*<[^>]+>\s*([\d.,]+)\s*m',
        r'caudal[^"]*"[^>]*>([\d.,]+)',
        r'([\d.,]+)\s*m.{0,5}3/s',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            try:
                val = float(m.group(1).replace(",", "."))
                if 0 < val < 10000:
                    return round(val, 1)
            except:
                pass
    return None

def get_embalse_nivel(embalse_id):
    """Consulta nivel de embalse en embalses.net."""
    url = f"https://www.embalses.net/pantano-{embalse_id}-.html"
    html = fetch_url(url)
    if not html:
        return None
    patterns = [
        r'([\d.,]+)\s*%',
        r'Volumen[^:]*:\s*([\d.,]+)',
    ]
    for pat in patterns:
        m = re.search(pat, html)
        if m:
            try:
                val = float(m.group(1).replace(",", "."))
                if 0 < val <= 110:
                    return round(val, 1)
            except:
                pass
    return None

def get_status(caudal, umbral_ok, umbral_warn, is_lake=False):
    """Determina el semáforo según el caudal."""
    if is_lake:
        return "green", "Pescable"
    if caudal is None:
        return "yellow", "Sin datos — consultar"
    if caudal <= umbral_ok:
        return "green", "Pescable"
    elif caudal <= umbral_warn:
        return "yellow", "Condiciones límite"
    else:
        return "red", "No pescable"

def get_nota(coto, caudal, embalse_nivel):
    """Genera la nota descriptiva según el estado actual."""
    name = coto["name"].split("–")[0].strip()
    emb = coto["embalse_name"]

    if coto["umbral_ok"] == 999:
        return "Lago artificial — sin dependencia de caudal"

    if caudal is None:
        return f"Sin datos de caudal disponibles — consulta {coto['link']}"

    nivel_str = f" · {emb} al {embalse_nivel}%" if embalse_nivel else ""

    if caudal <= coto["umbral_ok"]:
        return f"Condiciones óptimas · {caudal} m³/s{nivel_str}"
    elif caudal <= coto["umbral_warn"]:
        return f"Caudal algo alto · {caudal} m³/s — vadear con precaución{nivel_str}"
    else:
        return f"Caudal excesivo · {caudal} m³/s — no recomendable pescar{nivel_str}"

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("🎣 Tomba Fly Fishing — Actualizando datos...")
    fecha = datetime.now().strftime("%-d de %B de %Y")  # ej: "20 de marzo de 2026"
    hora = datetime.now().strftime("%H:%M")

    resultados = []

    for coto in COTOS:
        print(f"\n  📍 {coto['name']}")
        is_lake = coto["umbral_ok"] == 999

        # Caudal
        caudal = None
        if not is_lake and coto["saih_id"]:
            print(f"     → Consultando SAIH {coto['saih_id']}...")
            caudal = get_caudal_saih(coto["saih_id"])
            print(f"     → Caudal: {caudal} m³/s")

        # Embalse
        embalse_nivel = None
        if coto["embalse_id"]:
            print(f"     → Consultando embalse {coto['embalse_id']}...")
            embalse_nivel = get_embalse_nivel(coto["embalse_id"])
            print(f"     → Embalse: {embalse_nivel}%")

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
        print(f"     → Estado: {status} — {badge}")

    # Guardar JSON para debug
    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump({"fecha": fecha, "hora": hora, "cotos": resultados}, f, ensure_ascii=False, indent=2)
    print(f"\n✅ datos.json guardado")

    # Actualizar el HTML
    update_html(resultados, fecha, hora)
    print("✅ index.html actualizado")
    print(f"\n🎣 Listo — {fecha} {hora}")

def update_html(cotos, fecha, hora):
    """Inyecta los datos frescos en el HTML."""
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Reemplazar el array COTOS en el JS
    cotos_js_items = []
    for c in cotos:
        caudal_val = c["caudal"] if c["caudal"] is not None else "null"
        embalse_val = c["embalseNivel"] if c["embalseNivel"] is not None else "null"
        item = f"""  {{
    name: "{c['name']}", river: "{c['river']}", embalse: "{c['embalse_name']}",
    caudal: {caudal_val}, embalseNivel: {embalse_val}, status: "{c['status']}", badge: "{c['badge']}",
    nota: "{c['nota']}",
    link: "{c['link']}",
    plazas: {c['plazas']}, conca: "{c['conca']}", lat: {c['lat']}, lon: {c['lon']}
  }}"""
        cotos_js_items.append(item)

    nuevo_cotos = "const COTOS = [\n" + ",\n".join(cotos_js_items) + "\n];"
    html = re.sub(r"const COTOS = \[.*?\];", nuevo_cotos, html, flags=re.DOTALL)

    # Actualizar fecha en el header
    html = re.sub(
        r'id="lastUpdate">[^<]*<',
        f'id="lastUpdate">Actualizado: {fecha} {hora}<',
        html
    )

    # Actualizar trend badge si hay cotos pescables
    pescables = sum(1 for c in cotos if c["status"] == "green")
    if pescables > 0:
        trend = f"✅ {pescables} coto{'s' if pescables > 1 else ''} pescable{'s' if pescables > 1 else ''}"
    else:
        trend = "▼ Embalses bajando"
    html = re.sub(r'class="trend-badge">[^<]*<', f'class="trend-badge">{trend}<', html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
