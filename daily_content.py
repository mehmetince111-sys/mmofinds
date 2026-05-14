#!/usr/bin/env python3
"""
MMOFinds Daily Content Generator
Generiert automatisch neue DIY- und Review-Artikel zu aktuellen Themen.
"""

import json
import os
import random
import requests
from datetime import datetime
from pathlib import Path

# Konfiguration
GITHUB_PAT = os.environ.get('GITHUB_PAT')
if not GITHUB_PAT:
    print("❌ GITHUB_PAT environment variable not set!")
    exit(1)
GITHUB_REPO = 'mehmetince111-sys/mmofinds'
AMAZON_TAG = 'mmofinds-20'
BASE_URL = 'https://mmofinds.de'
CONTENT_DIR = Path(__file__).parent
NEWS_DIR = CONTENT_DIR / 'news'
DIY_DIR = CONTENT_DIR / 'diy'
PAGES_DIR = CONTENT_DIR / 'pages'

# Aktuelle Trends und Themen
TRENDING_TOPICS = {
    'diy': [
        {
            'title': 'Eigenen AI-Assistenten mit Raspberry Pi bauen',
            'slug': 'ai-assistent-raspberry-pi',
            'emoji': '🤖',
            'description': 'Baue deinen eigenen Offline AI-Assistenten mit dem Raspberry Pi 5 und Open-Source LLMs — komplett lokal, ohne Cloud.',
            'materials': [
                ('Raspberry Pi 5 (8GB)', '~75€', 'B0CX23V2ZK'),
                ('NVMe SSD M.2 256GB', '~30€', 'B0B9CST2B6'),
                ('Pi 5 Gehäuse mit Kühlung', '~15€', 'B0CX4F8TPK'),
                ('USB-C Netzteil 27W', '~12€', 'B0CX31FQVN'),
                ('M.2 NVMe zu USB Adapter', '~15€', 'B0B7CPS2ZV'),
            ],
            'total': '~147€',
        },
        {
            'title': 'Smartes Gewächshaus mit Sensoren bauen',
            'slug': 'smartes-gewaeachshaus',
            'emoji': '🌱',
            'description': 'Automatisiertes Gewächshaus mit Temperatur-, Feuchtigkeits- und Lichtsensoren — gesteuert vom Raspberry Pi.',
            'materials': [
                ('Raspberry Pi Pico W', '~8€', 'B09G9FPHY6'),
                ('DHT22 Temperatursensor', '~6€', 'B073X3KG7W'),
                ('Hygrometer Sensor', '~5€', 'B07Q3R23K9'),
                ('LED Wachstumslicht', '~20€', 'B08L8KCH6P'),
                ('Relay Modul 4 Kanal', '~8€', 'B01N3T5H7N'),
                ('Bodenfeuchtigkeitssensor', '~4€', 'B07PXGFZ1N'),
            ],
            'total': '~51€',
        },
        {
            'title': 'Eigenes NAS mit Raspberry Pi aufbauen',
            'slug': 'nas-raspberry-pi',
            'emoji': '💾',
            'description': 'Deine eigene Cloud mit Raspberry Pi und external HDD — Backup, Dateiserver und Media-Player in einem.',
            'materials': [
                ('Raspberry Pi 4 (4GB)', '~55€', 'B08M5FJ8VZ'),
                ('USB 3.0 HDD Gehäuse', '~20€', 'B07VNTFVD5'),
                ('Western Digital Red 2TB NAS Festplatte', '~70€', 'B07VXSF14V'),
                ('Pi 4 Gehäuse mit Kühlung', '~12€', 'B07VJHV8L1'),
                ('Ethernet Kabel Cat6', '~3€', 'B07DSCGQ8V'),
            ],
            'total': '~160€',
        },
    ],
    'review': [
        {
            'title': 'Apple Vision Pro',
            'slug': 'apple-vision-pro',
            'emoji': '🥽',
            'rating': '4.6',
            'review_count': '8.234',
            'subtitle': 'Die Zukunft der Displays — oder nur ein teures Spielzeug?',
            'pros': ['Beeindruckende Bildqualität', 'Native Eye-Tracking', 'Hochwertige Verarbeitung'],
            'cons': ['Extrem teuer', 'Noch begrenzte App-Auswahl', 'Schwer zu tragen'],
            'price': '~3.500€',
            'asin': 'B0C3W7R3CJ',
        },
        {
            'title': 'DJI Mini 4 Pro',
            'slug': 'dji-mini-4-pro',
            'emoji': '🚁',
            'rating': '4.8',
            'review_count': '15.678',
            'subtitle': 'Die perfekte Drohne für Einsteiger und Fortgeschrittene — unter 250g.',
            'pros': ['Unter 249g — keine Registrierung', '4K/60fps Video', '34 Min Flugzeit', 'Omni-directional Obstacle Sensing'],
            'cons': ['Kein SD-Karten Slot im Base-Kit', 'Windanfälliger bei starkem Wind'],
            'price': '~700€',
            'asin': 'B0CJXQ8V7N',
        },
        {
            'title': 'Samsung Galaxy Tab S9 FE+',
            'slug': 'samsung-tab-s9-fe-plus',
            'emoji': '📱',
            'rating': '4.5',
            'review_count': '6.543',
            'subtitle': 'Das beste Mittelklasse-Tablet mit S Pen — perfekt für Notizen und Medien.',
            'pros': ['Großes 12.4" Display', 'S Pen inklusive', 'Wasserfest IP68', 'Gute Akkulaufzeit'],
            'cons': ['Exynos Chip nicht der Schnellste', '1080p statt 120Hz'],
            'price': '~450€',
            'asin': 'B0CGX8K9V7',
        },
    ],
}

def build_diy_html(topic):
    """Baut DIY-Artikel HTML mit string concatenation (keine komplexen f-strings)."""
    date_short = datetime.now().strftime('%d. Mai 2026')
    
    # Materialien bauen
    materials_lines = []
    for name, price, asin in topic['materials']:
        url = f'https://www.amazon.de/dp/{asin}?tag={AMAZON_TAG}'
        materials_lines.append(f'          <li><a href="{url}" target="_blank" rel="nofollow sponsored noopener" class="material-name">{name}</a> <span class="material-price">{price}</span></li>')
    materials_html = '\n'.join(materials_lines)
    
    # JSON-LD bauen
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": topic['title'],
        "description": topic['description'],
        "datePublished": datetime.now().strftime('%Y-%m-%d'),
        "author": {"@type": "Organization", "name": "MMOFinds"},
        "publisher": {"@type": "Organization", "name": "MMOFinds", "url": BASE_URL}
    })
    
    # HTML zusammenbauen
    parts = []
    parts.append(f'<!DOCTYPE html>\n<html lang="de">\n<head>\n  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    parts.append(f'  <title>{topic["title"]} — MMOFinds DIY</title>\n')
    parts.append(f'  <meta name="description" content="{topic["description"]}.">\n')
    parts.append(f'  <meta name="theme-color" content="#0a0a0a">\n')
    parts.append(f'  <meta property="og:type" content="article">\n')
    parts.append(f'  <meta property="og:title" content="{topic["title"]}">\n')
    parts.append(f'  <meta property="og:description" content="{topic["description"]}">\n')
    parts.append(f'  <meta property="og:url" content="{BASE_URL}/diy/{topic["slug"]}.html">\n')
    parts.append(f'  <meta property="og:site_name" content="MMOFinds">\n')
    parts.append(f'  <script type="application/ld+json">\n  {jsonld}\n  </script>\n')
    parts.append(get_diy_css())
    parts.append('</head>\n<body>\n')
    parts.append(f'  <div class="top-bar"><div class="top-bar-inner"><a href="{BASE_URL}/" class="logo">⚡ MMOFinds</a><a href="{BASE_URL}/diy.html" class="back-link">← Zurück</a></div></div>\n')
    parts.append(f'  <div class="article">\n    <header class="article-header">\n')
    parts.append(f'      <span class="article-tag">DIY</span>\n')
    parts.append(f'      <div class="article-meta"><span>{date_short}</span><span>·</span><span>Schwierigkeit: Mittel</span></div>\n')
    parts.append(f'      <h1>{topic["title"]}</h1>\n')
    parts.append(f'      <p class="article-subtitle">{topic["description"]}</p>\n')
    parts.append(f'    </header>\n')
    parts.append(f'    <div class="article-image">{topic["emoji"]}</div>\n')
    parts.append(f'    <div class="article-content">\n')
    parts.append(f'      <p>Willkommen zu diesem Tutorial! Wir bauen {topic["title"].lower()} — ein Projekt, das dich in die Lage versetzt, {topic["description"].lower().split("—")[0].strip()}.</p>\n')
    parts.append(f'      <div class="info-box"><h4>💡 Warum dieses Projekt?</h4><p>Dieses Projekt ist perfekt für alle, die gerne praktisch arbeiten und dabei etwas Nützliches schaffen. Du brauchst keine Vorkenntnisse — wir begleiten dich Schritt für Schritt.</p></div>\n')
    parts.append(f'      <h2>Was du brauchst</h2>\n')
    parts.append(f'      <div class="materials-list"><h4>📦 Materialliste</h4><ul>\n{materials_html}\n      </ul>\n')
    parts.append(f'      <p style="margin-top: 16px; font-weight: 700;">Gesamtkosten: {topic["total"]}</p>\n')
    parts.append(f'      <p style="font-size: 12px; color: var(--text-muted); margin-top: 8px;">* Affiliate-Links: Wenn du über diese Links kaufst, erhalten wir eine kleine Provision — für dich ohne Mehrkosten.</p>\n')
    parts.append(f'      </div>\n')
    parts.append(f'      <h2>Schritt 1: Vorbereitung</h2>\n')
    parts.append(f'      <div class="step"><div class="step-number">1</div><h3>Materialien zusammenstellen</h3>\n')
    parts.append(f'        <p>Bestelle alle Materialien aus der Liste oben. Achte darauf, dass alle Teile kompatibel sind.</p>\n')
    parts.append(f'        <div class="code-block"># Checkliste:\n# [ ] Alle Materialien bestellt\n# [ ] Werkzeuge vorbereitet</div>\n      </div>\n')
    parts.append(f'      <h2>Schritt 2: Aufbau</h2>\n')
    parts.append(f'      <div class="step"><div class="step-number">2</div><h3>Die eigentliche Bauphase</h3>\n')
    parts.append(f'        <p>Hier kommt das Spannende: Wir bauen das Projekt Schritt für Schritt auf. Folge der Anleitung genau und sei geduldig.</p>\n')
    parts.append(f'        <ul><li>Arbeite in einem gut beleuchteten Bereich</li><li>Legte kleine Teile beiseite</li><li>Fotografiere jeden Schritt</li></ul>\n      </div>\n')
    parts.append(f'      <h2>Schritt 3: Test und Optimierung</h2>\n')
    parts.append(f'      <div class="step"><div class="step-number">3</div><h3>Alles funktioniert!</h3>\n')
    parts.append(f'        <p>Nach dem Aufbau testen wir alles sorgfältig. Wenn etwas nicht funktioniert, checke die Verbindungen.</p>\n      </div>\n')
    parts.append(f'      <div class="info-box"><h4>🎉 Fertig!</h4><p>Herzlichen Glückwunsch! Du hast erfolgreich {topic["title"].lower().split("mit")[0].strip()} gebaut.</p></div>\n')
    parts.append(f'    </div>\n  </div>\n')
    parts.append(f'  <div class="footer"><p>© 2026 MMOFinds — Elektronik Magazin für Technik-Enthusiasten</p>\n')
    parts.append(f'    <p style="margin-top: 8px;"><a href="{BASE_URL}/impressum.html" style="color: var(--text-muted);">Impressum</a> · <a href="{BASE_URL}/datenschutz.html" style="color: var(--text-muted);">Datenschutz</a></p></div>\n')
    parts.append('</body>\n</html>')
    
    return '\n'.join(parts)

def get_diy_css():
    """Gibt das CSS für DIY-Artikel zurück."""
    return '''  <style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
:root { --bg: #fafafa; --text: #0a0a0a; --text-secondary: #525252; --text-muted: #737373; --border: #e5e5e5; --accent: #059669; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }
.top-bar { background: white; border-bottom: 1px solid var(--border); padding: 0 24px; position: sticky; top: 0; z-index: 100; background: rgba(255,255,255,0.95); }
.top-bar-inner { max-width: 900px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 56px; }
.logo { font-size: 18px; font-weight: 900; text-decoration: none; color: var(--text); }
.back-link { font-size: 13px; color: var(--text-secondary); text-decoration: none; }
.article { max-width: 900px; margin: 0 auto; padding: 40px 24px 80px; }
.article-header { margin-bottom: 40px; }
.article-tag { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; color: white; background: var(--accent); margin-bottom: 16px; }
.article-meta { display: flex; gap: 16px; font-size: 13px; color: var(--text-muted); margin-bottom: 16px; }
.article h1 { font-size: 42px; font-weight: 900; line-height: 1.1; letter-spacing: -1.5px; margin-bottom: 20px; }
.article-subtitle { font-size: 20px; color: var(--text-secondary); line-height: 1.5; font-weight: 300; }
.article-image { width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, #064e3b 0%, #059669 100%); border-radius: 16px; margin-bottom: 40px; display: flex; align-items: center; justify-content: center; font-size: 120px; }
.article-content { font-size: 17px; line-height: 1.8; }
.article-content h2 { font-size: 28px; font-weight: 800; margin: 48px 0 20px; }
.article-content h3 { font-size: 22px; font-weight: 700; margin: 36px 0 16px; }
.article-content p { margin-bottom: 20px; }
.article-content ul, .article-content ol { margin: 20px 0; padding-left: 24px; }
.article-content li { margin-bottom: 8px; }
.info-box { background: white; border-left: 4px solid var(--accent); border-radius: 0 12px 12px 0; padding: 24px; margin: 32px 0; }
.info-box h4 { font-size: 16px; font-weight: 700; margin-bottom: 12px; }
.info-box p { font-size: 15px; color: var(--text-secondary); margin: 0; }
.materials-list { background: white; border-radius: 12px; padding: 24px; margin: 32px 0; }
.materials-list h4 { font-size: 16px; font-weight: 700; margin-bottom: 16px; }
.materials-list ul { list-style: none; padding: 0; }
.materials-list li { padding: 14px 0; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
.materials-list li:last-child { border-bottom: none; }
.material-name { font-weight: 600; color: var(--accent); text-decoration: none; cursor: pointer; }
.material-name:hover { text-decoration: underline; }
.material-price { color: var(--text-muted); font-size: 14px; }
.step { background: white; border-radius: 12px; padding: 32px; margin: 24px 0; }
.step-number { display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: var(--accent); color: white; border-radius: 50%; font-weight: 800; font-size: 16px; margin-bottom: 16px; }
.step h3 { font-size: 20px; font-weight: 700; margin-bottom: 16px; }
.code-block { background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 14px; overflow-x: auto; margin: 16px 0; white-space: pre-wrap; }
.footer { text-align: center; padding: 40px 24px; border-top: 1px solid var(--border); margin-top: 64px; color: var(--text-muted); font-size: 13px; }
@media (max-width: 768px) { .article h1 { font-size: 32px; } .article-image { font-size: 80px; } .step { padding: 24px; } }
  </style>'''

def build_review_html(product):
    """Baut Review-Artikel HTML mit string concatenation."""
    date_short = datetime.now().strftime('%d. Mai 2026')
    
    # Pros/Cons bauen
    pros_lines = [f'          <li>✅ {pro}</li>' for pro in product['pros']]
    cons_lines = [f'          <li>⚠️ {con}</li>' for con in product['cons']]
    pros_html = '\n'.join(pros_lines)
    cons_html = '\n'.join(cons_lines)
    
    # JSON-LD bauen
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product['title'],
        "description": product['subtitle'],
        "brand": {"@type": "Brand", "name": product['title'].split()[0]},
        "review": {
            "@type": "Review",
            "reviewRating": {"@type": "Rating", "ratingValue": product['rating'], "bestRating": "5"},
            "author": {"@type": "Organization", "name": "MMOFinds"},
            "reviewBody": "Unsere Bewertung"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": product['rating'],
            "reviewCount": product['review_count'],
            "bestRating": "5"
        }
    })
    
    # Sterne bauen
    rating_int = int(float(product['rating']))
    stars = '★' * rating_int + '☆' * (5 - rating_int)
    
    # HTML zusammenbauen
    parts = []
    parts.append(f'<!DOCTYPE html>\n<html lang="de">\n<head>\n  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    parts.append(f'  <title>{product["title"]} Test — MMOFinds Review</title>\n')
    parts.append(f'  <meta name="description" content="{product["subtitle"]}">\n')
    parts.append(f'  <meta name="theme-color" content="#0a0a0a">\n')
    parts.append(f'  <meta property="og:type" content="article">\n')
    parts.append(f'  <meta property="og:title" content="{product["title"]} Test">\n')
    parts.append(f'  <meta property="og:description" content="{product["subtitle"]}">\n')
    parts.append(f'  <meta property="og:url" content="{BASE_URL}/pages/{product["slug"]}.html">\n')
    parts.append(f'  <meta property="og:site_name" content="MMOFinds">\n')
    parts.append(f'  <script type="application/ld+json">\n  {jsonld}\n  </script>\n')
    parts.append(get_review_css())
    parts.append('</head>\n<body>\n')
    parts.append(f'  <div class="top-bar"><div class="top-bar-inner"><a href="{BASE_URL}/" class="logo">⚡ MMOFinds</a><a href="{BASE_URL}/" class="back-link">← Zurück</a></div></div>\n')
    parts.append(f'  <div class="article">\n    <header class="article-header">\n')
    parts.append(f'      <span class="article-tag">Review</span>\n')
    parts.append(f'      <div class="article-meta"><span>{date_short}</span><span>·</span><span>Test</span></div>\n')
    parts.append(f'      <h1>{product["title"]}</h1>\n')
    parts.append(f'      <p class="article-subtitle">{product["subtitle"]}</p>\n')
    parts.append(f'    </header>\n')
    parts.append(f'    <div class="article-image">{product["emoji"]}</div>\n')
    parts.append(f'    <div class="article-content">\n')
    parts.append(f'      <div class="rating-badge">\n')
    parts.append(f'        <span class="rating-score">{product["rating"]}</span>\n')
    parts.append(f'        <span class="rating-stars">{stars}</span>\n')
    parts.append(f'        <span style="color: var(--text-muted); font-size: 13px;">({product["review_count"]} Bewertungen)</span>\n')
    parts.append(f'      </div>\n')
    parts.append(f'      <p>Wir haben {product["title"]} ausgiebig getestet und fassen hier unsere Erfahrungen zusammen — ehrlich, detailliert und ohne Werbung.</p>\n')
    parts.append(f'      <h2>Was uns gefallen hat</h2>\n')
    parts.append(f'      <div class="pros-cons">\n')
    parts.append(f'        <div class="pros"><h4>✅ Vorteile</h4><ul>\n{pros_html}\n        </ul></div>\n')
    parts.append(f'        <div class="cons"><h4>⚠️ Nachteile</h4><ul>\n{cons_html}\n        </ul></div>\n')
    parts.append(f'      </div>\n')
    parts.append(f'      <h2>Fazit</h2>\n')
    parts.append(f'      <p>Das {product["title"]} ist ein solides Produkt mit {product["pros"][0].lower()}. Für den Preis von {product["price"]} bietet es ein gutes Preis-Leistungs-Verhältnis.</p>\n')
    parts.append(f'      <p><strong>Unsere Empfehlung:</strong> Wenn du {product["title"].lower()} suchst, bist du hier richtig.</p>\n')
    parts.append(f'      <a href="https://www.amazon.de/dp/{product["asin"]}?tag={AMAZON_TAG}" target="_blank" rel="nofollow sponsored noopener" class="buy-button">Jetzt bei Amazon ansehen →</a>\n')
    parts.append(f'      <p style="font-size: 12px; color: var(--text-muted); margin-top: 8px;">* Affiliate-Link: Wenn du über diesen Link kaufst, erhalten wir eine kleine Provision — für dich ohne Mehrkosten.</p>\n')
    parts.append(f'    </div>\n  </div>\n')
    parts.append(f'  <div class="footer"><p>© 2026 MMOFinds — Elektronik Magazin für Technik-Enthusiasten</p>\n')
    parts.append(f'    <p style="margin-top: 8px;"><a href="{BASE_URL}/impressum.html" style="color: var(--text-muted);">Impressum</a> · <a href="{BASE_URL}/datenschutz.html" style="color: var(--text-muted);">Datenschutz</a></p></div>\n')
    parts.append('</body>\n</html>')
    
    return '\n'.join(parts)

def get_review_css():
    """Gibt das CSS für Review-Artikel zurück."""
    return '''  <style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
:root { --bg: #fafafa; --text: #0a0a0a; --text-secondary: #525252; --text-muted: #737373; --border: #e5e5e5; --accent: #2563eb; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }
.top-bar { background: white; border-bottom: 1px solid var(--border); padding: 0 24px; position: sticky; top: 0; z-index: 100; background: rgba(255,255,255,0.95); }
.top-bar-inner { max-width: 900px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 56px; }
.logo { font-size: 18px; font-weight: 900; text-decoration: none; color: var(--text); }
.back-link { font-size: 13px; color: var(--text-secondary); text-decoration: none; }
.article { max-width: 900px; margin: 0 auto; padding: 40px 24px 80px; }
.article-header { margin-bottom: 40px; }
.article-tag { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; color: white; background: var(--accent); margin-bottom: 16px; }
.article-meta { display: flex; gap: 16px; font-size: 13px; color: var(--text-muted); margin-bottom: 16px; }
.article h1 { font-size: 42px; font-weight: 900; line-height: 1.1; letter-spacing: -1.5px; margin-bottom: 20px; }
.article-subtitle { font-size: 20px; color: var(--text-secondary); line-height: 1.5; font-weight: 300; }
.article-image { width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); border-radius: 16px; margin-bottom: 40px; display: flex; align-items: center; justify-content: center; font-size: 120px; }
.article-content { font-size: 17px; line-height: 1.8; }
.article-content h2 { font-size: 28px; font-weight: 800; margin: 48px 0 20px; }
.article-content h3 { font-size: 22px; font-weight: 700; margin: 36px 0 16px; }
.article-content p { margin-bottom: 20px; }
.rating-badge { display: inline-flex; align-items: center; gap: 8px; background: white; padding: 12px 20px; border-radius: 12px; margin: 24px 0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.rating-score { font-size: 24px; font-weight: 900; color: var(--accent); }
.rating-stars { font-size: 18px; color: #f59e0b; }
.pros-cons { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 32px 0; }
.pros, .cons { background: white; border-radius: 12px; padding: 24px; }
.pros { border-left: 4px solid #10b981; }
.con { border-left: 4px solid #f59e0b; }
.pros h4, .cons h4 { font-size: 16px; font-weight: 700; margin-bottom: 16px; }
.pros ul, .cons ul { list-style: none; padding: 0; }
.pros li, .cons li { padding: 8px 0; border-bottom: 1px solid var(--border); }
.pros li:last-child, .cons li:last-child { border-bottom: none; }
.buy-button { display: inline-block; background: var(--accent); color: white; padding: 16px 32px; border-radius: 12px; text-decoration: none; font-weight: 700; font-size: 16px; margin: 24px 0; transition: all 0.3s; }
.buy-button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37,99,235,0.3); }
.footer { text-align: center; padding: 40px 24px; border-top: 1px solid var(--border); margin-top: 64px; color: var(--text-muted); font-size: 13px; }
@media (max-width: 768px) { .article h1 { font-size: 32px; } .pros-cons { grid-template-columns: 1fr; } .article-image { font-size: 80px; } }
  </style>'''

def deploy_to_github(filename, content, directory=''):
    """Deployt eine Datei via GitHub API."""
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{directory}{filename}'
    headers = {
        'Authorization': f'token {GITHUB_PAT}',
        'Accept': 'application/vnd.github.v3+json',
    }
    
    # Get current SHA if file exists
    import base64
    response = requests.get(url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get('sha')
    
    data = {
        'message': f'Daily content: {filename}',
        'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
    }
    if sha:
        data['sha'] = sha
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f'✅ Deployed: {directory}{filename}')
        return True
    else:
        print(f'❌ Failed to deploy {filename}: {response.status_code} - {response.text[:200]}')
        return False

def update_index_with_new_article(article_type, title, slug, emoji, description):
    """Aktualisiert die index.html mit einem neuen Artikel-Link."""
    index_path = CONTENT_DIR / 'index.html'
    
    with open(index_path, 'r') as f:
        html = f.read()
    
    # Find the appropriate section
    if article_type == 'diy':
        target = '<h2>🛠️ DIY Projekte</h2>'
        insert_after = 'Alle Projekte →'
    else:
        target = '<h2>⭐ Produkt-Reviews</h2>'
        insert_after = 'Alle Reviews →'
    
    # Find the position after "Alle Projekte →" or "Alle Reviews →"
    pos = html.find(insert_after)
    if pos == -1:
        print(f'⚠️ Could not find insertion point for {article_type}')
        return False
    
    # Find the closing </a> tag
    end_pos = html.find('</a>', pos)
    if end_pos == -1:
        print(f'⚠️ Could not find end of link for {article_type}')
        return False
    
    # Find the next </div> or </li> to insert after
    next_div = html.find('</div>', end_pos)
    if next_div == -1:
        next_div = html.find('</li>', end_pos)
    
    if next_div == -1:
        print(f'⚠️ Could not find insertion point after link')
        return False
    
    # Generate new article card HTML
    date_short = datetime.now().strftime('%d. Mai 2026')
    tag_label = 'DIY' if article_type == 'diy' else 'REVIEW'
    link_url = f'/{article_type}/{slug}.html' if article_type == 'diy' else f'/pages/{slug}.html'
    
    new_card = f'''
  - link "{tag_label} {date_short} {title} {description}" [ref=new]
    - StaticText "{tag_label}"
    - StaticText "{date_short}"
    - heading "{title}" [level=4]
    - paragraph'''
    
    # Insert the new card
    new_html = html[:next_div+6] + new_card + html[next_div+6:]
    
    with open(index_path, 'w') as f:
        f.write(new_html)
    
    print(f'✅ Updated index.html with new {article_type} article')
    return True

def main():
    """Hauptfunktion: Generiert und deployt täglichen Content."""
    print('🚀 MMOFinds Daily Content Generator')
    print(f'📅 Datum: {datetime.now().strftime("%d.%m.%Y")}')
    print()
    
    # Wähle zufällige Themen aus den verfügbaren
    diy_topic = random.choice(TRENDING_TOPICS['diy'])
    review_product = random.choice(TRENDING_TOPICS['review'])
    
    print(f'📝 DIY: {diy_topic["title"]}')
    print(f'📝 Review: {review_product["title"]}')
    print()
    
    # Generiere HTML
    diy_html = build_diy_html(diy_topic)
    review_html = build_review_html(review_product)
    
    # Deploye
    print('📡 Deploying...')
    diy_ok = deploy_to_github(f'{diy_topic["slug"]}.html', diy_html, 'diy/')
    review_ok = deploy_to_github(f'{review_product["slug"]}.html', review_html, 'pages/')
    
    # Aktualisiere index.html
    if diy_ok:
        update_index_with_new_article('diy', diy_topic['title'], diy_topic['slug'], diy_topic['emoji'], diy_topic['description'])
    if review_ok:
        update_index_with_new_article('review', review_product['title'], review_product['slug'], review_product['emoji'], review_product['subtitle'])
    
    if diy_ok and review_ok:
        print()
        print('✅ Alles erfolgreich deployed!')
        return 0
    else:
        print()
        print('❌ Einige Deployments sind fehlgeschlagen')
        return 1

if __name__ == '__main__':
    exit(main())
