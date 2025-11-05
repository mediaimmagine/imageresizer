#!/usr/bin/env python3
"""
Test script to verify WordPress post creation via REST API
Tests creating a post with "Author" role privileges
"""

import requests
from requests.auth import HTTPBasicAuth

# WordPress site configuration
WP_SITE_URL = "https://udineoggi.news"
WP_USERNAME = "goriziaNews"  # Example username (Author role)
WP_APP_PASSWORD = "E7RP LRzc mGBc aUNQ 4kd3 N2m6"  # Application Password

print("=" * 60)
print("WordPress Post Creation Test")
print("=" * 60)
print(f"Site URL: {WP_SITE_URL}")
print(f"Username: {WP_USERNAME}")
print()
print("Testing post creation with Author role privileges...")
print()

# Test post data
test_post = {
    "title": "Test Post from REST API",
    "content": "<p>This is a test post created via WordPress REST API.</p><p>If you see this, post creation is working!</p>",
    "status": "draft",  # Create as draft first (safe to test)
    "excerpt": "This is a test excerpt for the post."
}

# Clean application password (remove spaces)
clean_password = WP_APP_PASSWORD.replace(" ", "")

# Create post
api_url = f"{WP_SITE_URL.rstrip('/')}/wp-json/wp/v2/posts"

headers = {
    'User-Agent': 'WordPressPostEditor-Test/1.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

print("Attempting to create post...")
print(f"Endpoint: {api_url}")
print()

try:
    resp = requests.post(
        api_url,
        auth=HTTPBasicAuth(WP_USERNAME, clean_password),
        json=test_post,
        headers=headers,
        timeout=30
    )
    
    print(f"Response Status: {resp.status_code}")
    print()
    
    if resp.status_code == 201:
        print("✓✓✓ POST CREATION SUCCESSFUL! ✓✓✓")
        print()
        
        post_data = resp.json()
        post_id = post_data.get("id")
        post_title = post_data.get("title", {}).get("rendered", "N/A")
        post_status = post_data.get("status", "unknown")
        post_link = post_data.get("link", "")
        
        print(f"Post ID: {post_id}")
        print(f"Title: {post_title}")
        print(f"Status: {post_status}")
        print(f"Link: {post_link}")
        print()
        
        # Ask if we should delete the test post
        print("=" * 60)
        print("Test post created successfully!")
        print()
        print("Next steps:")
        print("1. Check WordPress dashboard to see the draft post")
        print("2. You can publish it manually or delete it")
        print()
        print(f"To delete this test post, use:")
        print(f"  DELETE {api_url}/{post_id}?force=true")
        print("=" * 60)
        
        # Optionally delete the test post
        try:
            delete_url = f"{api_url}/{post_id}?force=true"
            delete_resp = requests.delete(
                delete_url,
                auth=HTTPBasicAuth(WP_USERNAME, clean_password),
                timeout=10
            )
            if delete_resp.status_code == 200:
                print("\n✓ Test post deleted successfully")
            else:
                print(f"\n⚠ Could not delete test post (you may want to delete ID {post_id} manually)")
        except Exception as e:
            print(f"\n⚠ Could not delete test post: {e}")
            print(f"   You may want to delete post ID {post_id} manually from WordPress")
    
    elif resp.status_code == 401:
        print("✗ Authentication failed (401 Unauthorized)")
        print()
        print("Possible issues:")
        print("- Username or Application Password incorrect")
        print("- Application Password not created correctly")
        print("- Extra spaces in credentials")
        print()
        print("Response:", resp.text[:300])
    
    elif resp.status_code == 403:
        print("✗ Permission denied (403 Forbidden)")
        print()
        print("Possible issues:")
        print("- User doesn't have 'publish_posts' or 'edit_posts' capability")
        print("- REST API is blocked by security plugin (WP Cerber, etc.)")
        print("- User role is insufficient")
        print()
        print("Note: 'Author' role should be able to:")
        print("- Create and publish their own posts")
        print("- Edit their own posts")
        print("- Upload media files")
        print()
        print("Check WordPress → Users → Edit user → Role")
        print("Verify role is 'Author' or higher")
        print()
        print("Response:", resp.text[:300])
    
    elif resp.status_code == 400:
        print("✗ Bad request (400)")
        print()
        print("Possible issues:")
        print("- Invalid post data")
        print("- Missing required fields")
        print()
        print("Response:", resp.text[:500])
    
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

print()
print("=" * 60)
print("Test complete")
print("=" * 60)

