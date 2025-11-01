# 🔐 WordPress Application Password Setup - Complete Guide

This guide documents the complete process of setting up the Image Resizer application to upload images to WordPress using Application Passwords via the REST API.

## 📋 Table of Contents

1. [Overview](#overview)
2. [WordPress User Setup](#wordpress-user-setup)
3. [Application Password Creation](#application-password-creation)
4. [User Permissions Required](#user-permissions-required)
5. [WP Cerber Security Configuration](#wp-cerber-security-configuration)
6. [Application Configuration](#application-configuration)
7. [Testing the Setup](#testing-the-setup)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Image Resizer application uses WordPress **Application Passwords** to authenticate with the WordPress REST API without requiring interactive login. This method is secure, non-interactive, and specifically designed for programmatic access.

**Key Points:**
- ✅ Uses WordPress REST API (`/wp-json/wp/v2/media`)
- ✅ Authentication via HTTP Basic Auth (username + Application Password)
- ✅ No browser interaction required
- ✅ Secure and revocable credentials
- ✅ Works with security plugins (WP Cerber) when properly configured

---

## WordPress User Setup

### 1. Create or Select a WordPress User

1. Log in to your WordPress admin dashboard
2. Go to **Users** → **All Users**
3. Either:
   - **Use an existing user** (recommended: Editor or Administrator)
   - **Create a new user** (see step 4)

### 2. Create a New User (if needed)

1. Go to **Users** → **Add New**
2. Fill in the required fields:
   - **Username**: Choose a descriptive name (e.g., `goriziaNews`, `udineNews`)
   - **Email**: Enter a valid email address
   - **Role**: Select **Editor** (minimum) or **Administrator** (for testing)
   - **Password**: WordPress will generate one, but we won't use it (Application Password will be used instead)
3. Click **Add New User**

### 3. Verify User Role

1. Go to **Users** → **All Users**
2. Find your user and verify the **Role** column shows **Editor** or **Administrator**
   - ⚠️ **Important**: Users with **Author** role or lower may not have sufficient permissions for REST API uploads

---

## Application Password Creation

### Step-by-Step Instructions

1. **Navigate to User Profile**
   - Go to **Users** → **All Users**
   - Click on the user you want to create an Application Password for

2. **Scroll to Application Passwords Section**
   - Scroll down to the **Application Passwords** section
   - If you don't see this section:
     - Ensure you're using WordPress 5.6 or later
     - Make sure you're logged in as an Administrator

3. **Create Application Password**
   - In the **New Application Password Name** field, enter a descriptive name:
     - Examples: `COED Image Resizer`, `Image Resizer MacOS`, `SiteName Upload Tool`
   - Click **Add New Application Password**

4. **Save the Password**
   - ⚠️ **CRITICAL**: WordPress will display the Application Password **ONCE**
   - It will look like: `xxxx xxxx xxxx xxxx xxxx xxxx` (24 characters, spaces included)
   - **Copy and save it immediately** - you cannot retrieve it later!
   - Format example: `E7RP LRzc mGBc aUNQ 4kd3 N2m6`

5. **Important Notes**
   - The Application Password is **NOT** the WordPress user password
   - The Application Password is used **WITH** the WordPress username for authentication
   - You can create multiple Application Passwords for different devices/applications
   - Each Application Password can be revoked individually

---

## User Permissions Required

### Minimum Role: Editor

For REST API media uploads, the WordPress user must have the following capabilities:

- ✅ `upload_files` - Required to upload media files
- ✅ `edit_posts` - Required for REST API POST operations
- ✅ `publish_posts` - May be required depending on WordPress configuration

### Role Comparison

| Role | upload_files | edit_posts | REST API Access | Recommended? |
|------|-------------|------------|-----------------|--------------|
| **Administrator** | ✅ | ✅ | ✅ Full access | ✅ Yes (for testing) |
| **Editor** | ✅ | ✅ | ✅ Full access | ✅ **Recommended** |
| **Author** | ✅ | ⚠️ Limited | ⚠️ May fail | ❌ Not recommended |
| **Contributor** | ❌ | ⚠️ Limited | ❌ No upload access | ❌ No |
| **Subscriber** | ❌ | ❌ | ❌ No access | ❌ No |

### Verifying Permissions

1. Go to **Users** → **All Users**
2. Click on your user
3. Scroll to **Role** section
4. Ensure it's set to **Editor** or **Administrator**

### If Upload Fails with 401 "rest_cannot_create"

This error usually indicates:
- User role is insufficient (e.g., Author)
- Application Password is not being used correctly
- Username/Application Password mismatch

**Solution:**
1. Change user role to **Editor** or **Administrator**
2. Verify you're using the **WordPress username** (not Application Password name) with the **Application Password**

---

## WP Cerber Security Configuration

WP Cerber Security can block REST API access. Follow these steps to allow authenticated requests.

### Step 1: Enable REST API for Authenticated Users

1. Go to **WordPress Dashboard** → **Cerber** → **Hardening**
2. Find the **"Disable REST API"** section
3. ✅ **Enable** the checkbox: **"Allow REST API for authenticated users"**
   - Italian: **"Consenti per utenti registrati"** (MUST be CHECKED ✅)
4. Click **Save Changes**

### Step 2: Whitelist REST API Namespace

1. In the same **"Disable REST API"** section
2. Find the field: **"Specificare gli spazi dei nomi REST API da consentire..."**
   - English: **"Specify REST API namespaces to allow..."**
3. Add the following (one per line):
   ```
   wp/v2
   ```
   - ⚠️ **Important**: No trailing spaces, one namespace per line
4. Click **Save Changes**

### Step 3: Whitelist Application Header (RECOMMENDED)

To prevent rate limiting and firewall blocks:

1. Go to **Cerber** → **Hardening** → **Firewall Policies**
2. Find: **"Escludere le richieste con queste intestazioni HTTP dall'ispezione da parte del firewall"**
   - English: **"Exclude requests with these HTTP headers from firewall inspection"**
3. Add the following header:
   ```
   X-ImageResizer-Client
   ```
4. This will exclude all ImageResizer requests from firewall inspection
5. Click **Save Changes**

### Step 4: Clear Cerber Cache

1. Go to **Cerber** → **Tools**
2. Click **"Clear cache"** or **"Clear All"**
3. Wait for confirmation

### Step 5: Alternative - Configure Rate Limiting (if needed)

If you still experience blocks with multiple uploads:

1. Go to **Cerber** → **Traffic Inspector**
2. Check **"Anti-spam engine"** and **"Rate limiting"** settings
3. Consider:
   - Disabling rate limiting for authenticated REST API requests
   - Whitelisting your IP address
   - Whitelisting User-Agent: `ImageResizer-MacOS`

### Verifying Cerber Configuration

After configuration, test REST API access:

```bash
curl -u "username:application_password" \
  -H "X-ImageResizer-Client: ImageResizer-MacOS/1.0" \
  https://yoursite.com/wp-json/wp/v2/media
```

If you get a **200 OK** response, Cerber is configured correctly.

---

## Application Configuration

### Hardcoded Sites (Pre-configured)

The application includes hardcoded credentials for these sites:

1. **Gorizia Oggi** (`goriziaoggi.news`)
   - Username: `goriziaNews`
   - Application Password: `E7RP LRzc mGBc aUNQ 4kd3 N2m6`

2. **Udine Oggi** (`udineoggi.news`)
   - Username: `udineNews`
   - Application Password: `9q7M ioUs j3ov F4WW fUqE h7F7`

### Adding New Sites

1. Open the application
2. Go to **WordPress** → **WordPress Settings...**
3. Click **Add Site** button
4. Fill in:
   - **Site Name**: Display name (e.g., "My WordPress Site")
   - **Site URL**: Full URL (e.g., `https://mysite.com`)
   - **Username**: WordPress username (NOT Application Password name)
   - **Application Password**: The 24-character Application Password from WordPress
5. Click **OK** to save

### Settings Storage

- Settings are stored in: `~/.imageresizer/wp_settings.json`
- Hardcoded sites are automatically restored on application start
- User-configured sites are preserved

---

## Testing the Setup

### Method 1: Using the Application

1. **Launch Image Resizer WP**
2. **Select an image** to resize
3. **Choose WordPress site** from the dropdown menu
4. **Click "⬆ Upload to WordPress"**
5. **Expected behavior:**
   - Progress bar appears
   - Upload completes successfully
   - Success message shows: Site name, Media ID, and URL

### Method 2: Command Line Test (GET)

Test REST API access with GET request:

```bash
python3 -c "
import requests
from requests.auth import HTTPBasicAuth

url = 'https://yoursite.com/wp-json/wp/v2/media'
username = 'your_username'
password = 'xxxx xxxx xxxx xxxx xxxx xxxx'  # Application Password
clean_password = password.replace(' ', '')

resp = requests.get(url, auth=HTTPBasicAuth(username, clean_password), timeout=10)
print(f'Status: {resp.status_code}')
if resp.status_code == 200:
    print('✓ Success! Media library accessible.')
    data = resp.json()
    print(f'Found {len(data)} items in media library')
else:
    print(f'✗ Error: {resp.text[:200]}')
"
```

**Expected output:**
```
Status: 200
✓ Success! Media library accessible.
Found X items in media library
```

### Method 3: Command Line Test (POST)

Test upload capability:

```bash
python3 -c "
import requests
from requests.auth import HTTPBasicAuth

url = 'https://yoursite.com/wp-json/wp/v2/media'
username = 'your_username'
password = 'xxxx xxxx xxxx xxxx xxxx xxxx'  # Application Password
clean_password = password.replace(' ', '')

headers = {
    'User-Agent': 'ImageResizer-MacOS/1.0 (WordPress REST API Client)',
    'X-ImageResizer-Client': 'ImageResizer-MacOS/1.0',
    'Accept': 'application/json'
}

# Test with minimal data (will fail but shows endpoint is accessible)
test_data = {'title': 'Test Upload', 'status': 'private'}
resp = requests.post(url, auth=HTTPBasicAuth(username, clean_password), 
                     headers=headers, data=test_data, timeout=10)
print(f'Status: {resp.status_code}')
if resp.status_code in [200, 201, 400]:
    if resp.status_code == 400:
        error_json = resp.json()
        if error_json.get('code') == 'rest_upload_no_content_disposition':
            print('✓ Endpoint accessible - needs file data (this is expected)')
    else:
        print('✓ Endpoint accessible')
else:
    print(f'✗ Error: {resp.text[:200]}')
"
```

**Expected output:**
```
Status: 400
✓ Endpoint accessible - needs file data (this is expected)
```

### Method 4: Using Test Scripts

The repository includes test scripts in the root directory:

1. **`test_wp_connection.py`** - Basic REST API connectivity test
2. **`test_wp_upload_direct.py`** - Direct upload test with cleanup
3. **`test_wp_detailed.py`** - Comprehensive diagnostic test

Run them with:
```bash
python3 test_wp_connection.py
```

---

## Troubleshooting

### Error 401: Unauthorized

**Symptoms:**
- HTTP 401 response
- Error message: "Unauthorized - Authentication failed"
- Or: "rest_cannot_create" / "Non hai i permessi per creare articoli con questo utente"

**Causes & Solutions:**

1. **Wrong Username**
   - ❌ **Wrong**: Using Application Password name (e.g., "COED Image Resizer")
   - ✅ **Correct**: Using WordPress username (e.g., "goriziaNews")
   - **Fix**: Verify you're using the actual WordPress username

2. **Incorrect Application Password**
   - Password may have been copied incorrectly (missing characters, extra spaces)
   - Application Password may have been revoked or regenerated
   - **Fix**: 
     - Verify Application Password format: exactly 24 characters (spaces removed = 24 chars)
     - Regenerate Application Password in WordPress if needed

3. **Insufficient User Permissions**
   - User role is too low (Author, Contributor, etc.)
   - **Fix**: Change user role to **Editor** or **Administrator**

4. **Application Password Not Active**
   - Application Password may have been deleted
   - **Fix**: Create a new Application Password

### Error 403: Forbidden

**Symptoms:**
- HTTP 403 response
- Error message: "Access Forbidden"
- Cerber log shows: "Richiesta di REST API bloccata"

**Causes & Solutions:**

1. **WP Cerber Blocking REST API**
   - REST API is disabled for all users
   - **Fix**: Enable "Allow REST API for authenticated users" in Cerber → Hardening

2. **Namespace Not Whitelisted**
   - `wp/v2` namespace is not in Cerber whitelist
   - **Fix**: Add `wp/v2` to allowed namespaces in Cerber → Hardening

3. **Cerber Cache Not Cleared**
   - Old blocking rules are cached
   - **Fix**: Clear Cerber cache (Cerber → Tools → Clear cache)

4. **Firewall Blocking Requests**
   - Rate limiting or anti-spam engine blocking
   - **Fix**: 
     - Add `X-ImageResizer-Client` header to Cerber firewall whitelist
     - Or disable rate limiting for authenticated REST API requests

### Error: "Site is not properly configured"

**Symptoms:**
- Application shows: "Site 'X' is not properly configured"
- Dropdown shows sites but upload fails immediately

**Causes & Solutions:**

1. **Missing Credentials**
   - Site URL, Username, or Application Password is empty
   - **Fix**: Go to WordPress Settings and configure the site

2. **Hardcoded Site Overwritten**
   - Hardcoded credentials were cleared in settings
   - **Fix**: 
     - Application will restore hardcoded credentials on next launch
     - Or manually re-enter credentials in settings

### Upload Fails Silently / No Progress Bar

**Symptoms:**
- Click upload button but nothing happens
- No progress bar appears

**Causes & Solutions:**

1. **No Image Loaded**
   - Must load an image before uploading
   - **Fix**: Click "Select Image" and choose an image first

2. **Image Size Exceeds 200KB**
   - Application blocks uploads over 200KB
   - **Fix**: 
     - Reduce image dimensions or quality
     - Or click "Yes" when prompted to proceed anyway

### Rate Limiting / Multiple Uploads Blocked

**Symptoms:**
- First upload succeeds, subsequent uploads fail
- Temporary 403 errors after multiple uploads

**Causes & Solutions:**

1. **Application Already Handles This**
   - Application includes 2-second delay between uploads
   - **Fix**: This should be automatic, but if issues persist:
     - Add `X-ImageResizer-Client` header to Cerber whitelist (recommended)
     - Or increase delay in code (currently 2 seconds)

2. **Cerber Rate Limiting Too Aggressive**
   - **Fix**: Configure Cerber to allow authenticated REST API requests

---

## Security Best Practices

### 1. Use Application Passwords (Not Regular Passwords)

✅ **DO:**
- Use Application Passwords for REST API access
- Create separate Application Passwords for each application/device
- Name Application Passwords descriptively

❌ **DON'T:**
- Share your main WordPress password
- Use the same Application Password for multiple sites
- Store Application Passwords in plain text (use secure storage)

### 2. Use Appropriate User Roles

✅ **DO:**
- Create dedicated WordPress users with **Editor** role for automated tools
- Use separate users for different applications/sites

❌ **DON'T:**
- Use Administrator accounts unless necessary
- Share user accounts between different tools

### 3. Monitor Application Passwords

- Regularly review Application Passwords in WordPress
- Revoke unused or compromised Application Passwords immediately
- Document which Application Password is used for which purpose

### 4. Configure Security Plugins Correctly

- Whitelist legitimate application headers (e.g., `X-ImageResizer-Client`)
- Enable REST API for authenticated users (not public access)
- Monitor security logs for unauthorized access attempts

---

## Quick Reference

### Application Password Format
```
Original:  E7RP LRzc mGBc aUNQ 4kd3 N2m6
Used in code: E7RPLRzcmGBcaUNQ4kd3N2m6 (spaces removed)
```

### REST API Endpoint
```
https://yoursite.com/wp-json/wp/v2/media
```

### Authentication Method
```
HTTP Basic Auth
Username: WordPress username
Password: Application Password (spaces removed)
```

### Required Headers
```
User-Agent: ImageResizer-MacOS/1.0 (WordPress REST API Client)
X-ImageResizer-Client: ImageResizer-MacOS/1.0
Accept: application/json
```

### Minimum WordPress Requirements
- WordPress 5.6+ (Application Passwords feature)
- PHP 7.4+
- REST API enabled (default)

---

## Additional Resources

- [WordPress Application Passwords Documentation](https://wordpress.org/support/article/using-application-passwords/)
- [WordPress REST API Handbook](https://developer.wordpress.org/rest-api/)
- [WP Cerber Security Documentation](https://wpcerber.com/)
- Application test scripts in repository root

---

## Support

If you encounter issues not covered in this guide:

1. Check application logs for detailed error messages
2. Verify WordPress user permissions (must be Editor or Administrator)
3. Test REST API access using command-line tools (see Testing section)
4. Review WP Cerber logs for blocked requests
5. Ensure Application Password is correctly formatted (24 characters, spaces removed)

---

**Last Updated:** 2025-01-01  
**Application Version:** ImageResizer WP 1.0  
**WordPress Requirements:** 5.6+ with Application Passwords enabled

