import psutil
import tkinter as tk
import time
from collections import deque

# Configuration
WIDTH = 100
HEIGHT_FULL = 25
HEIGHT_COLLAPSED = 7
REFRESH_RATE = 1000  # ms
MAX_SAMPLES = 50

# Themes
DARK_THEME = {
    'bg': "#000000",
    'text': "#FFFFFF",
    'graph': "#00FFFF",
    'warning': "#FF5555",
    'charging': "#55FF55"
}

LIGHT_THEME = {
    'bg': "#F0F0F0",
    'text': "#000000",
    'graph': "#FF00FF",
    'warning': "#FF0000",
    'charging': "#00AA00"
}

class BatteryMonitor:
    def __init__(self):
        self.is_hidden = False
        self.is_dark_mode = True
        self.current_theme = DARK_THEME
        self.speed_text = "0▲|0▼"
        self.cpu_samples = deque(maxlen=MAX_SAMPLES)
        
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
        self.root.configure(bg=self.current_theme['bg'])
        self.root.wm_attributes('-alpha', 0.5)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Position window
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"+{screen_width - 350}+0")
        
        # Main canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=WIDTH, 
            height=HEIGHT_FULL, 
            bg=self.current_theme['bg'], 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Battery percentage label
        self.label = tk.Label(
            self.canvas, 
            text="", 
            font=("Segoe UI", 12, "bold"), 
            fg=self.current_theme['text'], 
            bg=self.current_theme['bg']
        )
        self.label.place(x=10, y=10, anchor="w")
        
        # Create toggle button in a separate top-level window
        self.toggle_root = tk.Toplevel(self.root)
        self.toggle_root.overrideredirect(True)
        self.toggle_root.wm_attributes('-alpha', 0.5)
        self.toggle_root.attributes("-topmost", True)
        self.toggle_root.geometry(f"15x8+{screen_width - 350 - 15}+0")
        self.toggle_root.configure(bg=self.current_theme['bg'])
        
        # Toggle button canvas
        self.toggle_canvas = tk.Canvas(
            self.toggle_root,
            width=15,
            height=8,
            bg=self.current_theme['bg'],
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
            font=("Segoe UI", 7, "bold"),
            tag="toggle_text"
        )
        
        # Bind events
        self.toggle_canvas.bind("<Button-1>", lambda e: self.toggle_visibility())
        
        # Right-click menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        self.menu.add_command(label="Close", command=self.close_app)
        self.canvas.bind("<Button-3>", self.show_menu)

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.toggle_root.protocol("WM_DELETE_WINDOW", self.close_app)
        
    def toggle_theme(self):
        """Switch between light and dark themes"""
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = DARK_THEME if self.is_dark_mode else LIGHT_THEME
        
        # Update all UI elements
        self.root.configure(bg=self.current_theme['bg'])
        self.canvas.configure(bg=self.current_theme['bg'])
        self.toggle_root.configure(bg=self.current_theme['bg'])
        self.toggle_canvas.configure(bg=self.current_theme['bg'])
        
        # Update label colors
        self.label.config(
            fg=self.current_theme['text'],
            bg=self.current_theme['bg']
        )
        
        # Update network speed display
        self.canvas.itemconfig("speed", fill=self.current_theme['text'])
        
        # Update CPU graph color
        self.canvas.itemconfig("cpu_graph", fill=self.current_theme['graph'])
        
        # Update toggle button colors
        self.toggle_canvas.itemconfig("toggle_bg", fill="gray30" if self.is_dark_mode else "gray70")
        self.toggle_canvas.itemconfig("toggle_text", fill="gray70" if self.is_dark_mode else "gray30")

    def start_tasks(self):
        """Start all background update tasks"""
        self.update_battery()
        self.update_network()
        self.update_cpu_graph()
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
                color = self.current_theme['charging']
            elif percentage <= 20:
                color = self.current_theme['warning']
            elif percentage == 100:
                color = self.current_theme['charging']
            else:
                color = self.current_theme['text']
            
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
                fill=self.current_theme['text'],
                font=("Segoe UI", 7, "bold"),
                anchor="e",
                tag="speed",
                state="normal" if not self.is_hidden else "hidden"
            )
        
        self.root.after(REFRESH_RATE, self.update_network)

    def update_cpu_graph(self):
        """Update the subtle CPU usage graph in background"""
        usage = psutil.cpu_percent()
        self.cpu_samples.append(usage)
        
        self.canvas.delete("cpu_graph")
        
        if not self.is_hidden and len(self.cpu_samples) > 1:
            max_height = HEIGHT_FULL - 5
            
            points = []
            for i, sample in enumerate(self.cpu_samples):
                x = i * (WIDTH / (len(self.cpu_samples) - 1))
                y = max_height - (sample / 100) * (max_height - 5)
                points.extend([x, y])
            
            self.canvas.create_line(
                points,
                fill=self.current_theme['graph'],
                width=1,
                smooth=True,
                tag="cpu_graph"
            )
        
        self.root.after(500, self.update_cpu_graph)

    def toggle_visibility(self):
        """Toggle between expanded and collapsed states"""
        if self.is_hidden:
            self.is_hidden = False
            self.toggle_canvas.itemconfig("toggle_text", text="˄")
            self.root.geometry(f"{WIDTH}x{HEIGHT_FULL}")
            self.label.place(x=10, y=10, anchor="w")
            self.canvas.itemconfig("speed", state="normal")
        else:
            self.is_hidden = True
            self.toggle_canvas.itemconfig("toggle_text", text="˅")
            self.root.geometry(f"{WIDTH}x{HEIGHT_COLLAPSED}")
            self.label.place_forget()
            self.canvas.itemconfig("speed", state="hidden")

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
