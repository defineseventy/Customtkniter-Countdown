#Making a tkinter countdown timer
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import time
import threading
import json
import os
import pygame

#init audio
pygame.mixer.init()
ALARM = "stuff for alarms/alarm-327234.mp3"

#have a file to store the last timer
SAVE_FILE = "last_timer.json"

#set appearance and default colour
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

#crerate a Countdown class (used for app)
class Countdown(ctk.CTk):
    def __init__(self):
        super().__init__()

        #create title, window size
        self.title("Countdown Timer with an hourglass")
        self.geometry("400x450")

        #set the timer running 
        self.timer_running = False
        self.timer_paused = False
        self.remaining_seconds = 0
        self.total_seconds = 0

        #have a gif 
        self.gif_frames = []
        self.gif_index = 0
        self.animating = False

        #call functions
        self.load_last_timer()
        self.create_widgets()
        self.load_gif()
    
    def create_widgets(self):
        self.entry_label = ctk.CTkLabel(self, text="Enter time in (hh:mm:ss):")
        self.entry_label.pack(pady = (20, 5))

        #have a placeholder text
        self.time_entry = ctk.CTkEntry(self, placeholder_text="00:01:00")
        self.time_entry.pack (pady=15)
        self.time_entry.insert(0, self.seconds_to_hms(self.total_seconds))

        #have button frames
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady= 10)

        self.start_button = ctk.CTkButton(self.button_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = ctk.CTkButton(self.button_frame, text="Pause", command=self.pause_resume_timer, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=5)

        self.reset_button = ctk.CTkButton(self.button_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=2, padx=5)

        self.theme_button = ctk.CTkButton(self, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.pack(pady=10)

        self.time_display = ctk.CTkLabel(self, text="00:00:00", font=("Arial", 40))
        self.time_display.pack(pady=20)

        self.canvas = tk.Canvas(self, width=150, height=150, highlightthickness=0, bg=self.cget("bg"))
        self.canvas.pack(pady=10)

        self.gif_label = tk.Label(self.canvas, bd=0)
        self.gif_label.pack()
    def toggle_theme(self):
        curr = ctk.get_appearance_mode()
        ctk.set_appearance_mode("dark" if curr == "Light" else "light")

    def load_gif(self):
        gif = Image.open("stuff for alarms/time-times-up.gif")
        self.gif_frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(gif)]
    
    def animate_gif(self):
        if not self.animating or not self.gif_frames:
            return
        self.gif_label.config(image=self.gif_frames[self.gif_index])
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.after(100, self.animate_gif)
    
    def hms_to_seconds(self, time_str):
        try:
            parts = list(map(int, time_str.split(":")))
            while len(parts) < 3:
                parts.insert(0, 0)
            h, m, s = parts
            return h * 3600 + m * 60 + s
        except:
            return None

    def seconds_to_hms(self, seconds):
        h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
        return f"{h:02}:{m:02}:{s:02}"

    def start_timer(self):
        if self.timer_running:
            return

        time_input = self.time_entry.get()
        self.total_seconds = self.hms_to_seconds(time_input)
        if self.total_seconds is None or self.total_seconds <= 0:
            self.time_display.configure(text="Invalid")
            return

        self.remaining_seconds = self.total_seconds
        self.save_last_timer()

        self.timer_running = True
        self.timer_paused = False
        self.animating = True
        self.animate_gif()
        self.pause_button.configure(state="normal", text="Pause")
        threading.Thread(target=self.run_timer, daemon=True).start()

    def pause_resume_timer(self):
        if not self.timer_running:
            return

        self.timer_paused = not self.timer_paused
        self.pause_button.configure(text="Resume" if self.timer_paused else "Pause")

    def reset_timer(self):
        self.timer_running = False
        self.timer_paused = False
        self.animating = False
        self.gif_label.config(image="")
        self.time_display.configure(text="00:00:00")
        self.pause_button.configure(state="disabled", text="Pause")

    def run_timer(self):
        while self.remaining_seconds > 0 and self.timer_running:
            if not self.timer_paused:
                mins, secs = divmod(self.remaining_seconds, 60)
                time_str = self.seconds_to_hms(self.remaining_seconds)
                self.time_display.configure(text=time_str)
                time.sleep(1)
                self.remaining_seconds -= 1
            else:
                time.sleep(0.1)

        if self.remaining_seconds <= 0 and self.timer_running:
            self.time_display.configure(text="Time's up!")
            self.play_alarm()

        self.timer_running = False
        self.animating = False
        self.pause_button.configure(state="disabled", text="Pause")

    def play_alarm(self):
        pygame.mixer.music.load(ALARM)
        pygame.mixer.music.play()

    def save_last_timer(self):
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump({"last_timer": self.total_seconds}, f)
        except Exception as e:
            print("Error saving timer:", e)

    def load_last_timer(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    data = json.load(f)
                    self.total_seconds = data.get("last_timer", 0)
            except:
                self.total_seconds = 0


if __name__ == "__main__":
    app = Countdown()
    app.mainloop()