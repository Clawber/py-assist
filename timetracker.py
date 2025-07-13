import json
import os
from datetime import datetime
from pytz import timezone # For robust timezone handling

# --- Configuration ---
# DATA_FILE = 'time_log.json'
DATA_FILE = "/home/clawber/projects/py-assist/output/time_log.json"

# Assuming your current location is Quezon City, Metro Manila, Philippines
# which uses Asia/Manila timezone (PST is +08:00).
# You can change this to your desired timezone, e.g., 'America/New_York'
LOCAL_TIMEZONE = 'Asia/Manila' 

# --- Helper Functions ---

import os
import time

def minimize_current_terminal():
    """
    Minimizes the current terminal window using wmctrl.
    This assumes wmctrl is installed and the terminal is a 'normal' window.
    """
    try:
        # Find the active window ID
        # wmctrl -l lists all windows. Grep for "terminal" or "mint" related window titles.
        # This part might need adjustment based on your exact terminal emulator's title.
        # A more robust way is to find the window associated with the current process,
        # but that's significantly more complex. For simplicity, we'll try to find a terminal.
        
        # This command tries to find the window of the current shell.
        # It's not always reliable for all terminal emulators.
        # A more direct approach might be to target the known terminal window class or title.

        # Let's try to get the current terminal's window ID
        # This command is more reliable for the active terminal you're running in.
        # It often returns the ID of the window where 'wmctrl' itself is run.
        window_id = os.popen("xprop -root _NET_ACTIVE_WINDOW | awk '{print $NF}'").read().strip()
        
        # If the above doesn't work, you might need to manually find your terminal's exact title
        # For example, if your terminal title is "Terminal" or "user@hostname:~"
        # wmctrl -l | grep "Terminal" | awk '{print $1}' | head -n 1
        
        if window_id:
            print(f"Attempting to minimize window ID: {window_id}")
            os.system(f"wmctrl -i -b add,hidden -e 0,0,0,1,1 {window_id}")
            # -i: use window ID
            # -b add,hidden: add the 'hidden' state (minimizes it)
            # -e 0,0,0,1,1: this is a dummy geometry update to ensure the hidden state takes effect,
            #                sometimes necessary for certain window managers.
            print("Terminal window minimized (or attempted).")
        else:
            print("Could not find the current terminal window ID.")
            print("Please ensure 'wmctrl' is installed.")

    except Exception as e:
        print(f"An error occurred while trying to minimize: {e}")
        print("Ensure 'wmctrl' is installed and running in a graphical desktop environment.")



def load_data():
    """Loads existing time log data from the JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode {DATA_FILE}. Starting with an empty log.")
            return {}
    return {}

def save_data(data):
    """Saves the current time log data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_current_timestamp():
    """Returns the current datetime in ISO 8601 format with timezone offset."""
    # Get current UTC time, then convert to local timezone
    local_tz = timezone(LOCAL_TIMEZONE)
    now_local = datetime.now(local_tz)
    return now_local.isoformat()

def display_tasks(data):
    """Displays recently logged tasks."""
    if not data:
        print("\nNo tasks logged yet.")
        return

    print("\n--- Recent Tasks ---")
    # Sort by timestamp (keys are strings, so lexical sort works for ISO 8601)
    sorted_timestamps = sorted(data.keys(), reverse=True) # Show most recent first

    # Display only the last 10 tasks for brevity in terminal
    for i, ts in enumerate(sorted_timestamps):
        if i >= 10: # Limit to last 10 entries
            break
        task = data[ts]
        # Format timestamp for display (optional: parse back to datetime for friendlier display)
        try:
            dt_obj = datetime.fromisoformat(ts)
            display_ts = dt_obj.strftime("%Y-%m-%d %H:%M:%S") # e.g., "2025-06-28 03:54:02"
        except ValueError:
            display_ts = ts # Fallback if parsing fails

        print(f"[{display_ts}] {task}")
    print("--------------------\n")

# --- Main Application Logic ---

def main():
    print("--- Time Tracker App ---")
    print("Type your task and press Enter to log it.")
    print("Type 'view' to see recent tasks.")
    print("Type 'exit' to quit the application.")

    time_log = load_data()

    while True:
        task_input = input("What are you doing? > ").strip()

        if task_input.lower() == 'exit':
            print("Exiting Time Tracker. Happy tracking!")
            break
        elif task_input.lower() == 'view':
            display_tasks(time_log)
        elif task_input: # Only log if input is not empty
            timestamp = get_current_timestamp()
            time_log[timestamp] = task_input
            save_data(time_log)
            print(f"Logged: '{task_input}' at {timestamp.split('.')[0]} (approx)") # Show without microseconds for brevity
            minimize_current_terminal()
        else:
            print("Task cannot be empty. Please enter something or type 'exit'.")

if __name__ == "__main__":
    # Ensure pytz is installed: pip install pytz
    try:
        from pytz import timezone
    except ImportError:
        print("Error: 'pytz' library not found. Please install it using: pip install pytz")
        exit(1)
    
    main()