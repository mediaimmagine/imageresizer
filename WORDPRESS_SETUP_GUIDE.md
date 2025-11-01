# WordPress REST API Setup Guide

## Current Status: Testing Required

The test script shows that:
- ✓ REST API is accessible (`/wp-json/` endpoint works)
- ⚠ Authentication endpoints returning 403 (may be security plugin blocking)

## Credentials for udineoggi.news

- **Site URL:** https://udineoggi.news
- **Username:** COED Image Resizer
- **Application Password:** Hz1U RYxx PaVE 6x4O hKce yhgC

## Application Password Format

WordPress Application Passwords:
- **Format:** `XXXX XXXX XXXX XXXX XXXX XXXX` (with spaces)
- **Important:** Use EXACTLY as provided, including spaces
- Do NOT remove spaces or modify the password

## Troubleshooting 403 Errors

If you're getting 403 Forbidden errors, check:

### 1. Security Plugins
Common plugins that block REST API:
- **Wordfence** - Check Firewall → Blocking → REST API
- **iThemes Security** - Check Security → Settings → REST API
- **All In One WP Security** - Check Firewall → REST API
- **Disable REST API** plugin - Deactivate if installed

**Solution:** Whitelist REST API endpoints or allow Application Password authentication

### 2. User Permissions
The user must have:
- `upload_files` capability (Editor or Administrator role)
- REST API access enabled

**Check:** WordPress Dashboard → Users → Edit "COED Image Resizer" user → Verify role is Editor or Administrator

### 3. Application Password Setup
Verify the Application Password:
1. Go to: WordPress Dashboard → Users → Profile (for the "COED Image Resizer" user)
2. Scroll to: "Application Passwords"
3. Verify the password exists and is active
4. If needed, delete and recreate it

### 4. Server Configuration
Some servers block REST API at the server level. Check:
- `.htaccess` rules blocking `/wp-json/`
- Nginx/firewall rules
- Cloudflare or CDN security settings

## How to Configure in Image Resizer App

Once authentication is confirmed:

1. **Open Image Resizer**
2. **Go to:** WordPress → Settings...
3. **Edit:** "Udine Oggi" site
4. **Set:**
   - Site URL: `https://udineoggi.news`
   - Username: `COED Image Resizer`
   - Application Password: `Hz1U RYxx PaVE 6x4O hKce yhgC` (with spaces)
5. **Click:** Save

## Testing Upload

The app uses:
- **Endpoint:** `https://udineoggi.news/wp-json/wp/v2/media`
- **Method:** POST
- **Auth:** Basic Auth (username + application password)
- **No interactive login required**

If the upload works, you'll see:
- Status: "Uploading to Udine Oggi..."
- Success message with Media ID and URL

## Security Notes

✅ **Application Passwords are secure:**
- They only work for REST API calls
- Cannot be used for admin login
- Can be revoked individually
- Each application can have its own password

✅ **No interactive login needed:**
- All authentication happens via REST API
- No browser windows or cookies required
- Fully automated uploads

## Next Steps

1. **Verify REST API is not blocked** by security plugins
2. **Test upload** using the Image Resizer app
3. **If 403 persists**, check with WordPress admin about REST API restrictions
4. **If upload works**, configure the other 3 sites similarly

## Test Script

You can test the connection anytime by running:
```bash
python3 test_wp_connection.py
```

This will verify:
- REST API availability
- Authentication
- Media library access
- Upload capability

