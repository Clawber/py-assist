'''
which library to use
create a window, gets user input, prints user input to terminal

first script print command

autocomplete, suggestions

alarm function
function to add to brain dump

how to use fzf for this??



timer
edit braindump

clock 60


alarm sound
'''


import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from playsound import playsound
import os

# --- Configuration ---
ALARM_SOUND_FILE = "alarm-rooster.wav" 

class TimerApp:
    def __init__(self, master):
        """Initialize the Timer Application."""
        self.master = master
        self.master.title("Popup Timer")
        self.master.geometry("350x200")

        # --- State Variables ---
        self.remaining_seconds = 0
        self.timer_running = False
        self.timer_id = None # To store the ID of the 'after' job

        # --- Style Configuration ---
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("Time.TLabel", font=("Helvetica", 48, "bold"), foreground="navy")
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))

        # --- Create and place widgets ---
        self.create_widgets()

    def create_widgets(self):
        """Create and lay out all the GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input row
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(input_frame, text="Set timer for (minutes):").pack(side=tk.LEFT, padx=(0, 10))
        self.entry = ttk.Entry(input_frame, width=10)
        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.entry.focus_set() # Put cursor in entry box on start

        # Time display label
        self.time_label = ttk.Label(main_frame, text="00:00", style="Time.TLabel")
        self.time_label.pack(pady=10)

        # Buttons row
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=5, fill=tk.X)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

    def start_timer(self):
        """Starts the countdown timer."""
        if self.timer_running:
            return # Don't do anything if timer is already running

        try:
            # Get time in minutes and convert to seconds
            minutes = float(self.entry.get())
            if minutes <= 0:
                raise ValueError("Time must be a positive number.")
            self.remaining_seconds = int(minutes * 60)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for minutes.")
            return

        self.timer_running = True
        self.toggle_controls(active=False)
        self.update_countdown()
        
    def stop_timer(self):
        """Stops the currently running timer."""
        if self.timer_running and self.timer_id:
            self.master.after_cancel(self.timer_id) # Stop the scheduled 'after' job
        
        self.timer_running = False
        self.remaining_seconds = 0
        self.time_label.config(text="00:00")
        self.toggle_controls(active=True)

    def toggle_controls(self, active):
        """Enable or disable controls based on timer state."""
        if active:
            self.entry.config(state=tk.NORMAL)
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
        else: # Timer is running
            self.entry.config(state=tk.DISABLED)
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)


    def update_countdown(self):
        """The main loop that updates the timer every second."""
        if self.timer_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            # Format time as MM:SS
            mins, secs = divmod(self.remaining_seconds, 60)
            self.time_label.config(text=f"{mins:02d}:{secs:02d}")
            
            # Schedule this method to be called again after 1000ms (1 second)
            self.timer_id = self.master.after(1000, self.update_countdown)
        elif self.timer_running and self.remaining_seconds == 0:
            # Time's up!
            self.time_label.config(text="Done!")
            self.trigger_alarm()
            self.stop_timer() # Reset the state

    def trigger_alarm(self):
        """Brings window to front and plays the alarm sound."""
        print("ALARM! Time's up.")
        
        # --- Bring Window to Front ---
        # This makes the window pop up and steal focus
        self.master.lift()
        self.master.attributes('-topmost', True)
        self.master.after(100, lambda: self.master.attributes('-topmost', False))

        # --- Play Sound ---
        # Play sound in a separate thread to avoid freezing the GUI
        def play_sound_task():
            try:
                if os.path.exists(ALARM_SOUND_FILE):
                    playsound(ALARM_SOUND_FILE)
                else:
                    print(f"Warning: Alarm sound file not found at '{ALARM_SOUND_FILE}'")
                    # On Linux, you can make a system beep as a fallback
                    # This requires the 'beep' command to be installed
                    os.system('beep -f 500 -l 400') 
            except Exception as e:
                print(f"Error playing sound: {e}")
                messagebox.showwarning("Sound Error", f"Could not play alarm sound.\nError: {e}")
        
        sound_thread = threading.Thread(target=play_sound_task)
        sound_thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()