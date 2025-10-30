#!/usr/bin/env python3
"""
Final GUI Debug - Test what's actually rendering on macOS
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# macOS-specific fixes
if sys.platform == "darwin":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

def test_basic_elements():
    """Test basic Tkinter elements one by one"""
    print("Creating basic Tkinter test...")
    
    root = tk.Tk()
    root.title("GUI Debug Test")
    root.geometry("800x600")
    
    # Test 1: Basic label
    print("1. Creating basic label...")
    label1 = tk.Label(root, text="TEST LABEL 1 - Basic", fg="red", bg="yellow", font=("Arial", 14, "bold"))
    label1.pack(pady=10)
    
    # Test 2: Frame with background
    print("2. Creating frame with background...")
    frame1 = tk.Frame(root, bg="purple", height=50)
    frame1.pack(fill=tk.X, pady=10)
    frame1.pack_propagate(False)
    
    label2 = tk.Label(frame1, text="TEST LABEL 2 - In Purple Frame", fg="white", bg="purple", font=("Arial", 12, "bold"))
    label2.pack(pady=10)
    
    # Test 3: Button
    print("3. Creating button...")
    button1 = tk.Button(root, text="TEST BUTTON", bg="orange", fg="white", font=("Arial", 12, "bold"))
    button1.pack(pady=10)
    
    # Test 4: Canvas
    print("4. Creating canvas...")
    canvas1 = tk.Canvas(root, bg="lightblue", height=100)
    canvas1.pack(fill=tk.X, pady=10)
    canvas1.create_text(50, 50, text="CANVAS TEXT", fill="red", font=("Arial", 14, "bold"))
    
    # Test 5: Entry
    print("5. Creating entry...")
    entry1 = tk.Entry(root, font=("Arial", 12))
    entry1.pack(pady=10)
    entry1.insert(0, "TEST ENTRY TEXT")
    
    # Test 6: Checkbox
    print("6. Creating checkbox...")
    var1 = tk.BooleanVar()
    check1 = tk.Checkbutton(root, text="TEST CHECKBOX", variable=var1, font=("Arial", 12))
    check1.pack(pady=10)
    
    # Test 7: Scale
    print("7. Creating scale...")
    scale1 = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
    scale1.pack(pady=10)
    
    # Test 8: Listbox
    print("8. Creating listbox...")
    listbox1 = tk.Listbox(root, height=3)
    listbox1.pack(pady=10)
    listbox1.insert(0, "TEST ITEM 1")
    listbox1.insert(1, "TEST ITEM 2")
    listbox1.insert(2, "TEST ITEM 3")
    
    # Test 9: Text widget
    print("9. Creating text widget...")
    text1 = tk.Text(root, height=3, width=50)
    text1.pack(pady=10)
    text1.insert(tk.END, "TEST TEXT WIDGET\nLine 2\nLine 3")
    
    # Test 10: Menu
    print("10. Creating menu...")
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Test Item", command=lambda: print("Menu clicked!"))
    
    # Test 11: Message box
    print("11. Testing message box...")
    def show_message():
        tk.messagebox.showinfo("Test", "This is a test message box!")
    
    button2 = tk.Button(root, text="Show Message", command=show_message, bg="green", fg="white")
    button2.pack(pady=10)
    
    # Test 12: File dialog
    print("12. Testing file dialog...")
    def open_file():
        filename = tk.filedialog.askopenfilename()
        print(f"Selected file: {filename}")
    
    button3 = tk.Button(root, text="Open File", command=open_file, bg="blue", fg="white")
    button3.pack(pady=10)
    
    # Test 13: Progress bar
    print("13. Creating progress bar...")
    progress = ttk.Progressbar(root, mode='indeterminate')
    progress.pack(pady=10)
    progress.start()
    
    # Test 14: Notebook (tabs)
    print("14. Creating notebook...")
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, pady=10)
    
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text="Tab 1")
    tk.Label(tab1, text="TAB 1 CONTENT", font=("Arial", 14, "bold")).pack(pady=20)
    
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text="Tab 2")
    tk.Label(tab2, text="TAB 2 CONTENT", font=("Arial", 14, "bold")).pack(pady=20)
    
    # Test 15: Treeview
    print("15. Creating treeview...")
    tree = ttk.Treeview(root)
    tree.pack(fill=tk.BOTH, expand=True, pady=10)
    tree.insert("", "end", text="Item 1")
    tree.insert("", "end", text="Item 2")
    tree.insert("", "end", text="Item 3")
    
    # Test 16: Spinbox
    print("16. Creating spinbox...")
    spinbox1 = tk.Spinbox(root, from_=0, to=100)
    spinbox1.pack(pady=10)
    
    # Test 17: LabelFrame
    print("17. Creating label frame...")
    labelframe1 = tk.LabelFrame(root, text="TEST LABEL FRAME", font=("Arial", 12, "bold"))
    labelframe1.pack(fill=tk.X, pady=10)
    tk.Label(labelframe1, text="Content in label frame", font=("Arial", 10)).pack(pady=5)
    
    # Test 18: PanedWindow (fixed)
    print("18. Creating paned window...")
    paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True, pady=10)
    
    left_pane = tk.Frame(paned, bg="lightcoral")
    right_pane = tk.Frame(paned, bg="lightcyan")
    
    paned.add(left_pane)
    paned.add(right_pane)
    
    tk.Label(left_pane, text="LEFT PANE", font=("Arial", 12, "bold")).pack(pady=20)
    tk.Label(right_pane, text="RIGHT PANE", font=("Arial", 12, "bold")).pack(pady=20)
    
    print("All elements created. Starting mainloop...")
    print("You should see:")
    print("- Red label on yellow background")
    print("- Purple frame with white text")
    print("- Orange button")
    print("- Light blue canvas with red text")
    print("- Entry field with text")
    print("- Checkbox")
    print("- Scale slider")
    print("- Listbox with items")
    print("- Text widget with content")
    print("- Menu bar with File menu")
    print("- Green and blue buttons")
    print("- Progress bar")
    print("- Notebook with tabs")
    print("- Treeview with items")
    print("- Spinbox")
    print("- Label frame")
    print("- Paned window with left and right panes")
    
    root.mainloop()
    print("GUI closed.")

if __name__ == "__main__":
    test_basic_elements()







