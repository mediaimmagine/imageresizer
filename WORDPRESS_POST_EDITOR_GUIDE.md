# WordPress Post Editor - Offline Article Creator

## Overview

The WordPress Post Editor allows you to create articles **offline** in a GUI application, then publish them to WordPress via REST API. This is perfect for:

- Writing articles without needing internet connection
- Drafting content before publishing
- Using a comfortable desktop editor instead of WordPress web interface
- Batch writing multiple articles

## Security Features

✅ **Secure Authentication via Application Passwords**
- Uses WordPress Application Passwords (same as Image Resizer)
- No interactive login required - fully automated
- Each application can have its own password
- Passwords can be revoked individually
- **Cannot be used for admin login** - only REST API access

✅ **Author Role Support**
- Works with "Author" role privileges
- Authors can create and publish their own posts
- Authors can upload media files
- Authors can create categories and tags
- All posts created by the authenticated user

## Installation

### Requirements

```bash
pip install PyQt5 requests
```

### Running the Application

```bash
python wordpress_post_editor.py
```

Or on macOS:
```bash
chmod +x wordpress_post_editor.py
./wordpress_post_editor.py
```

## Setup

### 1. Create Application Password in WordPress

1. Log in to WordPress Dashboard
2. Go to **Users → Profile** (or edit the user you want to use)
3. Scroll to **"Application Passwords"** section
4. Enter a name (e.g., "Post Editor")
5. Click **"Add New Application Password"**
6. **Copy the password immediately** (you'll only see it once!)
   - Format: `XXXX XXXX XXXX XXXX XXXX XXXX` (with spaces)
   - **Important:** Use it exactly as shown, including spaces

### 2. Verify User Role

The user must have **"Author"** role or higher:
- **Author**: Can create and publish their own posts ✅
- **Editor**: Can create and publish all posts ✅
- **Administrator**: Full access ✅
- **Contributor**: Can create drafts only (cannot publish) ⚠️
- **Subscriber**: Cannot create posts ❌

To check/change role:
1. Go to **Users → All Users**
2. Edit the user
3. Set **Role** to "Author" or higher
4. Save

### 3. Configure WordPress Site

The Post Editor uses the **same settings** as Image Resizer:
- Settings are stored in `~/.imageresizer/wp_settings.json`
- If you've already configured sites in Image Resizer, they'll appear here automatically
- If not, click **⚙️ Settings** to add a site

**Settings needed:**
- **Site Name**: Friendly name (e.g., "Udine Oggi")
- **Site URL**: Full URL (e.g., `https://udineoggi.news`)
- **Username**: WordPress username
- **Application Password**: The password you created above

## Usage

### Creating a New Post

1. Click **📝 New Post** to start fresh
2. Enter **Title** (required)
3. Write **Content** in the editor
   - Supports HTML tags (`<p>`, `<strong>`, `<h2>`, `<ul>`, etc.)
   - Plain text will be wrapped in `<p>` tags automatically
4. Optionally add:
   - **Excerpt**: Short summary (appears in post previews)
   - **Categories**: Comma-separated (e.g., "News, Politics")
   - **Tags**: Comma-separated (e.g., "breaking-news, local")
   - **Featured Image**: Media ID from WordPress library
   - **Schedule**: Set future publish date/time

### Saving Drafts Locally

Click **💾 Save Draft** to save your work offline:
- Drafts are saved in `~/.imageresizer/wp_drafts/`
- Saved as JSON files with timestamp or title-based filename
- Can be loaded later with **📂 Load Draft**

### Publishing to WordPress

1. Select the WordPress site from dropdown
2. Set publish status:
   - **draft**: Save as draft (can edit later in WordPress)
   - **publish**: Publish immediately
   - **pending**: Submit for review (if Editor/Admin needs to approve)
3. Click **🚀 Publish to WordPress**
4. Wait for confirmation message with post ID and link

### Status Options

- **draft**: Post is saved but not published
- **publish**: Post is published immediately
- **pending**: Post is submitted for review (Author role)
- **future**: Post is scheduled (if "Schedule for later" is checked)

### Categories and Tags

- **Categories**: Comma-separated list (e.g., "News, Technology, Local")
  - If category doesn't exist, it will be created automatically
  - Categories are hierarchical (you can use "Parent/Child" format)
  
- **Tags**: Comma-separated list (e.g., "breaking-news, update, important")
  - If tag doesn't exist, it will be created automatically
  - Tags are flat (no hierarchy)

### Featured Image Upload

You can now upload and set a featured image directly from the Post Editor:

1. Click **📷 Select Image** button
2. Choose a JPEG or PNG image file (max 130KB)
3. The image will be displayed in the preview area
4. Click **⬆ Upload to WordPress** to upload it to your WordPress media library
5. The image will automatically be set as the featured image when you publish the post

**Requirements:**
- **File format**: JPEG (.jpg, .jpeg) or PNG (.png) only
- **File size**: Maximum 130KB
- **Validation**: The app will check file type and size before allowing upload

**Tips:**
- If your image is larger than 130KB, use Image Resizer to compress it first
- The uploaded image will be automatically linked to your post as the featured image
- You can remove the selected image using the **✕ Remove** button
- The image preview shows the selected image before upload

## WordPress REST API Endpoints Used

The application uses these WordPress REST API endpoints:

- **POST** `/wp-json/wp/v2/posts` - Create new post
- **GET** `/wp-json/wp/v2/categories` - Search/create categories
- **GET** `/wp-json/wp/v2/tags` - Search/create tags
- **POST** `/wp-json/wp/v2/categories` - Create new category
- **POST** `/wp-json/wp/v2/tags` - Create new tag

## Security Plugin Configuration

If you're using **WP Cerber** or other security plugins, you may need to configure them:

### WP Cerber Setup

1. Go to **WordPress Dashboard → Cerber → Hardening**
2. Find **"Disable REST API"** setting
3. ✅ **Enable** "Allow REST API for authenticated users"
   - (Italian: "Consenti per utenti registrati")
4. In **"Specificare gli spazi dei nomi REST API..."** field, add:
   ```
   wp/v2
   ```
   (One per line, no trailing spaces)
5. Save changes
6. **Clear Cerber cache**: Cerber → Tools → Clear cache

### Recommended: Whitelist Post Editor

1. Go to **Cerber → Hardening → Firewall Policies**
2. Find **"Escludere le richieste con queste intestazioni HTTP..."**
3. Add header: `X-ImageResizer-Client` (Post Editor uses same header)
4. This will exclude Post Editor requests from firewall inspection

## Troubleshooting

### "Authentication Failed (401)"

**Possible causes:**
- Username or Application Password incorrect
- Application Password was revoked or deleted
- Extra spaces in credentials

**Solution:**
1. Verify Application Password still exists in WordPress
2. Create a new Application Password if needed
3. Double-check credentials in Settings

### "Permission Denied (403)"

**Possible causes:**
- User role is insufficient (needs Author or higher)
- REST API is blocked by security plugin
- User doesn't have `publish_posts` capability

**Solution:**
1. Check user role: **Users → Edit User → Role** (must be Author or higher)
2. Configure WP Cerber (see above)
3. Check Cerber → Activity → Logs for blocked requests

### "Connection Error"

**Possible causes:**
- No internet connection
- Site URL incorrect
- Site is down or unreachable

**Solution:**
1. Check internet connection
2. Verify site URL is correct (must include `https://`)
3. Try accessing the site in a browser

### Categories/Tags Not Created

**Possible causes:**
- User doesn't have permission to create categories/tags
- REST API endpoint blocked

**Solution:**
- Categories/tags creation requires Editor or Administrator role
- Author role can use existing categories/tags but may not create new ones
- Check WordPress → Settings → Writing for category/tag creation permissions

## Testing

Test post creation with:

```bash
python test_wp_post_creation.py
```

This will:
- Create a test draft post
- Verify authentication works
- Check user permissions
- Clean up test post automatically

## Author Role Capabilities

When using "Author" role, the user can:

✅ **Can do:**
- Create new posts
- Publish their own posts
- Edit their own posts (even after publishing)
- Delete their own posts
- Upload media files
- Use existing categories and tags

❌ **Cannot do:**
- Edit other users' posts
- Delete other users' posts
- Publish posts for other users
- Create new categories (may require Editor role)
- Create new tags (may require Editor role)
- Manage users or settings

## Best Practices

1. **Save drafts frequently** - Use "Save Draft" often to avoid losing work
2. **Test with draft first** - Create as draft, then publish when ready
3. **Use categories** - Organize content with categories
4. **Add tags** - Improve discoverability with relevant tags
5. **Write offline** - Use the editor offline, publish when connected
6. **Keep backups** - Drafts are saved locally for backup

## Integration with Image Resizer

The Post Editor shares settings with Image Resizer:
- Same WordPress sites configuration
- Same Application Passwords
- Workflow: Upload images with Image Resizer → Create posts with Post Editor

**Typical workflow:**
1. Create article in **Post Editor**
2. Select and upload featured image directly in Post Editor (or use Image Resizer first)
3. Upload featured image to WordPress media library
4. Publish post with featured image automatically set

**Alternative workflow (using Image Resizer):**
1. Resize and upload images using **Image Resizer**
2. Note the Media IDs from upload confirmations
3. Create article in **Post Editor**
4. The featured image can be uploaded directly in Post Editor (recommended) or use Media ID if already uploaded
5. Publish post with embedded images

## Security Notes

✅ **Application Passwords are secure:**
- Only work for REST API calls
- Cannot be used for WordPress admin login
- Can be revoked individually
- Each application has its own password
- No cookies or session management needed

✅ **No browser login required:**
- All authentication via REST API
- No interactive login dialogs
- Fully automated publishing
- Works with any WordPress site

## Support

For issues or questions:
1. Check troubleshooting section above
2. Test connection with `test_wp_post_creation.py`
3. Check WordPress user permissions
4. Verify Application Password is active
5. Check security plugin settings (WP Cerber, etc.)

