#!/usr/bin/env python3
import re

with open('/root/mmofinds/create_images.py', 'r') as f:
    content = f.read()

# Fix all remaining triple-quoted strings used as extra parameter values
# Pattern: '''<circle.../>''')  ->  extra="<circle.../>")
content = re.sub(r"'''([^']+)'''\s*\)", r'extra="\1")', content)

with open('/root/mmofinds/create_images.py', 'w') as f:
    f.write(content)

print('Fixed all triple-quote extra parameters')
