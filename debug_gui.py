#!/usr/bin/env python3
"""
Debug GUI to see what's actually being displayed
"""

import tkinter as tk
import sys
import os

# macOS-specific fixes
if sys.platform == "darwin":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

def create_debug_gui():
    print("Creating debug GUI...")
    
    root = tk.Tk()
    root.title("DEBUG - Image Resizer")
    root.geometry("800x600")
    
    # Force window to front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(lambda: root.attributes('-topmost', False))
    
    print("Window created")
    
    # HEADER - Very obvious
    header = tk.Frame(root, bg="red", height=80, relief=tk.RAISED, bd=5)
    header.pack(fill=tk.X, padx=10, pady=10)
    header.pack_propagate(False)
    
    header_label = tk.Label(header, text="🔴 HEADER - This should be RED and VISIBLE", 
                           bg="red", fg="white", font=("Arial", 16, "bold"))
    header_label.pack(pady=20)
    
    print("Header created")
    
    # Main content
    main_frame = tk.Frame(root, bg="yellow", relief=tk.SUNKEN, bd=3)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Left panel
    left = tk.Frame(main_frame, bg="blue", width=300, relief=tk.RAISED, bd=2)
    left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
    
    left_label = tk.Label(left, text="🔵 LEFT PANEL\nThis should be BLUE", 
                         bg="blue", fg="white", font=("Arial", 12, "bold"))
    left_label.pack(pady=20)
    
    # Right panel
    right = tk.Frame(main_frame, bg="green", relief=tk.RAISED, bd=2)
    right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    right_label = tk.Label(right, text="🟢 RIGHT PANEL\nThis should be GREEN\nPreview area", 
                          bg="green", fg="white", font=("Arial", 12, "bold"))
    right_label.pack(pady=20)
    
    # Canvas in right panel
    canvas = tk.Canvas(right, bg="white", height=200, relief=tk.SUNKEN, bd=2)
    canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    canvas.create_text(150, 100, text="WHITE CANVAS\nThis should be visible", 
                      font=("Arial", 14, "bold"), fill="black")
    
    print("Main content created")
    
    # FOOTER - Very obvious
    footer = tk.Frame(root, bg="purple", height=60, relief=tk.RAISED, bd=5)
    footer.pack(fill=tk.X, padx=10, pady=10)
    footer.pack_propagate(False)
    
    footer_label = tk.Label(footer, text="🟣 FOOTER - This should be PURPLE and VISIBLE", 
                           bg="purple", fg="white", font=("Arial", 14, "bold"))
    footer_label.pack(pady=15)
    
    print("Footer created")
    
    # Force update
    root.update_idletasks()
    root.update()
    
    print("GUI updated, starting mainloop...")
    print("You should see:")
    print("- RED header at top")
    print("- YELLOW main area")
    print("- BLUE left panel")
    print("- GREEN right panel with white canvas")
    print("- PURPLE footer at bottom")
    
    def on_closing():
        print("Window closing...")
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()
    print("Mainloop ended")

if __name__ == "__main__":
    create_debug_gui()







