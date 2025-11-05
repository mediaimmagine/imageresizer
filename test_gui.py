#!/usr/bin/env python3
"""
Minimal GUI test to diagnose macOS Tkinter issues
"""

import tkinter as tk
import sys
import os

# macOS-specific fixes
if sys.platform == "darwin":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

def test_basic_gui():
    print("Creating basic GUI test...")
    
    try:
        root = tk.Tk()
        print("✓ Root window created")
        
        root.title("Image Resizer Test")
        root.geometry("600x400")
        print("✓ Window configured")
        
        # Header
        header = tk.Frame(root, bg="lightblue", height=60)
        header.pack(fill=tk.X, pady=5)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🖼️ Image Resizer Test", 
                        font=("Arial", 16, "bold"), 
                        bg="lightblue", fg="black")
        title.pack(pady=15)
        print("✓ Header created")
        
        # Main content
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel
        left = tk.Frame(main_frame, bg="lightgray", width=200)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        tk.Label(left, text="Controls", font=("Arial", 12, "bold"), bg="lightgray").pack(pady=10)
        
        upload_btn = tk.Button(left, text="Browse...", bg="blue", fg="white", 
                              font=("Arial", 10, "bold"))
        upload_btn.pack(pady=5)
        
        tk.Label(left, text="Width:", bg="lightgray").pack(anchor=tk.W, padx=5)
        width_entry = tk.Entry(left, width=10)
        width_entry.pack(pady=2, padx=5)
        width_entry.insert(0, "1920")
        
        tk.Label(left, text="Height:", bg="lightgray").pack(anchor=tk.W, padx=5)
        height_entry = tk.Entry(left, width=10)
        height_entry.pack(pady=2, padx=5)
        height_entry.insert(0, "1080")
        
        quality_btn = tk.Button(left, text="Quality: 50%", bg="orange", fg="white")
        quality_btn.pack(pady=5)
        
        save_btn = tk.Button(left, text="Save Image", bg="green", fg="white")
        save_btn.pack(pady=5)
        
        print("✓ Left panel created")
        
        # Right panel
        right = tk.Frame(main_frame, bg="white", relief=tk.SUNKEN, bd=2)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right, text="Preview Area", font=("Arial", 12, "bold"), bg="white").pack(pady=10)
        
        canvas = tk.Canvas(right, bg="lightyellow", height=200)
        canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas.create_text(150, 100, text="Image preview will appear here", 
                          font=("Arial", 12), fill="gray")
        
        print("✓ Right panel created")
        
        # Footer
        footer = tk.Frame(root, bg="lightgray", height=40)
        footer.pack(fill=tk.X, pady=(5, 0))
        footer.pack_propagate(False)
        
        credits = tk.Label(footer, text="Image Resizer v1.0 - Test Version", 
                          font=("Arial", 9), bg="lightgray", fg="black")
        credits.pack(pady=10)
        
        print("✓ Footer created")
        
        # Force update
        root.update_idletasks()
        root.update()
        print("✓ GUI updated")
        
        print("Starting mainloop...")
        root.mainloop()
        print("Mainloop ended")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_gui()











