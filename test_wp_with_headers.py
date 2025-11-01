#!/usr/bin/env python3
"""
Test upload with explicit headers to see if that helps
"""

import requests
from PIL import Image
import io

WP_SITE_URL = "https://udineoggi.news"
WP_USERNAME = "goriziaNews"  # Username WordPress
WP_APP_PASSWORD = "E7RP LRzc mGBc aUNQ 4kd3 N2m6"  # Application Password (nome: COED Image Resizer)

print("Testing upload with explicit headers...")
print()

# Create test image
test_img = Image.new('RGB', (10, 10), color='white')
img_buffer = io.BytesIO()
test_img.save(img_buffer, format='JPEG')
img_data = img_buffer.getvalue()

# Try upload with explicit headers
media_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media"
files = {'file': ('test.jpg', img_data, 'image/jpeg')}
headers = {
    'Content-Disposition': 'attachment; filename="test.jpg"',
    'Content-Type': 'image/jpeg'
}

print("Attempt 1: Standard upload")
resp1 = requests.post(media_url, 
                     auth=(WP_USERNAME, WP_APP_PASSWORD),
                     files=files,
                     timeout=15)
print(f"Status: {resp1.status_code}")
if resp1.status_code != 201:
    print(f"Error: {resp1.text[:300]}")
print()

# Try with Content-Type in data instead
print("Attempt 2: With Content-Type header")
resp2 = requests.post(media_url,
                     auth=(WP_USERNAME, WP_APP_PASSWORD),
                     files=files,
                     headers=headers,
                     timeout=15)
print(f"Status: {resp2.status_code}")
if resp2.status_code != 201:
    print(f"Error: {resp2.text[:300]}")
print()

# Check what WordPress expects
print("Checking WordPress media endpoint schema...")
schema_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media?context=edit"
schema_resp = requests.get(schema_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
print(f"Schema endpoint status: {schema_resp.status_code}")
if schema_resp.status_code == 200:
    print("✓ Can access edit context - user has edit permissions")
else:
    print(f"✗ Cannot access edit context: {schema_resp.status_code}")

