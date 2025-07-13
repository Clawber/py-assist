import subprocess
import sys # For sys.exit()

WINDOW_TITLE = "Timetracker"

# --- Step 1: Search for the window ID ---
# Equivalent to: WID=$(xdotool search --name "$WINDOW_TITLE" 2>/dev/null)
try:
    search_result = subprocess.run(
        ['xdotool', 'search', '--name', WINDOW_TITLE],
        stdout=subprocess.PIPE,  # Capture standard output
        stderr=subprocess.DEVNULL, # Discard standard error (equivalent to 2>/dev/null)
        text=True,               # Decode output as string
        check=False              # Don't raise an exception if xdotool search returns non-zero (e.g., if window not found)
    )

    # Get the output (Window ID) and remove any leading/trailing whitespace
    WID = search_result.stdout.strip()

    if not WID:
        print(f"Window with title '{WINDOW_TITLE}' not found.")
        # Optionally, you might want to exit or handle this case differently
        # sys.exit(0) 
    else:
        # --- Step 2: Minimize the window ---
        # Equivalent to: xdotool windowminimize "$WID"
        try:
            subprocess.run(
                ['xdotool', 'windowminimize', WID],
                check=True,  # Raise an exception if the command returns a non-zero exit code
                capture_output=True, # Capture output for potential debugging
                text=True # Decode output as string
            )
            print(f"Window '{WINDOW_TITLE}' (ID: {WID}) minimized successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error minimizing window: {e}")
            print(f"Command output (stdout): {e.stdout}")
            print(f"Command output (stderr): {e.stderr}")
        except FileNotFoundError:
            print("Error: 'xdotool' command not found. Please ensure xdotool is installed.")

except FileNotFoundError:
    print("Error: 'xdotool' command not found. Please ensure xdotool is installed.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")