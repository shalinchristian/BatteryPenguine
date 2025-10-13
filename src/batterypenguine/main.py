import tkinter as tk
import psutil
import time
from . import config, utils
from .gui import BatteryMonitorGUI

class BatteryMonitor(BatteryMonitorGUI):
    def __init__(self):
        super().__init__()
        self.is_hidden = False
        self.speed_text = "0▲|0▼"
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()

        self.toggle_canvas.bind("<Button-1>", lambda e: self.toggle_visibility())
        self.canvas.bind("<Button-3>", self.show_menu)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.toggle_root.protocol("WM_DELETE_WINDOW", self.close_app)

        self.start_tasks()

    def start_tasks(self):
        self.update_battery()
        self.update_network()
        self.sync_toggle_position()

    def sync_toggle_position(self):
        if not self.root.winfo_exists():
            return
        x, y = self.root.winfo_x(), self.root.winfo_y()
        self.toggle_root.geometry(f"15x8+{x - 15}+{y}")
        self.root.after(50, self.sync_toggle_position)

    def update_battery(self):
        percentage, charging = utils.get_battery_info()
        if percentage == "N/A":
            self.label.config(text="N/A", fg="gray")
        else:
            self.label.config(text=f"{percentage}%")
            if charging:
                color = "lime"
            elif percentage <= 20:
                color = "red"
            elif percentage == 100:
                color = "lime"
            else:
                color = "white"
            self.label.config(fg=color)
        self.root.after(2000, self.update_battery)

    def update_network(self):
        new_speed, self.last_net_io, self.last_time = utils.get_network_speed(
            self.last_net_io, self.last_time, self.speed_text
        )
        if new_speed != self.speed_text:
            self.canvas.delete("speed")
            self.speed_text = new_speed
            self.canvas.create_text(
                config.WIDTH - 10, 10,
                text=new_speed,
                fill=config.TEXT_COLOR,
                font=("Segoe UI", 7),
                anchor="e",
                tag="speed",
                state="normal" if not self.is_hidden else "hidden"
            )
        self.root.after(config.REFRESH_RATE, self.update_network)

    def toggle_visibility(self):
        if self.is_hidden:
            self.is_hidden = False
            self.toggle_canvas.itemconfig("toggle_text", text="˄")
            self.root.geometry(f"{config.WIDTH}x{config.HEIGHT_FULL}")
            self.label.place(x=10, y=10, anchor="w")
            self.canvas.itemconfig("speed", state="normal")
        else:
            self.is_hidden = True
            self.toggle_canvas.itemconfig("toggle_text", text="˅")
            self.root.geometry(f"{config.WIDTH}x{config.HEIGHT_COLLAPSED}")
            self.label.place_forget()
            self.canvas.itemconfig("speed", state="hidden")

    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def close_app(self):
        self.toggle_root.destroy()
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BatteryMonitor()
    app.run()