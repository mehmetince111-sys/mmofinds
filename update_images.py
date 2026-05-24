#!/usr/bin/env python3
"""Update review-hero-image src in all HTML files with Amazon product images."""

import re
import os

# Mapping: product_file -> amazon_image_url
product_images = {
    'sony-wh-1000xm5.html': 'https://m.media-amazon.com/images/I/61vJtKbAssL._AC_SX679_.jpg',
    'sony-wh1000xm4.html': 'https://m.media-amazon.com/images/I/71A9daPY+DL._AC_SX522_.jpg',
    'apple-airpods-pro-2.html': 'https://m.media-amazon.com/images/I/61SUj2aKoEL._AC_SX522_.jpg',
    'bose-quietcomfort-ultra.html': 'https://m.media-amazon.com/images/I/51ZR4lyxBHL._AC_SX522_.jpg',
    'canon-eos-r50.html': 'https://m.media-amazon.com/images/I/71mGk4WKh+L._AC_SX569_.jpg',
    'dyson-v15-detect.html': 'https://m.media-amazon.com/images/I/61LsOhLYNTL._AC_SX569_.jpg',
    'google-pixel-9-pro.html': 'https://m.media-amazon.com/images/I/517Jv7f6mRL._AC_SX679_.jpg',
    'ipad-air-m3.html': 'https://m.media-amazon.com/images/I/71OTzAMXQhL._AC_SX425_.jpg',
    'iphone-16-pro.html': 'https://m.media-amazon.com/images/I/614Eylbj5vL._AC_SX522_.jpg',
    'jbl-charge-5.html': 'https://m.media-amazon.com/images/I/61qMO3TS2RL._AC_SX522_.jpg',
    'kindle-paperwhite-2024.html': 'https://m.media-amazon.com/images/I/61JHHWFLArL._AC_SX569_.jpg',
    'logitech-mx-master-3s.html': 'https://m.media-amazon.com/images/I/618IJzC-fFL._AC_SX522_.jpg',
    'macbook-air-m4.html': 'https://m.media-amazon.com/images/I/71sQdN4lfYL._AC_SX425_.jpg',
    'nintendo-switch-2.html': 'https://m.media-amazon.com/images/I/717JrHodikL._SX466_.jpg',
    'playstation-5-pro.html': 'https://m.media-amazon.com/images/I/51dfg52K-cL._SX522_.jpg',
    'roborock-s8.html': 'https://m.media-amazon.com/images/I/71ZCXAWP1uL._AC_SX569_.jpg',
    'samsung-galaxy-s25-ultra.html': 'https://m.media-amazon.com/images/I/61q4u3Z+kkL._AC_SX679_.jpg',
    'samsung-galaxy-watch-7.html': 'https://m.media-amazon.com/images/I/715I+LEEfkL._AC_SX679_.jpg',
    'apple-watch-series-10.html': 'https://m.media-amazon.com/images/I/61NZWMhyHbL._AC_SX679_.jpg',
    'sony-alpha-7c-ii.html': 'https://m.media-amazon.com/images/I/91QmCUEChcL._AC_SX569_.jpg',
}

pages_dir = '/root/mmofinds/pages'
updated = 0
failed = 0

for filename, amazon_url in product_images.items():
    filepath = os.path.join(pages_dir, filename)
    if not os.path.exists(filepath):
        print(f"SKIP: {filename} not found")
        failed += 1
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find img tags with class="review-hero-image" and replace their src attribute
    # Use a function-based replacement to handle any attribute order
    def replace_hero_src(match):
        full_tag = match.group(0)
        # Replace any src="..." with the Amazon URL
        new_tag = re.sub(
            r'(src\s*=\s*)"[^"]*"',
            lambda s: f'{s.group(1)}"{amazon_url}"',
            full_tag
        )
        return new_tag
    
    # Match <img ...> tags that contain class="review-hero-image"
    pattern = r'<img\b[^>]*class="review-hero-image"[^>]*>'
    
    new_content = re.sub(pattern, replace_hero_src, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"UPDATED: {filename}")
        updated += 1
    else:
        print(f"NO CHANGE: {filename}")
        failed += 1

print(f"\nDone! {updated} updated, {failed} failed")
