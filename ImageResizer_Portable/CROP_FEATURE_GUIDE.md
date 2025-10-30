# ✂️ Image Cropping Feature Guide

## Overview

The Image Resizer now includes an intelligent **center-crop** feature that allows you to crop images to fit specific aspect ratios without stretching or distorting the image.

## 🎯 When to Use Crop Mode

### Problem: Aspect Ratio Mismatch
When your target dimensions have a different aspect ratio than your original image:
- **Square image → Horizontal format** (e.g., 1000x1000 → 1920x1080)
- **Vertical image → Horizontal format** (e.g., 1080x1920 → 1920x1080)
- **Wide image → Square format** (e.g., 1920x1080 → 1080x1080)

Without crop mode, the image would be **stretched**, causing distortion. With crop mode, the image is **cropped from the center** to match the target aspect ratio, then resized.

## 📋 How It Works

### Step 1: Enable Crop Mode
1. Uncheck "🔒 Keep aspect ratio" (if checked)
2. Enter your desired dimensions (width and height)
3. Check "✂️ Crop to fit (when aspect ratio differs)"

### Step 2: See Crop Information
When crop mode is enabled and aspect ratios don't match, you'll see:
- **Orange warning message** showing what percentage will be cropped
- Examples:
  - "⚠️ Will crop 43.8% from sides (center crop)"
  - "⚠️ Will crop 25.0% from top/bottom (center crop)"

### Step 3: Visual Preview
Click "🔄 Update Preview" to see:

#### 1. **Crop Area Visualization** 📍
- Shows the **original image** with crop overlay
- **Darkened areas** = will be removed
- **Orange border** = crop boundary (what will be kept)
- **Center crop** = equal amounts removed from both sides

#### 2. **Final Result** ✅
- Shows exactly what the final image will look like
- After cropping and resizing to target dimensions

### Step 4: Confirm and Save
If the preview looks good:
- Click "💾 Save Resized Image"
- The saved image will be cropped and resized as shown in the preview

## 🎨 Examples

### Example 1: Square to Horizontal (Instagram to Web)

**Original**: 1080x1080 (square)  
**Target**: 1920x1080 (16:9 horizontal)

**What happens**:
- Image is too tall for the target aspect ratio
- Crop mode will crop from **top and bottom**
- Keeps the center 1920x1080 portion
- Result: No distortion, centered content

**Crop visualization shows**:
```
┌─────────────────────────────┐
│█████████ CROPPED ███████████│ ← Top 25% darkened
├─────────────────────────────┤
│                             │
│    [KEPT AREA - CENTERED]   │ ← Orange border
│                             │
├─────────────────────────────┤
│█████████ CROPPED ███████████│ ← Bottom 25% darkened
└─────────────────────────────┘
```

### Example 2: Horizontal to Square (Web to Instagram)

**Original**: 1920x1080 (16:9 horizontal)  
**Target**: 1080x1080 (square)

**What happens**:
- Image is too wide for the target aspect ratio
- Crop mode will crop from **left and right sides**
- Keeps the center 1080x1080 portion
- Result: No distortion, centered content

**Crop visualization shows**:
```
┌──┬─────────────────────┬──┐
│█ │                     │█ │
│C │                     │C │
│R │   [KEPT AREA]      │R │ ← Orange border
│O │   [CENTERED]       │O │
│P │                     │P │
│█ │                     │█ │
└──┴─────────────────────┴──┘
  ↑                       ↑
  Left ~22% cropped     Right ~22% cropped
```

### Example 3: Portrait to Web Format (1024x683)

**Original**: 1080x1920 (9:16 portrait)  
**Target**: 1024x683 (1.5:1 web format)

**What happens**:
- Image is too tall
- Crop mode crops **57% from top and bottom**
- Keeps center portion with target aspect ratio
- Resizes to 1024x683

## 🔄 Crop vs. Stretch Comparison

### Without Crop Mode (Stretch)
```
Original (Square)     Target (Horizontal)
  ┌───┐                ┌─────────┐
  │ O │       →        │ O‿O‿O   │  ← Distorted!
  └───┘                └─────────┘
```

### With Crop Mode (Center Crop)
```
Original (Square)     Cropped        Target (Horizontal)
  ┌───┐                ┌───┐          ┌─────┐
  │ O │       →        │ O │    →     │  O  │  ← Perfect!
  └───┘                └───┘          └─────┘
     Remove sides      Keep center    Resize
```

## 🎯 Best Practices

### 1. **Use Crop Mode When**:
- Converting between different aspect ratios (square ↔ horizontal ↔ vertical)
- You want to maintain image quality and proportions
- The subject is centered in the original image

### 2. **Don't Use Crop Mode When**:
- You need the entire image content
- The subject is near the edges
- You're okay with slight stretching
- You've checked "Keep aspect ratio"

### 3. **Preview Before Saving**:
- **Always click "Update Preview"** before saving
- Check the crop visualization to ensure important content isn't removed
- Verify the orange border contains everything you need

### 4. **Center Crop Behavior**:
- Crops **equally from both sides** (top/bottom or left/right)
- Ensures the center of the image is preserved
- Best for centered subjects (portraits, logos, products)

## 📊 Technical Details

### How Center Crop Works

1. **Calculate Target Aspect Ratio**: `target_width / target_height`
2. **Compare with Original Aspect Ratio**: `original_width / original_height`
3. **Determine Crop Direction**:
   - If original is **wider**: crop left and right sides
   - If original is **taller**: crop top and bottom
4. **Calculate Crop Box**:
   - Start from center
   - Extend until target aspect ratio is achieved
5. **Crop → Resize**:
   - First crop to target aspect ratio
   - Then resize to exact target dimensions

### Crop Box Formula

**For wider images (crop width)**:
```
new_width = original_height × target_ratio
left = (original_width - new_width) / 2
right = left + new_width
crop_box = (left, 0, right, original_height)
```

**For taller images (crop height)**:
```
new_height = original_width / target_ratio
top = (original_height - new_height) / 2
bottom = top + new_height
crop_box = (0, top, original_width, bottom)
```

## 💡 Tips & Tricks

### Tip 1: Check Crop Percentage
- The warning message shows **how much will be cropped**
- If it's too much (>50%), consider:
  - Using a different target dimension
  - Manually adjusting the original image first
  - Accepting some stretch instead

### Tip 2: Use Presets with Crop
1. Disable "Keep aspect ratio"
2. Click a preset button (e.g., "Instagram 1080x1080")
3. Enable "Crop to fit"
4. Update preview to see how it looks

### Tip 3: Fine-tune Dimensions
- Start with a preset
- Manually adjust width/height
- Watch the crop warning update in real-time
- Find the sweet spot that crops the least

### Tip 4: Verify Content
The crop visualization shows:
- **Orange border** = what's kept
- **Darkened areas** = what's removed
- Make sure important content (faces, text, logos) is inside the orange border

## 🚫 When Crop Mode is Disabled

Crop mode is **automatically disabled** when:
- "Keep aspect ratio" is checked
- Original and target aspect ratios are the same (within 1%)
- No image is loaded

## 🎨 UI Indicators

| Indicator | Meaning |
|-----------|---------|
| No message | Aspect ratios match, no crop needed |
| Blue info message | Aspect ratios differ, crop available but not enabled |
| Orange warning | Crop mode enabled, shows crop percentage |
| "📍 Crop Area" preview | Visual showing what will be cropped |
| "✅ Final Result" preview | How the final image will look |

## 🔧 Troubleshooting

### "Why isn't crop mode working?"
- Ensure "Keep aspect ratio" is **unchecked**
- Check that aspect ratios actually differ
- Click "Update Preview" to refresh

### "Too much is being cropped!"
- Try different target dimensions
- Consider using "Keep aspect ratio" instead
- Or manually crop the original image first

### "I don't see the crop visualization"
- Make sure "Crop to fit" is **checked**
- Click "Update Preview"
- Verify aspect ratios are different

### "Can I choose what to crop?"
- Currently, crop is always **center-based**
- For custom crop positions, use image editing software first
- Future versions may include crop position control

---

**Happy cropping!** ✂️📸

