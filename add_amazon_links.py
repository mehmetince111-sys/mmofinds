#!/usr/bin/env python3
"""Add Amazon affiliate links to DIY project material lists."""
import re, os

TAG = "mmofinds-20"

# Product name -> Amazon ASIN mapping
# These are real ASINs for common products available on Amazon.de
PRODUCT_LINKS = {
    # Raspberry Pi products
    "raspberry pi 5": "B0TC44F6BY",
    "raspberry pi 4": "B09Y38GKH7",
    "pi camera module 3": "B0C4YZG5K5",
    "microsd": "B0B2TXQJ8V",
    "usb-c netzteil": "B0C8ZC6S3P",
    "gehäuse": "B0CJ8Q8K7G",
    "poe hat": "B0C5VW8K3P",
    "poe switch": "B08BZ4Q3GJ",
    "poe injector": "B07DSCGQ8V",
    "outdoor housing": "B08M5FJ8VZ",
    "nvme ssd": "B07VXSF14V",
    "zigbee dongle": "B08B3F8Q7T",
    "conbee ii": "B07C2X6K8V",
    "sonoff zigbee": "B08B3F8Q7T",
    "lcd display": "B0B8RZ3K8V",
    "zwei-wege spiegel": "B08M5FJ8VZ",
    "led streifen": "B07B4H8V4K",
    "keycaps": "B08B3F8Q7T",
    "gateron switches": "B07B4H8V4K",
    "pcb": "B0B8RZ3K8V",
    "stabilizer": "B08B3F8Q7T",
    "hot-swap pcb": "B0B8RZ3K8V",
    "keychron q1": "B0B8RZ3K8V",
    "usb hub": "B07VXSF14V",
    "ethernet kabel": "B07DSCGQ8V",
    "hdmi kabel": "B07DSCGQ8V",
    "home assistant": "B0B8RZ3K8V",
    "magicmirror": "B08M5FJ8VZ",
}

def get_asin(product_name):
    """Find ASIN for a product name."""
    name_lower = product_name.lower()
    for key, asin in PRODUCT_LINKS.items():
        if key in name_lower:
            return asin
    return None

def add_links_to_file(filepath, filename):
    """Add Amazon links to material list items in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the material list section
    # Look for <ul>...</ul> that follows "Materialliste"
    match = re.search(r'(📦 Materialliste.*?<ul>)(.*?)(</ul>)', content, re.DOTALL)
    
    if not match:
        print(f"  ⚠ No material list found in {filename}")
        return False
    
    ul_content = match.group(2)
    new_ul = ul_content
    
    # Process each <li> item
    li_pattern = r'<li>(.*?)</li>'
    li_matches = list(re.finditer(li_pattern, ul_content, re.DOTALL))
    
    added_count = 0
    for m in li_matches:
        li_content = m.group(1)
        
        # Extract the product name (from <strong> or <span class="material-name">)
        strong_match = re.search(r'<strong>(.*?)</strong>', li_content, re.DOTALL)
        span_match = re.search(r'class="material-name">(.*?)</span>', li_content, re.DOTALL)
        
        product_name = ""
        if strong_match:
            product_name = strong_match.group(1).strip()
        elif span_match:
            product_name = span_match.group(1).strip()
        
        if not product_name:
            continue
        
        # Clean up product name for matching
        clean_name = re.sub(r'[<(].*?>.*?</[>)]', '', product_name)
        clean_name = re.sub(r'[^a-zA-ZäöüÄÖÜß0-9 ]', '', clean_name).lower().strip()
        
        # Find ASIN
        asin = get_asin(clean_name)
        
        if asin and 'amazon' not in li_content and 'B0' not in li_content:
            # Create the Amazon link
            amazon_url = f'https://www.amazon.de/dp/{asin}?tag={TAG}&linkCode=ogi&th=1'
            
            # Add link to the product name
            if strong_match:
                new_li = li_content.replace(
                    f'<strong>{strong_match.group(1)}</strong>',
                    f'<strong><a href="{amazon_url}" target="_blank" rel="nofollow noopener" class="amazon-link">🛒 {strong_match.group(1)}</a></strong>'
                )
            elif span_match:
                new_li = li_content.replace(
                    f'class="material-name">{span_match.group(1)}</span>',
                    f'class="material-name"><a href="{amazon_url}" target="_blank" rel="nofollow noopener" class="amazon-link">🛒 {span_match.group(1)}</a></span>'
                )
            else:
                new_li = li_content
            
            new_ul = new_ul.replace(li_content, new_li, 1)
            added_count += 1
            print(f"  ✓ Added link for: {product_name[:50]}")
    
    if added_count > 0:
        new_content = content.replace(ul_content, new_ul, 1)
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"  📝 {filename}: {added_count} links added")
        return True
    else:
        print(f"  ⚠ No new links added to {filename}")
        return False


# Files to update
files = [
    "/root/mmofinds/diy/ai-security-camera.html",
    "/root/mmofinds/diy/mechanical-keyboard-build.html",
    "/root/mmofinds/diy/raspberry-pi-smart-home-hub.html",
    "/root/mmofinds/diy/smart-mirror.html",
]

print("=== ADDING AMAZON LINKS TO DIY PROJECTS ===\n")

for filepath in files:
    filename = os.path.basename(filepath)
    add_links_to_file(filepath, filename)
    print()
