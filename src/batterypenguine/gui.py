import tkinter as tk
from . import config

class BatteryMonitorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Battery+Network")
        self.root.geometry(f"{config.WIDTH}x{config.HEIGHT_FULL}")
        self.root.configure(bg=config.BG_COLOR)
        self.root.wm_attributes('-alpha', 0.5)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"+{screen_width - 350}+0")

        self.canvas = tk.Canvas(
            self.root,
            width=config.WIDTH,
            height=config.HEIGHT_FULL,
            bg=config.BG_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.label = tk.Label(
            self.canvas,
            text="",
            font=("Segoe UI", 12, "bold"),
            fg=config.TEXT_COLOR,
            bg=config.BG_COLOR
        )
        self.label.place(x=10, y=10, anchor="w")

        self.toggle_root = tk.Toplevel(self.root)
        self.toggle_root.overrideredirect(True)
        self.toggle_root.wm_attributes('-alpha', 0.5)
        self.toggle_root.attributes("-topmost", True)
        self.toggle_root.geometry(f"15x8+{screen_width - 350 - 15}+0")
        self.toggle_root.configure(bg=config.BG_COLOR)

        self.toggle_canvas = tk.Canvas(
            self.toggle_root,
            width=15,
            height=8,
            bg=config.BG_COLOR,
            highlightthickness=0
        )
        self.toggle_canvas.pack()

        self.toggle_canvas.create_rectangle(
            0, 0, 15, 8,
            fill="gray30",
            outline="",
            tag="toggle_bg"
        )
        self.toggle_canvas.create_text(
            7, 4,
            text="˄",
            fill="gray70",
            font=("Segoe UI", 6),
            tag="toggle_text"
        )

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Close", command=self.close_app)