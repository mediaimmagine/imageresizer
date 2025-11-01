# WP Cerber Security - REST API Configuration

## How to Allow REST API Access for Application Passwords

WP Cerber Security blocks REST API access by default for security. Here's how to configure it:

### Method 1: Allow REST API Completely (Simplest)

1. **Go to:** WordPress Dashboard
2. **Navigate to:** Cerber → Hardening
3. **Find:** "Disable REST API" setting
4. **Action:** Make sure "Disable REST API" is **UNCHECKED** or **DISABLED**
5. **Save changes**

### Method 2: Whitelist REST API Namespaces (More Secure)

1. **Go to:** WordPress Dashboard
2. **Navigate to:** Cerber → Hardening
3. **Find:** "Disable REST API" setting
4. **Look for:** Field labeled "Specify REST API namespaces to allow..." (Italian: "Specificare gli spazi dei nomi REST API da consentire...")
5. **Action:** Add namespace (one per line):
   ```
   wp/v2
   ```
   This allows all WordPress REST API v2 endpoints including `/wp-json/wp/v2/media`
6. **Save changes**

### Method 3: Allow by User/Authentication (Recommended)

1. **Go to:** WordPress Dashboard
2. **Navigate to:** Cerber → Hardening
3. **Find:** "Disable REST API" setting
4. **Check for options like:**
   - "Allow REST API for authenticated users" - **ENABLE this**
   - "Allow REST API with Application Passwords" - **ENABLE this** (if available)
5. **Save changes**

### Method 4: Allow Specific IP or User Agent (Advanced)

1. **Go to:** WordPress Dashboard
2. **Navigate to:** Cerber → Access Lists
3. **Add to Whitelist:**
   - The IP address where Image Resizer runs from
   - Or add custom user agent if Cerber supports it

### Method 5: Disable REST API Blocking via Code (If settings don't work)

If you have access to `functions.php` or a custom plugin:

```php
// Allow REST API for authenticated requests
add_filter( 'rest_authentication_errors', function( $result ) {
    // Allow REST API if user is authenticated
    if ( ! empty( $result ) ) {
        return $result;
    }
    if ( ! is_user_logged_in() ) {
        return $result;
    }
    return true;
}, 99 );
```

### Step-by-Step Visual Guide

1. **Login to WordPress Dashboard**
2. **Click:** "Cerber" in left menu
3. **Click:** "Hardening" tab
4. **Scroll to:** "REST API" section
5. **Look for:** 
   - "Disable REST API"
   - "REST API for authenticated users"
   - "REST API exceptions"
6. **Configure as follows:**
   - ✅ Uncheck "Disable REST API" OR
   - ✅ Enable "Allow REST API for authenticated users" OR
   - ✅ Add `/wp-json/wp/v2/media` to exceptions
7. **Click:** "Save Changes"

### Testing After Configuration

After making changes, test with:
```bash
python3 test_wp_connection.py
```

Or test directly in the Image Resizer app by trying to upload an image.

### What Each Method Does

- **Method 1:** Allows all REST API access (less secure but simplest)
- **Method 2:** Allows only specific endpoints (balanced security)
- **Method 3:** Allows REST API only for authenticated users (recommended - secure and functional)
- **Method 4:** Allows from specific locations (most secure)
- **Method 5:** Code-level override (if plugin settings don't work)

### Recommended Configuration

For Image Resizer with Application Passwords:
- ✅ Enable: "Allow REST API for authenticated users"
- ✅ Keep: "Disable REST API" for unauthenticated requests (better security)
- ✅ This allows Application Password authentication while blocking unauthorized access

### Common Issues

**Issue:** Still getting 403 after changes
- **Solution:** Clear Cerber cache: Cerber → Tools → Clear cache
- **Solution:** Check Cerber → Log for blocked requests

**Issue:** REST API works but uploads fail
- **Solution:** Check user permissions - user needs `upload_files` capability
- **Solution:** Check file size limits in WordPress Settings → Media

**Issue:** Can't find REST API settings
- **Solution:** Update WP Cerber Security plugin to latest version
- **Solution:** Settings might be in: Cerber → Settings → Hardening

### Verification

After configuration, verify REST API access:
1. Visit: `https://udineoggi.news/wp-json/wp/v2/media` in browser
2. You should see either:
   - A JSON response (if authenticated) OR
   - A 401 error (meaning endpoint exists and requires auth - this is good!)

If you see 403, the endpoint is still blocked.

### Additional Notes

- WP Cerber may also block based on IP address or user agent
- Check Cerber → Activity → Logs to see if requests are being blocked
- Application Passwords should work once REST API is allowed for authenticated users

