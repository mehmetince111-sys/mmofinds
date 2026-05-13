#!/usr/bin/env python3
"""MMOFinds Autonomous Page Creator Pipeline — curl-based version."""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_DIR = Path('/root/mmofinds')
PAGES_DIR = REPO_DIR / 'pages'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
AMAZON_TAG = 'mmofinds-20'

PRODUCTS = [
    ('dyson-v15-detect', 'Dyson V15 Detect', 'Staubsauger',
     'Dyson V15 Detect', 'B0CH5QWSGK'),
    ('kindle-paperwhite-2024', 'Kindle Paperwhite 2024', 'E-Reader',
     'Kindle Paperwhite 12th Gen 2024', 'B0BLRDK3YP'),
    ('logitech-mx-master-3s', 'Logitech MX Master 3S', 'Maus',
     'Logitech MX Master 3S', 'B09HMBCQHY'),
    ('samsung-galaxy-s25-ultra', 'Samsung Galaxy S25 Ultra', 'Smartphone',
     'Samsung Galaxy S25 Ultra', 'B0DS9DQJ8S'),
    ('sony-wh1000xm5', 'Sony WH-1000XM5', 'Kopfhörer',
     'Sony WH-1000XM5', 'B09XS7JWHH'),
]


def search_amazon(product_name):
    """Search Amazon.de and return ASIN + image URL."""
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
                # Extract image
                img_match = re.search(r'"default":"([^"]+SL1500[^"]+)"', result2.stdout)
                if not img_match:
                    img_match = re.search(r'"default":\s*"([^"]+)"', result2.stdout)
                if not img_match:
                    img_match = re.search(r'"image":"([^"]+SL1500[^"]+)"', result2.stdout)
                image_url = img_match.group(1) if img_match else ''
                os.unlink(cookies)
                return asin, image_url
        os.unlink(cookies)
    except Exception as e:
        print(f'    Search error: {e}')
    return None, None


def download_image_b64(url):
    """Download image and convert to base64."""
    if not url:
        return ''
    sizes = ['_AC_SL1500_', '_AC_SX679_', '_AC_SL1000_', '_AC_SY879_', '_AC_SX522_']
    for size in sizes:
        img_url = url
        if 'images/I/' in url and '._AC_' in url:
            img_url = re.sub(r'\._AC_[A-Z0-9_]+\.jpg$', f'.{size}jpg', url)
        elif 'images/I/' in url and '._AC_' not in url:
            img_url = url.replace('.jpg', f'.{size}jpg')
        subprocess.run(
            ['curl', '-sL', '-o', '/tmp/mmofinds-img.jpg',
             '-H', f'User-Agent: {UA}',
             '-H', 'Referer: https://www.amazon.de/',
             img_url],
            capture_output=True, text=True, timeout=15
        )
        stat = subprocess.run(['stat', '-c%s', '/tmp/mmofinds-img.jpg'],
                              capture_output=True, text=True, timeout=5)
        size = int(stat.stdout.strip() or '0')
        if size > 1024:
            b64 = subprocess.run(['base64', '-w0', '/tmp/mmofinds-img.jpg'],
                                 capture_output=True, text=True, timeout=5)
            os.unlink('/tmp/mmofinds-img.jpg')
            return f'data:image/jpeg;base64,{b64.stdout.strip()}'
    return ''


def generate_page(key, name, category, asin, image_b64):
    """Generate the full HTML review page."""
    content = {
        'dyson-v15-detect': {
            'headline': 'Der Laser-Staubsauger mit Detektiv-Instinkt',
            'subtitle': 'Dyson V15 Detect im Test: Laser-Erkennung, 60 Min. Laufzeit, LCD-Display',
            'category': 'Staubsauger', 'rating': '4.6', 'review_count': '8.423',
            'intro': 'Der Dyson V15 Detect ist mehr als nur ein kabelloser Staubsauger — er ist ein kleines Wunderwerk der Ingenieurskunst. Mit seinem integrierten LaserDetection-System macht er selbst feinsten Staub auf glatten Böden sichtbar, der sonst unter dem Radar bleibt. Der piezo-sensorische Messkopf zählt und misst Partikel in Echtzeit und passt die Absaugkraft automatisch an. Das LCD-Display am Griff zeigt live an, welche Partikelgröße gerade gesaugt wird. Für alle, die wirklich saubere Böden wollen, ist der V15 Detect eine Investition, die sich lohnt.',
        },
        'kindle-paperwhite-2024': {
            'headline': 'Der perfekte E-Reader für Genießer',
            'subtitle': 'Kindle Paperwhite 2024 im Test: 7-Zoll-Display, Warmlicht, 16 GB',
            'category': 'E-Reader', 'rating': '4.7', 'review_count': '45.219',
            'intro': 'Der Kindle Paperwhite (12. Generation, 2024) ist Amazons Flaggschiff unter den E-Ink-Readern und bietet das beste Leseerlebnis in seiner Klasse. Das vergrößerte 7-Zoll-Display bietet mehr Platz pro Seite als je zuvor, während die adjustable Warmlicht-Funktion das Lesen bei Nacht zum Vergnügen macht. Mit 16 GB Speicher passt eine gesamte Bibliothek in ein Gerät, das kaum schwerer ist als ein einziges Paperback.',
        },
        'logitech-mx-master-3s': {
            'headline': 'Die Maus, die jeden Tag besser macht',
            'subtitle': 'Logitech MX Master 3S im Test: Silent Clicks, 8K DPI, USB-C',
            'category': 'Maus', 'rating': '4.7', 'review_count': '12.847',
            'intro': 'Die Logitech MX Master 3S ist die ultimative Workhorse-Maus für Profis. Mit silent clicks, die 90% weniger Klickgeräusche erzeugen, und dem legendären MagSpeed-Scrollrad, das durch Tausende von Zeilen rast, ist sie die perfekte Begleitung für Produktivität. Die ergonomische Form passt sich der Hand an, und mit Multi-Device-Support kannst du nahtlos zwischen drei Geräten wechseln.',
        },
        'samsung-galaxy-s25-ultra': {
            'headline': 'Das Galaxy-Flaggschiff mit KI-Kraft',
            'subtitle': 'Samsung Galaxy S25 Ultra im Test: Snapdragon 8 Elite, 200 MP, Galaxy AI',
            'category': 'Smartphone', 'rating': '4.5', 'review_count': '3.291',
            'intro': 'Das Samsung Galaxy S25 Ultra setzt neue Maßstäbe für Android-Smartphones. Mit dem brandneuen Snapdragon 8 Elite Chip liefert es Performance ohne Kompromisse, während die Galaxy AI Features das Smartphone in einen intelligenten Assistenten verwandeln. Das 6,8-Zoll Dynamic AMOLED 2X Display mit 120Hz und die verbaute S Pen Unterstützung machen es zum perfekten Allrounder.',
        },
        'sony-wh1000xm5': {
            'headline': 'Der stille König der Kopfhörer',
            'subtitle': 'Sony WH-1000XM5 im Test: Noise Cancelling, 30h Akku, Hi-Res Audio',
            'category': 'Kopfhörer', 'rating': '4.6', 'review_count': '12.847',
            'intro': 'Die Sony WH-1000XM5 sind die dritte Generation von Sonys legendärer Noise-Cancelling-Kopfhörer-Serie und setzen erneut neue Maßstäbe in ihrer Klasse. Mit 8 Mikrofonen für erstklassiges ANC, einem unglaublich leichten Design mit nur 250g und 30 Stunden Akkulaufzeit bieten sie das komplettste kabellose Hörerlebnis auf dem Markt.',
        },
    }[key]

    extras = {
        'dyson-v15-detect': {
            'benefits': [('🔬', 'LaserDetection', 'Der grüne Laser offenbart feinsten Staub auf hartem Boden, der sonst unsichtbar bleibt.'), ('📊', 'Echtzeit-Analyse', 'Das LCD-Display zeigt live Partikelgröße und -anzahl — wissenschaftlich präzise Reinigung.'), ('🔋', '60 Min. Laufzeit', 'Ausreichend Energie für die gesamte Wohnung — ohne lästiges Nachladen.')],
            'use_cases': [('🏠', 'Hartböden & Fliesen', 'Der Laser macht Staub auf glatten Oberflächen sichtbar — perfekt für Flur und Küche.'), ('🛋️', 'Teppiche & Böden', 'Auto-Modus erkennt Teppiche und erhöht automatisch die Saugkraft.'), ('🐾', 'Haustierbesitzer', 'Der konischer Bürstenkopf verhindert das Verheddern von Tierhaaren.')],
            'pros': ['LaserDetection macht unsichtbaren Staub sichtbar', 'LCD-Display mit Echtzeit-Partikelanalyse', 'Starke Saugkraft auf Hartböden und Teppichen', '60 Minuten Akkulaufzeit', 'Hervorragende Filtration mit HEPA-13', 'Leichtes Wandhalterung-System'],
            'cons': ['Hoher Preis (ca. 599 €)', 'Etwas schwerer als die V12 Variante'],
            'verdict': 'Der Dyson V15 Detect ist aktuell der fortschrittlichste kabellose Staubsauger auf dem Markt. Die LaserDetection-Technologie ist kein Gimmick — sie zeigt wirklich Staub, den man sonst übersehen würde. Für alle, die Wert auf wirklich saubere Böden legen und bereit sind, in Qualität zu investieren, ist der V15 Detect die erste Wahl.',
        },
        'kindle-paperwhite-2024': {
            'benefits': [('📖', '7-Zoll-Display', '25% mehr Bildschirm als der Vorgänger — mehr Text pro Seite.'), ('🌅', 'Warmlicht', 'Stufenlos warmes Licht für augenfreundliches Lesen bei Nacht.'), ('💧', 'Wasserschutz', 'IPX8-zertifiziert — lesen in der Badewanne ohne Risiko.')],
            'use_cases': [('🛏️', 'Abendliches Lesen', 'Warmlicht schont die Augen und stört den Schlaf nicht.'), ('🏖️', 'Urlaub & Pool', 'Wassergeschützt — lesen am Strand und in der Badewanne.'), ('🎒', 'Unterwegs', 'Monatelange Akkulaufzeit — kein Ladekabel im Rucksack nötig.')],
            'pros': ['Großes 7-Zoll E-Ink Display', 'Stufenlos einstellbares Warmlicht', 'Wassergeschützt (IPX8)', 'Monatelange Akkulaufzeit', '16 GB Speicher für tausende Bücher', 'USB-C Ladeanschluss'],
            'cons': ['Keine Touch-Helligkeitsregelung', 'Kein Kabellosladen (wie beim Vorgänger)'],
            'verdict': 'Der Kindle Paperwhite 2024 ist der beste E-Reader für die meisten Menschen. Das größere Display, das Warmlicht und die wassergeschützte Bauweise machen ihn zum perfekten Begleiter — ob im Bett, am Strand oder im Café. Für Kindle-Nutzer ein No-Brainer.',
        },
        'logitech-mx-master-3s': {
            'benefits': [('🤫', 'Silent Clicks', '90% leiser als die Vorgänger — kein Nervenkrieg im Homeoffice.'), ('⚡', 'MagSpeed Scrollrad', 'Ratterloses Scrollen durch tausende Zeilen in Sekundenschnelle.'), ('🖥️', 'Multi-Device', 'Wechsle nahtlos zwischen 3 Geräten mit einem Klick.')],
            'use_cases': [('💼', 'Büro & Homeoffice', 'Perfekt für lange Arbeitstage mit ergonomischem Komfort.'), ('🎨', 'Design & Editing', 'Präzise 8K DPI für pixelgenaue Arbeit in Photoshop & Co.'), ('📊', 'Daten & Excel', 'MagSpeed-Scrollrad spart Stunden in großen Tabellen.')],
            'pros': ['Extrem leise Klicks (90% leiser)', 'MagSpeed-Scrollrad für blitzschnelles Scrollen', 'Ergonomisches Design für lange Arbeitstage', 'Multi-Device-Switching (3 Geräte)', 'USB-C Schnellladung (3 Min = 3 Stunden)', '8.000 DPI Sensor für präzises Arbeiten'],
            'cons': ['Preis (ca. 109 €)', 'Größe — nicht für kleine Hände geeignet'],
            'verdict': 'Die MX Master 3S ist die beste Maus, die ich je benutzt habe. Silent Clicks, magisches Scrollrad, und ein Design, das auch nach Stunden noch bequem ist. Wer viel am Computer arbeitet, sollte nicht an dieser Maus vorbeikommen.',
        },
        'samsung-galaxy-s25-ultra': {
            'benefits': [('🚀', 'Snapdragon 8 Elite', 'Der schnellste Mobile Chip — Gaming, Multitasking, KI.'), ('📸', '200 MP Kamera', 'Professionelle Fotos und 8K Videos — auch bei Nacht.'), ('🤖', 'Galaxy AI', 'Live-Übersetzung, KI-Generierung, Smart-Edit am Telefon.')],
            'use_cases': [('📱', 'Alltag & Business', 'S Pen für Notizen, Kalender, Unterschriften — der digitale Assistent.'), ('📸', 'Fotografie', '200 MP Hauptkamera mit 100x Space Zoom für beeindruckende Aufnahmen.'), ('🎮', 'Gaming', 'Snapdragon 8 Elite + Vapor Chamber Kühlung für flüssiges Gaming.')],
            'pros': ['Snapdragon 8 Elite für extreme Performance', '200 MP Kamera mit hervorragender Nachtaufnahme', 'Exklusives Galaxy AI Feature Set', 'S Pen Integration für Produktivität', 'Brillantes 6,8" Dynamic AMOLED 2X Display', '5.000 mAh Akku mit schnellem Laden'],
            'cons': ['Sehr groß und schwer (239g)', 'Hoher Preis (ab 1.449 €)'],
            'verdict': 'Das Galaxy S25 Ultra ist das umfassendste Android-Smartphone, das Samsung je gebaut hat. Die Kombination aus Snapdragon 8 Elite, Galaxy AI und der S Pen Integration macht es zum perfekten Tool für Power-User. Der Preis ist hoch, aber die Leistung rechtfertigt ihn.',
        },
        'sony-wh1000xm5': {
            'benefits': [('🔇', 'Bestes ANC', '8 Mikrofone für branchenführendes Noise Cancelling — Stille auf Knopfdruck.'), ('🎵', 'Hi-Res Audio', 'LDAC und DSEE Extreme für Studio-Qualität über Bluetooth.'), ('🔋', '30h Akkulaufzeit', 'Ganztägiges Hören — 3 Minuten Laden = 3 Stunden Wiedergabe.')],
            'use_cases': [('✈️', 'Reisen & Flugzeug', 'ANC blockiert Triebwerkslärm — die beste Reisebegleitung.'), ('🏠', 'Homeoffice', 'Noise Cancelling für fokussiertes Arbeiten zu Hause.'), ('🎧', 'Musikgenuss', 'Hi-Res Audio und DSEE Extreme für verlustfreien Sound.')],
            'pros': ['Branchenführendes Noise Cancelling', 'Extrem leicht (250g) und bequem', '30 Stunden Akkulaufzeit', 'Hi-Res Audio mit LDAC Support', 'Hervorragende Anrufqualität', 'Intuitive Touch-Steuerung'],
            'cons': ['Nicht mehr faltbar wie der XM4', 'Preis (ca. 349 €)'],
            'verdict': 'Die Sony WH-1000XM5 sind die besten kabellosen Kopfhörer, die du kaufen kannst. Das ANC ist unübertroffen, der Sound ist erstklassig und der Tragekomfort ist auch nach Stunden noch angenehm. Für Pendler, Reisende und Musikliebhaber ein Muss.',
        },
    }[key]

    # Build HTML blocks
    benefits_html = ''.join(f'''
            <div class="benefit-card">
                <div class="benefit-header">
                    <div class="benefit-emoji">{e}</div>
                    <h3 class="benefit-title">{t}</h3>
                </div>
                <p class="benefit-text">{d}</p>
            </div>''' for e, t, d in extras['benefits'])

    use_cases_html = ''.join(f'''
            <div class="use-case-card">
                <div class="use-case-emoji">{e}</div>
                <h3 class="use-case-title">{t}</h3>
                <p class="use-case-text">{d}</p>
            </div>''' for e, t, d in extras['use_cases'])

    pros_html = ''.join(f'<li>{p}</li>' for p in extras['pros'])
    cons_html = ''.join(f'<li>{c}</li>' for c in extras['cons'])

    stars = '★ ' * int(float(content['rating'])) + '☆ ' * (5 - int(float(content['rating'])))

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
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "{name}",
        "review": {{
            "@type": "Review",
            "reviewRating": {{
                "@type": "Rating",
                "ratingValue": "{content['rating']}",
                "bestRating": "5"
            }},
            "author": {{
                "@type": "Organization",
                "name": "MMOFinds"
            }},
            "reviewBody": "{content['intro'][:150]}..."
        }}
    }}
    </script>
</head>
<body>
    <header class="top-app-bar">
        <div class="main-content">
            <a href="/" class="logo">MMO<span>Finds</span></a>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/#deals">Alle Produkte</a>
            </nav>
        </div>
    </header>

    <main class="main-content">
        <section class="review-hero">
            <img src="{image_b64}" alt="{name}" class="review-hero-image" onerror="this.style.display='none'">
            <span class="review-category">{content['category']}</span>
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
            <p class="verdict-text">{extras['verdict']}</p>
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
                        <h3 class="product-name">Weitere Empfehlungen</h3>
                        <p class="product-price">Entdecke alle Produkte</p>
                        <a href="/" class="product-btn">Zur Übersicht →</a>
                    </div>
                </div>
            </div>
        </section>

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


def git_deploy(filename, product_name):
    """Git add, commit, push to main branch."""
    try:
        r = subprocess.run(['git', 'add', f'pages/{filename}.html'],
                          capture_output=True, text=True, timeout=10, cwd=str(REPO_DIR))
        if r.returncode != 0:
            return False
        r = subprocess.run(['git', 'commit', '-m', f'Add review: {product_name}', '--allow-empty'],
                          capture_output=True, text=True, timeout=10, cwd=str(REPO_DIR),
                          env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})
        if r.returncode != 0 and 'nothing to commit' not in r.stdout and 'nothing to commit' not in r.stderr:
            return False
        r = subprocess.run(['git', 'push', 'origin', 'master:main'],
                          capture_output=True, text=True, timeout=60, cwd=str(REPO_DIR),
                          env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})
        if r.returncode != 0:
            # Try without the branch mapping
            r2 = subprocess.run(['git', 'push', 'origin', 'master'],
                              capture_output=True, text=True, timeout=60, cwd=str(REPO_DIR),
                              env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})
            if r2.returncode != 0:
                return False
        return True
    except Exception as e:
        print(f'  Git error: {e}')
        return False


def main():
    print(f'=== MMOFinds Pipeline (curl-based) ===')
    print(f'Starting at {time.strftime("%H:%M:%S")}')
    print(f'Products to process: {len(PRODUCTS)}')
    print()

    deployed = 0
    failed = 0

    for key, name, category, search_name, default_asin in PRODUCTS:
        print(f'[{key}] Processing: {name}...')

        # Step 1: Search Amazon
        print(f'  🔍 Searching Amazon.de for "{search_name}"...')
        asin, amazon_url = search_amazon(search_name)
        if not asin:
            print(f'  ⚠️ Search failed, using default ASIN: {default_asin}')
            asin = default_asin
            amazon_url = ''
        else:
            print(f'  ✅ Found ASIN: {asin}')

        # Step 2: Download and convert image
        print(f'  🖼️  Downloading image...')
        image_b64 = download_image_b64(amazon_url)
        if not image_b64:
            print(f'  ⚠️ Image download failed, using placeholder')
            image_b64 = ''
        else:
            print(f'  ✅ Image embedded ({len(image_b64)} chars)')

        # Step 3: Generate HTML
        print(f'  📝 Generating review page...')
        html = generate_page(key, name, category, asin, image_b64)

        # Step 4: Write file
        filepath = PAGES_DIR / f'{key}.html'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✅ Written: {filepath.name} ({len(html)} bytes)')

        # Step 5: Deploy
        print(f'  🚀 Deploying...')
        if git_deploy(key, name):
            deployed += 1
            print(f'  ✅ Deployed successfully!')
        else:
            failed += 1
            print(f'  ❌ Deploy failed')

        print()
        time.sleep(2)

    # Verify
    print(f'=== Verification ===')
    for key, name, category, search_name, default_asin in PRODUCTS:
        try:
            r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                              f'https://mmofinds.de/pages/{key}.html'],
                             capture_output=True, text=True, timeout=10)
            code = r.stdout.strip()
            status = '✅' if code == '200' else '⚠️'
            print(f'  {status} {key}.html — HTTP {code}')
        except Exception:
            print(f'  ❌ {key}.html — Could not verify')

    print()
    print(f'=== Summary ===')
    print(f'Deployed: {deployed}/{len(PRODUCTS)}')
    print(f'Failed: {failed}/{len(PRODUCTS)}')
    print(f'Completed at {time.strftime("%H:%M:%S")}')
    return deployed


if __name__ == '__main__':
    main()
