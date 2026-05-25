#!/usr/bin/env python3
"""Generate SVG images for DIY and News cards on the homepage."""

import os

IMG_DIR = "/root/mmofinds/images"

def generate_svg(filename, title, icon, accent_color, bg_color="#1a2332", tag_text="BILD"):
    """Generate a themed SVG image."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f1923;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{accent_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1e3a5f;stop-opacity:1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="800" height="450" fill="url(#bg)" rx="12"/>
  <circle cx="650" cy="80" r="120" fill="{accent_color}" opacity="0.06"/>
  <circle cx="700" cy="400" r="80" fill="{accent_color}" opacity="0.04"/>
  <g transform="translate(40, 50)">
    <rect width="100" height="100" rx="20" fill="{accent_color}" opacity="0.15"/>
    <text x="50" y="65" text-anchor="middle" font-size="50">{icon}</text>
  </g>
  <text x="160" y="100" font-family="system-ui, -apple-system, sans-serif" font-size="28" font-weight="700" fill="#ffffff">{title}</text>
  <rect x="40" y="380" width="100" height="30" rx="15" fill="{accent_color}" opacity="0.2"/>
  <text x="90" y="400" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="600" fill="{accent_color}" text-transform="uppercase">{tag_text}</text>
</svg>'''
    filepath = os.path.join(IMG_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(svg)
    return filepath

# ─── DIY IMAGES ───
diy_images = [
    ("diy-ai-assistent-pi.svg",     "KI-Assistent",         "🤖",     "#22c55e"),
    ("diy-ai-security-camera.svg",  "Sicherheitskamera",    "📷",     "#3b82f6"),
    ("diy-mechanical-keyboard.svg", "Mech. Tastatur",       "⌨️",     "#a855f7"),
    ("diy-nas-raspberry-pi.svg",    "NAS Server",           "💾",     "#06b6d4"),
    ("diy-smart-home-hub.svg",      "Smart Home Hub",       "🏠",     "#f59e0b"),
    ("diy-smart-mirror.svg",        "Smart Mirror",         "🪞",     "#ec4899"),
]

# ─── NEWS IMAGES ───
news_images = [
    ("news-ai-sprachmodelle.svg",       "KI-Sprachmodelle",    "💬",     "#f97316"),
    ("news-apple-intelligence.svg",     "Apple Intelligence",  "🍎",     "#f97316"),
    ("news-deepmind-proteine.svg",      "DeepMind Proteine",   "🧬",     "#ef4444"),
    ("news-ki-agenten.svg",             "KI-Agenten",          "🧠",     "#f97316"),
    ("news-ki-bildgenerierung.svg",     "KI-Bildgenerierung",  "🎨",     "#ec4899"),
    ("news-ki-coding.svg",              "KI-Coding",           "💻",     "#f97316"),
    ("news-ki-medizin.svg",             "KI in der Medizin",   "🏥",     "#10b981"),
    ("news-ki-roboter.svg",             "KI-Roboter",          "🦾",     "#f97316"),
    ("news-ki-smartphones.svg",         "KI in Smartphones",   "📱",     "#f97316"),
    ("news-ki-chip-morinica.svg",       "KI-Chip Morinica",    "⚡",     "#f59e0b"),
    ("news-neuralink.svg",              "Neuralink",           "🧠",     "#f97316"),
    ("news-openai-gpt5.svg",            "OpenAI GPT-5",        "🚀",     "#f97316"),
    ("news-tesla-optimus.svg",          "Tesla Optimus",       "🤖",     "#ef4444"),
]

print("=== DIY IMAGES ===")
for fn, title, icon, accent in diy_images:
    fp = generate_svg(fn, title, icon, accent, tag_text="DIY")
    print(f"  ✓ {fn}")

print("\n=== NEWS IMAGES ===")
for fn, title, icon, accent in news_images:
    fp = generate_svg(fn, title, icon, accent)
    print(f"  ✓ {fn}")

print(f"\n✅ {len(diy_images) + len(news_images)} Bilder erstellt!")
