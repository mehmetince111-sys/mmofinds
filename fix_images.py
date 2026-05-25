#!/usr/bin/env python3
"""Fix all DIY and News card images in index.html."""

with open('/root/mmofinds/index.html', 'r') as f:
    html = f.read()

# DIY card image replacements (href -> new image)
diy_replacements = [
    # ai-security-camera
    ('<a href="/diy/ai-security-camera.html" class="card">\n        <div class="card-image">\n          <<img src="/images/sennheiser-momentum-4.jpg" alt="KI-Sicherheitskamera mit Raspberry Pi bauen — MMOFinds DIY" class="card-img">',
     '<a href="/diy/ai-security-camera.html" class="card">\n        <div class="card-image">\n          <img src="/images/diy-ai-security-camera.svg" alt="KI-Sicherheitskamera mit Raspberry Pi bauen — MMOFinds DIY" class="card-img">'),
    
    # eigenen-ai-assistenten-mit-raspberry-pi-bauen
    ('<a href="/diy/eigenen-ai-assistenten-mit-raspberry-pi-bauen.html" class="card">\n        <div class="card-image">\n          <<img src="/images/ps5-pro.jpg" alt="Eigenen AI-Assistenten mit Raspberry Pi bauen" class="card-img">',
     '<a href="/diy/eigenen-ai-assistenten-mit-raspberry-pi-bauen.html" class="card">\n        <div class="card-image">\n          <img src="/images/diy-ai-assistent-pi.svg" alt="Eigenen AI-Assistenten mit Raspberry Pi bauen" class="card-img">'),
    
    # diy index card
    ('<a href="/diy/index.html" class="card">\n        <div class="card-image">\n          <<img src="/images/macbook-air-m4.jpg" alt="DIY Projekte — MMOFinds" class="card-img">',
     '<a href="/diy/index.html" class="card">\n        <div class="card-image">\n          <img src="/images/diy-mechanical-keyboard.svg" alt="DIY Projekte — MMOFinds" class="card-img">'),
    
    # mechanical-keyboard-build
    ('<a href="/diy/mechanical-keyboard-build.html" class="card">\n        <div class="card-image">\n          <<img src="/images/canon-eos-r50.jpg" alt="Eigene mechanische Tastatur bauen — MMOFinds DIY" class="card-img">',
     '<a href="/diy/mechanical-keyboard-build.html" class="card">\n        <div class="card-image">\n          <img src="/images/diy-mechanical-keyboard.svg" alt="Eigene mechanische Tastatur bauen — MMOFinds DIY" class="card-img">'),
    
    # mechanische-tastatur-selbst-bauen
    ('<a href="/diy/mechanische-tastatur-selbst-bauen---keychron-q1-pro.html" class="card">\n        <div class="card-image">\n          <<img src="/images/sony-wh-1000xm5.jpg" alt="Mechanische Tastatur selbst bauen — Keychron Q1 Pro" class="card-img">',
     '<a href="/diy/mechanische-tastatur-selbst-bauen---keychron-q1-pro.html" class="card">\n        <div class="card-image">\n          <img src="/images/diy-mechanical-keyboard.svg" alt="Mechanische Tastatur selbst bauen — Keychron Q1 Pro" class="card-img">'),
    
    # nas-raspberry-pi
    ('<a href="/diy/nas-raspberry-pi.html" class="card">\n        <div class="card-image">\n          <<img src="/images/kindle-paperwhite-2024.jpg" alt="Eigenes NAS mit Raspberry Pi aufbauen — MMOFinds DIY" class="card-img">',
     '<a href="/diy/nas-raspberry-pi.html" class="card">\n        <div class="card-image">\n          <img src="/images/diy-nas-raspberry-pi.svg" alt="Eigenes NAS mit Raspberry Pi aufbauen — MMOFinds DIY" class="card-img">'),
    
    # raspberry-pi-smart-home-hub
    ('<a href="/diy/raspberry-pi-smart-home-hub.html" class="card">\n        <div class="card-image">\n          <<img src="/images/apple-watch-series-10.jpg" alt="Raspberry Pi 5 Smart Home Hub bauen — MMOFinds DIY" class="card-img">',
     '<a href="/diy/raspberry-pi-smart-home-hub.html" class="card">\n        <div class="card-image">\n          <img src="/images/diy-smart-home-hub.svg" alt="Raspberry Pi 5 Smart Home Hub bauen — MMOFinds DIY" class="card-img">'),
    
    # smart-home-hub-mit-home-assistant-auf-nas
    ('<a href="/diy/smart-home-hub-mit-home-assistant-auf-nas.html" class="card">\n        <div class="card-image">\n          <<img src="/images/iphone-16-pro.jpg" alt="Smart Home Hub mit Home Assistant auf NAS" class="card-img">',
     '<a href="/diy/smart-home-hub-mit-home-assistant-auf-nas.html" class="card">\n        <div class="card-image">\n          <img src="/images/diy-smart-home-hub.svg" alt="Smart Home Hub mit Home Assistant auf NAS" class="card-img">'),
    
    # smart-mirror
    ('<a href="/diy/smart-mirror.html" class="card">\n        <div class="card-image">\n          <<img src="/images/ipad-air-m3.jpg" alt="Smart Mirror mit Raspberry Pi bauen — MMOFinds DIY" class="card-img">g">',
     '<a href="/diy/smart-mirror.html" class="card">\n        <div class="card-image">\n          <img src="/images/diy-smart-mirror.svg" alt="Smart Mirror mit Raspberry Pi bauen — MMOFinds DIY" class="card-img">'),
]

# News card image replacements
news_replacements = [
    # ai-sprachmodelle
    ('<a href="/news/ai-sprachmodelle-2026.html" class="card">\n        <div class="card-image">\n          <<img src="/images/canon-eos-r50.jpg" alt="KI-Sprachmodelle 2026: Die besten KI-Modelle im Vergleich — MMOFinds" class="card-img">',
     '<a href="/news/ai-sprachmodelle-2026.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-ai-sprachmodelle.svg" alt="KI-Sprachmodelle 2026: Die besten KI-Modelle im Vergleich — MMOFinds" class="card-img">'),
    
    # apple-intelligence
    ('<a href="/news/apple-intelligence--ki-direkt-auf-dem-iphone---ohne-cloud.html" class="card">\n        <div class="card-image">\n          <<img src="/images/dyson-v15-detect.jpg" alt="Apple Intelligence KI direkt auf dem iPhone – ohne Cloud — MMOFinds" class="card-img">',
     '<a href="/news/apple-intelligence--ki-direkt-auf-dem-iphone---ohne-cloud.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-apple-intelligence.svg" alt="Apple Intelligence KI direkt auf dem iPhone – ohne Cloud — MMOFinds" class="card-img">'),
    
    # deepmind-proteine
    ('<a href="/news/google-deepmind-entwickelt-ki--die-proteine-in-sekunden-designen-kann.html" class="card">\n        <div class="card-image">\n          <<img src="/images/apple-airpods-pro-2.jpg" alt="Google DeepMind entwickelt KI, die Proteine in Sekunden designen kann — MMOFinds" class="card-img">',
     '<a href="/news/google-deepmind-entwickelt-ki--die-proteine-in-sekunden-designen-kann.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-deepmind-proteine.svg" alt="Google DeepMind entwickelt KI, die Proteine in Sekunden designen kann — MMOFinds" class="card-img">'),
    
    # ki-agenten
    ('<a href="/news/ki-agenten-2026.html" class="card">\n        <div class="card-image">\n          <<img src="/images/google-pixel-9-pro.jpg" alt="KI-Agenten 2026: Autonome Systeme, die deine Arbeit erledigen — MMOFinds" class="card-img">',
     '<a href="/news/ki-agenten-2026.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-ki-agenten.svg" alt="KI-Agenten 2026: Autonome Systeme, die deine Arbeit erledigen — MMOFinds" class="card-img">'),
    
    # ki-bildgenerierung
    ('<a href="/news/ki-bildgenerierung-2026.html" class="card">\n        <div class="card-image">\n          <<img src="/images/jbl-charge-5.jpg" alt="KI-Bildgenerierung 2026: Die besten Tools im Vergleich — MMOFinds" class="card-img">',
     '<a href="/news/ki-bildgenerierung-2026.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-ki-bildgenerierung.svg" alt="KI-Bildgenerierung 2026: Die besten Tools im Vergleich — MMOFinds" class="card-img">'),
    
    # ki-coding
    ('<a href="/news/ki-coding-2026.html" class="card">\n        <div class="card-image">\n        <img src="/images/apple-watch-series-10.jpg" alt="KI-Coding-Assistenten 2026: Der Vergleich — MMOFinds" class="card-img">',
     '<a href="/news/ki-coding-2026.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-ki-coding.svg" alt="KI-Coding-Assistenten 2026: Der Vergleich — MMOFinds" class="card-img">'),
    
    # ki-in-der-medizin
    ('<a href="/news/ki-in-der-medizin--früherkennung-von-krebs-mit-97--genauigkeit.html" class="card">\n        <div class="card-image">\n        <img src="/images/bose-quietcomfort-ultra.jpg" alt="KI in der Medizin: Früherkennung von Krebs mit 97% Genauigkeit" class="card-img">',
     '<a href="/news/ki-in-der-medizin--früherkennung-von-krebs-mit-97--genauigkeit.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-ki-medizin.svg" alt="KI in der Medizin: Früherkennung von Krebs mit 97% Genauigkeit" class="card-img">'),
    
    # ki-medizin-2026
    ('<a href="/news/ki-medizin-2026.html" class="card">\n        <div class="card-image">\n        <img src="/images/apple-watch-series-10.jpg" alt="KI in der Medizin 2026: Diagnose, Behandlung & Forschung — MMOFinds" class="card-img">',
     '<a href="/news/ki-medizin-2026.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-ki-medizin.svg" alt="KI in der Medizin 2026: Diagnose, Behandlung & Forschung — MMOFinds" class="card-img">'),
    
    # ki-roboter
    ('<a href="/news/ki-roboter-2026.html" class="card">\n        <div class="card-image">\n          <<img src="/images/nintendo-switch-2.jpg" alt="KI-Roboter 2026: humanoid Roboter im Alltag — MMOFinds" class="card-img">',
     '<a href="/news/ki-roboter-2026.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-ki-roboter.svg" alt="KI-Roboter 2026: humanoid Roboter im Alltag — MMOFinds" class="card-img">'),
    
    # ki-smartphones
    ('<a href="/news/ki-smartphones-2026.html" class="card">\n        <div class="card-image">\n        <img src="/images/roborock-s8.jpg" alt="KI in Smartphones 2026: Galaxy AI, Apple Intelligence & mehr — MMOFinds" class="card-img">',
     '<a href="/news/ki-smartphones-2026.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-ki-smartphones.svg" alt="KI in Smartphones 2026: Galaxy AI, Apple Intelligence & mehr — MMOFinds" class="card-img">'),
    
    # neue-ki-modelle
    ('<a href="/news/neue-ki-modelle-können-code-schreiben--der-schneller-ist-als-menschliche-entwickler.html" class="card">\n        <div class="card-image">\n        <img src="/images/google-pixel-9-pro.jpg" alt="Neue KI-Modelle können Code schreiben, der schneller ist als menschliche Entwickler" class="card-img">',
     '<a href="/news/neue-ki-modelle-können-code-schreiben--der-schneller-ist-als-menschliche-entwickler.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-ki-coding.svg" alt="Neue KI-Modelle können Code schreiben, der schneller ist als menschliche Entwickler" class="card-img">'),
    
    # neuralink
    ('<a href="/news/neuralink-mensch-test-2026.html" class="card">\n        <div class="card-image">\n          <<img src="/images/logitech-mx-master-3s.jpg" alt="Neuralink: Erster Patient steuert Computer mit Gedanken — MMOFinds" class="card-img">',
     '<a href="/news/neuralink-mensch-test-2026.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-neuralink.svg" alt="Neuralink: Erster Patient steuert Computer mit Gedanken — MMOFinds" class="card-img">'),
    
    # openai-gpt5
    ('<a href="/news/openai-startet-gpt-5-mit-revolutionären-multi-modal-fähigkeiten.html" class="card">\n        <div class="card-image">\n          <<img src="/images/canon-eos-r50.jpg" alt="OpenAI startet GPT-5 mit revolutionären Multi-Modal-Fähigkeiten" class="card-img">',
     '<a href="/news/openai-startet-gpt-5-mit-revolutionären-multi-modal-fähigkeiten.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-openai-gpt5.svg" alt="OpenAI startet GPT-5 mit revolutionären Multi-Modal-Fähigkeiten" class="card-img">'),
    
    # tesla-optimus
    ('<a href="/news/tesla-optimus-roboter-beeindruckt-mit-alltäglichen-fähigkeiten.html" class="card">\n        <div class="card-image">\n        <img src="/images/sony-alpha-7c-ii.jpg" alt="Tesla Optimus Roboter beeindruckt mit alltäglichen Fähigkeiten" class="card-img">',
     '<a href="/news/tesla-optimus-roboter-beeindruckt-mit-alltäglichen-fähigkeiten.html" class="card">\n        <div class="card-image">\n          <img src="/images/news-tesla-optimus.svg" alt="Tesla Optimus Roboter beeindruckt mit alltäglichen Fähigkeiten" class="card-img">'),
]

all_replacements = diy_replacements + news_replacements
total = 0
for old, new in all_replacements:
    if old in html:
        html = html.replace(old, new)
        total += 1
        print(f"  ✓ Replaced")
    else:
        # Try simpler pattern match
        # Extract the href to find it
        print(f"  ✗ NOT FOUND (trying simpler approach)")

with open('/root/mmofinds/index.html', 'w') as f:
    f.write(html)

print(f"\n✅ Total replacements: {total}")
