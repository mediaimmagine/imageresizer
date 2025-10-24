# 🎯 Manual Crop Positioning Guide

## Overview

The **Manual Crop Positioning** feature allows you to precisely control where the image is cropped by dragging the crop area to your desired position. The crop dimensions and aspect ratio remain fixed based on your target size.

## 🚀 How to Use

### Step 1: Enable Crop Mode
1. **Upload your image**
2. **Uncheck** "🔒 Keep aspect ratio" (if checked)
3. **Set your target dimensions** (e.g., 1920x1080 for horizontal from a square image)
4. **Check** "✂️ Crop to fit (when aspect ratio differs)"

### Step 2: Enable Manual Positioning
1. **Check** "🎯 Manual crop positioning (drag to adjust)"
   - This option only appears when crop mode is active
   - A new window will open automatically

### Step 3: Position Your Crop
In the interactive window:
1. **See your image** with an orange crop box overlay
2. **Darkened areas** = will be removed
3. **Orange box** = what will be kept
4. **Click and drag** anywhere to move the crop box
5. **Release** to see the updated preview in the main window

### Step 4: Fine-tune and Save
- **Drag** the crop box to frame your subject perfectly
- **Click "↺ Reset to Center"** to go back to centered crop
- **Click "✓ Apply & Close"** when satisfied
- **Save your image** from the main window

## 🎨 Example Use Cases

### Use Case 1: Portrait Photo → Landscape for Web
**Original**: 1080x1920 (portrait)  
**Target**: 1920x1080 (landscape)  
**Challenge**: You want to include the person's face, not just crop from center

**Solution with Manual Crop**:
1. Enable crop mode → Select 1920x1080
2. Enable manual positioning
3. Drag the crop box **down** to include the face
4. You can now control exactly what's in the frame!

### Use Case 2: Wide Landscape → Instagram Square
**Original**: 3000x2000 (3:2 landscape)  
**Target**: 1080x1080 (square)  
**Challenge**: Important subject is on the left side, not centered

**Solution with Manual Crop**:
1. Enable crop mode → Select 1080x1080
2. Enable manual positioning
3. Drag the crop box **left** to include your subject
4. Perfect Instagram square with your subject properly framed!

### Use Case 3: Product Photo with Off-Center Subject
**Original**: 4000x3000 (product with lots of white space)  
**Target**: 1024x683 (web banner)  
**Challenge**: Product is positioned off-center in original photo

**Solution with Manual Crop**:
1. Enable crop mode → Select 1024x683
2. Enable manual positioning
3. Drag to frame the product perfectly
4. Eliminate unwanted white space!

## 🎯 Interactive Window Features

### Visual Elements
- **Full original image**: See the entire image at once
- **Orange crop box**: Shows exactly what will be kept
- **Crosshair**: Shows the center of the crop area
- **Darkened overlay**: Shows what will be removed
- **Scrollbars**: For large images

### Controls
- **Click and drag**: Move crop box anywhere
- **↺ Reset to Center**: Return to automatic center crop
- **✓ Apply & Close**: Save position and close window

### Real-Time Preview
- As you drag, the **main window preview updates automatically**
- See both the crop visualization AND the final result
- No guesswork - what you see is what you get!

## 🔧 Technical Details

### Crop Box Behavior
- **Fixed dimensions**: The crop box size never changes
- **Fixed aspect ratio**: Maintains your target aspect ratio exactly
- **Clamped movement**: Can't drag beyond image boundaries
- **Pixel-perfect**: Offset calculated in original image coordinates

### Drag Mechanics
- **Click anywhere** on the canvas to start dragging
- **Drag in any direction** - left, right, up, down, diagonal
- **Release to apply** - preview updates when you release
- **Smooth dragging**: Responsive and fluid movement

### Coordinate System
- Internally tracks offset from center position
- Automatically clamps to valid ranges
- Converts between display and original image coordinates
- Maintains precision even with scaled preview

## 💡 Tips & Best Practices

### Tip 1: Start with Center, Adjust if Needed
The center crop is often good! Only enable manual positioning if you need to adjust.

### Tip 2: Use the Preview
- Main window shows **exactly** what will be saved
- Check it frequently as you adjust
- Verify important content is inside the orange box

### Tip 3: Reset if You Get Lost
Click "↺ Reset to Center" to return to the starting position

### Tip 4: Close Window When Done
Click "✓ Apply & Close" or just close the window - your position is saved

### Tip 5: Reopen Anytime
- Uncheck and recheck "Manual crop positioning" to reopen
- Your previous position is remembered
- Make further adjustments if needed

## 🔄 Workflow Comparison

### Center Crop (Automatic)
```
1. Upload image
2. Set dimensions
3. Enable crop mode
4. Save
✓ Fast and simple
✗ No control over position
```

### Manual Crop (Custom Position)
```
1. Upload image
2. Set dimensions
3. Enable crop mode
4. Enable manual positioning
5. Drag to position
6. Apply and close
7. Save
✓ Full control over framing
✓ Perfect for off-center subjects
✗ Slightly more steps
```

## 🎨 Visual Guide

### Before Manual Crop
```
┌─────────────────────┐
│                     │
│  [Subject]          │  ← Subject on left
│                     │
│        [Empty]      │  ← Lots of empty space
└─────────────────────┘
        ↓ Auto-center crop
┌────────────┐
│           │  ← Subject cut off!
│    [Empty]│
└────────────┘
```

### After Manual Crop
```
┌─────────────────────┐
│                     │
│  [Subject]          │  ← Subject on left
│                     │
│        [Empty]      │
└─────────────────────┘
        ↓ Manual crop (drag left)
┌────────────┐
│ [Subject]  │  ← Perfect framing!
│            │
└────────────┘
```

## ⚡ Keyboard Shortcuts (Coming Soon)
Future versions may include:
- Arrow keys to nudge crop box
- Shift + drag for constrained movement
- Spacebar to toggle overlay

## 🐛 Troubleshooting

### "Manual crop option is grayed out"
- Make sure "Crop to fit" is enabled first
- Ensure aspect ratios actually differ
- Check that an image is loaded

### "Can't drag the crop box"
- Make sure you're clicking inside the interactive window
- Try clicking directly on the canvas (not the buttons)
- Check that the window hasn't frozen

### "Crop position resets"
- Did you click "Reset to Center"?
- Did you change dimensions after positioning?
- Did you toggle crop mode off and on?

### "Preview doesn't update"
- Release the mouse button to apply changes
- Click "Update Preview" in main window
- Try closing and reopening the interactive window

## 📊 Comparison: Center vs Manual

| Feature | Center Crop | Manual Crop |
|---------|-------------|-------------|
| Speed | ⚡ Fast | 🐌 Slower |
| Control | 🎯 None | 🎯🎯🎯 Full |
| Best for | Centered subjects | Off-center subjects |
| Learning curve | ✓ Easy | ~ Medium |
| Steps | 3 | 6 |
| Precision | Center only | Pixel-perfect |

## 🎓 When to Use Manual Crop

✅ **Use manual crop when:**
- Subject is not centered
- You want specific framing
- Working with portraits (faces at top/bottom)
- Product photography with specific composition
- Need to avoid cutting off important elements

❌ **Skip manual crop when:**
- Subject is already centered
- Quick batch processing needed
- Aspect ratios match (no crop needed)
- Time is critical
- Auto-center looks good

---

**Master your crops with precision!** 🎯✂️

