#!/usr/bin/env python3
"""
Link-Checker für mmofinds.de Produktseiten.
Prüft alle Amazon-Links auf der live Website.
"""
import os
import re
import json
import time
import subprocess
from pathlib import Path

PAGES_DIR = Path("/root/mmofinds/pages")
RESULTS_FILE = "/root/mmofinds/link_check_results.json"

def extract_asin_from_file(filepath):
    """Extrahiert die ASIN aus einer HTML-Datei."""
    content = open(filepath).read()
    match = re.search(r'https://www\.amazon\.de/dp/([A-Z0-9]+)', content)
    return match.group(1) if match else None

def check_asin_via_curl(asin, retries=2):
    """
    Prüft einen Amazon-Link mit curl.
    Gibt (status_code, is_ok) zurück.
    """
    url = f"https://www.amazon.de/dp/{asin}?tag=mmofinds-20&linkCode=ogi&th=1"
    
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
                 '--max-time', '10', '--connect-timeout', '5', '-L', url],
                capture_output=True, text=True, timeout=15
            )
            status = result.stdout.strip()
            return int(status), status in ('200', '301', '302', '303', '307', '308')
        except Exception:
            time.sleep(1)
    
    return 0, False

def main():
    results = []
    
    print("🔍 Prüfe alle Amazon-Links auf mmofinds.de...\n")
    
    html_files = sorted(PAGES_DIR.glob("*.html"))
    total = len(html_files)
    
    for i, html_file in enumerate(html_files, 1):
        asin = extract_asin_from_file(html_file)
        product_name = html_file.stem.replace("-", " ").title()
        
        if not asin:
            print(f"  ❌ [{i}/{total}] {product_name}: KEIN LINK")
            results.append({"product": product_name, "asin": None, "status": "NO_LINK", "url": None})
            continue
        
        url = f"https://www.amazon.de/dp/{asin}?tag=mmofinds-20&linkCode=ogi&th=1"
        status_code, is_ok = check_asin_via_curl(asin)
        
        if is_ok:
            icon = "✅"
        else:
            icon = "❌"
        
        print(f"  {icon} [{i}/{total}] {product_name}: {asin} → HTTP {status_code}")
        results.append({
            "product": product_name,
            "asin": asin,
            "url": url,
            "status_code": status_code,
            "status": "OK" if is_ok else "BROKEN"
        })
        
        # Kurze Pause, um nicht zu viele Anfragen zu senden
        time.sleep(0.5)
    
    # Ergebnisse speichern
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Zusammenfassung
    ok_count = sum(1 for r in results if r["status"] == "OK")
    broken_count = sum(1 for r in results if r["status"] == "BROKEN")
    no_link_count = sum(1 for r in results if r["status"] == "NO_LINK")
    
    print(f"\n{'='*60}")
    print(f"📊 ZUSAMMENFASSUNG")
    print(f"{'='*60}")
    print(f"  ✅ OK: {ok_count}")
    print(f"  ❌ Defekt: {broken_count}")
    print(f"  ⚠️  Kein Link: {no_link_count}")
    print(f"  📄 Gesamt: {total}")
    print(f"{'='*60}")
    
    if broken_count > 0:
        print(f"\n❌ DEFELINKTE PRODUKTE:")
        for r in results:
            if r["status"] == "BROKEN":
                print(f"  - {r['product']} (ASIN: {r['asin']})")
    
    print(f"\n📄 Ergebnisse gespeichert: {RESULTS_FILE}")

if __name__ == "__main__":
    main()
