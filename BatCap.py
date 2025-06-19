import psutil
import tkinter as tk
import time
from collections import deque
from typing import Tuple, Optional, Deque, Dict, Callable


class Config:
    """Centralized configuration for the application"""
    # Window dimensions
    WIDTH = 100
    HEIGHT_FULL = 25
    HEIGHT_COLLAPSED = 7
    
    # Refresh rates (ms)
    BATTERY_UPDATE_INTERVAL = 2000
    NETWORK_UPDATE_INTERVAL = 1000
    CPU_UPDATE_INTERVAL = 500
    POSITION_SYNC_INTERVAL = 50
    
    # Data settings
    MAX_SAMPLES = 50
    
    # Color schemes
    DARK_THEME = {
        'bg': "#000000",
        'text': "#FFFFFF",
        'graph': "#00FFFF",
        'warning': "#FF5555",
        'charging': "#55FF55",
        'speed_bg': "#000000",
        'tooltip_bg': "#333333",
        'tooltip_text': "#FFFFFF"
    }
    
    LIGHT_THEME = {
        'bg': "#F0F0F0",
        'text': "#000000",
        'graph': "#FF00FF",
        'warning': "#FF0000",
        'charging': "#00AA00",
        'speed_bg': "#DDDDDD",
        'tooltip_bg': "#FFFFFF",
        'tooltip_text': "#000000"
    }


class Tooltip:
    """Enhanced tooltip class with better styling and positioning"""
    
    def __init__(self, widget: tk.Widget, text_func: Callable[[], str], theme: Dict[str, str]):
        """
        Initialize the tooltip
        
        Args:
            widget: The widget to attach the tooltip to
            text_func: Function that returns the tooltip text
            theme: Current theme dictionary
        """
        self.widget = widget
        self.text_func = text_func
        self.theme = theme
        self.tooltip_window = None
        self.tooltip_label = None
        
        # Bind events
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Motion>", self.update_tooltip_position)

    def show_tooltip(self, event=None):
        """Display the tooltip window"""
        if self.tooltip_window:
            return
            
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_attributes("-alpha", 0.9)
        
        # Create tooltip label
        self.tooltip_label = tk.Label(
            self.tooltip_window,
            text=self.text_func(),
            justify='left',
            background=self.theme['tooltip_bg'],
            foreground=self.theme['tooltip_text'],
            relief='solid',
            borderwidth=1,
            font=("Segoe UI", 8),
            padx=4,
            pady=2
        )
        self.tooltip_label.pack()
        
        # Position tooltip
        self.update_tooltip_position()
        
        # Start updates
        self.update_tooltip_content()

    def update_tooltip_content(self):
        """Update the tooltip text content"""
        if self.tooltip_window:
            self.tooltip_label.config(text=self.text_func())
            self.tooltip_window.after(1000, self.update_tooltip_content)

    def update_tooltip_position(self, event=None):
        """Update the tooltip position relative to the widget"""
        if not self.tooltip_window:
            return
            
        # Calculate position
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        
        # Adjust position to stay on screen
        screen_width = self.widget.winfo_screenwidth()
        tooltip_width = self.tooltip_window.winfo_reqwidth()
        
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 5
            
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        """Hide and destroy the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            self.tooltip_label = None

    def update_theme(self, new_theme: Dict[str, str]):
        """Update the tooltip colors when theme changes"""
        self.theme = new_theme
        if self.tooltip_label:
            self.tooltip_label.config(
                bg=new_theme['tooltip_bg'],
                fg=new_theme['tooltip_text']
            )


class BatteryMonitor:
    """Main application class for battery and network monitoring"""
    
    def __init__(self):
        # State tracking
        self.is_hidden = False
        self.is_dark_mode = True
        self.current_theme = Config.DARK_THEME
        
        # Data storage
        self.cpu_samples: Deque[float] = deque(maxlen=Config.MAX_SAMPLES)
        self.last_net_io = psutil.net_io_counters()
        self.last_update_time = time.time()
        self.speed_text = "0▼"
        
        # Initialize UI
        self.setup_main_window()
        self.setup_ui_components()
        self.setup_event_handlers()
        
        # Start monitoring tasks
        self.start_monitoring_tasks()

    def setup_main_window(self):
        """Configure the main application window"""
        self.root = tk.Tk()
        self.root.title("Battery+Network Monitor")
        self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT_FULL}")
        self.root.configure(bg=self.current_theme['bg'])
        self.root.wm_attributes('-alpha', 0.5)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Position window in top-right of screen
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"+{screen_width - 350}+0")
        
        # Create main canvas
        self.canvas = tk.Canvas(
            self.root,
            width=Config.WIDTH,
            height=Config.HEIGHT_FULL,
            bg=self.current_theme['bg'],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def setup_ui_components(self):
        """Create all UI components"""
        # Battery display
        self.battery_label = tk.Label(
            self.canvas,
            text="Initializing...",
            font=("Segoe UI", 12, "bold"),
            fg=self.current_theme['text'],
            bg=self.current_theme['bg']
        )
        self.battery_label.place(x=10, y=10, anchor=tk.W)
        
        # Tooltip for battery and CPU info
        self.battery_tooltip = Tooltip(
            self.battery_label,
            self.get_battery_tooltip_text,
            self.current_theme
        )

        # Network speed display background
        self.speed_bg = self.canvas.create_rectangle(
            Config.WIDTH - 60, 2,
            Config.WIDTH - 22, 18,
            fill=self.current_theme['speed_bg'],
            outline="",
            tags="speed_bg"
        )

        # Network speed text
        self.speed_display = self.canvas.create_text(
            Config.WIDTH - 8, 10,
            text=self.speed_text,
            fill=self.current_theme['text'],
            font=("Segoe UI", 8, "bold"),
            anchor=tk.E,
            tags="speed"
        )
        
        # Network speed tooltip
        self.speed_tooltip = Tooltip(
            self.canvas,
            self.get_network_tooltip_text,
            self.current_theme
        )
        
        # Toggle button
        self.setup_toggle_button()

    def setup_toggle_button(self):
        """Create the collapse/expand toggle button"""
        screen_width = self.root.winfo_screenwidth()
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
            tags="toggle_bg"
        )
        self.toggle_canvas.create_text(
            7, 4,
            text="˄",
            fill="gray70",
            font=("Segoe UI", 7, "bold"),
            tags="toggle_text"
        )

    def setup_event_handlers(self):
        """Configure all event bindings"""
        # Toggle button click
        self.toggle_canvas.bind("<Button-1>", lambda _: self.toggle_ui())
        
        # Right-click context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(
            label="Toggle Theme",
            command=self.toggle_theme
        )
        self.context_menu.add_command(
            label="Exit",
            command=self.cleanup_and_exit
        )
        self.canvas.bind("<Button-3>", self.show_context_menu)
        
        # Window management
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup_and_exit)
        self.toggle_root.protocol("WM_DELETE_WINDOW", self.cleanup_and_exit)

    def start_monitoring_tasks(self):
        """Start all background monitoring tasks"""
        self.update_battery()
        self.update_network()
        self.update_cpu_graph()
        self.sync_window_positions()

    def sync_window_positions(self):
        """Keep toggle window positioned correctly relative to main window"""
        if not self.root.winfo_exists():
            return
            
        x, y = self.root.winfo_x(), self.root.winfo_y()
        self.toggle_root.geometry(f"15x8+{x - 15}+{y}")
        self.root.after(Config.POSITION_SYNC_INTERVAL, self.sync_window_positions)

    def get_battery_info(self) -> Tuple[Optional[float], Optional[bool]]:
        """
        Retrieve battery information
        
        Returns:
            Tuple of (percentage, charging_status)
        """
        try:
            battery = psutil.sensors_battery()
            if battery:
                return (battery.percent, battery.power_plugged)
            return (None, None)
        except Exception:
            return (None, None)

    def get_battery_tooltip_text(self) -> str:
        """Generate text for battery tooltip"""
        percentage, charging = self.get_battery_info()
        cpu_usage = psutil.cpu_percent()
        
        if percentage is None:
            battery_text = "Battery: N/A"
        else:
            status = "Charging" if charging else "Discharging"
            battery_text = f"Battery: {percentage}% ({status})"
            
        return f"{battery_text}\nCPU Usage: {cpu_usage}%"

    def get_network_tooltip_text(self) -> str:
        """Generate text for network tooltip"""
        try:
            net_io = psutil.net_io_counters()
            return (
                f"Up: {net_io.bytes_sent / 1024:.1f} KB\n"
                f"Dw {net_io.bytes_recv / 1024:.1f} KB\n"
                f"Pac S: {net_io.packets_sent}\n"
                f"Pac R: {net_io.packets_recv}"
            )
        except Exception:
            return "Network information unavailable"

    def get_network_speed(self) -> str:
        """
        Calculate current network speed (shows only higher of upload/download)
        
        Returns:
            Formatted string showing the higher speed with direction indicator
        """
        try:
            current_net_io = psutil.net_io_counters()
            current_time = time.time()
            time_elapsed = current_time - self.last_update_time
            
            if time_elapsed < 0.1:  # Minimum interval to avoid spikes
                return self.speed_text
            
            # Calculate speeds in Kbps or Mbps
            upload = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) * 8 / 1024 / time_elapsed
            download = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) * 8 / 1024 / time_elapsed
            
            def format_speed(speed):
                return f"{speed/1000:.1f}M" if speed >= 1000 else f"{speed:.1f}K"
            
            self.last_net_io = current_net_io
            self.last_update_time = current_time
            
            # Show only the higher speed with appropriate direction indicator
            if upload > download:
                return f"{format_speed(upload)}▲"
            return f"{format_speed(download)}▼"
            
        except Exception:
            return "Err▼"

    def update_battery(self):
        """Update battery percentage display"""
        percentage, charging = self.get_battery_info()
        
        if percentage is None:
            self.battery_label.config(text="N/A", fg="gray")
        else:
            self.battery_label.config(text=f"{percentage}%")
            
            if charging:
                color = self.current_theme['charging']
            elif percentage <= 20:
                color = self.current_theme['warning']
            elif percentage == 100:
                color = self.current_theme['charging']
            else:
                color = self.current_theme['text']
            
            self.battery_label.config(fg=color)
        
        self.root.after(Config.BATTERY_UPDATE_INTERVAL, self.update_battery)

    def update_network(self):
        """Update network speed display (showing only higher speed)"""
        new_speed = self.get_network_speed()
        
        if new_speed != self.speed_text:
            self.speed_text = new_speed
            self.canvas.itemconfig(self.speed_display, text=new_speed)
        
        self.root.after(Config.NETWORK_UPDATE_INTERVAL, self.update_network)

    def update_cpu_graph(self):
        """Update the CPU usage graph"""
        if self.is_hidden:  # Skip updates when collapsed
            self.root.after(Config.CPU_UPDATE_INTERVAL, self.update_cpu_graph)
            return
            
        try:
            usage = psutil.cpu_percent()
            self.cpu_samples.append(usage)
            
            self.canvas.delete("cpu_graph")
            
            if len(self.cpu_samples) > 1:
                max_height = Config.HEIGHT_FULL - 5
                
                # Generate graph points
                points = []
                for i, sample in enumerate(self.cpu_samples):
                    x = i * (Config.WIDTH / (len(self.cpu_samples) - 1))
                    y = max_height - (sample / 100) * (max_height - 5)
                    points.extend([x, y])
                
                self.canvas.create_line(
                    points,
                    fill=self.current_theme['graph'],
                    width=1,
                    smooth=True,
                    tags="cpu_graph"
                )
                
        except Exception:
            pass
        
        self.root.after(Config.CPU_UPDATE_INTERVAL, self.update_cpu_graph)

    def toggle_ui(self):
        """Toggle between expanded and collapsed states"""
        self.is_hidden = not self.is_hidden
        
        if self.is_hidden:
            # Collapse the UI
            self.toggle_canvas.itemconfig("toggle_text", text="˅")
            self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT_COLLAPSED}")
            self.battery_label.place_forget()
            self.canvas.itemconfig(self.speed_display, state=tk.HIDDEN)
            self.canvas.itemconfig(self.speed_bg, state=tk.HIDDEN)
            self.canvas.delete("cpu_graph")
        else:
            # Expand the UI
            self.toggle_canvas.itemconfig("toggle_text", text="˄")
            self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT_FULL}")
            self.battery_label.place(x=10, y=10, anchor=tk.W)
            self.canvas.itemconfig(self.speed_display, state=tk.NORMAL)
            self.canvas.itemconfig(self.speed_bg, state=tk.NORMAL)

    def toggle_theme(self):
        """Switch between light and dark themes"""
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = Config.DARK_THEME if self.is_dark_mode else Config.LIGHT_THEME
        
        # Update all UI elements
        self.root.configure(bg=self.current_theme['bg'])
        self.canvas.configure(bg=self.current_theme['bg'])
        self.toggle_root.configure(bg=self.current_theme['bg'])
        self.toggle_canvas.configure(bg=self.current_theme['bg'])
        
        self.battery_label.config(
            fg=self.current_theme['text'],
            bg=self.current_theme['bg']
        )
        
        self.canvas.itemconfig(
            self.speed_display,
            fill=self.current_theme['text']
        )
        
        self.canvas.itemconfig(
            self.speed_bg,
            fill=self.current_theme['speed_bg']
        )
        
        # Update toggle button colors
        self.toggle_canvas.itemconfig(
            "toggle_bg",
            fill="gray30" if self.is_dark_mode else "gray70"
        )
        self.toggle_canvas.itemconfig(
            "toggle_text",
            fill="gray70" if self.is_dark_mode else "gray30"
        )
        
        # Update tooltips
        self.battery_tooltip.update_theme(self.current_theme)
        self.speed_tooltip.update_theme(self.current_theme)

    def show_context_menu(self, event):
        """Display the right-click context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def cleanup_and_exit(self):
        """Properly clean up resources and exit"""
        self.toggle_root.destroy()
        self.root.quit()
        self.root.destroy()

    def run(self):
        """Start the application main loop"""
        self.root.mainloop()


if __name__ == "__main__":
    app = BatteryMonitor()
    app.run()
