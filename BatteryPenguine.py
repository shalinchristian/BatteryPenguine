import psutil
import tkinter as tk
import pygetwindow as gw
import time

# Configuration
WIDTH = 100
HEIGHT_FULL = 25
HEIGHT_COLLAPSED = 7
REFRESH_RATE = 1000  # ms
BG_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"

class BatteryMonitor:
    def __init__(self):
        self.is_hidden = False
        self.speed_text = "0▲|0▼"
        
        # Network stats
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()
        
        # Initialize UI
        self.setup_ui()
        self.start_tasks()

    def setup_ui(self):
        """Initialize all UI components"""
        self.root = tk.Tk()
        self.root.title("Battery+Network")
        self.root.geometry(f"{WIDTH}x{HEIGHT_FULL}")
        self.root.configure(bg=BG_COLOR)
        self.root.wm_attributes('-alpha', 0.5)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Position window (screen_width - 350, y=0)
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"+{screen_width - 350}+0")
        
        # Main canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=WIDTH, 
            height=HEIGHT_FULL, 
            bg=BG_COLOR, 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Battery percentage label
        self.label = tk.Label(
            self.canvas, 
            text="", 
            font=("Segoe UI", 12, "bold"), 
            fg=TEXT_COLOR, 
            bg=BG_COLOR
        )
        self.label.place(x=10, y=10, anchor="w")
        
        # Separator line
        self.canvas.create_line(
            0, 25, WIDTH, 25, 
            fill="gray40", 
            width=1, 
            tag="separator"
        )
        
        # Create toggle button in a separate top-level window
        self.toggle_root = tk.Toplevel(self.root)
        self.toggle_root.overrideredirect(True)
        self.toggle_root.wm_attributes('-alpha', 0.5)
        self.toggle_root.attributes("-topmost", True)
        self.toggle_root.geometry(f"15x8+{screen_width - 350 - 15}+0")
        self.toggle_root.configure(bg=BG_COLOR)
        
        # Toggle button canvas
        self.toggle_canvas = tk.Canvas(
            self.toggle_root,
            width=15,
            height=8,
            bg=BG_COLOR,
            highlightthickness=0
        )
        self.toggle_canvas.pack()
        
        # Toggle button elements
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
        
        # Bind events
        self.toggle_canvas.bind("<Button-1>", lambda e: self.toggle_visibility())
        
        # Right-click menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Close", command=self.close_app)
        self.canvas.bind("<Button-3>", self.show_menu)

        # Add these lines at the END of this method
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.toggle_root.protocol("WM_DELETE_WINDOW", self.close_app)

    def start_tasks(self):
        """Start all background update tasks"""
        self.update_battery()
        self.update_network()
        self.sync_toggle_position()

    def sync_toggle_position(self):
        """Keep toggle window positioned correctly"""
        if not self.root.winfo_exists():
            return
            
        x, y = self.root.winfo_x(), self.root.winfo_y()
        self.toggle_root.geometry(f"15x8+{x - 15}+{y}")
        self.root.after(50, self.sync_toggle_position)

    def get_battery_info(self):
        """Get battery info"""
        battery = psutil.sensors_battery()
        if battery:
            return (battery.percent, battery.power_plugged)
        return ("N/A", False)

    def get_network_speed(self):
        """Calculate current network speeds"""
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_elapsed = current_time - self.last_time
        
        if time_elapsed < 0.1:
            return self.speed_text
        
        upload = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) * 8 / 1024 / time_elapsed
        download = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) * 8 / 1024 / time_elapsed
        
        def format_speed(speed):
            return f"{speed/1000:.1f}M" if speed >= 1000 else f"{speed:.1f}K"
        
        result = f"{format_speed(upload)}▲" if upload > download else f"{format_speed(download)}▼"
        
        self.last_net_io = current_net_io
        self.last_time = current_time
        
        return result

    def update_battery(self):
        """Update battery percentage display"""
        percentage, charging = self.get_battery_info()
        
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
        """Update network speed display"""
        new_speed = self.get_network_speed()
        
        if new_speed != self.speed_text:
            self.canvas.delete("speed")
            self.speed_text = new_speed
            
            self.canvas.create_text(
                WIDTH-10, 10,
                text=new_speed,
                fill=TEXT_COLOR,
                font=("Segoe UI", 7),
                anchor="e",
                tag="speed",
                state="normal" if not self.is_hidden else "hidden"
            )
        
        self.root.after(REFRESH_RATE, self.update_network)

    def toggle_visibility(self):
        """Toggle between expanded and collapsed states"""
        if self.is_hidden:
            # Show the battery and network info (expand)
            self.is_hidden = False
            self.toggle_canvas.itemconfig("toggle_text", text="˄")
            self.root.geometry(f"{WIDTH}x{HEIGHT_FULL}")
            self.label.place(x=10, y=10, anchor="w")
            self.canvas.itemconfig("speed", state="normal")
            self.canvas.itemconfig("separator", state="normal")
        else:
            # Hide the battery and network info (collapse)
            self.is_hidden = True
            self.toggle_canvas.itemconfig("toggle_text", text="˅")
            self.root.geometry(f"{WIDTH}x{HEIGHT_COLLAPSED}")
            self.label.place_forget()
            self.canvas.itemconfig("speed", state="hidden")
            self.canvas.itemconfig("separator", state="hidden")

    def show_menu(self, event):
        """Show right-click context menu"""
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def close_app(self):
        """Clean up and exit"""
        self.toggle_root.destroy()
        self.root.quit()
        self.root.destroy()

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BatteryMonitor()
    app.run()
