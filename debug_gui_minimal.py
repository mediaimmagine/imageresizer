#!/usr/bin/env python3
"""
Minimal GUI Debug - Test what's actually rendering on macOS
"""

import tkinter as tk
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
    root.geometry("600x400")
    
    # Test 1: Basic label
    print("1. Creating basic label...")
    label1 = tk.Label(root, text="TEST LABEL 1 - Basic", fg="red", bg="yellow")
    label1.pack(pady=10)
    
    # Test 2: Label with explicit font
    print("2. Creating label with font...")
    label2 = tk.Label(root, text="TEST LABEL 2 - With Font", font=("Arial", 16, "bold"), fg="blue", bg="lightgreen")
    label2.pack(pady=10)
    
    # Test 3: Frame with background
    print("3. Creating frame with background...")
    frame1 = tk.Frame(root, bg="purple", height=50)
    frame1.pack(fill=tk.X, pady=10)
    frame1.pack_propagate(False)
    
    label3 = tk.Label(frame1, text="TEST LABEL 3 - In Frame", fg="white", bg="purple")
    label3.pack(pady=10)
    
    # Test 4: Button
    print("4. Creating button...")
    button1 = tk.Button(root, text="TEST BUTTON", bg="orange", fg="white", font=("Arial", 12, "bold"))
    button1.pack(pady=10)
    
    # Test 5: Canvas
    print("5. Creating canvas...")
    canvas1 = tk.Canvas(root, bg="lightblue", height=100)
    canvas1.pack(fill=tk.X, pady=10)
    canvas1.create_text(50, 50, text="CANVAS TEXT", fill="red", font=("Arial", 14, "bold"))
    
    # Test 6: Entry
    print("6. Creating entry...")
    entry1 = tk.Entry(root, font=("Arial", 12))
    entry1.pack(pady=10)
    entry1.insert(0, "TEST ENTRY TEXT")
    
    # Test 7: Checkbox
    print("7. Creating checkbox...")
    var1 = tk.BooleanVar()
    check1 = tk.Checkbutton(root, text="TEST CHECKBOX", variable=var1, font=("Arial", 12))
    check1.pack(pady=10)
    
    # Test 8: Radio button
    print("8. Creating radio button...")
    var2 = tk.StringVar(value="option1")
    radio1 = tk.Radiobutton(root, text="TEST RADIO 1", variable=var2, value="option1", font=("Arial", 12))
    radio1.pack(pady=5)
    radio2 = tk.Radiobutton(root, text="TEST RADIO 2", variable=var2, value="option2", font=("Arial", 12))
    radio2.pack(pady=5)
    
    # Test 9: Scale
    print("9. Creating scale...")
    scale1 = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
    scale1.pack(pady=10)
    
    # Test 10: Listbox
    print("10. Creating listbox...")
    listbox1 = tk.Listbox(root, height=3)
    listbox1.pack(pady=10)
    listbox1.insert(0, "TEST ITEM 1")
    listbox1.insert(1, "TEST ITEM 2")
    listbox1.insert(2, "TEST ITEM 3")
    
    # Test 11: Text widget
    print("11. Creating text widget...")
    text1 = tk.Text(root, height=3, width=50)
    text1.pack(pady=10)
    text1.insert(tk.END, "TEST TEXT WIDGET\nLine 2\nLine 3")
    
    # Test 12: Menu
    print("12. Creating menu...")
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Test Item", command=lambda: print("Menu clicked!"))
    
    # Test 13: Message box
    print("13. Testing message box...")
    def show_message():
        tk.messagebox.showinfo("Test", "This is a test message box!")
    
    button2 = tk.Button(root, text="Show Message", command=show_message, bg="green", fg="white")
    button2.pack(pady=10)
    
    # Test 14: File dialog
    print("14. Testing file dialog...")
    def open_file():
        filename = tk.filedialog.askopenfilename()
        print(f"Selected file: {filename}")
    
    button3 = tk.Button(root, text="Open File", command=open_file, bg="blue", fg="white")
    button3.pack(pady=10)
    
    # Test 15: Progress bar
    print("15. Creating progress bar...")
    progress = tk.ttk.Progressbar(root, mode='indeterminate')
    progress.pack(pady=10)
    progress.start()
    
    # Test 16: Notebook (tabs)
    print("16. Creating notebook...")
    notebook = tk.ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, pady=10)
    
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text="Tab 1")
    tk.Label(tab1, text="TAB 1 CONTENT", font=("Arial", 14, "bold")).pack(pady=20)
    
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text="Tab 2")
    tk.Label(tab2, text="TAB 2 CONTENT", font=("Arial", 14, "bold")).pack(pady=20)
    
    # Test 17: Treeview
    print("17. Creating treeview...")
    tree = tk.ttk.Treeview(root)
    tree.pack(fill=tk.BOTH, expand=True, pady=10)
    tree.insert("", "end", text="Item 1")
    tree.insert("", "end", text="Item 2")
    tree.insert("", "end", text="Item 3")
    
    # Test 18: Spinbox
    print("18. Creating spinbox...")
    spinbox1 = tk.Spinbox(root, from_=0, to=100)
    spinbox1.pack(pady=10)
    
    # Test 19: LabelFrame
    print("19. Creating label frame...")
    labelframe1 = tk.LabelFrame(root, text="TEST LABEL FRAME", font=("Arial", 12, "bold"))
    labelframe1.pack(fill=tk.X, pady=10)
    tk.Label(labelframe1, text="Content in label frame", font=("Arial", 10)).pack(pady=5)
    
    # Test 20: PanedWindow
    print("20. Creating paned window...")
    paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True, pady=10)
    
    left_pane = tk.Frame(paned, bg="lightcoral")
    right_pane = tk.Frame(paned, bg="lightcyan")
    
    paned.add(left_pane, weight=1)
    paned.add(right_pane, weight=1)
    
    tk.Label(left_pane, text="LEFT PANE", font=("Arial", 12, "bold")).pack(pady=20)
    tk.Label(right_pane, text="RIGHT PANE", font=("Arial", 12, "bold")).pack(pady=20)
    
    print("All elements created. Starting mainloop...")
    print("You should see:")
    print("- Red label on yellow background")
    print("- Blue label with font on light green background")
    print("- Purple frame with white text")
    print("- Orange button")
    print("- Light blue canvas with red text")
    print("- Entry field with text")
    print("- Checkbox")
    print("- Radio buttons")
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









