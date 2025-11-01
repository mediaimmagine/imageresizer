#!/usr/bin/env python3
"""
Direct upload test - tests POST to media endpoint (what we actually use)
"""

import requests
from PIL import Image
import io

WP_SITE_URL = "https://udineoggi.news"
WP_USERNAME = "goriziaNews"  # Username WordPress
WP_APP_PASSWORD = "E7RP LRzc mGBc aUNQ 4kd3 N2m6"  # Application Password (nome: COED Image Resizer)

print("=" * 60)
print("Direct Upload Test (POST to /wp-json/wp/v2/media)")
print("=" * 60)
print(f"Site: {WP_SITE_URL}")
print(f"Username: {WP_USERNAME}")
print()

# Create a tiny test image
print("Creating test image...")
test_img = Image.new('RGB', (10, 10), color='white')
img_buffer = io.BytesIO()
test_img.save(img_buffer, format='JPEG', quality=95)
img_data = img_buffer.getvalue()
print(f"Test image size: {len(img_data)} bytes")
print()

# Try to upload
media_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media"
files = {'file': ('test_upload.jpg', img_data, 'image/jpeg')}
data = {'title': 'Test Upload from Image Resizer'}

print("Attempting upload to WordPress media library...")
print(f"Endpoint: {media_url}")
print()

try:
    resp = requests.post(media_url, 
                        auth=(WP_USERNAME, WP_APP_PASSWORD),
                        files=files,
                        data=data,
                        timeout=15)
    
    print(f"Response Status: {resp.status_code}")
    print()
    
    if resp.status_code == 201:
        print("✓✓✓ UPLOAD SUCCESSFUL! ✓✓✓")
        print()
        upload_data = resp.json()
        media_id = upload_data.get('id')
        media_url_result = upload_data.get('source_url') or upload_data.get('link') or upload_data.get('url')
        
        print(f"Media ID: {media_id}")
        print(f"Media URL: {media_url_result}")
        print()
        
        # Try to delete the test image
        print("Cleaning up test image...")
        delete_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media/{media_id}?force=true"
        del_resp = requests.delete(delete_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
        if del_resp.status_code == 200:
            print("✓ Test image deleted successfully")
        else:
            print(f"⚠ Could not delete test image (ID: {media_id})")
            print("  You may want to delete it manually from WordPress media library")
        
        print()
        print("=" * 60)
        print("SUCCESS! The Image Resizer app should work correctly.")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Open Image Resizer app")
        print("2. Go to WordPress → Settings...")
        print("3. Edit 'Udine Oggi' site")
        print("4. Enter credentials:")
        print(f"   Username: {WP_USERNAME}")
        print(f"   Application Password: {WP_APP_PASSWORD}")
        print("5. Save and try uploading an image!")
        
    elif resp.status_code == 401:
        print("✗ Authentication failed (401)")
        print()
        print("Possible issues:")
        print("- Username or Application Password incorrect")
        print("- Application Password not created correctly in WordPress")
        print("- Extra spaces in credentials")
        print()
        print("Response:", resp.text[:300])
        
    elif resp.status_code == 403:
        print("✗ Access forbidden (403)")
        print()
        print("Possible issues:")
        print("- REST API still blocked by security plugin")
        print("- User doesn't have 'upload_files' permission")
        print("- Cache not cleared after WP Cerber changes")
        print()
        print("Try:")
        print("1. Clear WP Cerber cache")
        print("2. Verify user has Editor or Administrator role")
        print("3. Check WP Cerber → Activity → Logs for blocked requests")
        print()
        print("Response:", resp.text[:300])
        
    elif resp.status_code == 413:
        print("✗ File too large (413)")
        print("(Unusual for a 10x10 image)")
        
    else:
        print(f"✗ Unexpected status code: {resp.status_code}")
        print()
        print("Response:", resp.text[:500])
        
except requests.exceptions.ConnectionError as e:
    print(f"✗ Connection error: {e}")
    print("Check your internet connection and site URL")
    
except requests.exceptions.Timeout:
    print("✗ Request timed out")
    print("The site may be slow or unresponsive")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

