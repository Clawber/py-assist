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
        self.master.title("Persistent Popup Timer")
        self.master.geometry("350x200")

        # --- State Variables ---
        self.remaining_seconds = 0
        self.timer_running = False
        self.timer_id = None

        # --- Style Configuration ---
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("Time.TLabel", font=("Helvetica", 48, "bold"), foreground="navy")
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))

        self.create_widgets()

    def create_widgets(self):
        """Create and lay out all the GUI widgets."""
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(input_frame, text="Set timer for (minutes):").pack(side=tk.LEFT, padx=(0, 10))
        self.entry = ttk.Entry(input_frame, width=10)
        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.entry.focus_set()

        self.time_label = ttk.Label(main_frame, text="00:00", style="Time.TLabel")
        self.time_label.pack(pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=5, fill=tk.X)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

    def start_timer(self):
        """Starts the countdown timer."""
        if self.timer_running: return
        try:
            minutes = float(self.entry.get())
            if minutes <= 0: raise ValueError
            self.remaining_seconds = int(minutes * 60)
        except (ValueError, TypeError):
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for minutes.")
            return

        self.timer_running = True
        self.toggle_controls(active=False)
        self.update_countdown()
        
    def stop_timer(self):
        """Stops the currently running timer."""
        if self.timer_running and self.timer_id:
            self.master.after_cancel(self.timer_id)
        
        self.timer_running = False
        self.remaining_seconds = 0
        self.time_label.config(text="00:00")
        self.toggle_controls(active=True)

    def toggle_controls(self, active):
        """Enable or disable controls based on timer state."""
        state = tk.NORMAL if active else tk.DISABLED
        self.entry.config(state=state)
        self.start_button.config(state=state)
        self.stop_button.config(state=tk.NORMAL if not active else tk.DISABLED)

    def update_countdown(self):
        """The main loop that updates the timer every second."""
        if self.timer_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            mins, secs = divmod(self.remaining_seconds, 60)
            self.time_label.config(text=f"{mins:02d}:{secs:02d}")
            self.timer_id = self.master.after(1000, self.update_countdown)
        elif self.timer_running and self.remaining_seconds == 0:
            self.time_label.config(text="Done!")
            self.trigger_alarm()
            self.stop_timer()

    def trigger_alarm(self):
        """Handles the entire alarm sequence: sound, and a persistent pop-up."""
        print("ALARM! Time's up.")
        
        # --- Play Sound in a separate thread to not block the GUI ---
        def play_sound_task():
            try:
                if os.path.exists(ALARM_SOUND_FILE):
                    playsound(ALARM_SOUND_FILE)
                else:
                    print(f"Warning: Alarm sound file not found: '{ALARM_SOUND_FILE}'")
                    # Fallback system beep for Linux
                    os.system('beep -f 500 -l 400 &') 
            except Exception as e:
                print(f"Error playing sound: {e}")
        
        sound_thread = threading.Thread(target=play_sound_task, daemon=True)
        sound_thread.start()

        # --- Force Window to Front and Demand Attention ---
        self.force_window_to_front()

    def force_window_to_front(self):
        """
        This is the key function to make the window appear and stay.
        It brings the window to the front and shows a modal dialog.
        """
        # 1. Restore the window if it's minimized (iconified)
        self.master.deiconify()

        # 2. Lift the window to the top of the stacking order
        self.master.lift()
        
        # 3. Force the window to stay on top of all other windows
        self.master.attributes('-topmost', True)

        # 4. Forcefully grab focus
        self.master.focus_force()

        # 5. Show a blocking message box. The code will PAUSE here until
        #    the user clicks "OK". This is our dismissal mechanism.
        messagebox.showinfo(
            title="Time's Up!",
            message=f"Your timer has finished.\nPress OK to dismiss."
        )

        # 6. Once the user clicks "OK", turn off the "topmost" attribute
        #    so the window behaves normally again.
        self.master.attributes('-topmost', False)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()