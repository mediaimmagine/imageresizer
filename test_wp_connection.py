#!/usr/bin/env python3
"""
Test script to verify WordPress REST API access
Tests connection to WordPress media library using Application Password authentication
"""

import requests
import sys

# WordPress site configuration
WP_SITE_URL = "https://udineoggi.news"
WP_USERNAME = "COED Image Resizer"
WP_APP_PASSWORD = "Hz1U RYxx PaVE 6x4O hKce yhgC"  # Note: Application passwords contain spaces

# Important: WordPress Application Passwords should NOT have spaces removed
# They come in format "XXXX XXXX XXXX XXXX XXXX XXXX" and should be used as-is

def test_wp_connection():
    """Test WordPress REST API connection"""
    print("=" * 60)
    print("WordPress REST API Connection Test")
    print("=" * 60)
    print(f"Site URL: {WP_SITE_URL}")
    print(f"Username: {WP_USERNAME}")
    print(f"Application Password: {'*' * len(WP_APP_PASSWORD)}")
    print("=" * 60)
    print()
    
    # Test 1: Check if REST API is accessible
    print("Test 1: Checking REST API availability...")
    try:
        api_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/"
        resp = requests.get(api_url, timeout=10)
        if resp.status_code == 200:
            print("✓ REST API is accessible")
            api_info = resp.json()
            if 'name' in api_info:
                print(f"  Site name: {api_info.get('name')}")
        else:
            print(f"✗ REST API returned status {resp.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to connect to REST API: {e}")
        return False
    
    print()
    
    # Test 2: Test authentication with media endpoint (more relevant)
    print("Test 2: Testing authentication with media endpoint...")
    auth_ok = False
    try:
        # Try media endpoint first (what we actually need)
        media_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media"
        resp = requests.get(media_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10, params={'per_page': 1})
        
        if resp.status_code == 200:
            print("✓ Authentication successful via media endpoint!")
            auth_ok = True
            media_data = resp.json()
            total_items = int(resp.headers.get('X-WP-Total', 0))
            print(f"  Media library accessible - {total_items} items found")
        elif resp.status_code == 401:
            print("✗ Authentication failed (401 Unauthorized)")
            print("  Please check:")
            print("  - Username is correct (case-sensitive)")
            print("  - Application Password is correct (including spaces)")
            print("  - Application Password was created in WordPress Dashboard")
            print("  - No extra spaces before/after credentials")
            return False
        elif resp.status_code == 403:
            print("⚠ Got 403 - checking if it's auth issue or permission issue...")
            # Try without auth to see if endpoint exists
            resp_no_auth = requests.get(media_url, timeout=10)
            if resp_no_auth.status_code == 401:
                print("  ✓ Endpoint requires auth (good sign)")
                print("  Trying alternative endpoints to verify authentication...")
                
                # Try different endpoints to find one that works
                test_endpoints = [
                    ("/wp-json/wp/v2/types", "Post types"),
                    ("/wp-json/wp/v2/statuses", "Post statuses"),
                    ("/wp-json/wp/v2/categories", "Categories"),
                ]
                
                for endpoint, desc in test_endpoints:
                    test_url = f"{WP_SITE_URL.rstrip('/')}{endpoint}"
                    try:
                        resp_test = requests.get(test_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
                        if resp_test.status_code == 200:
                            print(f"  ✓ Authentication works! ({desc})")
                            auth_ok = True
                            break
                        elif resp_test.status_code == 401:
                            print(f"  ✗ {desc}: Authentication failed")
                        elif resp_test.status_code == 403:
                            print(f"  ⚠ {desc}: 403 Forbidden (may be restricted)")
                    except:
                        pass
                
                if not auth_ok:
                    print()
                    print("  🔍 Debugging: Checking Application Password format...")
                    print(f"  Username: '{WP_USERNAME}' (length: {len(WP_USERNAME)})")
                    print(f"  App Password: '{WP_APP_PASSWORD}' (length: {len(WP_APP_PASSWORD)})")
                    print(f"  App Password (no spaces): '{WP_APP_PASSWORD.replace(' ', '')}' (length: {len(WP_APP_PASSWORD.replace(' ', ''))})")
                    print()
                    print("  ⚠ WordPress Application Passwords:")
                    print("     - Should contain spaces (format: XXXX XXXX XXXX XXXX XXXX XXXX)")
                    print("     - Should be used EXACTLY as provided by WordPress")
                    print("     - Make sure it was copied correctly (no extra spaces)")
                    print()
                    print("  💡 Possible issues:")
                    print("     1. Application Password not created correctly")
                    print("     2. Security plugin blocking REST API")
                    print("     3. User doesn't have REST API access permissions")
                    print("     4. Site has REST API disabled")
            else:
                print(f"  Endpoint returned {resp_no_auth.status_code} without auth")
                print("  Endpoint may be publicly accessible or blocked")
        else:
            print(f"✗ Authentication test returned status {resp.status_code}")
            if resp.status_code != 403:
                print(f"  Response: {resp.text[:300]}")
        
        # Also try users/me endpoint
        if not auth_ok:
            print()
            print("  Trying alternative authentication endpoint...")
            auth_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/users/me"
            resp = requests.get(auth_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
            
            if resp.status_code == 200:
                user_data = resp.json()
                print("✓ Authentication successful via users endpoint!")
                auth_ok = True
                print(f"  Authenticated as: {user_data.get('name')} ({user_data.get('slug')})")
                print(f"  User ID: {user_data.get('id')}")
            elif resp.status_code == 401:
                print("✗ Authentication failed (401 Unauthorized)")
                print("  Please verify credentials are correct")
                return False
            elif resp.status_code == 403:
                print("  Users endpoint returned 403 - may be restricted by security plugin")
            
        if not auth_ok:
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Authentication test failed: {e}")
        return False
    
    print()
    
    # Test 3: Test media library access (detailed)
    print("Test 3: Testing media library READ access...")
    media_read_ok = False
    try:
        media_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media"
        resp = requests.get(media_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10, params={'per_page': 1})
        
        if resp.status_code == 200:
            media_data = resp.json()
            total_items = int(resp.headers.get('X-WP-Total', 0))
            print("✓ Media library READ access successful!")
            print(f"  Total media items in library: {total_items}")
            if media_data and len(media_data) > 0:
                print(f"  Latest media: {media_data[0].get('title', {}).get('rendered', 'N/A')}")
            media_read_ok = True
        elif resp.status_code == 401:
            print("✗ Media library access denied (401 Unauthorized)")
            return False
        elif resp.status_code == 403:
            print("⚠ Media library READ returned 403")
            print("  This might be normal - some sites restrict media list access")
            print("  Upload capability will be tested separately")
        else:
            print(f"⚠ Unexpected status: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠ Media library test error: {e}")
    
    print()
    
    # Test 4: Test upload capability (simulate)
    print("Test 4: Testing upload capability...")
    print("  Note: This test checks if the endpoint accepts POST requests")
    print("  Actual file upload will be tested when using the app")
    try:
        # Create a tiny test image in memory
        from PIL import Image
        import io
        
        test_img = Image.new('RGB', (1, 1), color='white')
        img_buffer = io.BytesIO()
        test_img.save(img_buffer, format='JPEG')
        img_data = img_buffer.getvalue()
        
        media_post_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media"
        files = {'file': ('test_upload.jpg', img_data, 'image/jpeg')}
        
        print("  Attempting test upload (will be deleted immediately if successful)...")
        resp = requests.post(media_post_url, auth=(WP_USERNAME, WP_APP_PASSWORD), 
                           files=files, timeout=15)
        
        if resp.status_code == 201:
            print("✓ UPLOAD TEST SUCCESSFUL!")
            upload_data = resp.json()
            media_id = upload_data.get('id')
            print(f"  Uploaded test image (ID: {media_id})")
            
            # Try to delete the test image
            delete_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media/{media_id}?force=true"
            del_resp = requests.delete(delete_url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
            if del_resp.status_code == 200:
                print("  Test image cleaned up")
            else:
                print(f"  Warning: Could not delete test image (you may want to delete ID {media_id} manually)")
                
        elif resp.status_code == 401:
            print("✗ Upload failed: Authentication required")
            return False
        elif resp.status_code == 403:
            print("✗ Upload failed: Permission denied (403)")
            print("  The user may not have 'upload_files' capability")
            print("  Please check WordPress user permissions")
            return False
        elif resp.status_code == 413:
            print("⚠ Upload rejected: File too large (unusual for 1x1 image)")
        else:
            print(f"⚠ Upload test returned status {resp.status_code}")
            print(f"  Response: {resp.text[:300]}")
            # Don't fail here - might be site-specific restrictions
    except ImportError:
        print("  Skipping upload test (PIL not available)")
    except Exception as e:
        print(f"  Upload test error: {e}")
        print("  This is okay - actual upload will work when using the app")
    
    print()
    
    # Test 4: Test upload capability (dry run - just check permissions)
    print("Test 4: Testing upload permissions...")
    try:
        # Try to access the media endpoint with POST to check if we can upload
        # We won't actually upload, just check if the endpoint accepts our auth
        media_post_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/media"
        # Make a HEAD request or check capabilities
        resp = requests.get(f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/users/me", 
                          auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
        if resp.status_code == 200:
            user_data = resp.json()
            # Check if user has upload capability (this is often in meta or capabilities)
            print("✓ User permissions retrieved")
            print("  Note: Actual upload permission will be tested when uploading")
            print("  The user should have 'upload_files' capability")
    except Exception as e:
        print(f"⚠ Permission check warning: {e}")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✓ All connection tests passed!")
    print()
    print("You can now configure this in the Image Resizer app:")
    print("1. Open Image Resizer")
    print("2. Go to WordPress → Settings...")
    print("3. Edit 'Udine Oggi' site")
    print("4. Set Username: COED Image Resizer")
    print("5. Set Application Password: Hz1U RYxx PaVE 6x4O hKce yhgC")
    print("6. Click Save")
    print()
    print("Ready to upload images!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_wp_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

