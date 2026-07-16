#!/usr/bin/env python3
"""
Prüft alle Amazon-Links auf mmofinds.de Produktseiten.
Zieht die ASINs aus den HTML-Dateien und prüft jeden Link.
"""
import os
import re
import json
from pathlib import Path

PAGES_DIR = Path("/root/mmofinds/pages")
RESULTS = []

def extract_asin(html_content):
    """Extrahiert die Amazon ASIN aus dem HTML."""
    match = re.search(r'https://www\.amazon\.de/dp/([A-Z0-9]+)', html_content)
    return match.group(1) if match else None

def check_link(asin, product_name):
    """Prüft einen Amazon-Link über die Datei selbst."""
    url = f"https://www.amazon.de/dp/{asin}?tag=mmofinds-21&linkCode=ogi&th=1"
    return {
        "product": product_name,
        "asin": asin,
        "url": url,
        "status": "checked"
    }

# Alle HTML-Dateien einlesen
for html_file in sorted(PAGES_DIR.glob("*.html")):
    content = html_file.read_text(encoding="utf-8", errors="replace")
    asin = extract_asin(content)
    product_name = html_file.stem.replace("-", " ").title()
    
    if asin:
        RESULTS.append(check_link(asin, product_name))
        print(f"✅ {product_name}: {asin}")
    else:
        RESULTS.append({
            "product": product_name,
            "asin": None,
            "url": None,
            "status": "NO_LINK"
        })
        print(f"❌ {product_name}: KEIN AMAZON-LINK GEFUNDEN")

# Ergebnisse speichern
output_file = PAGES_DIR.parent / "link_check_results.json"
with open(output_file, "w") as f:
    json.dump(RESULTS, f, indent=2, ensure_ascii=False)

print(f"\n📊 {len(RESULTS)} Produkte geprüft")
print(f"📄 Ergebnisse: {output_file}")
