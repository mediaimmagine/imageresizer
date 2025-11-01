#!/usr/bin/env python3
"""
Detailed WordPress REST API test - checks capabilities and permissions
"""

import requests

WP_SITE_URL = "https://udineoggi.news"
WP_USERNAME = "goriziaNews"  # Username WordPress
WP_APP_PASSWORD = "E7RP LRzc mGBc aUNQ 4kd3 N2m6"  # Application Password (nome: COED Image Resizer)

print("=" * 60)
print("Detailed WordPress REST API Test")
print("=" * 60)
print()

# Test 1: Check if we can get user info
print("Test 1: Getting user information...")
try:
    user_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/users/me"
    resp = requests.get(user_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
    
    if resp.status_code == 200:
        user_data = resp.json()
        print("✓ User authenticated successfully!")
        print(f"  User ID: {user_data.get('id')}")
        print(f"  Username: {user_data.get('slug')}")
        print(f"  Name: {user_data.get('name')}")
        print(f"  Email: {user_data.get('email', 'N/A')}")
        
        # Check capabilities if available
        if 'capabilities' in user_data:
            caps = user_data['capabilities']
            print(f"  Capabilities: {list(caps.keys())[:10]}...")  # First 10
        
        # Check meta for capabilities
        if 'meta' in user_data and isinstance(user_data['meta'], dict):
            if 'capabilities' in user_data['meta']:
                meta_caps = user_data['meta']['capabilities']
                print(f"  Meta Capabilities: {list(meta_caps.keys())[:10]}...")
        
        print()
    else:
        print(f"✗ Failed to get user info: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
        print()
except Exception as e:
    print(f"✗ Error: {e}")
    print()

# Test 2: Try to access media endpoint with different methods
print("Test 2: Testing media endpoint access...")
try:
    media_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media"
    
    # Try GET first
    print("  Trying GET request...")
    resp = requests.get(media_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10, params={'per_page': 1})
    print(f"  GET Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print("  ✓ GET request successful - can read media library")
        data = resp.json()
        total = resp.headers.get('X-WP-Total', 0)
        print(f"  Total media items: {total}")
    elif resp.status_code == 401:
        print("  ✗ GET returned 401 - authentication issue")
    elif resp.status_code == 403:
        print("  ✗ GET returned 403 - permission issue")
    else:
        print(f"  ⚠ GET returned {resp.status_code}")
    
    print()
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    print()

# Test 3: Check what capabilities are needed
print("Test 3: Checking available endpoints...")
try:
    types_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/types"
    resp = requests.get(types_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
    
    if resp.status_code == 200:
        types_data = resp.json()
        print("✓ Can access post types endpoint")
        if 'attachment' in types_data:
            attachment = types_data['attachment']
            print(f"  Media endpoint info:")
            print(f"    REST Base: {attachment.get('rest_base')}")
            print(f"    Capabilities: {attachment.get('capabilities', {})}")
    else:
        print(f"✗ Cannot access types: {resp.status_code}")
    print()
except Exception as e:
    print(f"✗ Error: {e}")
    print()

# Test 4: Try upload with more detailed error checking
print("Test 4: Attempting upload with detailed error analysis...")
try:
    from PIL import Image
    import io
    
    test_img = Image.new('RGB', (10, 10), color='white')
    img_buffer = io.BytesIO()
    test_img.save(img_buffer, format='JPEG')
    img_data = img_buffer.getvalue()
    
    media_post_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media"
    files = {'file': ('test.jpg', img_data, 'image/jpeg')}
    
    print("  Uploading test image...")
    resp = requests.post(media_post_url, 
                        auth=(WP_USERNAME, WP_APP_PASSWORD),
                        files=files,
                        timeout=15)
    
    print(f"  Status: {resp.status_code}")
    
    if resp.status_code == 201:
        print("  ✓✓✓ UPLOAD SUCCESSFUL! ✓✓✓")
        data = resp.json()
        print(f"  Media ID: {data.get('id')}")
    else:
        print(f"  ✗ Upload failed")
        print(f"  Full response:")
        print(f"  {resp.text[:500]}")
        
        # Try to parse error
        try:
            error_data = resp.json()
            if 'code' in error_data:
                print(f"  Error code: {error_data['code']}")
            if 'message' in error_data:
                print(f"  Error message: {error_data['message']}")
        except:
            pass
    
except ImportError:
    print("  Skipping (PIL not available)")
except Exception as e:
    print(f"  ✗ Error: {e}")

print()
print("=" * 60)

