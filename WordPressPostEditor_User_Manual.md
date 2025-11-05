# WordPress Post Editor - User Manual

## Version 1.0
## Compatible with macOS Ventura 13.7.8+

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Creating a Post](#creating-a-post)
5. [Publishing Options](#publishing-options)
6. [Featured Images](#featured-images)
7. [Multi-Site Publishing](#multi-site-publishing)
8. [Scheduling Posts](#scheduling-posts)
9. [Draft Management](#draft-management)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

WordPress Post Editor is a desktop application that allows you to create and publish WordPress articles offline, without needing to use a web browser. The app supports publishing to multiple WordPress sites simultaneously and includes a rich text editor with formatting tools.

### Features

- **Offline Editing**: Create and edit posts without an internet connection
- **Rich Text Editor**: Format text with bold, italic, underline, headings, and links
- **Multi-Site Publishing**: Publish the same article to multiple sites at once
- **Featured Images**: Upload and attach featured images to your posts
- **Scheduling**: Schedule posts for future publication
- **Draft Management**: Save and load drafts locally
- **MiniOrange Support**: Works with MiniOrange-protected WordPress sites

---

## Installation

### Requirements

- macOS Ventura 13.7.8 or later
- Intel or Apple Silicon Mac

### Installation Steps

1. **Extract the ZIP file**: 
   - Double-click `WordPressPostEditor_Portable_macOS.zip`
   - Extract to your desired location (e.g., Applications folder)

2. **Launch the Application**:
   - Open the `WordPressPostEditor_Portable` folder
   - Double-click `WordPressPostEditor.command`
   - Or double-click `WordPressPostEditor.app` directly

3. **First Launch**:
   - The app may take a few seconds to initialize on first launch
   - If macOS warns about security, go to System Preferences → Security & Privacy → Allow

**Note**: No additional installation is required. The app is completely portable and includes all dependencies.

---

## Getting Started

### Interface Overview

The WordPress Post Editor interface consists of:

1. **Header**: Logo and application name
2. **Title Field**: Enter your post title here
3. **Content Editor**: Rich text editor with formatting toolbar
4. **Metadata Panel** (left side):
   - WordPress Sites selection
   - Categories dropdown
   - Tags input
   - Featured image
   - Author options
   - Publish status
5. **Action Buttons**:
   - Save Draft
   - Load Draft
   - Publish Post

### Supported WordPress Sites

The app is pre-configured with the following sites:

- **Trieste News** (MiniOrange authentication)
- **Gorizia Oggi**
- **Udine Oggi**
- **Venezia Orientale**

---

## Creating a Post

### Step 1: Enter Title

Type your post title in the "Post Title" field at the top of the window.

### Step 2: Write Content

1. Click in the content editor area
2. Type your article text
3. Use the formatting toolbar to style your text:
   - **Bold** (B): Make selected text bold
   - **Italic** (I): Make selected text italic
   - **Underline** (U): Underline selected text
   - **H2**: Create a heading (level 2)
   - **H3**: Create a heading (level 3)
   - **Link**: Add a hyperlink to selected text

### Step 3: Format Content

The app automatically adds:
- Publication date and time prefix (bold)
- Bold first sentence until the first period
- Author signature at the end
- WhatsApp channel link

You don't need to add these manually; they're added automatically when publishing.

### Step 4: Add Metadata

**Categories**: Select from the dropdown menu:
- CRONACA
- ATTUALITÀ
- EDITORIALI
- POLITICA

**Tags**: Enter 5-7 tags separated by commas (e.g., `trieste, cultura, eventi, musica, teatro`)

**Excerpt** (optional): Enter a short summary of your article

---

## Publishing Options

### Select WordPress Sites

- Check the boxes next to the sites where you want to publish
- You can select multiple sites to publish to all of them simultaneously
- The app remembers your last selection

### Publish Status

Choose from the dropdown:
- **Draft**: Save as draft (not published)
- **Publish**: Publish immediately
- **Pending**: Submit for review

### Author Options

**Redazione User** (default):
- Uses the site's default credentials
- Shows as "Redazione FVG.news COED Assistant" in the signature

**Custom Author**:
- Check "Use Custom Author" checkbox
- Enter the author's WordPress username
- Enter the author's Application Password
- The signature will show as `[FirstInitial.LastInitial]`

---

## Featured Images

### Adding a Featured Image

1. Click the "Select Featured Image" button in the metadata panel
2. Choose an image file (JPEG or PNG)
3. The image must be:
   - Maximum size: 130KB
   - Format: JPEG or PNG
4. A preview will appear below the button
5. To remove: Click "Remove Featured Image"

### Image Upload

- Featured images are automatically uploaded when you publish
- Each site gets its own copy of the image
- A progress bar shows upload status

---

## Multi-Site Publishing

### Publishing to Multiple Sites

1. Check multiple site checkboxes
2. Fill in all post details
3. Click "Publish Post"
4. The app will:
   - Upload featured images to each site (if selected)
   - Create the post on each site
   - Show results for each site

### Results

After publishing, you'll see:
- ✅ Success messages with post links
- ❌ Error messages if something went wrong
- Post IDs for each successful publication

---

## Scheduling Posts

### Schedule for Later

1. Check "Schedule for later" checkbox
2. Select a date using the calendar widget
3. Select a time using the time picker (HH:MM format)
4. The post will be scheduled for that date and time

**Note**: The post must be published (not draft) to be scheduled.

---

## Draft Management

### Save Draft

1. Click "Save Draft" button
2. Your current work is saved locally
3. Includes: title, content, metadata, featured image path

### Load Draft

1. Click "Load Draft" button
2. Select a saved draft from the list
3. All fields are restored from the draft

**Note**: Drafts are stored locally on your computer.

---

## Troubleshooting

### App Won't Launch

**Solution**: 
- Right-click the `.command` file and select "Open"
- Go to System Preferences → Security & Privacy → Allow

### Authentication Errors

**For Trieste News**:
- Ensure MiniOrange Client ID and Secret are correctly configured
- Check that the Client ID is mapped to a user with Editor/Administrator role

**For Other Sites**:
- Verify Application Passwords are correct
- Check that usernames are correct
- Ensure users have appropriate permissions (Author role minimum)

### Featured Image Upload Fails

**Possible causes**:
- Image is larger than 130KB (resize the image first)
- Image format is not JPEG or PNG
- Network connection issue

**Solution**:
- Resize the image using Image Resizer or another tool
- Convert to JPEG or PNG format
- Check your internet connection

### Post Not Published

**Check**:
- Internet connection
- WordPress site is accessible
- User has publishing permissions
- Selected the correct site checkbox

### Categories Not Showing

**Solution**:
- If a selected category doesn't exist, the app will automatically use "CRONACA" as fallback
- Categories are retrieved from WordPress, so ensure they exist on the site

### Tags Not Working

**Requirements**:
- Minimum 5 tags
- Maximum 7 tags
- Separate tags with commas
- Each tag should be a single word or short phrase

---

## Tips and Best Practices

1. **Always Save Drafts**: Save your work frequently to avoid losing content
2. **Check Tags**: Ensure you have 5-7 relevant tags before publishing
3. **Test with Draft**: Publish as draft first to verify formatting
4. **Image Optimization**: Keep featured images under 130KB for faster uploads
5. **Multi-Site Publishing**: Verify all sites are selected before publishing
6. **Scheduling**: Use scheduling for timed publications across multiple sites

---

## Keyboard Shortcuts

- **Cmd + B**: Bold text
- **Cmd + I**: Italic text
- **Cmd + U**: Underline text
- **Cmd + S**: Save draft (if implemented)
- **Cmd + P**: Publish post (if implemented)

---

## Support

For technical support or questions:
- Contact Media Immagine support team
- Check the README.md file in the portable directory
- Review error messages in the status bar

---

## Version History

### Version 1.0 (November 2025)
- Initial release
- Multi-site publishing support
- Rich text editor
- Featured image upload
- MiniOrange authentication support
- Scheduling functionality
- Draft management

---

## License

Free to use for personal and commercial projects.

---

**Developed by**: Media Immagine  
**Last Updated**: November 2025

