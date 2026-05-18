#!/usr/bin/env python3
"""
MMOFinds - Amazon Product Data Updater
=======================================
Sammelt Amazon-Produktdaten (Preis, Bild, Amazon-Link) und aktualisiert
die existierenden Review-Seiten.

Da curl von Amazon blockiert wird, verwenden wir den Browser.
"""

import json
import os
import re
import subprocess
import time
from pathlib import Path

REPO_DIR = Path('/root/mmofinds')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
AMAZON_TAG = 'mmofinds-20'

# Alle Produkte aus der Pipeline
PRODUCTS = [
    ('iphone-16-pro', 'iPhone 16 Pro', 'Smartphone', 'iPhone 16 Pro', 'B0DGRD7HBY'),
    ('samsung-galaxy-s25-ultra', 'Samsung Galaxy S25 Ultra', 'Smartphone', 'Samsung Galaxy S25 Ultra', 'B0DS9DQJ8S'),
    ('google-pixel-9-pro', 'Google Pixel 9 Pro', 'Smartphone', 'Google Pixel 9 Pro', 'B0DCKJ4P8V'),
    ('sony-wh1000xm5', 'Sony WH-1000XM5', 'Kopfhörer', 'Sony WH-1000XM5', 'B09XS7JWHH'),
    ('apple-airpods-pro-2', 'Apple AirPods Pro 2', 'In-Ear', 'Apple AirPods Pro 2 USB-C', 'B0D63ZB1V3'),
    ('bose-quietcomfort-ultra', 'Bose QuietComfort Ultra', 'Kopfhörer', 'Bose QuietComfort Ultra Headphones', 'B0CCZ26V5V'),
    ('sennheiser-momentum-4', 'Sennheiser Momentum 4', 'Kopfhörer', 'Sennheiser Momentum 4 Wireless', 'B0B8RZ3K8V'),
    ('apple-watch-series-10', 'Apple Watch Series 10', 'Smartwatch', 'Apple Watch Series 10', 'B0DGRJ8F8L'),
    ('samsung-galaxy-watch-7', 'Samsung Galaxy Watch 7', 'Smartwatch', 'Samsung Galaxy Watch 7', 'B0CDBGK5P3'),
    ('ipad-air-m3', 'iPad Air M3', 'Tablet', 'iPad Air M3 2025', 'B0DS95F4HT'),
    ('sony-alpha-7c-ii', 'Sony Alpha 7C II', 'Kamera', 'Sony Alpha 7C II', 'B0C7CDCK1G'),
    ('canon-eos-r50', 'Canon EOS R50', 'Kamera', 'Canon EOS R50', 'B0C93F5K7G'),
    ('macbook-air-m4', 'MacBook Air M4', 'Laptop', 'MacBook Air M4 2024', 'B0CX24R21T'),
    ('logitech-mx-master-3s', 'Logitech MX Master 3S', 'Maus', 'Logitech MX Master 3S', 'B09HMBCQHY'),
    ('dyson-v15-detect', 'Dyson V15 Detect', 'Staubsauger', 'Dyson V15 Detect', 'B0CH5QWSGK'),
    ('roborock-s8', 'Roborock S8', 'Staubsauger', 'Roborock S8', 'B0C1L6F3VH'),
    ('kindle-paperwhite-2024', 'Kindle Paperwhite 2024', 'E-Reader', 'Kindle Paperwhite 2024', 'B0BLRDK3YP'),
]


def scrape_amazon_product(browser, asin, product_name):
    """
    Sammelt Amazon-Produktdaten über den Browser.
    Gibt ein Dict zurück mit: title, price, image_url, amazon_url
    """
    try:
        # Navigiere zur Amazon-Produktdetailseite
        url = f'https://www.amazon.de/dp/{asin}'
        browser_navigate(url)
        time.sleep(3)  # Warte auf Laden
        
        # Akzeptiere Cookies
        try:
            # Versuche, das Cookie-Banner zu schließen
            for ref in ['@e83', '@e84']:  # Accept oder Decline
                try:
                    browser_click(ref)
                    time.sleep(1)
                    break
                except:
                    continue
        except:
            pass
        
        # Extrahiere Produktdaten
        title_result = browser_console(
            expression=f"""
                const t = document.querySelector('#productTitle')?.textContent?.trim() || '{product_name}';
                const p = document.querySelector('#priceblock_ourprice, #priceblock_dealprice')?.textContent?.trim() || '';
                const i = document.querySelector('#landingImage, #imgBlkFront')?.src || '';
                JSON.stringify({title: t, price: p, image: i});
            """
        )
        
        # Parse das Ergebnis
        if isinstance(title_result, dict) and 'result' in title_result:
            data = json.loads(title_result['result'])
        else:
            data = {'title': product_name, 'price': '', 'image': ''}
        
        # Wenn kein Preis gefunden, versuche alle Preise zu parsen
        if not data['price'] or '€' not in data['price']:
            all_prices = browser_console(
                expression="""
                    const prices = [];
                    document.querySelectorAll('.a-price .a-offscreen').forEach(el => {
                        prices.push(el.textContent.trim());
                    });
                    JSON.stringify(prices);
                """
            )
            if isinstance(all_prices, dict) and 'result' in all_prices:
                price_list = json.loads(all_prices['result'])
                # Filtere Preise, die > 100 sind (wahrscheinlich der Hauptpreis)
                high_prices = [p for p in price_list if '€' in p and float(p.replace('€', '').replace(',', '')) > 100]
                if high_prices:
                    data['price'] = high_prices[0]
        
        # Amazon-Link mit Tag
        amazon_url = f'https://www.amazon.de/dp/{asin}?tag={AMAZON_TAG}'
        
        return {
            'title': data.get('title', product_name),
            'price': data.get('price', ''),
            'image_url': data.get('image', ''),
            'amazon_url': amazon_url,
        }
    except Exception as e:
        print(f'    ❌ Error scraping {asin}: {e}')
        return None


def update_html_with_amazon_data(filepath, amazon_data):
    """
    Aktualisiert die HTML-Datei mit Amazon-Produktdaten.
    """
    if not os.path.exists(filepath):
        print(f'    ⚠️  File not found: {filepath}')
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Prüfe, ob Amazon-Daten bereits vorhanden sind
    if 'amazon.de' in html and 'tag=mmofinds-20' in html:
        print(f'    ⏭️  Already has Amazon data')
        return False
    
    price = amazon_data['price']
    image_url = amazon_data['image_url']
    amazon_url = amazon_data['amazon_url']
    
    # Ersetze das Hero-Bild mit dem Amazon-Bild
    if image_url:
        # Verwende ein höheres Bild
        high_res_url = image_url.replace('_AC_SX569_', '_AC_SL1500_')
        html = re.sub(
            r'<img[^>]*class="review-hero-image"[^>]*src="[^"]*"[^>]*>',
            f'<img src="{high_res_url}" alt="Product" class="review-hero-image" loading="lazy">',
            html,
            count=1
        )
    
    # Füge Amazon-Preis und Link hinzu
    if price:
        # Finde die Rating-Sektion und füge Preis darunter ein
        price_section = f'''
        <section class="price-section">
            <span class="price-label">Aktueller Preis:</span>
            <span class="price-value">{price}</span>
            <a href="{amazon_url}" class="amazon-link" target="_blank" rel="nofollow sponsored">
                Bei Amazon ansehen →
            </a>
        </section>'''
        
        # Füge nach der Rating-Sektion ein
        if 'rating-section' in html:
            html = html.replace(
                '</div>\n        </section>',
                f'</div>\n        </section>\n{price_section}',
                1
            )
    
    # Schreibe die aktualisierte HTML-Datei
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'    ✅ Updated with Amazon data')
    return True


def main():
    print("=" * 60)
    print("  MMOFinds - Amazon Product Data Updater")
    print("=" * 60)
    print()
    
    updated_count = 0
    skipped_count = 0
    
    for key, name, category, search_term, asin in PRODUCTS:
        print(f"📦 {name} (ASIN: {asin})")
        
        # Finde die HTML-Datei
        filepath = REPO_DIR / 'pages' / f'{key}.html'
        if not filepath.exists():
            print(f'    ⏭️  Skipped (file not found)')
            skipped_count += 1
            continue
        
        # Sammle Amazon-Daten
        print(f'    🌐 Scraping Amazon...')
        amazon_data = scrape_amazon_product(None, asin, name)
        
        if not amazon_data:
            print(f'    ❌ Failed to scrape')
            skipped_count += 1
            continue
        
        print(f'    📊 Title: {amazon_data["title"]}')
        print(f'    💰 Price: {amazon_data["price"]}')
        print(f'    🔗 Amazon URL: {amazon_data["amazon_url"]}')
        
        # Aktualisiere die HTML-Datei
        if update_html_with_amazon_data(filepath, amazon_data):
            updated_count += 1
        
        # Warte kurz, um nicht zu viele Anfragen zu senden
        time.sleep(1)
    
    print()
    print("=" * 60)
    print(f"  ✅ SUMMARY")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    main()
