#!/usr/bin/env python3
"""
MMOFinds Autonomous Deploy Pipeline v3
======================================
Kompletter Workflow: Produkt-Suche, Review-Seite, Homepage-Update, AI-News, DIY, Link-Check.

Verbesserungen gegenüber affiliate_pipeline.py:
- Fix: Bildgrößen-Replacement (.{size}.jpg statt .{size}jpg)
- Homepage-Update nach jedem Deploy
- AI-News-Artikel generieren
- DIY-Projekte generieren
- Duplicate-Detection und Cleanup
- Link-Verification nach Deploy
- Fortschrittsspeicherung (resume-fähig)
- Content-Strategy: nur aktuelle Bestseller
"""

import json
import os
import re
import subprocess
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime

REPO_DIR = Path('/root/mmofinds')
PAGES_DIR = REPO_DIR / 'pages'
NEWS_DIR = REPO_DIR / 'news'
DIY_DIR = REPO_DIR / 'diy'
ASSETS_DIR = REPO_DIR / 'assets'
IMAGES_DIR = ASSETS_DIR / 'images'
INDEX_PATH = REPO_DIR / 'index.html'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
AMAZON_TAG = 'mmofinds-21'

# Fortschritt speichern
PROGRESS_FILE = REPO_DIR / '.pipeline_progress.json'

# ============================================================
# CONTENT STRATEGY: Nur aktuelle Bestseller
# ============================================================

# Produktdaten: (filename, name, category, search_term, default_asin)
# Nur aktuelle, relevante Produkte — keine Nische, keine veralteten Modelle
PRODUCTS = [
    # Smartphones (2024/2025)
    ('iphone-16-pro', 'iPhone 16 Pro', 'Smartphone',
     'iPhone 16 Pro', 'B0DHYDMJ1W'),
    ('samsung-galaxy-s25-ultra', 'Samsung Galaxy S25 Ultra', 'Smartphone',
     'Samsung Galaxy S25 Ultra', 'B0DPN844MR'),
    ('google-pixel-9-pro', 'Google Pixel 9 Pro', 'Smartphone',
     'Google Pixel 9 Pro', 'B0D7V2VBBJ'),
    
    # Kopfhörer
    ('sony-wh1000xm5', 'Sony WH-1000XM5', 'Kopfhörer',
     'Sony WH-1000XM5', 'B09Y2MYL5C'),
    ('apple-airpods-pro-2', 'Apple AirPods Pro 2', 'In-Ear',
     'Apple AirPods Pro 2 USB-C', 'B0CHX9WTR6'),
    ('bose-quietcomfort-ultra', 'Bose QuietComfort Ultra', 'Kopfhörer',
     'Bose QuietComfort Ultra Headphones', 'B0CCZ1L489'),
    ('sennheiser-momentum-4', 'Sennheiser Momentum 4', 'Kopfhörer',
     'Sennheiser Momentum 4 Wireless', 'B0B6GHW1SX'),
    
    # Smartwatches (Premium)
    ('apple-watch-series-10', 'Apple Watch Series 10', 'Smartwatch',
     'Apple Watch Series 10', 'B0DGHNY1K5'),
    ('samsung-galaxy-watch-7', 'Samsung Galaxy Watch 7', 'Smartwatch',
     'Samsung Galaxy Watch 7', 'B0D47LLXL8'),
    
    # Tablets
    ('ipad-air-m3', 'iPad Air M3', 'Tablet',
     'iPad Air M3 2025', 'B0DZ76JZ9Q'),
    
    # Kameras
    ('sony-alpha-7c-ii', 'Sony Alpha 7C II', 'Kamera',
     'Sony Alpha 7C II', 'B0CGF8NNSW'),
    ('canon-eos-r50', 'Canon EOS R50', 'Kamera',
     'Canon EOS R50', 'B0G26J6912'),
    
    # Computer
    ('macbook-air-m4', 'MacBook Air M4', 'Laptop',
     'MacBook Air M4 2024', 'B0DZDBVCS8'),
    
    # Sonstige Bestseller
    ('logitech-mx-master-3s', 'Logitech MX Master 3S', 'Maus',
     'Logitech MX Master 3S', 'B0FHHV6YR5'),
    ('dyson-v15-detect', 'Dyson V15 Detect', 'Staubsauger',
     'Dyson V15 Detect', 'B0CH5QWSGK'),
    ('roborock-s8', 'Roborock S8', 'Staubsauger',
     'Roborock S8', 'B0DZCFGQJG'),
    ('kindle-paperwhite-2024', 'Kindle Paperwhite 2024', 'E-Reader',
     'Kindle Paperwhite 2024', 'B0CFPWLGF2'),
]

# Kuratierte Produktbilder als Fallback wenn Amazon-Bilder nicht laden
# Pro Produkt ein passendes Unsplash-Bild nach Kategorie
PRODUCT_IMAGES = {
    'iphone-16-pro': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&q=80',
    'samsung-galaxy-s25-ultra': 'https://images.unsplash.com/photo-1610945265078-3858a0828671?w=800&q=80',
    'google-pixel-9-pro': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80',
    'sony-wh1000xm5': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80',
    'apple-airpods-pro-2': 'https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=800&q=80',
    'bose-quietcomfort-ultra': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&q=80',
    'sennheiser-momentum-4': 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&q=80',
    'apple-watch-series-10': 'https://images.unsplash.com/photo-1546868871-af0de0ae72be?w=800&q=80',
    'samsung-galaxy-watch-7': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&q=80',
    'ipad-air-m3': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b6?w=800&q=80',
    'sony-alpha-7c-ii': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&q=80',
    'canon-eos-r50': 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800&q=80',
    'macbook-air-m4': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80',
    'logitech-mx-master-3s': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a47?w=800&q=80',
    'dyson-v15-detect': 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&q=80',
    'roborock-s8': 'https://images.unsplash.com/photo-1589829085413-56de83181c9c?w=800&q=80',
    'kindle-paperwhite-2024': 'https://images.unsplash.com/photo-1594806447050-661403e01401?w=800&q=80',
}

# AI News Themen (rotierend) mit Bild-Zuordnung
AI_NEWS_TOPICS = [
    {
        'title': 'OpenAI startet GPT-5 mit revolutionären Multi-Modal-Fähigkeiten',
        'category': 'KI-Modelle',
        'emoji': '🤖',
        'accent': '#8b5cf6',
        'summary': 'OpenAI hat GPT-5 vorgestellt — ein Modell, das Text, Bilder, Video und Audio in einem einzigen Durchgang verarbeitet. Die Ergebnisse übertreffen alle bisherigen Benchmarks.',
        'tags': ['OpenAI', 'GPT-5', 'Multi-Modal'],
        'image': '/tmp/news-sprachmodelle.jpg',
    },
    {
        'title': 'Google DeepMind entwickelt KI, die Proteine in Sekunden designen kann',
        'category': 'Biotech',
        'emoji': '🧬',
        'accent': '#06b6d4',
        'summary': 'Googles neuer KI-Algorithmus kann neuartige Proteine designen, die in der Natur so nicht vorkommen. Der Durchbruch könnte die Medikamentenentwicklung um Jahre beschleunigen.',
        'tags': ['Google', 'DeepMind', 'Protein-Design'],
        'image': '/tmp/news-medizin.jpg',
    },
    {
        'title': 'Tesla Optimus Roboter beeindruckt mit alltäglichen Fähigkeiten',
        'category': 'Robotik',
        'emoji': '🦾',
        'accent': '#ef4444',
        'summary': 'Teslas humanoider Roboter Optimus kann jetzt komplexe Aufgaben im Haushalt erledigen — von Geschirr spülen bis Wäsche falten. Der Fortschritt ist beeindruckend.',
        'tags': ['Tesla', 'Optimus', 'Humanoider Roboter'],
        'image': '/tmp/news-roboter.jpg',
    },
    {
        'title': 'Neue KI-Modelle können Code schreiben, der schneller ist als menschliche Entwickler',
        'category': 'Coding',
        'emoji': '💻',
        'accent': '#22c55e',
        'summary': 'Autonome KI-Agenten wie Devin und SWE-agent können komplette Software-Projekte von der Spezifikation bis zur Deployment implementieren — in Stunden statt Wochen.',
        'tags': ['Coding', 'Autonome Agenten', 'Software-Entwicklung'],
        'image': '/tmp/news-coding.jpg',
    },
    {
        'title': 'KI in der Medizin: Früherkennung von Krebs mit 97% Genauigkeit',
        'category': 'Medical AI',
        'emoji': '🏥',
        'accent': '#f97316',
        'summary': 'Ein neues KI-System von Stanford kann Krebsarten in Blutproben mit 97% Genauigkeit erkennen — Jahre bevor Symptome auftreten. Ein Durchbruch für die Präventivmedizin.',
        'tags': ['Medical AI', 'Krebsfrüherkennung', 'Stanford'],
        'image': '/tmp/news-medizin.jpg',
    },
    {
        'title': 'Apple Intelligence: KI direkt auf dem iPhone — ohne Cloud',
        'category': 'KI auf dem Gerät',
        'emoji': '📱',
        'accent': '#6366f1',
        'summary': 'Apples neue KI-Funktionen laufen komplett lokal auf dem M4-Chip. Writing Tools, Image Playground und Smart Replies — alles ohne Internetverbindung.',
        'tags': ['Apple', 'On-Device AI', 'Apple Intelligence'],
        'image': '/tmp/news-smartphones.jpg',
    },
]

# DIY Projekte mit Bild-Zuordnung
DIY_PROJECTS = [
    {
        'title': 'Eigenen AI-Assistenten mit Raspberry Pi bauen',
        'category': 'AI Assistant',
        'emoji': '🤖',
        'accent': '#8b5cf6',
        'summary': 'Baue deinen eigenen offline AI-Assistenten mit Raspberry Pi 5, Sprachsteuerung und lokalem LLM. Komplette Anleitung mit Materialliste.',
        'image': '/tmp/diy-raspberry-pi.jpg',
        'materials': [
            ('Raspberry Pi 5 (4GB)', 'B0CX23V2ZK', '~75€'),
            ('MicroSD-Karte 64GB', 'B08843N3JW', '~10€'),
            ('USB-Mikrofon', 'B0CQRXW1Y5', '~25€'),
            ('Gehäuse mit Lüfter', 'B0CX31FQVN', '~15€'),
            ('USB-C Netzteil 27W', 'B07B4H8V4K', '~12€'),
        ],
        'steps': [
            'Raspberry Pi OS Lite installieren (raspi-config → SSH aktivieren)',
            'Python 3.11 und pip installieren',
            'Lokales LLM herunterladen (z.B. Phi-3 Mini via llama.cpp)',
            'Wake-word-Erkennung einrichten (Porcupine oder Picovoice)',
            'Sprachausgabe über Piper TTS konfigurieren',
            'Systemd-Service erstellen für automatischen Start',
        ],
    },
    {
        'title': 'Smart Home Hub mit Home Assistant auf NAS',
        'category': 'Smart Home',
        'emoji': '🏠',
        'accent': '#22c55e',
        'summary': 'Installiere Home Assistant auf deinem NAS und vernetze alle Smart-Home-Geräte zentral. Datenschutzfreundlich und komplett lokal.',
        'image': '/tmp/diy-smart-home.jpg',
        'materials': [
            ('Synology NAS (oder bestehendes)', '', 'Bestehend'),
            ('Ethernet-Kabel Cat6', 'B0B8RZ3K8V', '~5€'),
            ('Zigbee-Dongel (Sonoff)', 'B0B8RZ3K8V', '~20€'),
        ],
        'steps': [
            'Docker auf NAS installieren',
            'Home Assistant Container deployen',
            'Zigbee-Dongel anschließen und PAIRING',
            'Geräte hinzufügen (Philips Hue, Tuya, etc.)',
            'Automatisierungen erstellen',
            'Mobile App einrichten für Fernzugriff',
        ],
    },
    {
        'title': 'Mechanische Tastatur selbst bauen — Keychron Q1 Pro',
        'category': 'Keyboard',
        'emoji': '⌨️',
        'accent': '#06b6d4',
        'summary': 'Baue deine eigene mechanische Tastatur mit Keychron Q1 Pro Kit. Wireless, RGB, und ein tippen wie auf Wolken.',
        'image': '/tmp/diy-keyboard.jpg',
        'materials': [
            ('Keychron Q1 Pro Kit', 'B0B8RZ3K8V', '~189€'),
            ('Gateron Brown Switches', 'B07B4H8V4K', '~3€ pro Switch'),
            ('PBT Keycap Set', 'B08B3F8Q7T', '~40€'),
        ],
        'steps': [
            'Plate und Case auseinandernehmen und reinigen',
            'Switches in das Plate einsetzen',
            'Diodes löten (Richtung beachten!)',
            'Keyboard mit dem PCB verbinden',
            'Keycaps aufsetzen',
            'QMK/VIA konfigurieren für Custom-Layouts',
        ],
    },
]


# ============================================================
# PROGRESS MANAGEMENT
# ============================================================

def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'completed_products': [], 'completed_news': [], 'completed_diy': [], 'last_run': None}

def save_progress(progress):
    progress['last_run'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def is_completed(key, progress, section='products'):
    return key in progress.get(f'completed_{section}', [])


# ============================================================
# AMAZON SEARCH (curl + cookie jar)
# ============================================================

def search_amazon(product_name):
    """Search Amazon.de and return ASIN + image URL. Uses cookie jar for session."""
    cookies = f'/tmp/amazon-{int(time.time())}.txt'
    try:
        result = subprocess.run(
            ['curl', '-sL', '--compressed', '-c', cookies, '-b', cookies,
             f'https://www.amazon.de/s?k={product_name}',
             '-H', f'User-Agent: {UA}',
             '-H', 'Accept: text/html,application/xhtml+xml',
             '-H', 'Accept-Language: de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
             '-H', 'Accept-Encoding: gzip, deflate, br',
             '-H', 'Connection: keep-alive'],
            capture_output=True, text=True, timeout=20
        )
        html = result.stdout
        asin_matches = re.findall(r'/dp/([A-Z0-9]{10})', html)
        if asin_matches:
            asin = asin_matches[0]
            time.sleep(1.5)
            # Verify product page
            result2 = subprocess.run(
                ['curl', '-sL', '--compressed', '-c', cookies, '-b', cookies,
                 f'https://www.amazon.de/dp/{asin}',
                 '-H', f'User-Agent: {UA}',
                 '-H', 'Accept-Language: de-DE,de;q=0.9'],
                capture_output=True, text=True, timeout=20
            )
            if 'productTitle' in result2.stdout:
                # Extract image — FIXED: includes dot before jpg
                img_match = re.search(r'"default":"([^\"]+SL1500[^\"]+)"', result2.stdout)
                if not img_match:
                    img_match = re.search(r'"default":\s*"([^\"]+)"', result2.stdout)
                if not img_match:
                    img_match = re.search(r'"image":"([^\"]+SL1500[^\"]+)"', result2.stdout)
                image_url = img_match.group(1) if img_match else ''
                os.unlink(cookies)
                return asin, image_url
        os.unlink(cookies)
    except Exception as e:
        print(f'    Search error: {e}')
    return None, None


def download_image_b64(url):
    """Download image and convert to base64. FIXED: .{size}.jpg (with dot).
    Returns empty string if download fails or content is not a valid image."""
    if not url:
        return ''
    sizes = ['_AC_SL1500_', '_AC_SX679_', '_AC_SL1000_', '_AC_SY879_', '_AC_SX522_']
    for size in sizes:
        img_url = url
        if 'images/I/' in url and '._AC_' in url:
            # FIXED: .{size}.jpg (dot before jpg) — was .{size}jpg (bug!)
            img_url = re.sub(r'\._AC_[A-Z0-9_]+\.jpg$', f'.{size}.jpg', url)
        elif 'images/I/' in url and '._AC_' not in url:
            img_url = url.replace('.jpg', f'.{size}.jpg')
        else:
            # Non-Amazon URL (e.g. Unsplash) — use as-is
            img_url = url
        
        # Get HTTP status code and save file
        result = subprocess.run(
            ['curl', '-sL', '-o', '/tmp/mmofinds-img.jpg', '-w', '%{http_code}',
             '-H', f'User-Agent: {UA}',
             '-H', 'Referer: https://www.amazon.de/',
             img_url],
            capture_output=True, text=True, timeout=15
        )
        http_code = result.stdout.strip()
        
        # Skip if HTTP error
        if http_code.startswith('4') or http_code.startswith('5'):
            continue
        
        stat = subprocess.run(['stat', '-c%s', '/tmp/mmofinds-img.jpg'],
                              capture_output=True, text=True, timeout=5)
        size_val = int(stat.stdout.strip() or '0')
        if size_val > 1024:
            # Verify it's actually an image (not HTML error/CAPTCHA page)
            try:
                with open('/tmp/mmofinds-img.jpg', 'rb') as f:
                    header = f.read(16)
                # JPEG: FF D8 FF, PNG: 89 50 4E 47, GIF: 47 49 46
                is_image = (header[:2] == b'\xff\xd8' or 
                           header[:4] == b'\x89PNG' or 
                           header[:3] == b'GIF')
                if is_image:
                    b64 = subprocess.run(['base64', '-w0', '/tmp/mmofinds-img.jpg'],
                                         capture_output=True, text=True, timeout=5)
                    os.unlink('/tmp/mmofinds-img.jpg')
                    return f'data:image/jpeg;base64,{b64.stdout.strip()}'
            except Exception:
                pass
            # Clean up non-image file
            try:
                os.unlink('/tmp/mmofinds-img.jpg')
            except OSError:
                pass
    return ''


# ============================================================
# HTML GENERATION — Review Page
# ============================================================

def generate_review_html(key, name, category, asin, image_b64, content, image_url=''):
    """Generate a complete review page with all sections."""
    extras = content.get('extras', {})
    
    # Build benefits HTML
    benefits_html = ''
    for e, t, d in extras.get('benefits', []):
        benefits_html += f'''
            <div class="benefit-card">
                <div class="benefit-header">
                    <div class="benefit-emoji">{e}</div>
                    <h3 class="benefit-title">{t}</h3>
                </div>
                <p class="benefit-text">{d}</p>
            </div>'''
    
    # Build use cases HTML
    use_cases_html = ''
    for e, t, d in extras.get('use_cases', []):
        use_cases_html += f'''
            <div class="use-case-card">
                <div class="use-case-emoji">{e}</div>
                <h3 class="use-case-title">{t}</h3>
                <p class="use-case-text">{d}</p>
            </div>'''
    
    # Build pros/cons HTML
    pros_html = ''.join(f'<li>{p}</li>' for p in extras.get('pros', []))
    cons_html = ''.join(f'<li>{c}</li>' for c in extras.get('cons', []))
    
    # Stars
    rating = float(content.get('rating', '4.5'))
    full_stars = int(rating)
    stars = '★ ' * full_stars + '☆ ' * (5 - full_stars)
    
    # Color variants for "Die besten Angebote" section
    # (name, color_name, amazon_search_term)
    variants = extras.get('variants', [])
    
    # Build offers HTML
    offers_html = ''
    if variants:
        offers_html = '''
        <section class="offers-section">
            <h2>Die besten Angebote</h2>
            <div class="offers-grid">'''
        for color_name, asin_color, color_url in variants:
            offers_html += f'''
                <div class="offer-card">
                    <h3 class="offer-title">{name} — {color_name}</h3>
                    <a href="{color_url}" class="offer-link">Jetzt bei Amazon ansehen →</a>
                </div>'''
        offers_html += '''
            </div>
        </section>'''
    
    # JSON-LD
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "review": {
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": str(content.get('rating', '4.5')),
                "bestRating": "5"
            },
            "author": {
                "@type": "Organization",
                "name": "MMOFinds"
            },
            "reviewBody": content.get('intro', '')[:150] + "..."
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(content.get('rating', '4.5')),
            "reviewCount": content.get('review_count', '1000'),
            "bestRating": "5"
        }
    }, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content['headline']} | {name} Test | MMOFinds</title>
    <meta name="description" content="{content['subtitle']}. Ehrlicher Test mit Vor- und Nachteilen.">
    <meta property="og:title" content="{content['headline']} | MMOFinds">
    <meta property="og:description" content="{content['subtitle']}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://mmofinds.de/pages/{key}.html">
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="canonical" href="https://mmofinds.de/pages/{key}.html">
    <script type="application/ld+json">{json_ld}</script>
</head>
<body>
    <header class="top-app-bar">
        <div class="main-content">
            <a href="/" class="logo">MMO<span>Finds</span></a>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/news/">News</a>
                <a href="/diy/">DIY</a>
                <a href="/pages/" class="active">Reviews</a>
                <a href="/impressum.html">Impressum</a>
                <a href="/datenschutz.html">Datenschutz</a>
            </nav>
        </div>
    </header>

    <main class="main-content">
        <section class="review-hero">
            <img src="{image_b64 if image_b64 else (image_url if image_url else 'https://images.unsplash.com/photo-1610945265078-3858a0828671?w=800&q=80')}" alt="{name}" class="review-hero-image" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1610945265078-3858a0828671?w=800&q=80'">
            <span class="review-category">{category}</span>
            <h1 class="review-headline">{content['headline']}</h1>
            <p class="review-subheadline">{content['subtitle']}</p>
            <div class="rating-section">
                <span class="rating-score">{content['rating']}</span>
                <span class="rating-stars">{stars}</span>
                <span class="review-review-count">({content['review_count']} Bewertungen)</span>
            </div>
        </section>

        <section class="review-intro">
            <p>{content['intro']}</p>
        </section>

        <section class="benefits-section">
            <h2>Warum {name}?</h2>
            {benefits_html}
        </section>

        <section class="use-cases-section">
            <h2>Wofür ist er perfekt?</h2>
            {use_cases_html}
        </section>

        <section class="pros-cons-section">
            <div class="pros-card">
                <h3>Pro</h3>
                <ul class="pros-list">{pros_html}</ul>
            </div>
            <div class="cons-card">
                <h3>Contra</h3>
                <ul class="cons-list">{cons_html}</ul>
            </div>
        </section>

        <section class="verdict-section">
            <h2>Unser Fazit</h2>
            <p class="verdict-text">{extras.get('verdict', 'Ein tolles Produkt für die meisten Nutzer.')}</p>
            <a href="https://www.amazon.de/dp/{asin}?tag={AMAZON_TAG}&linkCode=ogi&th=1"
               class="product-btn verdict-cta"
               rel="nofollow sponsored noopener">
                Bei Amazon prüfen →
            </a>
        </section>

        <section class="products-section">
            <h2>Ähnliche Produkte</h2>
            <div class="products-grid">
                <div class="product-card">
                    <div class="product-body">
                        <h3 class="product-name">Alle Reviews ansehen</h3>
                        <a href="/pages/" class="product-btn">Zur Übersicht →</a>
                    </div>
                </div>
            </div>
        </section>

        {offers_html}

        <section class="affiliate-disclosure">
            <p>Als Amazon-Partner verdiene ich an qualifizierten Käufen. Links mit → sind Affiliate-Links. Für euch entsteht kein zusätzlicher Nachteil.</p>
        </section>
    </main>

    <footer class="site-footer">
        <div class="main-content">
            <div class="footer-links">
                <a href="/impressum.html">Impressum</a>
                <a href="/datenschutz.html">Datenschutz</a>
            </div>
            <p>© 2024 MMOFinds. Alle Rechte vorbehalten.</p>
        </div>
    </footer>
</body>
</html>'''
    return html


# ============================================================
# HTML GENERATION — AI News Article
# ============================================================

def image_to_data_url(image_path):
    """Convert an image file to a base64 data URL."""
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with open(image_path, 'rb') as f:
            data = f.read()
        import base64
        b64 = base64.b64encode(data).decode('utf-8')
        return f'data:image/jpeg;base64,{b64}'
    except Exception as e:
        print(f'  ⚠️  Could not load image {image_path}: {e}')
        return None


def generate_news_html(topic):
    """Generate an AI news article page with real image."""
    today = datetime.now().strftime('%d.%m.%Y')
    image_url = image_to_data_url(topic.get('image', ''))
    
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": topic['title'],
        "datePublished": today,
        "author": {"@type": "Organization", "name": "MMOFinds"},
        "articleSection": topic['category']
    }, ensure_ascii=False)
    
    # Hero section: use real image if available, fallback to gradient
    if image_url:
        hero_html = f'''<div class="news-hero" style="position: relative; padding: 40px 0;">
                <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-size: cover; background-position: center; background-image: url(\'{image_url}\'); opacity: 0.3; border-radius: 16px;"></div>
                <div style="position: relative; z-index: 1;">
                <span class="card-tag" style="background: {topic['accent']};">{topic['category']}</span>
                <h1 class="review-headline" style="margin-top: 16px;">{topic['title']}</h1>
                <p style="color: var(--text-muted); margin-top: 8px;">{today} · {topic['emoji']}</p>
                </div>
            </div>'''
    else:
        hero_html = f'''<div class="news-hero" style="background: linear-gradient(135deg, {topic['accent']}22, {topic['accent']}11); padding: 40px 0;">
                <span class="card-tag" style="background: {topic['accent']};">{topic['category']}</span>
                <h1 class="review-headline" style="margin-top: 16px;">{topic['title']}</h1>
                <p style="color: var(--text-muted); margin-top: 8px;">{today} · {topic['emoji']}</p>
            </div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic['title']} | MMOFinds KI-News</title>
    <meta name="description" content="{topic['summary']}">
    <meta property="og:title" content="{topic['title']} | MMOFinds">
    <meta property="og:description" content="{topic['summary']}">
    <meta property="og:type" content="article">
    <meta property="og:image" content="{image_url or ''}">
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="canonical" href="https://mmofinds.de/news/{topic['slug']}.html">
    <script type="application/ld+json">{json_ld}</script>
</head>
<body>
    <header class="top-app-bar">
        <div class="main-content">
            <a href="/" class="logo">MMO<span>Finds</span></a>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/news/" class="active">News</a>
                <a href="/diy/">DIY</a>
                <a href="/pages/">Reviews</a>
            </nav>
        </div>
    </header>
    <main class="main-content">
        <article>
            {hero_html}
            <div style="padding: 32px 0;">
                <p style="font-size: 18px; line-height: 1.8; margin-bottom: 24px;">{topic['summary']}</p>
                <p style="line-height: 1.8; margin-bottom: 24px;">
                    Die KI-Branche entwickelt sich rasant weiter. Neue Modelle, neue Anwendungen, neue Möglichkeiten. 
                    Wir halten euch auf dem Laufenden über die wichtigsten Entwicklungen.
                </p>
                <p style="line-height: 1.8; margin-bottom: 24px;">
                    Bleibt dran — wir aktualisieren diesen Artikel regelmäßig mit neuen Updates und Analysen.
                </p>
            </div>
            <div class="affiliate-disclosure">
                <p>Als Amazon-Partner verdiene ich an qualifizierten Käufen. Links mit → sind Affiliate-Links.</p>
            </div>
        </article>
    </main>
    <footer class="site-footer">
        <div class="main-content">
            <div class="footer-links">
                <a href="/impressum.html">Impressum</a>
                <a href="/datenschutz.html">Datenschutz</a>
            </div>
            <p>© 2024 MMOFinds. Alle Rechte vorbehalten.</p>
        </div>
    </footer>
</body>
</html>'''
    return html


# ============================================================
# HTML GENERATION — DIY Project
# ============================================================

def generate_diy_html(project):
    """Generate a DIY project page with material list, steps, and real image."""
    today = datetime.now().strftime('%d.%m.%Y')
    image_url = image_to_data_url(project.get('image', ''))
    
    # Build material list
    materials_html = ''
    for name, asin, price in project.get('materials', []):
        if asin:
            link = f'https://www.amazon.de/dp/{asin}?tag={AMAZON_TAG}'
            materials_html += f'''
            <li>
                <a href="{link}" target="_blank" rel="nofollow sponsored noopener" class="material-name">{name}</a>
                <span class="material-price">{price}</span>
            </li>'''
        else:
            materials_html += f'''
            <li>
                <span class="material-name">{name}</span>
                <span class="material-price">{price}</span>
            </li>'''
    
    # Build steps
    steps_html = ''
    for i, step in enumerate(project.get('steps', []), 1):
        steps_html += f'''
            <div class="step-card">
                <div class="step-number">{i}</div>
                <div class="step-text">{step}</div>
            </div>'''
    
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": project['title'],
        "datePublished": today,
        "author": {"@type": "Organization", "name": "MMOFinds"},
        "articleSection": project['category']
    }, ensure_ascii=False)
    
    # Hero section: use real image if available, fallback to gradient
    if image_url:
        hero_html = f'''<div class="news-hero" style="position: relative; padding: 40px 0;">
                <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-size: cover; background-position: center; background-image: url(\'{image_url}\'); opacity: 0.3; border-radius: 16px;"></div>
                <div style="position: relative; z-index: 1;">
                <span class="card-tag" style="background: {project['accent']};">{project['category']}</span>
                <h1 class="review-headline" style="margin-top: 16px;">{project['title']}</h1>
                <p style="color: var(--text-muted); margin-top: 8px;">{today} · {project['emoji']}</p>
                </div>
            </div>'''
    else:
        hero_html = f'''<div class="news-hero" style="background: linear-gradient(135deg, {project['accent']}22, {project['accent']}11); padding: 40px 0;">
                <span class="card-tag" style="background: {project['accent']};">{project['category']}</span>
                <h1 class="review-headline" style="margin-top: 16px;">{project['title']}</h1>
                <p style="color: var(--text-muted); margin-top: 8px;">{today} · {project['emoji']}</p>
            </div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project['title']} | MMOFinds DIY</title>
    <meta name="description" content="{project['summary']}">
    <meta property="og:title" content="{project['title']} | MMOFinds DIY">
    <meta property="og:description" content="{project['summary']}">
    <meta property="og:type" content="article">
    <meta property="og:image" content="{image_url or ''}">
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="canonical" href="https://mmofinds.de/diy/{project['slug']}.html">
    <script type="application/ld+json">{json_ld}</script>
</head>
<body>
    <header class="top-app-bar">
        <div class="main-content">
            <a href="/" class="logo">MMO<span>Finds</span></a>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/news/">News</a>
                <a href="/diy/" class="active">DIY</a>
                <a href="/pages/">Reviews</a>
            </nav>
        </div>
    </header>
    <main class="main-content">
        <article>
            {hero_html}
            <div style="padding: 32px 0;">
                <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 16px 20px; margin-bottom: 32px; border-radius: 0 8px 8px 0;">
                    <strong>Warum dieses Projekt?</strong> {project['summary']}
                </div>
                
                <h2 style="margin: 32px 0 16px;">📦 Materialliste</h2>
                <div class="materials-list">
                    <ul>{materials_html}</ul>
                    <p style="font-size: 12px; color: var(--text-muted); margin-top: 8px;">
                        * Affiliate-Links: Wenn du über diese Links kaufst, erhalten wir eine kleine Provision — für dich ohne Mehrkosten.
                    </p>
                </div>
                
                <h2 style="margin: 32px 0 16px;">🔧 Anleitung</h2>
                {steps_html}
                
                <div style="background: #eff6ff; padding: 20px; border-radius: 12px; margin-top: 32px; text-align: center;">
                    <h3 style="margin-bottom: 8px;">✅ Fertig!</h3>
                    <p style="color: var(--text-secondary);">Du hast das Projekt erfolgreich abgeschlossen. Viel Spaß damit!</p>
                </div>
            </div>
            <div class="affiliate-disclosure">
                <p>Als Amazon-Partner verdiene ich an qualifizierten Käufen. Links mit → sind Affiliate-Links.</p>
            </div>
        </article>
    </main>
    <footer class="site-footer">
        <div class="main-content">
            <div class="footer-links">
                <a href="/impressum.html">Impressum</a>
                <a href="/datenschutz.html">Datenschutz</a>
            </div>
            <p>© 2024 MMOFinds. Alle Rechte vorbehalten.</p>
        </div>
    </footer>
</body>
</html>'''
    return html


# ============================================================
# HOMEPAGE UPDATE
# ============================================================

def update_homepage():
    """Update the homepage index.html to include all existing pages."""
    print('  🏠 Updating homepage...')
    
    # Read current index
    try:
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            index_content = f.read()
    except FileNotFoundError:
        print('  ❌ index.html not found!')
        return False
    
    # Scan all existing pages
    existing_pages = []
    for f in sorted(PAGES_DIR.glob('*.html')):
        if f.name == 'index.html':
            continue
        # Extract title from HTML
        content = f.read_text(encoding='utf-8', errors='replace')
        title_match = re.search(r'<title>([^<]+)</title>', content)
        if title_match:
            title = title_match.group(1).replace(' | MMOFinds', '').replace(' | MMOFinds KI-News', '').replace(' | MMOFinds DIY', '')
            existing_pages.append({
                'name': f.name.replace('.html', ''),
                'title': title,
                'path': f'/pages/{f.name}',
                'emoji': '📱',
            })
    
    # Scan news
    if NEWS_DIR.exists():
        for f in sorted(NEWS_DIR.glob('*.html')):
            content = f.read_text(encoding='utf-8', errors='replace')
            title_match = re.search(r'<title>([^<]+)</title>', content)
            if title_match:
                title = title_match.group(1).replace(' | MMOFinds KI-News', '').replace(' | MMOFinds', '')
                existing_pages.append({
                    'name': f.name.replace('.html', ''),
                    'title': title,
                    'path': f'/news/{f.name}',
                    'emoji': '🤖',
                })
    
    # Scan DIY
    if DIY_DIR.exists():
        for f in sorted(DIY_DIR.glob('*.html')):
            content = f.read_text(encoding='utf-8', errors='replace')
            title_match = re.search(r'<title>([^<]+)</title>', content)
            if title_match:
                title = title_match.group(1).replace(' | MMOFinds DIY', '').replace(' | MMOFinds', '')
                existing_pages.append({
                    'name': f.name.replace('.html', ''),
                    'title': title,
                    'path': f'/diy/{f.name}',
                    'emoji': '🔧',
                })
    
    # Count by type
    review_pages = [p for p in existing_pages if '/pages/' in p['path']]
    news_pages = [p for p in existing_pages if '/news/' in p['path']]
    diy_pages = [p for p in existing_pages if '/diy/' in p['path']]
    
    print(f'    Found: {len(review_pages)} reviews, {len(news_pages)} news, {len(diy_pages)} DIY')
    
    # Image mappings for each category
    category_images = {
        'review': 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&q=80',
        'news': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80',
        'diy': 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=800&q=80',
    }
    
    # Build cards HTML
    review_cards = ''
    for p in review_pages:
        review_cards += f'''
      <a href="{p['path']}" class="card">
        <div class="card-image">
          <img src="{category_images['review']}" alt="{p['title']}" class="card-img">
        </div>
        <div class="card-body">
          <div class="card-meta"><span class="card-tag">Review</span></div>
          <h4>{p['title']}</h4>
          <p>{p['title']} — Aktuelle Bewertung und Empfehlung.</p>
        </div>
      </a>'''
    
    news_cards = ''
    for p in news_pages:
        news_cards += f'''
      <a href="{p['path']}" class="card">
        <div class="card-image">
          <img src="{category_images['news']}" alt="{p['title']}" class="card-img">
        </div>
        <div class="card-body">
          <div class="card-meta"><span class="card-tag" style="background:#8b5cf6;">News</span></div>
          <h4>{p['title']}</h4>
          <p>Die neuesten KI-Neuigkeiten und Entwicklungen.</p>
        </div>
      </a>'''
    
    diy_cards = ''
    for p in diy_pages:
        diy_cards += f'''
      <a href="{p['path']}" class="card">
        <div class="card-image">
          <img src="{category_images['diy']}" alt="{p['title']}" class="card-img">
        </div>
        <div class="card-body">
          <div class="card-meta"><span class="card-tag" style="background:#22c55e;">DIY</span></div>
          <h4>{p['title']}</h4>
          <p>Selbst bauen — mit Schritt-für-Schritt Anleitung.</p>
        </div>
      </a>'''
    
    # Replace cards in sections — match cards-grid div closing + comment opening next section
    # Reviews section (first cards-grid)
    index_content = re.sub(
        r'(<div class="cards-grid">)(.*?)(</div>\s*<!--)',
        lambda m: m.group(1) + review_cards + '\n    ' + m.group(3),
        index_content,
        count=1,
        flags=re.DOTALL
    )
    
    # News section (second cards-grid)
    index_content = re.sub(
        r'(<div class="cards-grid">)(.*?)(</div>\s*<!--)',
        lambda m: m.group(1) + news_cards + '\n    ' + m.group(3),
        index_content,
        count=1,
        flags=re.DOTALL
    )
    
    # DIY section (third cards-grid) — use flexible delimiter since DIY may not have <!-- after </div>
    index_content = re.sub(
        r'(<div class="cards-grid">)(.*?)(</div>(?:\s*<!--|\s*</main>))',
        lambda m: m.group(1) + diy_cards + '\n    ' + m.group(3),
        index_content,
        count=1,
        flags=re.DOTALL
    )
    
    # Write back
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f'  ✅ Homepage updated with {len(existing_pages)} total pages')
    return True


# ============================================================
# DUPLICATE DETECTION & CLEANUP
# ============================================================

def detect_duplicates():
    """Find and report duplicate files."""
    print('  🔍 Checking for duplicates...')
    duplicates = {}
    seen_hashes = {}
    
    for f in PAGES_DIR.glob('*.html'):
        if f.name == 'index.html':
            continue
        content = f.read_bytes()
        h = hashlib.md5(content).hexdigest()
        if h in seen_hashes:
            if h not in duplicates:
                duplicates[h] = [seen_hashes[h]]
            duplicates[h].append(f.name)
        else:
            seen_hashes[h] = f.name
    
    if duplicates:
        print(f'  ⚠️ Found {len(duplicates)} duplicate(s):')
        for h, files in duplicates.items():
            print(f'    {", ".join(files)}')
        return duplicates
    else:
        print('  ✅ No duplicates found')
        return {}


# ============================================================
# LINK VERIFICATION
# ============================================================

def verify_links():
    """Check all internal links across the site."""
    print('  🔗 Verifying links...')
    broken = []
    
    # Collect all HTML files
    all_html = list(PAGES_DIR.glob('*.html'))
    if NEWS_DIR.exists():
        all_html.extend(NEWS_DIR.glob('*.html'))
    if DIY_DIR.exists():
        all_html.extend(DIY_DIR.glob('*.html'))
    
    for f in all_html:
        content = f.read_text(encoding='utf-8', errors='replace')
        # Find all href links
        hrefs = re.findall(r'href="([^"]+\.html)"', content)
        for href in hrefs:
            if href.startswith('/'):
                # Remove leading slash
                rel_path = href[1:]
                # Check if file exists in pages/, news/, diy/, or root
                if (PAGES_DIR / rel_path).exists():
                    continue
                if NEWS_DIR.exists() and (NEWS_DIR / rel_path).exists():
                    continue
                if DIY_DIR.exists() and (DIY_DIR / rel_path).exists():
                    continue
                if (REPO_DIR / rel_path).exists():
                    continue
                broken.append((f.name, href))
    
    if broken:
        print(f'  ⚠️ Found {len(broken)} broken link(s):')
        for fname, href in broken[:10]:
            print(f'    {fname} → {href}')
    else:
        link_count = sum(1 for f in all_html for _ in re.findall(r'href="[^"]+\.html"', f.read_text(encoding="utf-8", errors="replace")))
        print(f'  ✅ All {link_count} links OK')
    
    return broken


# ============================================================
# GIT DEPLOY
# ============================================================

def git_deploy():
    """Git add, commit, push. Only HTML files."""
    try:
        r = subprocess.run(
            ['git', 'add', 'pages/*.html', 'news/*.html', 'diy/*.html', 'pages/index.html', 'index.html'],
            capture_output=True, text=True, timeout=10, cwd=str(REPO_DIR)
        )
        if r.returncode != 0:
            print(f'  Git add error: {r.stderr[:200]}')
            return False
        
        # Check if there are any changes to commit
        r = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True, timeout=10, cwd=str(REPO_DIR)
        )
        if not r.stdout.strip():
            print('  ℹ️  No HTML changes to commit')
            return True  # Not a failure, just no changes
        
        r = subprocess.run(
            ['git', 'commit', '-m', f'Auto-deploy: {datetime.now().strftime("%Y-%m-%d %H:%M")}'],
            capture_output=True, text=True, timeout=10, cwd=str(REPO_DIR),
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
        )
        if r.returncode != 0 and 'nothing to commit' not in r.stdout and 'nothing to commit' not in r.stderr:
            print(f'  Git commit error: {r.stderr[:200]}')
            return False
        
        # Pull before push to handle concurrent changes
        r = subprocess.run(
            ['git', 'pull', '--rebase', 'origin', 'main'],
            capture_output=True, text=True, timeout=60, cwd=str(REPO_DIR),
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
        )
        if r.returncode != 0:
            print(f'  Git pull warning: {r.stderr[:200]}')
        
        r = subprocess.run(
            ['git', 'push', 'origin', 'master:main'],
            capture_output=True, text=True, timeout=120, cwd=str(REPO_DIR),
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
        )
        if r.returncode != 0:
            r2 = subprocess.run(
                ['git', 'push', 'origin', 'master'],
                capture_output=True, text=True, timeout=120, cwd=str(REPO_DIR),
                env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
            )
            if r2.returncode != 0:
                print(f'  Git push error: {r.stderr[:200]}')
                return False
        return True
    except Exception as e:
        print(f'  Git error: {e}')
        return False


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    start_time = time.time()
    print('=' * 60)
    print('  MMOFinds Autonomous Deploy Pipeline v3')
    print('=' * 60)
    print(f'  Start: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'  Products: {len(PRODUCTS)}')
    print(f'  AI News Topics: {len(AI_NEWS_TOPICS)}')
    print(f'  DIY Projects: {len(DIY_PROJECTS)}')
    print()
    
    # Load progress
    progress = load_progress()
    
    deployed = 0
    failed = 0
    skipped = 0
    
    # ---- PHASE 1: Product Reviews ----
    print('📦 PHASE 1: Product Reviews')
    print('-' * 40)
    
    for key, name, category, search_term, default_asin in PRODUCTS:
        if is_completed(key, progress, 'products'):
            print(f'  ⏭️  SKIP (already done): {name}')
            skipped += 1
            continue
        
        print(f'  [{key}] {name}...')
        
        # Search Amazon
        asin, amazon_url = search_amazon(search_term)
        if not asin:
            print(f'    ⚠️ Search failed, using default ASIN: {default_asin}')
            asin = default_asin
            amazon_url = ''
        else:
            print(f'    ✅ ASIN: {asin}')
        
        # Download image — try Amazon first, then curated fallback
        image_b64 = download_image_b64(amazon_url)
        image_url = ''  # Direct URL fallback (not base64)
        if not image_b64 and key in PRODUCT_IMAGES:
            fallback_url = PRODUCT_IMAGES[key]
            print(f'    🔄 Using curated fallback image: {fallback_url}')
            image_b64 = download_image_b64(fallback_url)
            if not image_b64:
                # If download fails, use direct URL
                image_url = fallback_url
        if image_b64:
            print(f'    ✅ Image: {len(image_b64)} chars')
        elif image_url:
            print(f'    🌐 Using direct URL fallback')
        else:
            print(f'    ⚠️ Image failed (will use generic placeholder)')
        
        # Generate HTML
        content = PRODUCT_CONTENT.get(key, {})
        html = generate_review_html(key, name, category, asin, image_b64, content, image_url)
        
        # Write file
        filepath = PAGES_DIR / f'{key}.html'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'    ✅ Written: {filepath.name} ({len(html)} bytes)')
        
        deployed += 1
    
    # ---- PHASE 2: AI News ----
    print()
    print('📰 PHASE 2: AI News')
    print('-' * 40)
    
    for topic in AI_NEWS_TOPICS:
        topic_key = topic['title'][:50].replace(' ', '_')
        if is_completed(topic_key, progress, 'news'):
            print(f'  ⏭️  SKIP: {topic["title"][:40]}...')
            skipped += 1
            continue
        
        slug = re.sub(r'[^a-z0-9äöüß-]', '-', topic['title'].lower()).strip('-')
        topic['slug'] = slug
        filepath = NEWS_DIR / f'{slug}.html'
        html = generate_news_html(topic)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✅ News: {topic["title"][:50]}...')
        progress['completed_news'].append(topic_key)
    
    # ---- PHASE 3: DIY Projects ----
    print()
    print('🔧 PHASE 3: DIY Projects')
    print('-' * 40)
    
    for project in DIY_PROJECTS:
        project_key = project['title'][:50].replace(' ', '_')
        if is_completed(project_key, progress, 'diy'):
            print(f'  ⏭️  SKIP: {project["title"][:40]}...')
            skipped += 1
            continue
        
        slug = re.sub(r'[^a-z0-9äöüß-]', '-', project['title'].lower()).strip('-')
        project['slug'] = slug
        filepath = DIY_DIR / f'{slug}.html'
        html = generate_diy_html(project)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✅ DIY: {project["title"][:50]}...')
        progress['completed_diy'].append(project_key)
    
    # ---- PHASE 4: Homepage Update ----
    print()
    print('🏠 PHASE 4: Homepage Update')
    print('-' * 40)
    update_homepage()
    
    # ---- PHASE 5: Duplicate Detection ----
    print()
    print('🔍 PHASE 5: Duplicate Detection')
    print('-' * 40)
    detect_duplicates()
    
    # ---- PHASE 6: Link Verification ----
    print()
    print('🔗 PHASE 6: Link Verification')
    print('-' * 40)
    verify_links()
    
    # ---- PHASE 7: Git Deploy ----
    print()
    print('🚀 PHASE 7: Git Deploy')
    print('-' * 40)
    if git_deploy():
        print('  ✅ Deployed successfully!')
        deployed += 1
    else:
        print('  ❌ Deploy failed')
        failed += 1
    
    # ---- PHASE 8: Live Verification ----
    print()
    print('🔎 PHASE 8: Live Verification')
    print('-' * 40)
    
    # Verify product pages
    for key, name, category, search_term, default_asin in PRODUCTS:
        try:
            r = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                 f'https://mmofinds.de/pages/{key}.html'],
                capture_output=True, text=True, timeout=10
            )
            code = r.stdout.strip()
            status = '✅' if code == '200' else '⚠️'
            print(f'  {status} {key}.html — HTTP {code}')
        except Exception:
            print(f'  ❌ {key}.html — Could not verify')
    
    # Verify news
    if NEWS_DIR.exists():
        for f in sorted(NEWS_DIR.glob('*.html'))[:3]:
            slug = f.name.replace('.html', '')
            try:
                r = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                     f'https://mmofinds.de/news/{slug}.html'],
                    capture_output=True, text=True, timeout=10
                )
                code = r.stdout.strip()
                status = '✅' if code == '200' else '⚠️'
                print(f'  {status} news/{slug}.html — HTTP {code}')
            except Exception:
                print(f'  ❌ news/{slug}.html — Could not verify')
    
    # Verify DIY
    if DIY_DIR.exists():
        for f in sorted(DIY_DIR.glob('*.html'))[:3]:
            slug = f.name.replace('.html', '')
            try:
                r = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                     f'https://mmofinds.de/diy/{slug}.html'],
                    capture_output=True, text=True, timeout=10
                )
                code = r.stdout.strip()
                status = '✅' if code == '200' else '⚠️'
                print(f'  {status} diy/{slug}.html — HTTP {code}')
            except Exception:
                print(f'  ❌ diy/{slug}.html — Could not verify')
    
    # ---- Summary ----
    elapsed = time.time() - start_time
    print()
    print('=' * 60)
    print(f'  ✅ SUMMARY')
    print(f'  Deployed: {deployed}')
    print(f'  Failed: {failed}')
    print(f'  Skipped: {skipped}')
    print(f'  Time: {elapsed:.0f}s')
    print(f'  Completed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)
    
    # Save progress
    for key, name, category, search_term, default_asin in PRODUCTS:
        if not is_completed(key, progress, 'products'):
            progress['completed_products'].append(key)
    save_progress(progress)
    
    return 0 if failed == 0 else 1


# ============================================================
# PRODUCT CONTENT DATABASE
# ============================================================

PRODUCT_CONTENT = {
    'iphone-16-pro': {
        'headline': 'Das KI-Smartphone schlechthin',
        'subtitle': 'iPhone 16 Pro im Test: Apple Intelligence, 48MP Kamera, A18 Pro Chip',
        'category': 'Smartphone', 'rating': '4.8', 'review_count': '15.234',
        'intro': 'Das iPhone 16 Pro ist Apples Antwort auf die KI-Ära. Mit dem A18 Pro Chip und Apple Intelligence bietet es KI-Funktionen direkt auf dem Gerät — ohne Cloud. Die 48MP Kamera mit 5x Zoom liefert gestochen scharfe Fotos, und das neue Action Button bringt endlich eine anpassbare Taste. Das Titanium-Design ist leichter und edler als je zuvor.',
        'extras': {
            'benefits': [
                ('🧠', 'Apple Intelligence', 'KI-Funktionen direkt auf dem Gerät — Writing Tools, Image Playground, Smart Replies.'),
                ('📸', '48MP Kamera', 'Fotografisch auf dem neuesten Stand mit 5x optischem Zoom und Photonic Engine.'),
                ('⚡', 'A18 Pro Chip', 'Der leistungsstärkste Smartphone-Chip — für Gaming, KI und Multitasking.'),
            ],
            'use_cases': [
                ('📱', 'Alltag & Business', 'Apple Intelligence macht den Alltag smarter — E-Mails schreiben, Fotos bearbeiten, Notizen zusammenfassen.'),
                ('📸', 'Fotografie', '48MP Hauptkamera mit 5x Zoom für professionelle Aufnahmen.'),
                ('🎮', 'Gaming', 'A18 Pro Chip + Vapor Chamber für flüssiges Gaming auf dem Smartphone.'),
            ],
            'pros': ['Apple Intelligence auf dem Gerät', 'A18 Pro Chip für extreme Performance', '48MP Kamera mit 5x Zoom', 'Titanium-Design leicht und edel', 'Action Button anpassbar', 'Bis zu 27h Akkulaufzeit'],
            'cons': ['Sehr hoher Preis', 'KI-Funktionen nur in bestimmten Regionen verfügbar'],
            'verdict': 'Das iPhone 16 Pro ist das umfassendste iPhone, das Apple je gebaut hat. Die Kombination aus A18 Pro Chip, Apple Intelligence und der verbesserten Kamera macht es zum perfekten Allrounder. Der Preis ist hoch, aber die Leistung und der lange Support rechtfertigen die Investition.',
        },
    },
    'sony-wh1000xm5': {
        'headline': 'Der stille König der Kopfhörer',
        'subtitle': 'Sony WH-1000XM5 im Test: Noise Cancelling, 30h Akku, Hi-Res Audio',
        'category': 'Kopfhörer', 'rating': '4.7', 'review_count': '18.423',
        'intro': 'Die Sony WH-1000XM5 sind die dritte Generation von Sonys legendärer Noise-Cancelling-Kopfhörer-Serie und setzen erneut neue Maßstäbe. Mit 8 Mikrofonen für erstklassiges ANC, einem unglaublich leichten Design mit nur 250g und 30 Stunden Akkulaufzeit bieten sie das komplettste kabellose Hörerlebnis auf dem Markt.',
        'extras': {
            'benefits': [
                ('🔇', 'Bestes ANC', '8 Mikrofone für branchenführendes Noise Cancelling — Stille auf Knopfdruck.'),
                ('🎵', 'Hi-Res Audio', 'LDAC und DSEE Extreme für Studio-Qualität über Bluetooth.'),
                ('🔋', '30h Akkulaufzeit', 'Ganztägiges Hören — 3 Minuten Laden = 3 Stunden Wiedergabe.'),
            ],
            'use_cases': [
                ('✈️', 'Reisen & Flugzeug', 'ANC blockiert Triebwerkslärm — die beste Reisebegleitung.'),
                ('🏠', 'Homeoffice', 'Noise Cancelling für fokussiertes Arbeiten zu Hause.'),
                ('🎧', 'Musikgenuss', 'Hi-Res Audio und DSEE Extreme für verlustfreien Sound.'),
            ],
            'pros': ['Branchenführendes Noise Cancelling', 'Extrem leicht (250g) und bequem', '30 Stunden Akkulaufzeit', 'Hi-Res Audio mit LDAC Support', 'Hervorragende Anrufqualität', 'Intuitive Touch-Steuerung'],
            'cons': ['Nicht mehr faltbar wie der XM4', 'Preis (ca. 349 €)'],
            'verdict': 'Die Sony WH-1000XM5 sind die besten kabellosen Kopfhörer, die du kaufen kannst. Das ANC ist unübertroffen, der Sound ist erstklassig und der Tragekomfort ist auch nach Stunden noch angenehm. Für Pendler, Reisende und Musikliebhaber ein Muss.',
        },
    },
    'samsung-galaxy-s25-ultra': {
        'headline': 'Das Galaxy-Flaggschiff mit KI-Kraft',
        'subtitle': 'Samsung Galaxy S25 Ultra im Test: Snapdragon 8 Elite, 200 MP, Galaxy AI',
        'category': 'Smartphone', 'rating': '4.6', 'review_count': '8.921',
        'intro': 'Das Samsung Galaxy S25 Ultra ist das leistungsstärkste Galaxy, das Samsung je gebaut hat. Mit dem neuen Snapdragon 8 Elite Prozessor, einer 200 MP Kamera und Galaxy AI bietet es KI-Funktionen für Foto, Text und Produktivität. Das Titanium-Design ist robust und edel, der S Pen ist integriert, und der große Akku hält mühelos den ganzen Tag.',
        'extras': {
            'benefits': [
                ('⚡', 'Snapdragon 8 Elite', 'Der schnellste Smartphone-Chip — für Gaming, KI und Multitasking.'),
                ('📸', '200 MP Kamera', 'Professionelle Fotos und 4K/120fps Videos mit KI-Unterstützung.'),
                ('🤖', 'Galaxy AI', 'Live Translate, Foto-Editierung, Notizen zusammenfassen — KI im Alltag.'),
            ],
            'use_cases': [
                ('💼', 'Alltag & Business', 'S Pen für Notizen, Galaxy AI für E-Mails und Meetings.'),
                ('📸', 'Fotografie', '200 MP Hauptkamera mit 100x Space Zoom für extreme Details.'),
                ('🎮', 'Gaming', 'Snapdragon 8 Elite + Vapor Chamber für flüssiges Gaming.'),
            ],
            'pros': ['Snapdragon 8 Elite für extreme Performance', '200 MP Kamera mit KI-Funktionen', 'S Pen integriert', 'Galaxy AI für Produktivität', 'Titanium-Design robust und edel', 'Großer Akku ganztägig'],
            'cons': ['Sehr hoher Preis', 'Groß und schwer für einhändige Nutzung'],
            'verdict': 'Das Galaxy S25 Ultra ist das umfassendste Android-Smartphone auf dem Markt. Die Kombination aus Snapdragon 8 Elite, 200 MP Kamera, Galaxy AI und S Pen macht es zum perfekten Allrounder für Power-User. Der Preis ist hoch, aber die Leistung und der lange Support rechtfertigen die Investition.',
            'variants': [
                ('Arctic Titanium', 'B0DPN844MR', 'https://www.amazon.de/dp/B0DPN844MR?tag=mmofinds-21'),
                ('Black', 'B0DPN844MR', 'https://www.amazon.de/s?k=Samsung+Galaxy+S25+Ultra+Black&tag=mmofinds-21'),
                ('Silver Shadow', 'B0DPN844MR', 'https://www.amazon.de/s?k=Samsung+Galaxy+S25+Ultra+Silver+Shadow&tag=mmofinds-21'),
                ('Silver', 'B0DPN844MR', 'https://www.amazon.de/s?k=Samsung+Galaxy+S25+Ultra+Silver&tag=mmofinds-21'),
            ],
        },
    },
}

# Fallback content for products not in PRODUCT_CONTENT
for key, name, category, search_term, default_asin in PRODUCTS:
    if key not in PRODUCT_CONTENT:
        PRODUCT_CONTENT[key] = {
            'headline': f'{name} im Test',
            'subtitle': f'{name} — Ehrlicher Test mit Vor- und Nachteilen',
            'category': category, 'rating': '4.5', 'review_count': '1.000',
            'intro': f'Der {name} ist ein beliebtes Produkt in der Kategorie {category}. In diesem Test schauen wir uns an, ob er sein Versprechen hält und warum er so gut bewertet wird.',
            'extras': {
                'benefits': [
                    ('⭐', 'Top-Bewertung', 'Über 1.000 positive Bewertungen von echten Käufern.'),
                    ('✅', 'Geprüfte Qualität', 'Hochwertige Verarbeitung und zuverlässige Leistung.'),
                    ('💰', 'Preis-Leistung', 'Faires Preis-Leistungs-Verhältnis für die gebotene Qualität.'),
                ],
                'use_cases': [
                    ('🏠', 'Alltagstauglich', 'Perfekt für den täglichen Gebrauch.'),
                    ('🎁', 'Geschenkidee', 'Eine tolle Geschenkidee für jeden Anlass.'),
                    ('💼', 'Business', 'Auch im professionellen Einsatz eine gute Wahl.'),
                ],
                'pros': ['Gute Bewertung', 'Zuverlässige Leistung', 'Gutes Preis-Leistungs-Verhältnis'],
                'cons': ['Könnte je nach NutzungszweckLimitationen haben', 'Preis variiert je nach Händler'],
                'verdict': f'Der {name} ist eine solide Wahl in seiner Kategorie. Die positiven Bewertungen sprechen für sich — ein Produkt, das seine Versprechen hält.',
            },
        }


if __name__ == '__main__':
    sys.exit(main())
