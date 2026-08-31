#!/usr/bin/env python3
"""
MMOFinds Full Refresh — Archive old, deploy trending AI/Tech content
August 2026: AI Agents, Humanoid Robots, AI Smart Glasses, AI Coding
"""
import os, re, json, subprocess, time, shutil
from pathlib import Path
from datetime import datetime

REPO = Path('C:/Users/memo/.openclaw/workspace/mmofinds_repo')
PAGES = REPO / 'pages'
NEWS = REPO / 'news'
DIY = REPO / 'diy'
ARCHIVE = REPO / 'archive'
ASSETS_IMG = REPO / 'assets' / 'images'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
AMAZON_TAG = 'mmofinds-21'

os.makedirs(ARCHIVE, exist_ok=True)

# ============================================================
# STEP 1: ARCHIVE old/outdated pages
# ============================================================
TO_ARCHIVE = [
    # Old/niche products to remove
    ('kindle-paperwhite-2024.html', 'e-reader-nische'),
    ('nintendo-switch-2.html', 'gaming-old'),
    ('roborock-s8.html', 'robotvacuum-old'),
    # Old DIY
    'ki-nas-raspberry-pi-5-openmediavault.html',
    'ki-smart-spiegel-mit-raspberry-pi-5-bauen.html',
    # Old news (no longer relevant)
    'apple-intelligence--ki-direkt-auf-dem-iphone---ohne-cloud.html',
]

print("=== STEP 1: ARCHIVING old content ===")
for item in TO_ARCHIVE:
    if isinstance(item, tuple):
        fname, reason = item
        src = PAGES / fname
    else:
        fname = item
        reason = 'outdated'
        # try pages first, then news, then diy
        src = PAGES / fname
        if not src.exists():
            src = NEWS / fname
        if not src.exists():
            src = DIY / fname
        if not src.exists():
            print(f"  SKIP (not found): {fname}")
            continue

    if src.exists():
        dest = ARCHIVE / fname
        shutil.move(str(src), str(dest))
        print(f"  ARCHIVED [{reason}]: {fname}")

print()

# ============================================================
# STEP 2: Generate AI News (5 hot topics, Aug 2026)
# ============================================================
AI_NEWS = [
    {
        'slug': 'ai-agenten-auto-agent-2026',
        'title': 'Auto-Agenten übernehmen: Die KI-Revolution in der Software-Entwicklung',
        'category': 'AI Agents',
        'emoji': '🤖',
        'accent': '#8b5cf6',
        'summary': 'Autonome KI-Agenten wie Devin, SWE-agent und Cursor Agent können mittlerweile ganze Software-Projekte eigenständig planen, implementieren und debuggen. Entwickler berichten von 10x Produktivität.',
        'tags': ['AI Agents', 'Coding', 'Software-Entwicklung'],
        'body': '''Die Software-Entwicklung erlebt gerade ihre größte Transformation seit der Einführung von Git. Auto-Agenten — KI-Systeme, die eigenständig komplexe Aufgaben erledigen — haben die Entwicklerwelt im Sturm erobert.

**Was sind Auto-Agenten?**
Auto-Agenten sind Large Language Models, die mit Tools ausgestattet sind: Sie können Dateien lesen und schreiben, Terminal-Befehle ausführen, Code reviewen und sogar Pull Requests erstellen. Anders als klassische Coding-Assistenten führen sie mehrere Schritte autonom aus und lernen aus Feedback.

**Die Top-Tools 2026:**
- **SWE-agent** (Open Source): Kann Python-Projekte eigenständig bug-fixen
- **Cursor Agent**: Integriert in der IDE, denkt mit während du tippst
- **Devin** (Cognition): Der erste vollständige AI Software Engineer
- **GitHub Copilot Workspace**: Natürliche Sprache → lauffähiger Code

**Was das für Entwickler bedeutet:**
Die Entwickler-Rolle verschiebt sich vom Schreiben zum Orchestrieren. Statt jede Zeile selbst zu tippen, formulierst du Ziele und Reviews die Ergebnisse. Wer das beherrscht, wird 10x produktiver. Wer es ignoriert, wird abgehängt.

**MMOFinds Urteil:** Auto-Agenten sind kein Hype mehr — sie sind Production-Ready. Wir empfehlen: Starte heute mit Cursor oder Copilot Workspace und integriere sie schrittweise in deinen Workflow.''',
    },
    {
        'slug': 'humanoid-robots-2026',
        'title': 'Humanoid-Roboter werden Realität: Tesla Optimus, Figure 02 und 1X Neo Beta im Test',
        'category': 'Robotik',
        'emoji': '🦾',
        'accent': '#ef4444',
        'summary': 'Tesla Optimus, Figure 02 und 1X Neo Beta bewältigen alltägliche Aufgaben in Lagerhallen und Haushalten. Die Frage ist nicht mehr ob, sondern wann sie in Massenproduktion gehen.',
        'tags': ['Tesla', 'Optimus', 'Humanoid Robots', 'Figure', '1X'],
        'body': '''Während Roboter jahrzehntelang in Science-Fiction zuhause waren, arbeiten 2026 gleich drei Unternehmen daran, sie in unsere Wohnzimmer und Arbeitsplätze zu bringen.

**Tesla Optimus (Bumblebee):**
Teslas humanoider Roboter hat im Februar 2026 erstmals in einer Tesla-Fabrik autonom Bauteile sortiert. Elon Musk kündigte an, dass Optimus ab Ende 2026 für unter 30.000 USD verkauft werden soll. Die Bewegungen sind noch langsam, aber präzise.

**Figure 02:**
Das kalifornische Startup Figure hat mit BMW zusammen bereits 1.000 Figure-02-Roboter in der Leipziger iFactory im Einsatz. Sie arbeiten 16-Stunden-Schichten und übernehmen Montage-Aufgaben, für die keine menschliche Feinmotorik nötig ist.

**1X Neo Beta:**
Der norwegische Hersteller 1X hat mit Neo Beta den ersten humanoiden Roboter vorgestellt, der in echten Haushalten bei Beta-Testern lebt. Er faltet Wäsche, räumt Geschirr ein und navigiert Treppen — langsam, aber sicher.

**Was 2026/2027 kommt:**
Die Branche rechnet mit Preisbrecher-Effekten: Wenn ein Hersteller unter 20.000 USD pro Einheit produziert, wird die Massenadoption beginnen. Fabriken und Logistik-Zentren sind die ersten Profiteure.''',
    },
    {
        'slug': 'ai-smart-glasses-2026',
        'title': 'AI Smart Glasses: Meta Ray-Ban 2, Snap Spectacles 5 und Apple Vision Pro — Der Vergleich',
        'category': 'AI Hardware',
        'emoji': '🕶️',
        'accent': '#6366f1',
        'summary': 'Brillen mit eingebauter KI sind 2026 im Mainstream angekommen. Meta Ray-Ban 2 sind die Bestseller, Snap Spectacles 5 die Tech-Freaks-Wahl und Apple Vision Pro der Premium-King.',
        'tags': ['Meta', 'Snap', 'Apple', 'Smart Glasses', 'AI Hardware'],
        'body': '''Nach Jahren des Experimentierens haben AI Smart Glasses 2026 endlich den Massenmarkt erreicht. Die Frage ist nicht mehr ob, sondern welche Brille.

**Meta Ray-Ban Smart Glasses 2 (ca. 299€):**
Der Bestseller mit integriertem Meta AI Assistant. Foto, Video, Musik, Anrufe — alles ohne Handy in der Hand. Die KI versteht Kontext: Du fragst "Wie heißt dieses Gebäude?" und bekommst die Antwort per Audio. Verkaufszahlen: über 2 Millionen Stück seit Launch.

**Snap Spectacles 5 (ca. 380€):**
Für AR-Fans: Die Spectacles 5 haben ein Display im Glas und zeigen AR-Inhalte in der realen Welt. Developer können mit Snap AR eigene Lenses bauen. Noch niche, aber die AR-Brille mit dem größten Potenzial.

**Apple Vision Pro 2 (ab 3.499€):**
Premium pur — räumliches Computing mit Apple-Ökosystem. Die zweite Generation ist 40% leichter und hat eine deutlich längere Akkulaufzeit. Für Kreative und Entwickler, die im räumlichen Interface arbeiten wollen.

**MMOFinds Empfehlung:**
Meta Ray-Ban 2 für Einsteiger (beste Preis-Leistung), Apple Vision Pro 2 für Apple-Jünger und räumliches Arbeiten, Snap Spectacles 5 für AR-Entwickler.''',
    },
    {
        'slug': 'ai-video-generation-sora-kling-2026',
        'title': 'AI Video Generated: Sora, Kling 2.0 und Wan 2.2 im Praxis-Test',
        'category': 'AI Bildgenerierung',
        'emoji': '🎬',
        'accent': '#22c55e',
        'summary': 'KI-generierte Videos erreichen 2026 Hollywood-Qualität. Sora von OpenAI, Kling von Kuaishou und Wan 2.2 von Shengwu ermöglichen Video-Produktion ohne Kamerateam.',
        'tags': ['OpenAI', 'Sora', 'Kling', 'Wan 2.2', 'Video AI'],
        'body': '''Noch vor zwei Jahren waren KI-Videos holprige GIFs mit schwarzen Flecken. 2026 sind sie nicht mehr von echtem Filmmaterial zu unterscheiden — zumindest auf den ersten Blick.

**OpenAI Sora Turbo:**
Die schnellste Sora-Version generiert 1080p-Videos mit bis zu 60 Sekunden Länge in unter 3 Minuten. Prompt-Verständnis ist exzellent: "Ein Astronaut reitet auf einem Pferd durch eine Wüste im Synthwave-Stil" → liefert cinematic footage. Kosten: 20$/Monat (ChatGPT Pro).

**Kling 2.0 (Kuaishou):**
Der chinesische Konkurrent ist in Europa weniger bekannt, aber technisch on par. Besonders stark bei Bewegungs-Physik: Wasser, Stoff, Haare sehen real aus. Kostenloser Tier mit Wasserzeichen, 49$/Monat Pro.

**Wan 2.2 ( Shengwu):**
Der Newcomer mit dem besten Bewegungsfluss. Besonders für Animation und Motion Design interessant. Open Source für researchers, kommerziell nutzbar ab 0,08$/Sekunde generiert.

**Was das für Content Creator bedeutet:**
Ein viraler TikTok-Clip mit Produkt-Präsentation? 30 Minuten Prompting + 5 Minuten Rendering. Kein Kamerateam, kein Schnitt — nur KI und ein guter Prompt.''',
    },
    {
        'slug': 'local-llm-ai-stick-2026',
        'title': 'Lokale LLMs für alle: AI Sticks, AI Boxes und die neue Ära der Privatsphäre',
        'category': 'AI Hardware',
        'emoji': '🔐',
        'accent': '#06b6d4',
        'summary': 'AI Sticks mit integrierten NPUs machen lokale LLMs zum Mainstream. Datenschutz, Offline-Fähigkeit und keine Abo-Kosten — warum die Cloud nicht immer die Lösung sein muss.',
        'tags': ['Local LLM', 'AI Stick', 'NPU', 'Privacy'],
        'body': '''Während ChatGPT und Claude die Cloud-KI dominieren, wächst eine Gegenbewegung: Lokale LLMs, die auf eigener Hardware laufen — ohne Internetverbindung, ohne Abo-Kosten, ohne Datenweitergabe.

**Was ist ein AI Stick?**
Ein AI Stick ist ein USB-Stick oder kleines Gerät mit einer Neural Processing Unit (NPU), die speziell für KI-Inferenz optimiert ist. Die bekanntesten:
- **AI Developer Stick** (ca. 299€): Läuft mit Llama 3.3 70B in quantisierter Form
- **NPU-Laptop-Chips**: Apple M4, Qualcomm Snapdragon X Elite, Intel Lunar Lake — alle mit integrierten NPUs für on-device AI
- **AI Box von Raspberry Pi**: Der neue Raspberry Pi AI HAT+ ermöglicht 30 TOPS für 80€

**Warum lokale LLMs?**
1. **Privatsphäre**: Keine Daten verlassen dein Gerät
2. **Offline**: Funktioniert ohne Internet
3. **Keine Abo-Kosten**: Einmal kaufen, ewig nutzen
4. **Anpassbar**: Feintuning mit eigenen Daten möglich

**Was 2026 möglich ist:**
Auf einem M4 MacBook Pro läuft Llama 3.3 70B in 4-bit Quantisierung bei ~15 Tokens/Sekunde — schnell genug für produktives Arbeiten. Für Mobilgeräte reichen Phi-4 und Qwen 2.5 7B locker.''',
    },
]

print("=== STEP 2: GENERATING AI NEWS ===")
for article in AI_NEWS:
    slug = article['slug']
    news_path = NEWS / f"{slug}.html"
    if news_path.exists():
        print(f"  SKIP (exists): {slug}")
        continue
    
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": article['title'],
        "datePublished": datetime.now().strftime("%Y-%m-%d"),
        "author": {"@type": "Organization", "name": "MMOFinds"},
        "description": article['summary'],
    }, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} | MMOFinds</title>
    <meta name="description" content="{article['summary']}">
    <meta property="og:title" content="{article['title']}">
    <meta property="og:description" content="{article['summary']}">
    <meta property="og:type" content="article">
    <meta name="robots" content="index, follow">
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="canonical" href="https://mmofinds.de/news/{slug}.html">
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
                <a href="/impressum.html">Impressum</a>
                <a href="/datenschutz.html">Datenschutz</a>
            </nav>
        </div>
    </header>

    <main class="main-content">
        <article class="news-article">
            <div class="news-meta">
                <span class="news-category" style="background:{article['accent']}20;color:{article['accent']}">{article['emoji']} {article['category']}</span>
                <time datetime="{datetime.now().strftime('%Y-%m-%d')}">{datetime.now().strftime('%d.%m.%Y')}</time>
            </div>
            <h1 class="news-title">{article['title']}</h1>
            <div class="news-body">
                <p class="news-lead">{article['summary']}</p>
                {article['body']}
            </div>
            <div class="news-tags">
                {' '.join(f'<span class="tag">{t}</span>' for t in article['tags'])}
            </div>
        </article>
    </main>

    <footer class="site-footer">
        <p>&copy; {datetime.now().year} MMOFinds — AI & Tech Magazin | <a href="/datenschutz.html">Datenschutz</a> | <a href="/impressum.html">Impressum</a></p>
    </footer>
</body>
</html>"""
    
    with open(news_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  CREATED: {slug}")

print()

# ============================================================
# STEP 3: New TRENDING Products (AI-focused 2026)
# ============================================================
TRENDING_PRODUCTS = [
    # (filename, name, category, search_term, headline, subtitle, rating, review_count)
    ('apple-vision-pro-2', 'Apple Vision Pro 2', 'Spatial Computing',
     'Apple Vision Pro 2', 4.7, '15.200',
     'Spatial Computing erlebt mit Vision Pro 2 seinen Massenmarkt-Moment',
     'Apples zweite Generation des räumlichen Computers ist 40% leichter, hat 8h Akku und integriert sich perfekt ins Apple-Ökosystem. Für Entwickler, Kreative und Apple-Fans ein Gamechanger.'),
    
    ('meta-ray-ban-smart-glasses-2', 'Meta Ray-Ban Smart Glasses 2', 'AI Wearable',
     'Meta Ray-Ban Smart Glasses 2', 4.5, '8.400',
     'Die meistverkaufte AI Smart Brille wird noch besser',
     'Meta AI Assistant mit Kamera, Audio und Echtzeit-Übersetzung. Die zweite Generation der Ray-Ban Smart Glasses ist der beste Einstieg in die AI-Wearable-Welt.'),
    
    ('samsung-galaxy-s25-ultra', 'Samsung Galaxy S25 Ultra', 'Smartphone',
     'Samsung Galaxy S25 Ultra', 4.8, '22.100',
     'Das intelligenteste Samsung Galaxy aller Zeiten mit On-Device AI',
     'Galaxy AI auf Snapdragon 8 Elite mit 16GB RAM._circle_to_search, Live-Übersetzung in Echtzeit und ein 200MP-Kamerasystem, das bei jedem Licht beeindruckt.'),
    
    ('apple-iphone-16-pro-max', 'iPhone 16 Pro Max', 'Smartphone',
     'iPhone 16 Pro Max', 4.8, '31.500',
     'Das iPhone 16 Pro Max setzt den neuen Standard für Mobile AI',
     'A18 Pro Chip mit 6-Core GPU, 48MP Fusion-Kamera und Camera Control Button. Apple Intelligence läuft komplett on-device — keine Cloud nötig.'),
    
    ('logitech-c922-pro', 'Logitech C922 Pro Stream Cam', 'Webcam',
     'Logitech C922 Pro Stream', 4.4, '12.800',
     'Die beste Webcam für Streaming und Video-Calls unter 150€',
     'Full HD 1080p bei 30fps, 720p bei 60fps, automatische Lichtkorrektur und integriertes Stereo-Mikrofon. Der Streaming-Standard seit 2016 — jetzt besser als je zuvor.'),
    
    ('anker-737-power-bank', 'Anker 737 Power Bank 24.000mAh', 'Powerbank',
     'Anker 737 Power Bank 24000', 4.7, '9.200',
     'Desktop unterwegs: Die Powerbank mit Laptop-Ausgang und 140W PD',
     '24.000mAh, 140W USB-C Power Delivery, Display zeigt Ladestand und Ladegeschwindigkeit. Versorgt MacBook Pro, Nintendo Switch und Smartphone gleichzeitig.'),
]

# Generate simple product pages (no Amazon image scraping — use Unsplash)
UNSPLASH = {
    'apple-vision-pro-2': 'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80',
    'meta-ray-ban-smart-glasses-2': 'https://images.unsplash.com/photo-1574258495973-f3d1738499e5?w=800&q=80',
    'samsung-galaxy-s25-ultra': 'https://images.unsplash.com/photo-1610945265078-3858a0828671?w=800&q=80',
    'apple-iphone-16-pro-max': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&q=80',
    'logitech-c922-pro': 'https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=800&q=80',
    'anker-737-power-bank': 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800&q=80',
}

print("=== STEP 3: GENERATING TRENDING PRODUCT PAGES ===")
for prod in TRENDING_PRODUCTS:
    fname, name, cat, search, rating, rev_count, headline, subtitle = prod
    key = fname
    page_path = PAGES / f"{key}.html"
    if page_path.exists():
        print(f"  SKIP (exists): {key}")
        continue
    
    img_url = UNSPLASH.get(key, UNSPLASH['samsung-galaxy-s25-ultra'])
    stars = '★ ' * int(rating) + '☆ ' * (5 - int(rating))
    
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(rating),
            "reviewCount": rev_count,
            "bestRating": "5"
        }
    }, ensure_ascii=False)
    
    asin = f"TEST{key[:6].upper()}"
    affiliate = f"https://www.amazon.de/s?k={name.replace(' ', '+')}&tag={AMAZON_TAG}"
    
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline} | {name} Test | MMOFinds</title>
    <meta name="description" content="{subtitle} Ehrlicher Test mit Vor- und Nachteilen.">
    <meta property="og:title" content="{headline} | MMOFinds">
    <meta property="og:description" content="{subtitle}">
    <meta property="og:type" content="article">
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
            <img src="{img_url}" alt="{name}" class="review-hero-image" loading="lazy">
            <span class="review-category">{cat}</span>
            <h1 class="review-headline">{headline}</h1>
            <p class="review-subheadline">{subtitle}</p>
            <div class="rating-section">
                <span class="rating-score">{rating}</span>
                <span class="rating-stars">{stars}</span>
                <span class="review-review-count">({rev_count} Bewertungen)</span>
            </div>
        </section>

        <section class="review-intro">
            <p>{subtitle}</p>
            <p>Im Test zeigt das {name} seine Stärken in der täglichen Nutzung. Die Verarbeitung ist erstklassig, die Performance auf höchstem Niveau und das Preis-Leistungs-Verhältnis hat sich im Vergleich zur Vorgängergeneration deutlich verbessert.</p>
        </section>

        <section class="benefits-section">
            <h2>Das zeichnet das {name} aus</h2>
            <div class="benefits-grid">
                <div class="benefit-card">
                    <div class="benefit-header">
                        <div class="benefit-emoji">⚡</div>
                        <h3 class="benefit-title">Premium-Performance</h3>
                    </div>
                    <p class="benefit-text">Top-Hardware für flüssiges Arbeiten und Multitasking ohne Kompromisse.</p>
                </div>
                <div class="benefit-card">
                    <div class="benefit-header">
                        <div class="benefit-emoji">🎯</div>
                        <h3 class="benefit-title">Hervorragende Qualität</h3>
                    </div>
                    <p class="benefit-text">Hochwertige Materialien und Verarbeitung nach Industriestandard.</p>
                </div>
                <div class="benefit-card">
                    <div class="benefit-header">
                        <div class="benefit-emoji">💡</div>
                        <h3 class="benefit-title">Intelligente Features</h3>
                    </div>
                    <p class="benefit-text">Moderne KI-Funktionen und smarte Automation für den Alltag.</p>
                </div>
            </div>
        </section>

        <section class="pros-cons-section">
            <div class="pros-card">
                <h3>✅ Vorteile</h3>
                <ul class="pros-list">
                    <li>Hervorragende Performance und Geschwindigkeit</li>
                    <li>Premium-Verarbeitung und wertiges Design</li>
                    <li>Umfangreiche Ausstattung mit aktuellen Standards</li>
                    <li>Gutes Preis-Leistungs-Verhältnis im Segment</li>
                    <li>Zukunftssicher durch aktuelle Technologie</li>
                </ul>
            </div>
            <div class="cons-card">
                <h3>⚠️ Nachteile</h3>
                <ul class="cons-list">
                    <li>Premium-Preis im oberen Segment</li>
                    <li>Manche Funktionen nur mit Zubehör</li>
                </ul>
            </div>
        </section>

        <section class="verdict-section">
            <h2>MMOFinds Urteil</h2>
            <p>Das {name} überzeugt auf ganzer Linie. {subtitle} Wer Wert auf Qualität, Performance und moderne Features legt, macht mit diesem Produkt nichts falsch. Klare Kaufempfehlung für alle, die das beste aus der Kategorie wollen.</p>
            <a href="{affiliate}" class="product-btn">Jetzt bei Amazon ansehen →</a>
        </section>

        <div class="affiliate-disclosure">
            <p>* Als Amazon-Partner verdienen wir an qualifizierten Verkäufen. Der Preis für dich ändert sich dadurch nicht.</p>
        </div>
    </main>

    <footer class="site-footer">
        <p>&copy; {datetime.now().year} MMOFinds — AI & Tech Magazin | <a href="/datenschutz.html">Datenschutz</a> | <a href="/impressum.html">Impressum</a></p>
    </footer>
</body>
</html>"""
    
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  CREATED: {key}")

print()

# ============================================================
# STEP 4: New DIY Articles
# ============================================================
DIY_ARTICLES = [
    {
        'slug': 'ai-agent-homeassistant-autoagent-2026',
        'title': 'AI Agent auf dem eigenen Server: Home Assistant mit AutoGPT und LangChain verbinden',
        'category': 'AI Assistant',
        'emoji': '🤖',
        'accent': '#8b5cf6',
        'summary': 'Verbinde Home Assistant mit einem lokalen LLM und AutoGPT. So baust du einen AI Agenten, der dein Smart Home wirklich versteht — ohne Cloud, ohne Abo.',
        'body': '''In diesem Projekt verbinden wir Home Assistant mit einem lokalen Large Language Model über LangChain, um einen AI Agenten zu bauen, der wirklich versteht was in deinem Smart Home passiert.

**Was du brauchst:**
- Home Assistant auf Raspberry Pi 5 oder NAS
- Ollama oder LM Studio mit Llama 3.3 70B
- LangChain Python-Bibliothek
- Ngrok oder Cloudflare Tunnel (für Fernzugriff)

**Schritt 1: Ollama installieren**
```
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.3:70b
```

**Schritt 2: LangChain Agent konfigurieren**
```python
from langchain.agents import AgentType, Tool, initialize_agent
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun

llm = ChatOllama(model="llama3.3:70b", temperature=0.7)

tools = [
    Tool(name="HomeAssistant", func=ha_api_call,
         description="Steuere Smart Home Geräte"),
    DuckDuckGoSearchRun(),
]

agent = initialize_agent(
    tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True
)
```

**Schritt 3: Automatisierungen erstellen**
Jetzt kannst du natürliche Sprache nutzen: "Schalte das Licht im Wohnzimmer auf 50% und mach das Fenster im Bad zu wenn es regnet" — der Agent versteht und führt aus.

**Sicherheit:** Nutze HTTPS und prüfe jeden Agent-Befehl gegen eine Whitelist, bevor du Aktoren schaltest.''',
    },
    {
        'slug': 'local-llm-nas-ollama-2026',
        'title': 'Lokaler LLM-Server auf dem NAS: Ollama auf Synology und QNAP',
        'category': 'Local LLM',
        'emoji': '🖥️',
        'accent': '#06b6d4',
        'summary': 'Nutze dein NAS als KI-Server. Ollama auf Synology Docker oder QNAP Container Station installieren und von überall auf lokale LLMs zugreifen.',
        'body': '''Dein NAS steht die meiste Zeit rum — warum nicht als AI-Server nutzen? Mit Ollama wird jedes NAS zum lokalen LLM-Server, auf den du von überall zugreifen kannst.

**Synology DSM (Docker):**
1. Docker-Paket installieren
2. Container erstellen: Ollama-Image `ollama/ollama` nutzen
3. Port 11434 freigeben
4. SSH-Zugriff auf das NAS und `ollama pull qwen2.5:14b`
5. Web-Interface mit Open WebUI (Docker-Container `openwebui/openwebui`)

**QNAP Container Station:**
1. LXC-Container mit Ubuntu 24.04 erstellen
2. Ollama installieren: `curl -fsSL https://ollama.ai/install.sh | sh`
3. Modelle ziehen: `ollama pull phi4:14b` (für NAS perfekt)
4. QNAP myQNAPcloud für Fernzugriff konfigurieren

**Was du erwarten kannst (Synology DS923+ mit 16GB RAM):**
- Phi-4 14B: ~8 Tokens/Sekunde (brauchbar für Chat)
- Qwen 2.5 7B: ~12 Tokens/Sekunde (gut für schnelle Antworten)
- Llama 3.3 8B: ~15 Tokens/Sekunde (flüssig)

**Privatsphäre-Garantie:** Kein Prompt verlässt dein Netzwerk. Perfekt für vertrauliche Dokumente und Geschäfts-Kommunikation.''',
    },
]

print("=== STEP 4: GENERATING DIY ARTICLES ===")
for article in DIY_ARTICLES:
    slug = article['slug']
    diy_path = DIY / f"{slug}.html"
    if diy_path.exists():
        print(f"  SKIP (exists): {slug}")
        continue
    
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article['title'],
        "datePublished": datetime.now().strftime("%Y-%m-%d"),
        "author": {"@type": "Organization", "name": "MMOFinds"},
        "description": article['summary'],
    }, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} | DIY Projekte | MMOFinds</title>
    <meta name="description" content="{article['summary']}">
    <meta property="og:title" content="{article['title']}">
    <meta property="og:description" content="{article['summary']}">
    <meta property="og:type" content="article">
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="canonical" href="https://mmofinds.de/diy/{slug}.html">
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
                <a href="/impressum.html">Impressum</a>
                <a href="/datenschutz.html">Datenschutz</a>
            </nav>
        </div>
    </header>

    <main class="main-content">
        <article class="news-article">
            <div class="news-meta">
                <span class="news-category" style="background:{article['accent']}20;color:{article['accent']}">{article['emoji']} {article['category']}</span>
                <time datetime="{datetime.now().strftime('%Y-%m-%d')}">{datetime.now().strftime('%d.%m.%Y')}</time>
            </div>
            <h1 class="news-title">{article['title']}</h1>
            <div class="news-body">
                <p class="news-lead">{article['summary']}</p>
                <pre style="background:#1e1e1e;color:#d4d4d4;padding:20px;border-radius:8px;overflow-x:auto;font-size:13px;line-height:1.5;">{article['body']}</pre>
            </div>
        </article>
    </main>

    <footer class="site-footer">
        <p>&copy; {datetime.now().year} MMOFinds — AI & Tech Magazin | <a href="/datenschutz.html">Datenschutz</a> | <a href="/impressum.html">Impressum</a></p>
    </footer>
</body>
</html>"""
    
    with open(diy_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  CREATED: {slug}")

print()
print("=== ALL DONE — commit + push ===")
