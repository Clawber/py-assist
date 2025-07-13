#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import re

folder_location = "/home/clawber/projects/py-assist/output/"

filenames_dict = {
    'u': 'urgent', 
    'd': 'do', 
    'l': 'lessons', 
    'c': 'create', 
    'e': 'experiences', 
    'b': 'bored', 
    'w': 'wins',
    'x': 'deleted',
    'q': 'questions'
}


class LineSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Line Sorter")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.lines = []
        self.current_line = 0
        self.current_file = None
        self.modified = False
        
        # Create menu
        self.create_menu()
        
        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File info label
        self.file_label = tk.Label(main_frame, text="No file loaded", 
                                  font=("Arial", 10, "bold"))
        self.file_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Instructions
        instructions = tk.Label(main_frame, 
                               text="Instructions: Use ↑/↓ arrows to navigate, press any letter (a-z) to sort line into file",
                               font=("Arial", 9))
        instructions.pack(anchor=tk.W, pady=(0, 10))
        
        # Text display area
        self.text_area = scrolledtext.ScrolledText(main_frame, 
                                                  wrap=tk.WORD, 
                                                  font=("Consolas", 11),
                                                  height=25)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Ready", 
                                    font=("Arial", 9), 
                                    relief=tk.SUNKEN, 
                                    anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
        # Bind keyboard events
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()
        
        # Configure text tags for highlighting
        self.text_area.tag_config("highlight", background="yellow", foreground="black")
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.lines = content.splitlines()
                    self.current_file = file_path
                    self.current_line = 0
                    self.modified = False
                    
                    # Update file label
                    filename = os.path.basename(file_path)
                    self.file_label.config(text=f"File: {filename} ({len(self.lines)} lines)")
                    
                    # Display content
                    self.display_content()
                    self.update_status(f"Loaded {len(self.lines)} lines from {filename}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        if not self.current_file:
            return
            
        try:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                if self.lines:
                    file.write('\n'.join(self.lines) + '\n')
                # If no lines left, create empty file
            
            self.modified = False
            self.update_status("File saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def display_content(self):
        if not self.lines:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, "No content to display")
            return
        
        # Clear existing content
        self.text_area.delete(1.0, tk.END)
        
        # Insert all lines
        for i, line in enumerate(self.lines):
            self.text_area.insert(tk.END, f"{i+1:4d}: {line}\n")
        
        # Highlight current line
        self.highlight_current_line()
    
    def highlight_current_line(self):
        if not self.lines:
            return
        
        # Clear previous highlights
        self.text_area.tag_remove("highlight", 1.0, tk.END)
        
        # Highlight current line
        line_start = f"{self.current_line + 1}.0"
        line_end = f"{self.current_line + 1}.end"
        self.text_area.tag_add("highlight", line_start, line_end)
        
        # Scroll to make sure the line is visible
        self.text_area.see(line_start)
    
    def on_key_press(self, event):
        if not self.lines:
            return
        
        key = event.keysym
        
        # Handle arrow keys for navigation
        if key == 'Up':
            if self.current_line > 0:
                self.current_line -= 1
                self.highlight_current_line()
                self.update_status(f"Line {self.current_line + 1} of {len(self.lines)}")
        
        elif key == 'Down':
            if self.current_line < len(self.lines) - 1:
                self.current_line += 1
                self.highlight_current_line()
                self.update_status(f"Line {self.current_line + 1} of {len(self.lines)}")
        
        # Handle letter keys for sorting
        elif len(key) == 1 and key.isalpha():
            self.sort_line_to_file(key.lower())
    
    def sort_line_to_file(self, letter):
        if not self.lines or self.current_line >= len(self.lines):
            return
        
        # Get the line to move
        line_to_move = self.lines[self.current_line]
        
        # Create filename
        filename = f"stored{letter.upper()}.txt"
        
        try:
            # Append line to the target file
            with open(filename, 'a', encoding='utf-8') as file:
                file.write(line_to_move + '\n')
            
            # Remove line from current content
            self.lines.pop(self.current_line)
            self.modified = True
            
            # Adjust current line position
            if self.current_line >= len(self.lines) and self.lines:
                self.current_line = len(self.lines) - 1
            elif not self.lines:
                self.current_line = 0
            
            # Update display
            self.display_content()
            
            # Update file label
            if self.current_file:
                filename_display = os.path.basename(self.current_file)
                self.file_label.config(text=f"File: {filename_display} ({len(self.lines)} lines) *")
            
            self.update_status(f"Line moved to {filename}. {len(self.lines)} lines remaining.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not write to {filename}: {str(e)}")
    
    def on_exit(self):
        # Save file if modified before exiting
        if self.modified and self.current_file:
            self.save_file()
        self.root.quit()
    
    def on_exit(self):
        # Save file if modified before exiting
        if self.modified and self.current_file:
            self.save_file()
        self.root.quit()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.after(3000, lambda: self.status_label.config(text="Ready"))

def main():
    root = tk.Tk()
    app = LineSorterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()