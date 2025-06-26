import tkinter as tk
from tkinter import ttk

# --- The dictionary of commands ---
# The keys are what the user will type and what will be suggested.
# The values could be anything (e.g., functions, descriptions, etc.).
COMMANDS = {
    "show status": "Display the current system status.",
    "show version": "Display the application version.",
    "set user": "Set the current user context.",
    "set log_level": "Change the logging verbosity (debug, info, warn, error).",
    "reboot system": "Initiate a system reboot.",
    "reboot device": "Reboot a specific attached device.",
    "exit": "Exit the application.",
    "help": "Show this help message.",
}

def fuzzy_match(query, text):
    """
    Checks if all characters in the query appear in the text in the correct order.

    Args:
        query (str): The search string (e.g., "sv").
        text (str): The string to search within (e.g., "show version").

    Returns:
        bool: True if it's a fuzzy match, False otherwise.
    """
    query = query.lower()
    text = text.lower()
    
    # Use an iterator to avoid re-scanning the string
    it = iter(text)
    
    # Check if for each character in the query, you can find it in the
    # remainder of the text iterator.
    return all(char in it for char in query)

class AutocompleteEntry(ttk.Entry):
    """
    A ttk.Entry widget that displays a dropdown list of suggestions
    as the user types.
    """
    def __init__(self, master, autocomplete_list, **kwargs):
        super().__init__(master, **kwargs)

        self.autocomplete_list = autocomplete_list
        self._listbox = None
        
        # --- Bind events ---
        # When a key is released, update the suggestion list.
        self.bind("<KeyRelease>", self._on_key_release)
        # When the user navigates with arrow keys or Enter.
        self.bind("<Down>", self._on_arrow_down)
        self.bind("<Up>", self._on_arrow_up)
        self.bind("<Return>", self._on_enter)
        # When the user clicks away, hide the listbox.
        self.bind("<FocusOut>", self._hide_listbox)
        self.bind("<Escape>", self._hide_listbox)

    def _create_listbox(self):
        """Creates and places the listbox for suggestions."""
        if self._listbox is None:
            # The listbox needs to be a Toplevel window's child to float over others
            toplevel = self.winfo_toplevel()
            self._listbox = tk.Listbox(toplevel, font=("Helvetica", 12), highlightthickness=0)
            
            # When an item is selected in the listbox (e.g., by clicking)
            self._listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
            self._listbox.bind("<Button-1>", self._on_listbox_select) # For single click selection

    def _show_listbox(self):
        """Calculates position and displays the listbox."""
        if self._listbox is None:
            self._create_listbox()

        # Get position of the entry widget
        x = self.winfo_x()
        y = self.winfo_y()
        height = self.winfo_height()
        width = self.winfo_width()
        
        # Use .place() to position the listbox just below the entry
        self._listbox.place(x=x, y=y + height, width=width)
        self.focus_set() # Keep focus on the entry widget

    def _hide_listbox(self, event=None):
        """Hides the listbox."""
        if self._listbox is not None:
            self._listbox.place_forget()

    def _on_key_release(self, event):
        """Handles updating the suggestion list as the user types."""
        # Ignore control keys that don't change the text
        if event.keysym in ("Down", "Up", "Return", "Escape"):
            return

        current_text = self.get().lower()

        # If the entry is empty, hide the listbox
        if not current_text:
            self._hide_listbox()
            return

        # Find matches
        matches = [cmd for cmd in self.autocomplete_list if fuzzy_match(current_text, cmd)]
        matches.sort(key=lambda cmd: (not cmd.lower().startswith(current_text), len(cmd)))

        if matches:
            self._show_listbox()
            self._listbox.delete(0, tk.END)
            for item in matches:
                self._listbox.insert(tk.END, item)
        else:
            self._hide_listbox()
    
    def _on_arrow_down(self, event):
        """Handles the Down arrow key to navigate the listbox."""
        if self._listbox and self._listbox.winfo_viewable():
            current_selection = self._listbox.curselection()
            
            if not current_selection: # If nothing is selected
                next_index = 0
            else:
                next_index = current_selection[0] + 1
            
            if next_index < self._listbox.size():
                self._listbox.selection_clear(0, tk.END)
                self._listbox.selection_set(next_index)
                self._listbox.activate(next_index)
            
            # This prevents the default Entry behavior (moving the cursor)
            return "break"

    def _on_arrow_up(self, event):
        """Handles the Up arrow key to navigate the listbox."""
        if self._listbox and self._listbox.winfo_viewable():
            current_selection = self._listbox.curselection()
            
            if not current_selection: # If nothing is selected
                next_index = tk.END
            else:
                next_index = current_selection[0] - 1
            
            if next_index >= 0:
                self._listbox.selection_clear(0, tk.END)
                self._listbox.selection_set(next_index)
                self._listbox.activate(next_index)
            
            return "break"

    def _on_enter(self, event):
        """Handles the Enter key to select an item or submit the command."""
        # If the listbox is visible and an item is selected
        if self._listbox and self._listbox.winfo_viewable() and self._listbox.curselection():
            self._select_item()
            return "break"  # Prevents the default Enter key behavior
        
        # Otherwise, submit the command currently in the entry
        self._submit_command()
        
    def _on_listbox_select(self, event):
        """Handles selecting an item from the listbox (e.g., with a click)."""
        self._select_item()

    def _select_item(self):
        """Fills the entry with the selected item from the listbox."""
        if not self._listbox.curselection():
            return
            
        selected_text = self._listbox.get(self._listbox.curselection())
        
        self.delete(0, tk.END)
        self.insert(0, selected_text)
        self.icursor(tk.END) # Move cursor to the end
        self._hide_listbox()

    def _submit_command(self):
        """Finalizes the command, prints it, and clears the entry."""
        command = self.get()
        if command:
            print(f"Executing command: '{command}'")
            # You could add logic here to look up the command in the dictionary
            # and actually run a function associated with it.
            # e.g., command_function = COMMANDS[command] -> command_function()
            
            self.delete(0, tk.END) # Clear for next command
            self._hide_listbox()

# --- Main Application Setup ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Autocomplete Command Entry")
    root.geometry("450x200")

    # Use the keys from our dictionary as the list of possible completions
    command_list = list(COMMANDS.keys())

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        main_frame,
        text="Enter a command:",
        font=("Helvetica", 14, "bold")
    ).pack(pady=(0, 10))

    # Create and place our custom AutocompleteEntry widget
    entry = AutocompleteEntry(
        main_frame,
        autocomplete_list=command_list,
        font=("Helvetica", 14)
    )
    entry.pack(fill=tk.X, expand=True)
    entry.focus_set() # Start with the cursor in the entry box

    root.mainloop()