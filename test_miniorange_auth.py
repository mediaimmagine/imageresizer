#!/usr/bin/env python3
"""
Test script to debug MiniOrange authentication for Trieste News
"""

import requests
from requests.auth import HTTPBasicAuth
import json

# Credentials from settings (must use www for MiniOrange)
site_url = "https://www.triesteallnews.it"
# Use Client ID as username (per MiniOrange documentation)
username_wp = "redazioneTriesteallnews"  # WordPress user (for reference)
username_client_id = "61kgHITprXR2"  # Use this as Basic Auth username
password = "GZ8706mxMfgMitqVnD3uBpf1"  # Client Secret

# Use Client ID as username (per MiniOrange API docs)
username = username_client_id
# Clean password (remove spaces like Image Resizer does)
clean_password = password.replace(" ", "")

print("=" * 60)
print("Testing MiniOrange Authentication for Trieste News")
print("=" * 60)
print(f"Site URL: {site_url}")
print(f"WordPress Username: {username_wp}")
print(f"Client ID: {username_client_id}")
print(f"Password length: {len(password)}")
print(f"Password has spaces: {' ' in password}")
print()

# Test 1a: Try with Client ID as username (per MiniOrange documentation)
print("Test 1a: Check current user with Client ID as username (MiniOrange API method)")
print("-" * 60)
# Use Client ID as username (already set above)
try:
    import base64
    # Manually create auth header to see what we're sending
    auth_string = f"{username}:{clean_password}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    url = f"{site_url}/wp-json/wp/v2/users/me"
    headers = {
        'User-Agent': 'ImageResizer-MacOS/1.0 (WordPress REST API Client)',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-ImageResizer-Client': 'ImageResizer-MacOS/1.0',
        'Authorization': f'Basic {auth_b64}',
    }
    
    print(f"Sending Authorization header: Basic {auth_b64[:20]}...")
    print(f"Username: {username}")
    print(f"Password length: {len(clean_password)}")
    
    # Also try with requests.auth to compare
    resp1 = requests.get(
        url,
        auth=HTTPBasicAuth(username, clean_password),
        headers={k:v for k,v in headers.items() if k != 'Authorization'},
        timeout=10,
        allow_redirects=True
    )
    
    print(f"Using HTTPBasicAuth - Status Code: {resp1.status_code}")
    
    # Try with manual header
    resp2 = requests.get(
        url,
        headers=headers,
        timeout=10,
        allow_redirects=True
    )
    
    print(f"Using manual Authorization header - Status Code: {resp2.status_code}")
    
    if resp1.status_code == 200 or resp2.status_code == 200:
        resp = resp1 if resp1.status_code == 200 else resp2
        print(f"✅ SUCCESS! User: {resp.json().get('name')}")
    else:
        print(f"❌ Both methods failed")
        print(f"HTTPBasicAuth error: {resp1.text[:200]}")
        print(f"Manual header error: {resp2.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 1b: Try with Client ID in headers + Client ID in Basic Auth
print("Test 1b: Try with Client ID in X-Client-ID header (already using Client ID as username)")
print("-" * 60)
# Already using Client ID as username
try:
    url = f"{site_url}/wp-json/wp/v2/users/me"
    headers = {
        'User-Agent': 'ImageResizer-MacOS/1.0 (WordPress REST API Client)',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-ImageResizer-Client': 'ImageResizer-MacOS/1.0',
        'X-Client-ID': username_client_id,  # Try adding Client ID as header
    }
    
    resp = requests.get(
        url,
        auth=HTTPBasicAuth(username, clean_password),
        headers=headers,
        timeout=10,
        allow_redirects=True
    )
    
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print(f"✅ SUCCESS with Client ID header! User: {resp.json().get('name')}")
    else:
        print(f"❌ Failed: {resp.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

print()

# Test 2: Try to get categories
print("Test 2: Get categories")
print("-" * 60)
try:
    url = f"{site_url}/wp-json/wp/v2/categories"
    headers = {
        'User-Agent': 'WordPressPostEditor/1.0 (WordPress REST API Client)',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-ImageResizer-Client': 'WordPressPostEditor/1.0',
    }
    
    resp = requests.get(
        url,
        auth=HTTPBasicAuth(username, clean_password),
        headers=headers,
        params={"per_page": 10},
        timeout=10,
        allow_redirects=True
    )
    
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        categories = resp.json()
        print(f"Success! Found {len(categories)} categories")
        for cat in categories[:5]:
            print(f"  - {cat.get('name')} (ID: {cat.get('id')})")
    else:
        print(f"Error Response: {resp.text[:500]}")
        try:
            error_json = resp.json()
            print(f"Error JSON: {json.dumps(error_json, indent=2)}")
        except:
            pass
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Try to create a test post
print("Test 3: Create a test post (draft)")
print("-" * 60)
try:
    url = f"{site_url}/wp-json/wp/v2/posts"
    headers = {
        'User-Agent': 'WordPressPostEditor/1.0 (WordPress REST API Client)',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-ImageResizer-Client': 'WordPressPostEditor/1.0',
    }
    
    post_data = {
        "title": "Test Post - MiniOrange Auth",
        "content": "This is a test post to verify MiniOrange authentication.",
        "status": "draft"
    }
    
    resp = requests.post(
        url,
        auth=HTTPBasicAuth(username, clean_password),
        json=post_data,
        headers=headers,
        timeout=30,
        allow_redirects=True
    )
    
    print(f"Status Code: {resp.status_code}")
    print(f"Response Headers: {dict(resp.headers)}")
    if resp.status_code == 201:
        post = resp.json()
        print(f"Success! Post created with ID: {post.get('id')}")
        print(f"Post link: {post.get('link')}")
    else:
        print(f"Error Response: {resp.text[:500]}")
        try:
            error_json = resp.json()
            print(f"Error JSON: {json.dumps(error_json, indent=2)}")
        except:
            pass
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Try media endpoint (like Image Resizer does)
print("Test 4: Try media endpoint (like Image Resizer)")
print("-" * 60)
try:
    # Create a small test image
    from PIL import Image
    import io
    
    # Create a 1x1 pixel test image
    test_img = Image.new('RGB', (1, 1), color='red')
    img_bytes = io.BytesIO()
    test_img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    img_data = img_bytes.read()
    
    url = f"{site_url}/wp-json/wp/v2/media"
    headers = {
        'User-Agent': 'ImageResizer-MacOS/1.0 (WordPress REST API Client)',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-ImageResizer-Client': 'ImageResizer-MacOS/1.0',
    }
    
    files = {"file": ("test.jpg", img_data, "image/jpeg")}
    fields = {"title": "Test Image"}
    
    resp = requests.post(
        url,
        auth=HTTPBasicAuth(username, clean_password),
        files=files,
        data=fields,
        headers=headers,
        timeout=30,
        allow_redirects=True
    )
    
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 201:
        media = resp.json()
        print(f"Success! Media uploaded with ID: {media.get('id')}")
    else:
        print(f"Error Response: {resp.text[:500]}")
        try:
            error_json = resp.json()
            print(f"Error JSON: {json.dumps(error_json, indent=2)}")
        except:
            pass
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Test completed")
print("=" * 60)

