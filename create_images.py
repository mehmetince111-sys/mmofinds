#!/usr/bin/env python3
"""Generate beautiful SVG images for DIY and News cards."""
import os, json

IMG = "/root/mmofinds/images"

# All image definitions as JSON-like data
images = [
    # DIY Images
    {"file": "diy-ai-assistent-pi.svg", "bg1": "#0f1a0f", "bg2": "#1a2e1a", "accent": "#22c55e",
     "icon": '<circle cx="75" cy="75" r="40" fill="#22c55e" opacity="0.15"/><rect x="55" y="55" width="40" height="30" rx="5" fill="#22c55e" opacity="0.3"/><circle cx="75" cy="65" r="8" fill="#22c55e"/><rect x="60" y="90" width="30" height="4" rx="2" fill="#22c55e" opacity="0.4"/>',
     "title": "DIY Assistent", "tag": "DIY", "tag_color": "#22c55e",
     "extra": '<circle cx="680" cy="380" r="100" fill="#22c55e" opacity="0.02"/>'},
    
    {"file": "diy-ai-security-camera.svg", "bg1": "#0f1a2e", "bg2": "#1a2a3e", "accent": "#3b82f6",
     "icon": '<circle cx="75" cy="75" r="45" fill="none" stroke="#3b82f6" stroke-width="3" opacity="0.5"/><circle cx="75" cy="75" r="25" fill="#3b82f6" opacity="0.2"/><circle cx="75" cy="75" r="12" fill="#3b82f6" opacity="0.5"/>',
     "title": "Sicherheitskamera", "tag": "DIY", "tag_color": "#3b82f6",
     "extra": '<circle cx="700" cy="350" r="120" fill="#3b82f6" opacity="0.03"/>'},
    
    {"file": "diy-mechanical-keyboard.svg", "bg1": "#1a0f2e", "bg2": "#2e1a3e", "accent": "#a855f7",
     "icon": '<rect x="30" y="45" width="90" height="60" rx="8" fill="#a855f7" opacity="0.15"/><rect x="35" y="50" width="20" height="18" rx="3" fill="#a855f7" opacity="0.5"/><rect x="58" y="50" width="20" height="18" rx="3" fill="#a855f7" opacity="0.4"/><rect x="81" y="50" width="20" height="18" rx="3" fill="#a855f7" opacity="0.3"/><rect x="35" y="72" width="66" height="18" rx="3" fill="#a855f7" opacity="0.3"/>',
     "title": "Mech. Tastatur", "tag": "DIY", "tag_color": "#a855f7",
     "extra": '<circle cx="700" cy="120" r="80" fill="#a855f7" opacity="0.04"/>'},
    
    {"file": "diy-nas-raspberry-pi.svg", "bg1": "#0a1a2e", "bg2": "#0f2a3e", "accent": "#06b6d4",
     "icon": '<rect x="30" y="30" width="90" height="90" rx="8" fill="#06b6d4" opacity="0.1"/><rect x="30" y="30" width="90" height="90" rx="8" fill="none" stroke="#06b6d4" stroke-width="2" opacity="0.4"/><rect x="40" y="40" width="70" height="12" rx="3" fill="#06b6d4" opacity="0.2"/><rect x="40" y="58" width="70" height="12" rx="3" fill="#06b6d4" opacity="0.15"/><rect x="40" y="76" width="70" height="12" rx="3" fill="#06b6d4" opacity="0.15"/><circle cx="95" cy="46" r="4" fill="#06b6d4" opacity="0.6"/><circle cx="95" cy="62" r="4" fill="#06b6d4" opacity="0.4"/>',
     "title": "NAS Server", "tag": "DIY", "tag_color": "#06b6d4",
     "extra": '<circle cx="700" cy="350" r="130" fill="#06b6d4" opacity="0.03"/>'},
    
    {"file": "diy-smart-home-hub.svg", "bg1": "#2e1a0a", "bg2": "#3e2a0f", "accent": "#f59e0b",
     "icon": '<path d="M75 30 L120 65 L108 65 L108 120 L42 120 L42 65 L30 65 Z" fill="#f59e0b" opacity="0.15" stroke="#f59e0b" stroke-width="2" opacity="0.5"/><rect x="55" y="80" width="40" height="30" rx="4" fill="#f59e0b" opacity="0.2"/>',
     "title": "Smart Home Hub", "tag": "DIY", "tag_color": "#f59e0b",
     "extra": '<circle cx="700" cy="100" r="90" fill="#f59e0b" opacity="0.04"/>'},
    
    {"file": "diy-smart-mirror.svg", "bg1": "#2e0a1a", "bg2": "#3e0f2a", "accent": "#ec4899",
     "icon": '<rect x="40" y="25" width="70" height="100" rx="12" fill="none" stroke="#ec4899" stroke-width="2.5" opacity="0.5"/><rect x="48" y="35" width="54" height="75" rx="6" fill="#ec4899" opacity="0.08"/><rect x="65" y="105" width="20" height="6" rx="3" fill="#ec4899" opacity="0.3"/>',
     "title": "Smart Mirror", "tag": "DIY", "tag_color": "#ec4899",
     "extra": '<circle cx="700" cy="350" r="100" fill="#ec4899" opacity="0.03"/>'},
    
    # News Images
    {"file": "news-ai-sprachmodelle.svg", "bg1": "#1a0f2e", "bg2": "#2e1a3e", "accent": "#f97316",
     "icon": '<circle cx="75" cy="75" r="45" fill="#f97316" opacity="0.08"/><path d="M55 65 Q75 45 95 65 Q95 85 75 95 Q55 85 55 65Z" fill="none" stroke="#f97316" stroke-width="2.5" opacity="0.6"/><circle cx="65" cy="70" r="3" fill="#f97316" opacity="0.7"/><circle cx="85" cy="70" r="3" fill="#f97316" opacity="0.7"/>',
     "title": "KI-Sprachmodelle", "tag": "NEWS", "tag_color": "#f97316",
     "extra": '<circle cx="700" cy="350" r="120" fill="#f97316" opacity="0.03"/>'},
    
    {"file": "news-apple-intelligence.svg", "bg1": "#1a0f2e", "bg2": "#2e1a3e", "accent": "#f97316",
     "icon": '<path d="M75 35 C68 48 58 52 58 65 C58 75 65 85 75 85 C85 85 92 75 92 65 C92 52 82 48 75 35Z" fill="#f97316" opacity="0.7"/><line x1="65" y1="55" x2="85" y2="55" stroke="#fff" stroke-width="2" opacity="0.5" stroke-linecap="round"/>',
     "title": "Apple Intelligence", "tag": "NEWS", "tag_color": "#f97316",
     "extra": '<circle cx="680" cy="100" r="100" fill="#f97316" opacity="0.04"/>'},
    
    {"file": "news-deepmind-proteine.svg", "bg1": "#2e0a0a", "bg2": "#3e0f1a", "accent": "#ef4444",
     "icon": '<path d="M60 40 Q75 60 90 40 Q105 60 90 80 Q75 100 60 80 Q45 60 60 40Z" fill="none" stroke="#ef4444" stroke-width="2" opacity="0.5"/><circle cx="75" cy="65" r="5" fill="#ef4444" opacity="0.4"/><circle cx="60" cy="50" r="3" fill="#ef4444" opacity="0.3"/><circle cx="90" cy="50" r="3" fill="#ef4444" opacity="0.3"/><circle cx="60" cy="80" r="3" fill="#ef4444" opacity="0.3"/><circle cx="90" cy="80" r="3" fill="#ef4444" opacity="0.3"/>',
     "title": "DeepMind Proteine", "tag": "NEWS", "tag_color": "#ef4444",
     "extra": '<circle cx="700" cy="350" r="130" fill="#ef4444" opacity="0.03"/>'},
    
    {"file": "news-ki-agenten.svg", "bg1": "#1a1a0f", "bg2": "#2e2e1a", "accent": "#f97316",
     "icon": '<circle cx="75" cy="55" r="18" fill="#f97316" opacity="0.2"/><circle cx="75" cy="55" r="10" fill="#f97316" opacity="0.4"/><circle cx="75" cy="55" r="4" fill="#f97316"/><line x1="75" y1="73" x2="75" y2="95" stroke="#f97316" stroke-width="2.5" opacity="0.5"/><line x1="55" y1="80" x2="95" y2="80" stroke="#f97316" stroke-width="2.5" stroke-linecap="round" opacity="0.5"/>',
     "title": "KI-Agenten", "tag": "NEWS", "tag_color": "#f97316",
     "extra": '<circle cx="700" cy="100" r="100" fill="#f97316" opacity="0.03"/>'},
    
    {"file": "news-ki-bildgenerierung.svg", "bg1": "#2e0a1a", "bg2": "#3e0f2a", "accent": "#ec4899",
     "icon": '<rect x="30" y="30" width="90" height="80" rx="8" fill="#ec4899" opacity="0.1"/><rect x="30" y="30" width="90" height="80" rx="8" fill="none" stroke="#ec4899" stroke-width="2" opacity="0.4"/><circle cx="55" cy="55" r="8" fill="#ec4899" opacity="0.3"/><path d="M30 80 L55 60 L75 75 L95 50 L120 70 L120 110 L30 110Z" fill="#ec4899" opacity="0.15"/>',
     "title": "KI-Bildgenerierung", "tag": "NEWS", "tag_color": "#ec4899",
     "extra": '<circle cx="700" cy="350" r="110" fill="#ec4899" opacity="0.03"/>'},
    
    {"file": "news-ki-coding.svg", "bg1": "#1a0f2e", "bg2": "#2e1a3e", "accent": "#f97316",
     "icon": '<text x="35" y="55" font-family="monospace" font-size="24" font-weight="bold" fill="#f97316" opacity="0.8">&lt;/&gt;</text><text x="35" y="78" font-family="monospace" font-size="10" fill="#f97316" opacity="0.4">const ai = await</text><text x="35" y="93" font-family="monospace" font-size="10" fill="#f97316" opacity="0.3">  generate({code});</text>',
     "title": "KI-Coding", "tag": "NEWS", "tag_color": "#f97316",
     "extra": '<circle cx="700" cy="100" r="120" fill="#f97316" opacity="0.03"/>'},
    
    {"file": "news-ki-medizin.svg", "bg1": "#0a2e1a", "bg2": "#0f3e2a", "accent": "#10b981",
     "icon": '<rect x="55" y="30" width="40" height="80" rx="5" fill="#10b981" opacity="0.15"/><rect x="30" y="55" width="90" height="30" rx="5" fill="#10b981" opacity="0.15"/><path d="M60 70 L80 70 M70 60 L70 80" stroke="#10b981" stroke-width="3.5" stroke-linecap="round" opacity="0.7"/>',
     "title": "KI in der Medizin", "tag": "NEWS", "tag_color": "#10b981",
     "extra": '<circle cx="700" cy="350" r="130" fill="#10b981" opacity="0.03"/>'},
    
    {"file": "news-ki-roboter.svg", "bg1": "#1a1a0f", "bg2": "#2e2e1a", "accent": "#f97316",
     "icon": '<circle cx="75" cy="40" r="15" fill="#f97316" opacity="0.2"/><circle cx="75" cy="40" r="15" fill="none" stroke="#f97316" stroke-width="2" opacity="0.4"/><circle cx="68" cy="37" r="3" fill="#f97316" opacity="0.6"/><circle cx="82" cy="37" r="3" fill="#f97316" opacity="0.6"/><rect x="55" y="58" width="40" height="45" rx="5" fill="#f97316" opacity="0.15"/><rect x="55" y="58" width="40" height="45" rx="5" fill="none" stroke="#f97316" stroke-width="2" opacity="0.4"/>',
     "title": "KI-Roboter", "tag": "NEWS", "tag_color": "#f97316",
     "extra": '<circle cx="700" cy="100" r="100" fill="#f97316" opacity="0.03"/>'},
    
    {"file": "news-ki-smartphones.svg", "bg1": "#1a1a0f", "bg2": "#2e2e1a", "accent": "#f97316",
     "icon": '<rect x="55" y="20" width="40" height="95" rx="12" fill="#f97316" opacity="0.12"/><rect x="55" y="20" width="40" height="95" rx="12" fill="none" stroke="#f97316" stroke-width="2" opacity="0.4"/><circle cx="75" cy="105" r="4" fill="#f97316" opacity="0.3"/><rect x="62" y="30" width="26" height="60" rx="3" fill="#f97316" opacity="0.08"/>',
     "title": "KI in Smartphones", "tag": "NEWS", "tag_color": "#f97316",
     "extra": '<circle cx="700" cy="350" r="120" fill="#f97316" opacity="0.03"/>'},
    
    {"file": "news-ki-chip-morinica.svg", "bg1": "#2e1a0a", "bg2": "#3e2a0f", "accent": "#f59e0b",
     "icon": '<rect x="45" y="35" width="60" height="60" rx="6" fill="#f59e0b" opacity="0.12"/><rect x="45" y="35" width="60" height="60" rx="6" fill="none" stroke="#f59e0b" stroke-width="2" opacity="0.4"/><rect x="55" y="45" width="40" height="40" rx="3" fill="#f59e0b" opacity="0.2"/><line x1="45" y1="50" x2="35" y2="50" stroke="#f59e0b" stroke-width="2" opacity="0.3"/><line x1="45" y1="65" x2="35" y2="65" stroke="#f59e0b" stroke-width="2" opacity="0.3"/><line x1="45" y1="80" x2="35" y2="80" stroke="#f59e0b" stroke-width="2" opacity="0.3"/><line x1="105" y1="50" x2="115" y2="50" stroke="#f59e0b" stroke-width="2" opacity="0.3"/><line x1="105" y1="65" x2="115" y2="65" stroke="#f59e0b" stroke-width="2" opacity="0.3"/><line x1="105" y1="80" x2="115" y2="80" stroke="#f59e0b" stroke-width="2" opacity="0.3"/>',
     "title": "KI-Chip Morinica", "tag": "NEWS", "tag_color": "#f59e0b",
     "extra": '<circle cx="700" cy="350" r="100" fill="#f59e0b" opacity="0.03"/>'},
    
    {"file": "news-neuralink.svg", "bg1": "#1a1a0f", "bg2": "#2e2e1a", "accent": "#f97316",
     "icon": '<circle cx="75" cy="75" r="40" fill="none" stroke="#f97316" stroke-width="1.5" opacity="0.15"/><circle cx="75" cy="75" r="25" fill="none" stroke="#f97316" stroke-width="1.5" opacity="0.25"/><circle cx="75" cy="75" r="10" fill="#f97316" opacity="0.2"/><circle cx="75" cy="75" r="4" fill="#f97316"/><path d="M75 35 Q90 55 75 75 Q60 95 75 115" fill="none" stroke="#f97316" stroke-width="2" opacity="0.4"/><path d="M35 75 Q55 60 75 75 Q95 90 115 75" fill="none" stroke="#f97316" stroke-width="2" opacity="0.4"/>',
     "title": "Neuralink", "tag": "NEWS", "tag_color": "#f97316",
     "extra": '<circle cx="700" cy="100" r="110" fill="#f97316" opacity="0.03"/>'},
    
    {"file": "news-openai-gpt5.svg", "bg1": "#1a1a0f", "bg2": "#2e2e1a", "accent": "#f97316",
     "icon": '<text x="30" y="55" font-family="system-ui,sans-serif" font-size="28" font-weight="900" fill="#f97316" opacity="0.85">GPT</text><text x="30" y="90" font-family="system-ui,sans-serif" font-size="24" font-weight="900" fill="#f97316" opacity="0.45">5</text><circle cx="100" cy="45" r="20" fill="#f97316" opacity="0.08"/><circle cx="100" cy="45" r="12" fill="#f97316" opacity="0.12"/>',
     "title": "OpenAI GPT-5", "tag": "NEWS", "tag_color": "#f97316",
     "extra": '<circle cx="700" cy="350" r="120" fill="#f97316" opacity="0.03"/>'},
    
    {"file": "news-tesla-optimus.svg", "bg1": "#2e0a0a", "bg2": "#3e0f1a", "accent": "#ef4444",
     "icon": '<circle cx="75" cy="38" r="16" fill="#ef4444" opacity="0.15"/><circle cx="75" cy="38" r="16" fill="none" stroke="#ef4444" stroke-width="2" opacity="0.4"/><circle cx="68" cy="35" r="3" fill="#ef4444" opacity="0.6"/><circle cx="82" cy="35" r="3" fill="#ef4444" opacity="0.6"/><rect x="55" y="56" width="40" height="40" rx="5" fill="#ef4444" opacity="0.12"/><rect x="55" y="56" width="40" height="40" rx="5" fill="none" stroke="#ef4444" stroke-width="2" opacity="0.35"/>',
     "title": "Tesla Optimus", "tag": "NEWS", "tag_color": "#ef4444",
     "extra": '<circle cx="700" cy="100" r="100" fill="#ef4444" opacity="0.03"/>'},
]


def make_svg(img):
    """Create a beautiful SVG image."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{img['bg1']}"/>
      <stop offset="100%" style="stop-color:{img['bg2']}"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="40%" r="60%">
      <stop offset="0%" style="stop-color:{img['accent']};stop-opacity:0.15"/>
      <stop offset="100%" style="stop-color:{img['accent']};stop-opacity:0"/>
    </radialGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="0.4"/>
    </filter>
  </defs>
  <rect width="800" height="450" fill="url(#bg)" rx="8"/>
  <rect width="800" height="450" fill="url(#glow)"/>
  <g opacity="0.025" stroke="#fff" stroke-width="0.5">
    <line x1="0" y1="0" x2="800" y2="0"/><line x1="0" y1="75" x2="800" y2="75"/>
    <line x1="0" y1="150" x2="800" y2="150"/><line x1="0" y1="225" x2="800" y2="225"/>
    <line x1="0" y1="300" x2="800" y2="300"/><line x1="0" y1="375" x2="800" y2="375"/>
    <line x1="0" y1="450" x2="800" y2="450"/>
    <line x1="0" y1="0" x2="0" y2="450"/><line x1="100" y1="0" x2="100" y2="450"/>
    <line x1="200" y1="0" x2="200" y2="450"/><line x1="300" y1="0" x2="300" y2="450"/>
    <line x1="400" y1="0" x2="400" y2="450"/><line x1="500" y1="0" x2="500" y2="450"/>
    <line x1="600" y1="0" x2="600" y2="450"/><line x1="700" y1="0" x2="700" y2="450"/>
  </g>
  <g transform="translate(55, 70)" filter="url(#shadow)">
    <circle cx="75" cy="75" r="75" fill="{img['accent']}" opacity="0.1"/>
  </g>
  <g transform="translate(55, 70)">{img['icon']}</g>
  <text x="190" y="120" font-family="system-ui,-apple-system,sans-serif" font-size="32" font-weight="800" fill="#fff" letter-spacing="-0.5">{img['title']}</text>
  <rect x="40" y="385" width="720" height="3" rx="1.5" fill="{img['accent']}" opacity="0.4"/>
  <rect x="40" y="395" width="80" height="28" rx="14" fill="{img['tag_color']}" opacity="0.2"/>
  <text x="80" y="414" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="12" font-weight="700" fill="{img['tag_color']}" text-transform="uppercase" letter-spacing="1">{img['tag']}</text>
  {img['extra']}
</svg>'''
    filepath = os.path.join(IMG, img['file'])
    with open(filepath, 'w') as f:
        f.write(svg)
    print(f"  ✓ {img['file']}")


print("=== GENERATING IMAGES ===\n")
for img in images:
    make_svg(img)

print(f"\n✅ {len(images)} Bilder erstellt!")
