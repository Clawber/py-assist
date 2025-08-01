#!/bin/bash

# --- Configuration ---
# The exact command to run your Python script. Use 'python3' and the full path.
PYTHON_SCRIPT_COMMAND="python3 /home/clawber/projects/py-assist/timetracker.py"

# This is the title you want your terminal window to have.
# Make sure it's unique and specific.
WINDOW_TITLE="Timetracker script"

# Your preferred terminal emulator. Common options:
# gnome-terminal (Cinnamon default)
# mate-terminal (MATE default)
# alacritty
# kitty
# xfce4-terminal
TERMINAL_EMULATOR="gnome-terminal"
# ---------------------

# Get the Window ID (WID) of the terminal running your script, if it's open
# We use --name with the exact WINDOW_TITLE we set when launching.
WID=$(xdotool search --name "$WINDOW_TITLE" 2>/dev/null)

if [ -z "$WID" ]; then
    # Window not found, so launch the script in a new terminal
    # Use the -e flag to execute the command, and --title to set the window title.
    # The 'bash -c ...; exec bash' part ensures the terminal stays open after your Python script finishes.
    "$TERMINAL_EMULATOR" --title="$WINDOW_TITLE" -e "bash -c '$PYTHON_SCRIPT_COMMAND; exec bash'" &
else
    # Window found, check if it's currently active (focused)
    ACTIVE_WID=$(xdotool getactivewindow)

    if [ "$WID" = "$ACTIVE_WID" ]; then
        # Script's terminal is active, minimize it
        xdotool windowminimize "$WID"
    else
        # Script's terminal exists but is not active, restore/activate it
        xdotool windowactivate "$WID"
        xdotool windowraise "$WID" # Bring it to the front
    fi
fi